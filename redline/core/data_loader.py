#!/usr/bin/env python3
"""
REDLINE Core Data Loader
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
    """Main data loading and processing class for REDLINE."""
    
    def __init__(self, config_path: str = 'data_config.ini'):
        """Initialize DataLoader with configuration."""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize paths from config
        self.db_path = self.config['Data'].get('db_path', '/app/redline_data.duckdb')
        self.csv_dir = self.config['Data'].get('csv_dir', '/app/data')
        self.json_dir = self.config['Data'].get('json_dir', '/app/data/json')
        self.parquet_dir = self.config['Data'].get('parquet_dir', '/app/data/parquet')
        
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
        data = []
        skipped_files = []
        
        for path in file_paths:
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
                
            except Exception as e:
                self.logger.error(f"Failed to load {path}: {str(e)}")
                skipped_files.append({
                    'file': os.path.basename(path),
                    'reason': str(e)
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
            
        except Exception as e:
            self.logger.exception(f"Failed to save to {table}: {str(e)}")
            raise
    
    def load_ticker_data(self, ticker: str) -> pd.DataFrame:
        """
        Load data for a specific ticker from the database.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            DataFrame with ticker data
        """
        try:
            conn = duckdb.connect(self.db_path)
            query = f"SELECT * FROM tickers_data WHERE ticker = '{ticker}' ORDER BY timestamp"
            result = conn.execute(query).fetchdf()
            conn.close()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading ticker data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_data_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about the loaded data.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with statistics
        """
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
            
        except Exception as e:
            self.logger.error(f"Error calculating data stats: {str(e)}")
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
        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
            filtered_data = data.loc[mask]
            
            if filtered_data.empty:
                self.logger.warning(f"No data found between {start_date} and {end_date}")
            else:
                self.logger.info(f"Filtered data from {start_date} to {end_date}. Tickers: {filtered_data['ticker'].unique()}")
                
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error filtering data by date range: {str(e)}")
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
