#!/usr/bin/env python3
"""
REDLINE Database Connector
Handles database connections and basic CRUD operations.
"""

import logging
import pandas as pd
from typing import Union

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

class DatabaseConnector:
    """Handles database connections and basic operations."""
    
    def __init__(self, db_path: str = '/app/redline_data.duckdb'):
        """Initialize database connector."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def create_connection(self, db_path: str = None):
        """
        Create a database connection.
        
        Args:
            db_path: Database path (optional, uses instance path if not provided)
            
        Returns:
            Database connection object
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError("duckdb not available. Please install duckdb to use database features.")
        
        try:
            path = db_path or self.db_path
            conn = duckdb.connect(path)
            return conn
        except Exception as e:
            self.logger.error(f"Failed to create database connection: {str(e)}")
            raise
    
    def read_shared_data(self, table: str, format: str = 'pandas') -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']:
        """
        Read data from a shared table.
        
        Args:
            table: Table name
            format: Output format ('pandas', 'polars', 'pyarrow')
            
        Returns:
            Data in requested format
        """
        try:
            conn = self.create_connection()
            df = conn.execute(f"SELECT * FROM {table}").fetchdf()
            conn.close()
            
            if format == 'polars':
                return pl.from_pandas(df)
            elif format == 'pyarrow':
                return pa.Table.from_pandas(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to read from {table}: {str(e)}")
            raise
    
    def write_shared_data(self, table: str, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], format: str) -> None:
        """
        Write data to a shared table.
        
        Args:
            table: Table name
            data: Data to write
            format: Data format identifier
        """
        try:
            # Convert to pandas if needed
            if POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif PYARROW_AVAILABLE and isinstance(data, pa.Table):
                data = data.to_pandas()
            
            # Add format column
            data['format'] = format
            
            # Create table and insert data
            conn = self.create_connection()
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                ticker VARCHAR,
                timestamp TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                vol DOUBLE,
                openint DOUBLE,
                format VARCHAR
            )
            """
            conn.execute(create_table_sql)
            
            # Insert data
            conn.register('temp_df', data)
            insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
            conn.execute(insert_sql)
            conn.unregister('temp_df')
            conn.close()
            
            self.logger.info(f"Wrote data to {table} in format {format}")
            
        except Exception as e:
            self.logger.exception(f"Failed to write to {table}: {str(e)}")
            raise
    
    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results as DataFrame
        """
        try:
            conn = self.create_connection()
            
            if params:
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()
            
            conn.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            conn = self.create_connection()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = conn.execute(query, [table_name]).fetchall()
            conn.close()
            return len(result) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check if table {table_name} exists: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        try:
            conn = self.create_connection()
            
            # Get row count
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            
            # Get column info
            columns_result = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            columns = [col[1] for col in columns_result] if columns_result else []
            
            # Get sample data
            sample_result = conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
            
            conn.close()
            
            return {
                'row_count': row_count,
                'columns': columns,
                'sample_data': sample_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return {}
    
    def backup_table(self, table_name: str, backup_suffix: str = None) -> str:
        """
        Create a backup of a table.
        
        Args:
            table_name: Name of the table to backup
            backup_suffix: Suffix for backup table name
            
        Returns:
            Name of the backup table
        """
        try:
            if backup_suffix is None:
                from datetime import datetime
                backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            backup_table_name = f"{table_name}_backup_{backup_suffix}"
            
            conn = self.create_connection()
            conn.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}")
            conn.close()
            
            self.logger.info(f"Created backup table: {backup_table_name}")
            return backup_table_name
            
        except Exception as e:
            self.logger.error(f"Failed to backup table {table_name}: {str(e)}")
            raise
    
    def restore_table(self, backup_table_name: str, target_table_name: str) -> None:
        """
        Restore a table from backup.
        
        Args:
            backup_table_name: Name of the backup table
            target_table_name: Name of the target table to restore to
        """
        try:
            conn = self.create_connection()
            
            # Drop target table if it exists
            conn.execute(f"DROP TABLE IF EXISTS {target_table_name}")
            
            # Restore from backup
            conn.execute(f"CREATE TABLE {target_table_name} AS SELECT * FROM {backup_table_name}")
            
            conn.close()
            
            self.logger.info(f"Restored table {target_table_name} from {backup_table_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore table {target_table_name}: {str(e)}")
            raise
