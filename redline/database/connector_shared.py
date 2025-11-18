#!/usr/bin/env python3
"""
DatabaseConnector class extracted from data_module_shared.py (shared module)
Handles database operations for DuckDB.
"""

import logging
from typing import Union, Any
import pandas as pd

# Optional dependencies
try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None

try:
    import duckdb
except ImportError:
    duckdb = None

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Legacy database connector for DuckDB operations."""
    
    def __init__(self, db_path: str = '/app/redline_data.duckdb'):
        """Initialize database connector."""
        self.db_path = db_path

    def create_connection(self, db_path: str):
        """Create a database connection."""
        if not duckdb:
            raise ImportError("duckdb is not installed")
        return duckdb.connect(db_path)

    def read_shared_data(self, table: str, format: str) -> Union[pd.DataFrame, Any, Any]:
        """Read data from shared table."""
        try:
            if not duckdb:
                raise ImportError("duckdb is not installed")
            conn = duckdb.connect(self.db_path)
            df = conn.execute(f"SELECT * FROM {table}").fetchdf()
            conn.close()
            if format == 'polars' and pl:
                return pl.from_pandas(df)
            elif format == 'pyarrow' and pa:
                return pa.Table.from_pandas(df)
            return df
        except Exception as e:
            logger.error(f"Failed to read from {table}: {str(e)}")
            print(f"Failed to read from {table}: {str(e)}")
            raise

    def write_shared_data(self, table: str, data: Union[pd.DataFrame, Any, Any], 
                         format: str) -> None:
        """Write data to shared table."""
        try:
            if not duckdb:
                raise ImportError("duckdb is not installed")
            # Convert to pandas if needed
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, pa.Table):
                data = data.to_pandas()
            
            # Import DataLoader for clean_and_select_columns
            from redline.core.data_loader_shared import DataLoader
            data['format'] = format
            data = DataLoader.clean_and_select_columns(data)
            
            # Diagnostic output
            print("Column dtypes before saving:")
            print(data.dtypes)
            for col in ['open', 'high', 'low', 'close', 'vol', 'openint']:
                if col in data.columns:
                    print(f"Sample values for {col}:")
                    print(data[col].head(10).to_list())
            
            # Create table and insert data
            conn = duckdb.connect(self.db_path)
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
            conn.register('temp_df', data)
            insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
            conn.execute(insert_sql)
            conn.unregister('temp_df')
            conn.close()
            logger.info(f"Wrote data to {table} in format {format}")
        except Exception as e:
            logger.exception(f"Failed to write to {table}: {str(e)}")
            print(f"Failed to write to {table}: {str(e)}")
            raise

