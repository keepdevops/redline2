#!/usr/bin/env python3
"""
VarioSync Core Data Loader
Main data loading and processing functionality for financial data.
"""

import logging
import configparser
import pandas as pd
from typing import Union, List, Dict, Any
import os

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

from .schema import SCHEMA, EXT_TO_FORMAT, FORMAT_DIALOG_INFO
from .data_validator import DataValidator
from .data_cleaner import DataCleaner
from .format_converter import FormatConverter

logger = logging.getLogger(__name__)

class DataLoader:
    """Main data loading and processing class for VarioSync."""
    
    def __init__(self, config_path: str = 'data_config.ini'):
        """Initialize DataLoader with configuration."""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize paths from config with fallbacks
        self.db_path = self.config.get('Data', 'db_path', fallback='redline_data.duckdb')
        self.csv_dir = self.config.get('Data', 'csv_dir', fallback='data')
        self.json_dir = self.config.get('Data', 'json_dir', fallback='data/json')
        self.parquet_dir = self.config.get('Data', 'parquet_dir', fallback='data/parquet')
        
        # Initialize helper classes
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.converter = FormatConverter()
        
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, file_paths: List[str], format: str, delete_empty: bool = False) -> List[Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']]:
        """
        Load data from multiple files.

        Args:
            file_paths: List of file paths to load
            format: Data format type
            delete_empty: Whether to delete empty files

        Returns:
            List of loaded DataFrames
        """
        # Pre-validation with if-else
        if not file_paths:
            self.logger.error("File paths list is empty")
            raise ValueError("File paths list cannot be empty")

        if not isinstance(file_paths, list):
            self.logger.error(f"File paths must be a list, got {type(file_paths)}")
            raise TypeError(f"File paths must be a list, got {type(file_paths)}")

        if not format:
            self.logger.error("Format is empty or None")
            raise ValueError("Format cannot be empty")

        if not isinstance(format, str):
            self.logger.error(f"Format must be a string, got {type(format)}")
            raise TypeError(f"Format must be a string, got {type(format)}")

        data = []
        skipped_files = []

        for path in file_paths:
            # Pre-validation for each file path
            if not path:
                skipped_files.append({
                    'file': 'unknown',
                    'reason': 'Empty file path'
                })
                continue

            if not isinstance(path, str):
                skipped_files.append({
                    'file': str(path),
                    'reason': f'Invalid path type: {type(path)}'
                })
                continue

            try:
                # Convert absolute path to relative path if needed
                relative_path = path.replace('/app/', '')
                
                # Validate file before attempting to load
                if not self.validator.validate_data(relative_path, format):
                    skipped_files.append({
                        'file': os.path.basename(path),
                        'reason': 'Failed validation'
                    })
                    continue
                
                # Load and standardize the data
                if format == 'txt':
                    df = pd.read_csv(relative_path)
                    df = self.cleaner.standardize_txt_columns(df)
                else:
                    df = self.converter.load_file_by_type(relative_path, format)
                
                # Validate required columns after standardization
                if not all(col in df.columns for col in ['ticker', 'timestamp', 'close']):
                    skipped_files.append({
                        'file': os.path.basename(path),
                        'reason': 'Missing required columns after standardization'
                    })
                    continue
                
                data.append(df)
                self.logger.info(f"Successfully loaded {path}")

            except FileNotFoundError as e:
                self.logger.error(f"File not found: {path}: {str(e)}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': f'File not found: {str(e)}'
                })
            except PermissionError as e:
                self.logger.error(f"Permission denied reading {path}: {str(e)}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': f'Permission denied: {str(e)}'
                })
            except pd.errors.EmptyDataError as e:
                self.logger.warning(f"Empty file: {path}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': 'Empty file'
                })
            except pd.errors.ParserError as e:
                self.logger.error(f"Parse error in {path}: {str(e)}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': f'Parse error: {str(e)}'
                })
            except Exception as e:
                self.logger.error(f"Unexpected error loading {path}: {type(e).__name__}: {str(e)}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': f'{type(e).__name__}: {str(e)}'
                })
        
        if not data:
            raise ValueError(f"No valid data could be loaded. Skipped files: {', '.join([f['file'] for f in skipped_files])}")
        
        return data
    
    def save_to_shared(self, table: str, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], format: str) -> None:
        """
        Save data to shared database table.

        Args:
            table: Table name
            data: Data to save
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
            self.logger.error("Data is None - cannot save")
            raise ValueError("Data cannot be None")

        if not isinstance(data, (pd.DataFrame, pl.DataFrame if POLARS_AVAILABLE else type(None), pa.Table if PYARROW_AVAILABLE else type(None))):
            self.logger.error(f"Data must be pandas DataFrame, polars DataFrame, or pyarrow Table, got {type(data)}")
            raise TypeError(f"Invalid data type: {type(data)}")

        if not format:
            self.logger.error("Format is empty or None")
            raise ValueError("Format cannot be empty")

        if not DUCKDB_AVAILABLE:
            self.logger.error("DuckDB not available - cannot save to shared database")
            raise ImportError("duckdb not available. Install with: pip install duckdb")

        if not self.db_path:
            self.logger.error("Database path is not configured")
            raise ValueError("Database path is not configured")

        try:
            # Convert to pandas DataFrame if needed
            if POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif PYARROW_AVAILABLE and isinstance(data, pa.Table):
                data = data.to_pandas()
            
            data['format'] = format
            data = self.cleaner.clean_and_select_columns(data)
            
            # Ensure timestamp is in datetime format
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            # Create table if not exists and insert data using DuckDB
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
            
            # Insert data
            conn.register('temp_df', data)
            insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
            conn.execute(insert_sql)
            conn.unregister('temp_df')
            conn.close()

            self.logger.info(f"Saved data to {table} in format {format}")

        except duckdb.CatalogException as e:
            self.logger.error(f"Database catalog error saving to {table}: {str(e)}")
            raise
        except duckdb.ConnectionException as e:
            self.logger.error(f"Database connection error saving to {table}: {str(e)}")
            raise
        except KeyError as e:
            self.logger.error(f"Missing required column saving to {table}: {str(e)}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error saving to {table}: {type(e).__name__}: {str(e)}")
            raise
    
    def load_ticker_data(self, ticker: str) -> pd.DataFrame:
        """
        Load data for a specific ticker from the database.

        Args:
            ticker: Ticker symbol

        Returns:
            DataFrame with ticker data
        """
        # Pre-validation with if-else
        if not ticker:
            self.logger.error("Ticker symbol is empty or None")
            return pd.DataFrame()

        if not isinstance(ticker, str):
            self.logger.error(f"Ticker must be a string, got {type(ticker)}")
            return pd.DataFrame()

        if not DUCKDB_AVAILABLE:
            self.logger.error("DuckDB not available - cannot load ticker data")
            return pd.DataFrame()

        if not self.db_path:
            self.logger.error("Database path is not configured")
            return pd.DataFrame()

        try:
            conn = duckdb.connect(self.db_path)
            query = f"SELECT * FROM tickers_data WHERE ticker = '{ticker}' ORDER BY timestamp"
            result = conn.execute(query).fetchdf()
            conn.close()

            return result

        except duckdb.CatalogException as e:
            self.logger.error(f"Table not found loading ticker data for {ticker}: {str(e)}")
            return pd.DataFrame()
        except duckdb.ConnectionException as e:
            self.logger.error(f"Database connection error loading ticker data for {ticker}: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Unexpected error loading ticker data for {ticker}: {type(e).__name__}: {str(e)}")
            return pd.DataFrame()
    
    def get_data_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about the loaded data.

        Args:
            data: DataFrame to analyze

        Returns:
            Dictionary with statistics
        """
        # Pre-validation with if-else
        if data is None:
            self.logger.error("Data is None - cannot get stats")
            return {}

        if not isinstance(data, pd.DataFrame):
            self.logger.error(f"Data must be a pandas DataFrame, got {type(data)}")
            return {}

        if data.empty:
            self.logger.warning("DataFrame is empty - returning empty stats")
            return {
                'total_records': 0,
                'total_tickers': 0,
                'date_range': {'start': None, 'end': None},
                'avg_records_per_ticker': 0
            }

        try:
            stats = {
                'total_records': len(data),
                'total_tickers': len(data['ticker'].unique()) if 'ticker' in data.columns else 0,
                'date_range': {
                    'start': data['timestamp'].min() if 'timestamp' in data.columns else None,
                    'end': data['timestamp'].max() if 'timestamp' in data.columns else None
                },
                'avg_records_per_ticker': 0
            }
            
            if stats['total_tickers'] > 0:
                stats['avg_records_per_ticker'] = stats['total_records'] // stats['total_tickers']

            return stats

        except KeyError as e:
            self.logger.error(f"Missing required column calculating stats: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error calculating data stats: {type(e).__name__}: {str(e)}")
            return {}
    
    def filter_data_by_date_range(self, data: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter the dataframe by date range for all tickers.

        Args:
            data: DataFrame to filter
            start_date: Start date string
            end_date: End date string

        Returns:
            Filtered DataFrame
        """
        # Pre-validation with if-else
        if data is None:
            self.logger.error("Data is None - cannot filter")
            raise ValueError("Data cannot be None")

        if not isinstance(data, pd.DataFrame):
            self.logger.error(f"Data must be a pandas DataFrame, got {type(data)}")
            raise TypeError(f"Data must be a pandas DataFrame, got {type(data)}")

        if data.empty:
            self.logger.warning("DataFrame is empty - returning empty DataFrame")
            return pd.DataFrame()

        if not start_date:
            self.logger.error("Start date is empty or None")
            raise ValueError("Start date cannot be empty")

        if not end_date:
            self.logger.error("End date is empty or None")
            raise ValueError("End date cannot be empty")

        if not isinstance(start_date, str) or not isinstance(end_date, str):
            self.logger.error(f"Dates must be strings, got start: {type(start_date)}, end: {type(end_date)}")
            raise TypeError("Dates must be strings")

        if 'timestamp' not in data.columns:
            self.logger.error("DataFrame missing 'timestamp' column - cannot filter")
            raise KeyError("DataFrame must have 'timestamp' column")

        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
            filtered_data = data.loc[mask]
            
            if filtered_data.empty:
                self.logger.warning(f"No data found between {start_date} and {end_date}")
            else:
                self.logger.info(f"Filtered data from {start_date} to {end_date}. Tickers: {filtered_data['ticker'].unique()}")

            return filtered_data

        except pd.errors.OutOfBoundsDatetime as e:
            self.logger.error(f"Date out of bounds filtering data: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid date format filtering data: {str(e)}")
            raise
        except KeyError as e:
            self.logger.error(f"Missing required column filtering data: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error filtering data by date range: {type(e).__name__}: {str(e)}")
            raise
    
    def convert_format(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], 
                      from_format: str, to_format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict]:
        """Convert data between different formats."""
        return self.converter.convert_format(data, from_format, to_format)
    
    def validate_data(self, file_path: str, format: str) -> bool:
        """Validate data file format and structure."""
        return self.validator.validate_data(file_path, format)
    
    def clean_and_select_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame columns."""
        return self.cleaner.clean_and_select_columns(data)
    
    def load_file_by_type(self, file_path: str, format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']:
        """Load data from file based on format type."""
        return self.converter.load_file_by_type(file_path, format)
    
    @staticmethod
    def save_file_by_type(data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict], 
                         file_path: str, format: str) -> None:
        """Static method to save data to file."""
        converter = FormatConverter()
        converter.save_file_by_type(data, file_path, format)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.converter.get_supported_formats()
    
    def get_format_info(self, format: str) -> Dict[str, Any]:
        """Get information about a specific format."""
        if format in FORMAT_DIALOG_INFO:
            ext, desc, pattern = FORMAT_DIALOG_INFO[format]
            return {
                'extension': ext,
                'description': desc,
                'pattern': pattern
            }
        return {}
