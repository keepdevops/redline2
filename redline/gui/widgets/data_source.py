#!/usr/bin/env python3
"""
REDLINE GUI Data Source Widget
Abstract data source for virtual scrolling in GUI components.
"""

import logging
import pandas as pd
from typing import List, Union
from ...core.data_loader import DataLoader

# Optional dependencies
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

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None
    DUCKDB_AVAILABLE = False

logger = logging.getLogger(__name__)

class DataSource:
    """Abstract data source for virtual scrolling."""
    
    def __init__(self, file_path: str, format_type: str, table_name: str = "tickers_data"):
        """Initialize data source."""
        self.file_path = file_path
        self.format_type = format_type
        self.table_name = table_name
        self.connection = None
        self.total_rows = 0
        self.data = None
        self.logger = logging.getLogger(__name__)
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the data source based on format type."""
        try:
            if self.format_type == 'duckdb' and self.file_path:
                if DUCKDB_AVAILABLE:
                    self.connection = duckdb.connect(self.file_path)
                    self.total_rows = self.connection.execute(f"SELECT COUNT(*) FROM {self.table_name}").fetchone()[0]
                else:
                    raise ImportError("DuckDB not available")
            elif self.format_type == 'pandas' and self.data is not None:
                # Direct pandas data provided
                self.total_rows = len(self.data)
                self.logger.info(f"Using direct pandas data: {self.total_rows} rows")
            elif self.file_path:
                # For other formats, load into memory (not ideal for large files)
                df = DataLoader.load_file_by_type(self.file_path, self.format_type)
                
                if isinstance(df, pd.DataFrame):
                    self.data = df
                    self.total_rows = len(df)
                else:
                    # Convert other formats to pandas
                    if POLARS_AVAILABLE and isinstance(df, pl.DataFrame):
                        self.data = df.to_pandas()
                    elif PYARROW_AVAILABLE and isinstance(df, pa.Table):
                        self.data = df.to_pandas()
                    else:
                        self.data = pd.DataFrame()
                    
                    self.total_rows = len(self.data)
            else:
                # No file path and no data provided
                self.data = pd.DataFrame()
                self.total_rows = 0
                    
        except Exception as e:
            self.logger.error(f"Error initializing data source: {str(e)}")
            self.data = pd.DataFrame()
            self.total_rows = 0
    
    def get_total_rows(self) -> int:
        """Get total number of rows."""
        return self.total_rows
    
    def get_row(self, index: int) -> List:
        """Get a specific row by index."""
        try:
            if self.format_type == 'duckdb' and self.connection:
                query = f"SELECT * FROM {self.table_name} LIMIT 1 OFFSET {index}"
                result = self.connection.execute(query).fetchone()
                return list(result) if result else []
            else:
                if self.data is not None and index < len(self.data):
                    return list(self.data.iloc[index])
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting row {index}: {str(e)}")
            return []
    
    def get_rows(self, start: int, end: int) -> List[List]:
        """Get a range of rows."""
        try:
            if self.format_type == 'duckdb' and self.connection:
                query = f"SELECT * FROM tickers_data LIMIT {end - start} OFFSET {start}"
                result = self.connection.execute(query).fetchdf()
                return [list(row) for _, row in result.iterrows()]
            else:
                if self.data is not None:
                    return [list(row) for _, row in self.data.iloc[start:end].iterrows()]
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting rows {start}-{end}: {str(e)}")
            return []
    
    def get_columns(self) -> List[str]:
        """Get column names."""
        try:
            if self.format_type == 'duckdb' and self.connection:
                result = self.connection.execute("PRAGMA table_info(tickers_data)").fetchall()
                return [col[1] for col in result] if result else []
            else:
                if self.data is not None:
                    return list(self.data.columns)
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting columns: {str(e)}")
            return []
    
    def search_rows(self, search_term: str, column: str = None) -> List[int]:
        """
        Search for rows containing the search term.
        
        Args:
            search_term: Term to search for
            column: Specific column to search (None for all columns)
            
        Returns:
            List of row indices that match
        """
        try:
            if self.format_type == 'duckdb' and self.connection:
                if column:
                    query = f"SELECT rowid FROM tickers_data WHERE {column} LIKE ?"
                    result = self.connection.execute(query, [f'%{search_term}%']).fetchall()
                else:
                    # Search all text columns
                    columns = self.get_columns()
                    conditions = []
                    params = []
                    for col in columns:
                        conditions.append(f"{col} LIKE ?")
                        params.append(f'%{search_term}%')
                    
                    query = f"SELECT rowid FROM tickers_data WHERE {' OR '.join(conditions)}"
                    result = self.connection.execute(query, params).fetchall()
                
                return [row[0] for row in result]
                
            else:
                # Search in pandas DataFrame
                if self.data is not None:
                    if column and column in self.data.columns:
                        mask = self.data[column].astype(str).str.contains(search_term, case=False, na=False)
                    else:
                        # Search all columns
                        mask = self.data.astype(str).apply(
                            lambda x: x.str.contains(search_term, case=False, na=False)
                        ).any(axis=1)
                    
                    return self.data[mask].index.tolist()
                
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching rows: {str(e)}")
            return []
    
    def filter_rows(self, conditions: dict) -> List[int]:
        """
        Filter rows based on conditions.
        
        Args:
            conditions: Dictionary of column -> value conditions
            
        Returns:
            List of row indices that match conditions
        """
        try:
            if self.format_type == 'duckdb' and self.connection:
                where_clauses = []
                params = []
                
                for column, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        placeholders = ','.join(['?' for _ in value])
                        where_clauses.append(f"{column} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_clauses.append(f"{column} = ?")
                        params.append(value)
                
                query = f"SELECT rowid FROM tickers_data WHERE {' AND '.join(where_clauses)}"
                result = self.connection.execute(query, params).fetchall()
                return [row[0] for row in result]
                
            else:
                # Filter in pandas DataFrame
                if self.data is not None:
                    mask = pd.Series([True] * len(self.data))
                    
                    for column, value in conditions.items():
                        if column in self.data.columns:
                            if isinstance(value, (list, tuple)):
                                mask &= self.data[column].isin(value)
                            else:
                                mask &= (self.data[column] == value)
                    
                    return self.data[mask].index.tolist()
                
                return []
                
        except Exception as e:
            self.logger.error(f"Error filtering rows: {str(e)}")
            return []
    
    def get_statistics(self) -> dict:
        """Get basic statistics about the data."""
        try:
            stats = {
                'total_rows': self.total_rows,
                'total_columns': len(self.get_columns()),
                'format_type': self.format_type,
                'file_path': self.file_path
            }
            
            if self.format_type == 'duckdb' and self.connection:
                # Get additional stats from database
                try:
                    result = self.connection.execute("SELECT COUNT(DISTINCT ticker) FROM tickers_data").fetchone()
                    stats['unique_tickers'] = result[0] if result else 0
                except:
                    stats['unique_tickers'] = 0
            elif self.data is not None and 'ticker' in self.data.columns:
                stats['unique_tickers'] = self.data['ticker'].nunique()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {str(e)}")
            return {'total_rows': 0, 'total_columns': 0, 'format_type': self.format_type}
    
    def close(self):
        """Close the data source and free resources."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            # Clear data to free memory
            self.data = None
            
        except Exception as e:
            self.logger.error(f"Error closing data source: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure resources are freed."""
        self.close()
