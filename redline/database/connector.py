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
    
    def __init__(self, db_path: str = None):
        """Initialize database connector."""
        if db_path is None:
            # Use local path instead of Docker path
            import os
            db_path = os.path.join(os.getcwd(), 'redline_data.duckdb')
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """
        Check if database is available.

        Returns:
            True if database can be connected, False otherwise
        """
        if not DUCKDB_AVAILABLE:
            return False

        conn = None
        try:
            conn = self.create_connection()
            return True
        except Exception as e:
            self.logger.warning(f"Database not available: {str(e)}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def get_tables(self) -> list:
        """
        Get list of all tables in the database.

        Returns:
            List of table names
        """
        conn = None
        try:
            conn = self.create_connection()

            # Query table names from DuckDB's system catalog
            result = conn.execute("SHOW TABLES").fetchall()
            tables = [row[0] for row in result] if result else []

            return tables
        except Exception as e:
            self.logger.error(f"Failed to get tables: {str(e)}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def create_connection(self, db_path: str = None):
        """
        Create a database connection.

        Args:
            db_path: Database path (optional, uses instance path if not provided)

        Returns:
            Database connection object
        """
        # Pre-validation with if-else
        if not DUCKDB_AVAILABLE:
            self.logger.error("duckdb not available - cannot create connection")
            raise ImportError("duckdb not available. Please install duckdb to use database features.")

        path = db_path or self.db_path

        if not path:
            self.logger.error("Database path is empty or None")
            raise ValueError("Database path cannot be empty")

        if not isinstance(path, str):
            self.logger.error(f"Database path must be a string, got {type(path)}")
            raise TypeError(f"Database path must be a string, got {type(path)}")

        try:

            # Create directory if it doesn't exist (fix for empty dirname)
            import os
            import time
            parent_dir = os.path.dirname(path)
            if parent_dir:  # Only create if parent_dir is not empty
                os.makedirs(parent_dir, exist_ok=True)

            # Connect to database with retry logic for transient lock conditions
            max_retries = 3
            retry_delay = 0.5  # Start with 500ms
            conn = None

            for attempt in range(max_retries):
                try:
                    conn = duckdb.connect(path)
                    return conn
                except Exception as lock_error:
                    error_msg = str(lock_error).lower()
                    if 'lock' in error_msg or 'conflicting' in error_msg:
                        # Database is locked
                        if attempt < max_retries - 1:
                            # Retry with exponential backoff
                            self.logger.warning(f"Database locked (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s: {str(lock_error)}")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            # Final attempt: try read-only mode
                            self.logger.warning(f"Database locked after {max_retries} attempts, attempting read-only connection")
                            try:
                                conn = duckdb.connect(path, read_only=True)
                                self.logger.info("Connected in read-only mode")
                                return conn
                            except Exception as read_error:
                                self.logger.error(f"Failed to connect even in read-only mode: {str(read_error)}")
                                raise lock_error  # Raise original error
                    else:
                        # Not a lock error, raise immediately
                        raise

            # Should not reach here, but just in case
            raise RuntimeError(f"Failed to connect to database after {max_retries} attempts")
        except PermissionError as e:
            self.logger.error(f"Permission denied accessing database {path}: {str(e)}")
            raise
        except OSError as e:
            self.logger.error(f"OS error creating database connection to {path}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating database connection: {str(e)}")
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
        # Pre-validation with if-else
        if not table:
            self.logger.error("Table name is empty or None")
            raise ValueError("Table name cannot be empty")

        if not isinstance(table, str):
            self.logger.error(f"Table name must be a string, got {type(table)}")
            raise TypeError(f"Table name must be a string, got {type(table)}")

        valid_formats = ['pandas', 'polars', 'pyarrow']
        if format not in valid_formats:
            self.logger.error(f"Invalid format: {format}. Must be one of {valid_formats}")
            raise ValueError(f"Format must be one of {valid_formats}, got: {format}")

        if format == 'polars' and not POLARS_AVAILABLE:
            self.logger.error("Polars not available but requested")
            raise ImportError("polars not available. Install with: pip install polars")

        if format == 'pyarrow' and not PYARROW_AVAILABLE:
            self.logger.error("PyArrow not available but requested")
            raise ImportError("pyarrow not available. Install with: pip install pyarrow")

        conn = None
        try:
            conn = self.create_connection()
            df = conn.execute(f"SELECT * FROM {table}").fetchdf()

            if format == 'polars':
                return pl.from_pandas(df)
            elif format == 'pyarrow':
                return pa.Table.from_pandas(df)

            return df

        except duckdb.CatalogException as e:
            self.logger.error(f"Table not found or catalog error reading {table}: {str(e)}")
            raise
        except duckdb.ConnectionException as e:
            self.logger.error(f"Database connection error reading {table}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error reading from {table}: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def write_shared_data(self, table: str, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], format: str) -> None:
        """
        Write data to a shared table.

        Args:
            table: Table name
            data: Data to write
            format: Data format identifier
        """
        # Pre-validation with if-else
        if not table:
            self.logger.error("Table name is empty or None")
            raise ValueError("Table name cannot be empty")

        if not isinstance(table, str):
            self.logger.error(f"Table name must be a string, got {type(table)}")
            raise TypeError(f"Table name must be a string, got {type(table)}")

        if data is None:
            self.logger.error("Data is None - cannot write")
            raise ValueError("Data cannot be None")

        if not isinstance(data, (pd.DataFrame, pl.DataFrame if POLARS_AVAILABLE else type(None), pa.Table if PYARROW_AVAILABLE else type(None))):
            self.logger.error(f"Data must be pandas DataFrame, polars DataFrame, or pyarrow Table, got {type(data)}")
            raise TypeError(f"Invalid data type: {type(data)}")

        if not format:
            self.logger.error("Format is empty or None")
            raise ValueError("Format cannot be empty")

        conn = None
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

            # Convert Stooq format to standard format for database storage
            db_data = data.copy()

            # Handle Stooq format columns
            if '<TICKER>' in db_data.columns:
                db_data['ticker'] = db_data['<TICKER>']
            if '<DATE>' in db_data.columns:
                # Convert YYYYMMDD to proper timestamp
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

            # Check if we have any valid columns and data
            if not available_columns or len(db_data) == 0:
                raise ValueError(f"Cannot write empty data or data with no valid columns to {table}")

            db_data = db_data[available_columns]

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

            # Insert data only if we have valid data
            if len(db_data) > 0 and len(db_data.columns) > 0:
                conn.register('temp_df', db_data)
                insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
                conn.execute(insert_sql)
                conn.unregister('temp_df')
            else:
                self.logger.warning(f"No data to insert into {table}")

            self.logger.info(f"Wrote data to {table} in format {format}")

        except duckdb.CatalogException as e:
            self.logger.error(f"Database catalog error writing to {table}: {str(e)}")
            raise
        except duckdb.ConnectionException as e:
            self.logger.error(f"Database connection error writing to {table}: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Value error writing to {table}: {str(e)}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error writing to {table}: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query results as DataFrame
        """
        conn = None
        try:
            conn = self.create_connection()

            if params:
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()

            return result

        except Exception as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        conn = None
        try:
            conn = self.create_connection()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = conn.execute(query, [table_name]).fetchall()
            return len(result) > 0

        except Exception as e:
            self.logger.error(f"Failed to check if table {table_name} exists: {str(e)}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table information
        """
        conn = None
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

            return {
                'row_count': row_count,
                'columns': columns,
                'sample_data': sample_result
            }

        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return {}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def backup_table(self, table_name: str, backup_suffix: str = None) -> str:
        """
        Create a backup of a table.

        Args:
            table_name: Name of the table to backup
            backup_suffix: Suffix for backup table name

        Returns:
            Name of the backup table
        """
        conn = None
        try:
            if backup_suffix is None:
                from datetime import datetime
                backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')

            backup_table_name = f"{table_name}_backup_{backup_suffix}"

            conn = self.create_connection()
            conn.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}")

            self.logger.info(f"Created backup table: {backup_table_name}")
            return backup_table_name

        except Exception as e:
            self.logger.error(f"Failed to backup table {table_name}: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def restore_table(self, backup_table_name: str, target_table_name: str) -> None:
        """
        Restore a table from backup.

        Args:
            backup_table_name: Name of the backup table
            target_table_name: Name of the target table to restore to
        """
        conn = None
        try:
            conn = self.create_connection()

            # Drop target table if it exists
            conn.execute(f"DROP TABLE IF EXISTS {target_table_name}")

            # Restore from backup
            conn.execute(f"CREATE TABLE {target_table_name} AS SELECT * FROM {backup_table_name}")

            self.logger.info(f"Restored table {target_table_name} from {backup_table_name}")

        except Exception as e:
            self.logger.error(f"Failed to restore table {target_table_name}: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
