#!/usr/bin/env python3
"""
REDLINE Optimized Database Connector
Enhanced database connector with connection pooling and query caching for improved performance.
"""

import logging
import pandas as pd
import threading
import time
import hashlib
from typing import Union, Dict, Any, Optional, List
from functools import lru_cache
import queue

# Optional dependencies
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None
    DUCKDB_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False

try:
    import pyarrow as pa
    PYARROW_AVAILABLE = True
except ImportError:
    pa = None
    PYARROW_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConnectionPool:
    """Thread-safe connection pool for database connections."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        """Initialize connection pool."""
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.active_connections = 0
        self.logger = logging.getLogger(__name__)
        
        # Pre-populate pool with initial connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with initial connections."""
        try:
            for _ in range(min(3, self.max_connections)):  # Start with 3 connections
                conn = self._create_connection()
                self.pool.put(conn)
                self.active_connections += 1
            self.logger.info(f"Initialized connection pool with {self.active_connections} connections")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {str(e)}")
    
    def _create_connection(self):
        """Create a new database connection."""
        if not DUCKDB_AVAILABLE:
            raise ImportError("duckdb not available. Please install duckdb to use database features.")
        
        try:
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = duckdb.connect(self.db_path)
            return conn
        except Exception as e:
            self.logger.error(f"Failed to create database connection: {str(e)}")
            raise
    
    def get_connection(self, timeout: int = 30):
        """Get a connection from the pool."""
        try:
            # Try to get existing connection
            conn = self.pool.get(timeout=timeout)
            return conn
        except queue.Empty:
            # Pool is empty, try to create new connection
            with self.lock:
                if self.active_connections < self.max_connections:
                    conn = self._create_connection()
                    self.active_connections += 1
                    self.logger.debug(f"Created new connection. Active: {self.active_connections}")
                    return conn
                else:
                    # Wait for a connection to become available
                    conn = self.pool.get(timeout=timeout)
                    return conn
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            conn.close()
            with self.lock:
                self.active_connections -= 1
            self.logger.debug(f"Closed excess connection. Active: {self.active_connections}")
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break
            self.active_connections = 0
        self.logger.info("Closed all connections in pool")

class QueryCache:
    """Thread-safe query result cache with TTL."""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        """Initialize query cache."""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def _generate_key(self, query: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for query and parameters."""
        cache_string = f"{query}:{str(params) if params else ''}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query: str, params: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
        """Get cached query result."""
        with self.lock:
            key = self._generate_key(query, params)
            
            if key in self.cache:
                cached_item = self.cache[key]
                
                # Check TTL
                if time.time() - cached_item['timestamp'] < self.ttl_seconds:
                    self.logger.debug(f"Cache hit for query: {query[:50]}...")
                    return cached_item['result'].copy()
                else:
                    # Expired, remove from cache
                    del self.cache[key]
                    self.logger.debug(f"Cache expired for query: {query[:50]}...")
            
            return None
    
    def set(self, query: str, result: pd.DataFrame, params: Dict[str, Any] = None):
        """Cache query result."""
        with self.lock:
            # Remove oldest entries if cache is full
            while len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
            
            key = self._generate_key(query, params)
            self.cache[key] = {
                'result': result.copy(),
                'timestamp': time.time()
            }
            self.logger.debug(f"Cached query result: {query[:50]}...")
    
    def clear(self):
        """Clear all cached results."""
        with self.lock:
            self.cache.clear()
        self.logger.info("Cleared query cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'oldest_entry': min((item['timestamp'] for item in self.cache.values()), default=None),
                'newest_entry': max((item['timestamp'] for item in self.cache.values()), default=None)
            }

class OptimizedDatabaseConnector:
    """Optimized database connector with connection pooling and query caching."""
    
    def __init__(self, db_path: str = None, max_connections: int = 10, cache_size: int = 128, cache_ttl: int = 300):
        """Initialize optimized database connector."""
        if db_path is None:
            import os
            db_path = os.path.join(os.getcwd(), 'redline_data.duckdb')
        
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool and query cache
        self.connection_pool = ConnectionPool(db_path, max_connections)
        self.query_cache = QueryCache(cache_size, cache_ttl)
        
        self.logger.info(f"Initialized optimized database connector with {max_connections} connections and {cache_size} cache entries")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None, use_cache: bool = True) -> pd.DataFrame:
        """Execute a SQL query with caching and connection pooling."""
        try:
            # Check cache first
            if use_cache:
                cached_result = self.query_cache.get(query, params)
                if cached_result is not None:
                    return cached_result
            
            # Get connection from pool
            conn = self.connection_pool.get_connection()
            
            try:
                # Execute query
                if params:
                    result = conn.execute(query, params).fetchdf()
                else:
                    result = conn.execute(query).fetchdf()
                
                # Cache result if caching is enabled
                if use_cache:
                    self.query_cache.set(query, result, params)
                
                return result
                
            finally:
                # Return connection to pool
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            raise
    
    @lru_cache(maxsize=32)
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get table information with caching."""
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                # Get row count
                count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                row_count = count_result[0] if count_result else 0
                
                # Get column info
                columns_result = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                columns = [col[1] for col in columns_result] if columns_result else []
                
                # Get sample data
                sample_result = conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
                
                return {
                    'row_count': row_count,
                    'columns': columns,
                    'sample_data': sample_result
                }
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return {}
    
    def create_indexes(self, table_name: str = 'tickers_data') -> None:
        """
        Create indexes for common query patterns to improve performance.
        
        Args:
            table_name: Name of the table to create indexes for
        """
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                self.logger.info(f"Creating indexes for {table_name}...")
                
                # Create indexes for common query patterns
                indexes = [
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_ticker ON {table_name}(ticker)",
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name}(timestamp)",
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_ticker_timestamp ON {table_name}(ticker, timestamp)",
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_close ON {table_name}(close)",
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_volume ON {table_name}(vol)"
                ]
                
                for index_sql in indexes:
                    try:
                        conn.execute(index_sql)
                        self.logger.debug(f"Created index: {index_sql[:50]}...")
                    except Exception as e:
                        self.logger.warning(f"Failed to create index: {str(e)}")
                
                # Commit indexes
                conn.commit()
                self.logger.info(f"Successfully created indexes for {table_name}")
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to create indexes for {table_name}: {str(e)}")
    
    def drop_indexes(self, table_name: str = 'tickers_data') -> None:
        """
        Drop indexes for a table (useful for performance testing or index recreation).
        
        Args:
            table_name: Name of the table to drop indexes for
        """
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                self.logger.info(f"Dropping indexes for {table_name}...")
                
                # Drop indexes for the table
                indexes = [
                    f"DROP INDEX IF EXISTS idx_{table_name}_ticker",
                    f"DROP INDEX IF EXISTS idx_{table_name}_timestamp",
                    f"DROP INDEX IF EXISTS idx_{table_name}_ticker_timestamp",
                    f"DROP INDEX IF EXISTS idx_{table_name}_close",
                    f"DROP INDEX IF EXISTS idx_{table_name}_volume"
                ]
                
                for index_sql in indexes:
                    try:
                        conn.execute(index_sql)
                        self.logger.debug(f"Dropped index: {index_sql}")
                    except Exception as e:
                        self.logger.warning(f"Failed to drop index: {str(e)}")
                
                # Commit changes
                conn.commit()
                self.logger.info(f"Successfully dropped indexes for {table_name}")
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to drop indexes for {table_name}: {str(e)}")
    
    def get_index_info(self, table_name: str = 'tickers_data') -> List[Dict[str, Any]]:
        """
        Get information about indexes for a table.
        
        Args:
            table_name: Name of the table to get index info for
            
        Returns:
            List of index information dictionaries
        """
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                # Get index information
                result = conn.execute(
                    "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND tbl_name=?",
                    [table_name]
                ).fetchall()
                
                indexes = []
                for row in result:
                    indexes.append({
                        'name': row[0],
                        'table': row[1],
                        'sql': row[2]
                    })
                
                return indexes
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to get index info for {table_name}: {str(e)}")
            return []
    
    def analyze_table(self, table_name: str = 'tickers_data') -> None:
        """
        Run ANALYZE on a table to update query planner statistics.
        
        Args:
            table_name: Name of the table to analyze
        """
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                self.logger.info(f"Running ANALYZE on {table_name}...")
                conn.execute(f"ANALYZE {table_name}")
                self.logger.info(f"Successfully analyzed {table_name}")
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to analyze {table_name}: {str(e)}")
    
    def read_shared_data(self, table: str, format: str = 'pandas') -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']:
        """Read data from a shared table with connection pooling."""
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                df = conn.execute(f"SELECT * FROM {table}").fetchdf()
                
                if format == 'polars':
                    return pl.from_pandas(df)
                elif format == 'pyarrow':
                    return pa.Table.from_pandas(df)
                
                return df
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to read from {table}: {str(e)}")
            raise
    
    def write_shared_data(self, table: str, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], format: str) -> None:
        """Write data to a shared table with connection pooling."""
        try:
            # Convert to pandas if needed
            if POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif PYARROW_AVAILABLE and isinstance(data, pa.Table):
                data = data.to_pandas()
            
            # Add format column
            data['format'] = format
            
            conn = self.connection_pool.get_connection()
            
            try:
                # Drop table if exists
                conn.execute(f"DROP TABLE IF EXISTS {table}")
                
                # Handle Stooq format columns
                db_data = data.copy()
                if '<TICKER>' in db_data.columns:
                    db_data['ticker'] = db_data['<TICKER>']
                if '<DATE>' in db_data.columns:
                    db_data['timestamp'] = pd.to_datetime(db_data['<DATE>'], format='%Y%m%d')
                if '<OPEN>' in db_data.columns:
                    db_data['open'] = db_data['<OPEN>']
                if '<HIGH>' in db_data.columns:
                    db_data['high'] = db_data['<HIGH>']
                if '<LOW>' in db_data.columns:
                    db_data['low'] = db_data['<LOW>']
                if '<CLOSE>' in db_data.columns:
                    db_data['close'] = db_data['<CLOSE>']
                if '<VOL>' in db_data.columns:
                    db_data['vol'] = db_data['<VOL>']
                
                # Select standard columns for database
                standard_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol']
                available_columns = [col for col in standard_columns if col in db_data.columns]
                
                if not available_columns or len(db_data) == 0:
                    raise ValueError(f"Cannot write empty data or data with no valid columns to {table}")
                
                db_data = db_data[available_columns]
                
                # Create table
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    ticker VARCHAR,
                    timestamp TIMESTAMP,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    vol DOUBLE
                )
                """
                conn.execute(create_table_sql)
                
                # Insert data
                if len(db_data) > 0:
                    conn.register('temp_df', db_data)
                    conn.execute(f"INSERT INTO {table} SELECT * FROM temp_df")
                    conn.unregister('temp_df')
                
                # Create indexes for better query performance
                try:
                    indexes = [
                        f"CREATE INDEX IF NOT EXISTS idx_{table}_ticker ON {table}(ticker)",
                        f"CREATE INDEX IF NOT EXISTS idx_{table}_timestamp ON {table}(timestamp)",
                        f"CREATE INDEX IF NOT EXISTS idx_{table}_ticker_timestamp ON {table}(ticker, timestamp)",
                        f"CREATE INDEX IF NOT EXISTS idx_{table}_close ON {table}(close)",
                        f"CREATE INDEX IF NOT EXISTS idx_{table}_volume ON {table}(vol)"
                    ]
                    
                    for index_sql in indexes:
                        try:
                            conn.execute(index_sql)
                        except Exception as e:
                            self.logger.debug(f"Index may already exist: {str(e)}")
                            
                except Exception as e:
                    self.logger.warning(f"Failed to create indexes: {str(e)}")
                
                self.logger.info(f"Wrote data to {table} in format {format}")
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to write to {table}: {str(e)}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            conn = self.connection_pool.get_connection()
            
            try:
                query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
                result = conn.execute(query, [table_name]).fetchall()
                return len(result) > 0
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Failed to check if table {table_name} exists: {str(e)}")
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the database connector."""
        cache_stats = self.query_cache.get_stats()
        pool_stats = {
            'active_connections': self.connection_pool.active_connections,
            'max_connections': self.connection_pool.max_connections,
            'pool_size': self.connection_pool.pool.qsize()
        }
        
        return {
            'cache': cache_stats,
            'connection_pool': pool_stats
        }
    
    def close(self):
        """Close all connections and clear cache."""
        self.connection_pool.close_all()
        self.query_cache.clear()
        self.logger.info("Closed optimized database connector")
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        try:
            self.close()
        except:
            pass
