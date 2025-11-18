#!/usr/bin/env python3
"""
DataSource class extracted from data_module_shared.py (shared module)
Abstract data source for virtual scrolling.
"""

import logging
import pandas as pd

# Optional dependencies
try:
    import duckdb
except ImportError:
    duckdb = None

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None

logger = logging.getLogger(__name__)


class DataSource:
    """Abstract data source for virtual scrolling."""
    
    def __init__(self, file_path, format_type):
        """Initialize data source."""
        self.file_path = file_path
        self.format_type = format_type
        self.connection = None
        self.total_rows = 0
        self._initialize()
        
    def _initialize(self):
        """Initialize the data source."""
        if self.format_type == 'duckdb' and duckdb:
            self.connection = duckdb.connect(self.file_path)
            self.total_rows = self.connection.execute(
                "SELECT COUNT(*) FROM tickers_data"
            ).fetchone()[0]
        else:
            # For other formats, load into memory
            from redline.core.data_loader_shared import DataLoader
            df = DataLoader.load_file_by_type(self.file_path, self.format_type)
            if isinstance(df, pd.DataFrame):
                self.data = df
                self.total_rows = len(df)
            else:
                # Convert other formats to pandas
                if pl and isinstance(df, pl.DataFrame):
                    self.data = df.to_pandas()
                elif pa and isinstance(df, pa.Table):
                    self.data = df.to_pandas()
                else:
                    self.data = pd.DataFrame()
                self.total_rows = len(self.data)
                
    def get_total_rows(self):
        """Get total number of rows."""
        return self.total_rows
        
    def get_row(self, index):
        """Get a specific row by index."""
        if self.format_type == 'duckdb' and self.connection:
            query = f"SELECT * FROM tickers_data LIMIT 1 OFFSET {index}"
            result = self.connection.execute(query).fetchone()
            return list(result) if result else []
        else:
            if hasattr(self, 'data') and index < len(self.data):
                return list(self.data.iloc[index])
            return []
            
    def get_rows(self, start, end):
        """Get a range of rows."""
        if self.format_type == 'duckdb' and self.connection:
            query = f"SELECT * FROM tickers_data LIMIT {end - start} OFFSET {start}"
            result = self.connection.execute(query).fetchdf()
            return [list(row) for _, row in result.iterrows()]
        else:
            if hasattr(self, 'data'):
                return [list(row) for _, row in self.data.iloc[start:end].iterrows()]
            return []
            
    def close(self):
        """Close the data source."""
        if self.connection:
            self.connection.close()

