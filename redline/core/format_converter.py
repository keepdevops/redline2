#!/usr/bin/env python3
"""
REDLINE Format Converter
Handles conversion between different data formats and file I/O operations.
"""

import logging
import pandas as pd
from typing import Union, List, Dict, Any
import os
import json

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

class FormatConverter:
    """Handles format conversion and file I/O operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_format(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], 
                      from_format: str, to_format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict]:
        """
        Convert data between different formats.
        
        Args:
            data: Data to convert
            from_format: Source format
            to_format: Target format
            
        Returns:
            Converted data in target format
        """
        if from_format == to_format:
            return data
            
        if isinstance(data, list):
            return [self.convert_format(d, from_format, to_format) for d in data]
            
        try:
            if from_format == 'pandas':
                if to_format == 'polars':
                    if not POLARS_AVAILABLE:
                        raise ImportError("polars not available")
                    return pl.from_pandas(data)
                elif to_format == 'pyarrow':
                    if not PYARROW_AVAILABLE:
                        raise ImportError("pyarrow not available")
                    return pa.Table.from_pandas(data)
            elif from_format == 'polars':
                if not POLARS_AVAILABLE:
                    raise ImportError("polars not available")
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'pyarrow':
                    if not PYARROW_AVAILABLE:
                        raise ImportError("pyarrow not available")
                    return data.to_arrow()
            elif from_format == 'pyarrow':
                if not PYARROW_AVAILABLE:
                    raise ImportError("pyarrow not available")
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'polars':
                    if not POLARS_AVAILABLE:
                        raise ImportError("polars not available")
                    return pl.from_arrow(data)
                    
            self.logger.info(f"Converted from {from_format} to {to_format}")
            return data
            
        except Exception as e:
            self.logger.error(f"Conversion failed from {from_format} to {to_format}: {str(e)}")
            raise
    
    def save_file_by_type(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict], 
                          file_path: str, format: str) -> None:
        """
        Save data to file based on format type.
        
        Args:
            data: Data to save
            file_path: Path to save file
            format: Format type
        """
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(file_path)
            if output_dir:  # Only create directory if path has a directory component
                os.makedirs(output_dir, exist_ok=True)
            
            if format == 'csv':
                try:
                    if isinstance(data, pd.DataFrame):
                        self.logger.info(f"Saving {len(data)} rows to CSV: {file_path}")
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty CSV file")
                        data.to_csv(file_path, index=False)
                        self.logger.info(f"Successfully saved CSV file: {file_path}")
                    elif POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                        self.logger.info(f"Saving Polars DataFrame to CSV: {file_path}")
                        if data.is_empty():
                            self.logger.warning("Polars DataFrame is empty, creating empty CSV file")
                        data.write_csv(file_path)
                        self.logger.info(f"Successfully saved CSV file: {file_path}")
                    else:
                        raise ValueError(f"Cannot save {type(data)} to CSV format")
                except Exception as e:
                    self.logger.error(f"Error saving CSV file: {str(e)}")
                    self.logger.error(f"File path: {file_path}")
                    self.logger.error(f"Data type: {type(data)}")
                    if hasattr(data, 'shape'):
                        self.logger.error(f"Data shape: {data.shape}")
                    raise Exception(f"Failed to save CSV file: {str(e)}")
                    
            elif format == 'parquet':
                if isinstance(data, pd.DataFrame):
                    try:
                        # Try pyarrow first (faster, better compression)
                        data.to_parquet(file_path, index=False, engine='pyarrow')
                    except Exception as e:
                        self.logger.warning(f"Error saving parquet with pyarrow engine: {str(e)}")
                        # Fallback to fastparquet
                        try:
                            self.logger.info("Attempting fallback to fastparquet engine")
                            data.to_parquet(file_path, index=False, engine='fastparquet')
                        except Exception as e2:
                            self.logger.error(f"Error saving parquet with fastparquet engine: {str(e2)}")
                            # Try without specifying engine
                            try:
                                data.to_parquet(file_path, index=False)
                            except Exception as e3:
                                self.logger.error(f"Error saving parquet without engine: {str(e3)}")
                                raise Exception(f"Failed to save parquet: {str(e3)}")
                elif POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                    data.write_parquet(file_path)
                elif PYARROW_AVAILABLE and isinstance(data, pa.Table):
                    pa.parquet.write_table(data, file_path)
                else:
                    raise ValueError(f"Cannot save {type(data)} to Parquet format")
                    
            elif format == 'feather':
                try:
                    if isinstance(data, pd.DataFrame):
                        self.logger.info(f"Saving {len(data)} rows to Feather: {file_path}")
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty Feather file")
                        data.to_feather(file_path)
                        self.logger.info(f"Successfully saved Feather file: {file_path}")
                    elif POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                        self.logger.info(f"Saving Polars DataFrame to Feather: {file_path}")
                        if data.is_empty():
                            self.logger.warning("Polars DataFrame is empty, creating empty Feather file")
                        data.write_ipc(file_path)
                        self.logger.info(f"Successfully saved Feather file: {file_path}")
                    else:
                        raise ValueError(f"Cannot save {type(data)} to Feather format")
                except Exception as e:
                    self.logger.error(f"Error saving Feather file: {str(e)}")
                    self.logger.error(f"File path: {file_path}")
                    self.logger.error(f"Data type: {type(data)}")
                    if hasattr(data, 'shape'):
                        self.logger.error(f"Data shape: {data.shape}")
                    raise Exception(f"Failed to save Feather file: {str(e)}")
                    
            elif format == 'json':
                try:
                    if isinstance(data, dict):
                        self.logger.info(f"Saving dictionary to JSON: {file_path}")
                        with open(file_path, 'w') as f:
                            json.dump(data, f, indent=2, default=str)
                        self.logger.info(f"Successfully saved JSON file: {file_path}")
                    elif isinstance(data, pd.DataFrame):
                        self.logger.info(f"Saving {len(data)} rows to JSON: {file_path}")
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty JSON file")
                        data.to_json(file_path, orient='records', indent=2)
                        self.logger.info(f"Successfully saved JSON file: {file_path}")
                    else:
                        raise ValueError(f"Cannot save {type(data)} to JSON format")
                except Exception as e:
                    self.logger.error(f"Error saving JSON file: {str(e)}")
                    self.logger.error(f"File path: {file_path}")
                    self.logger.error(f"Data type: {type(data)}")
                    if hasattr(data, 'shape'):
                        self.logger.error(f"Data shape: {data.shape}")
                    raise Exception(f"Failed to save JSON file: {str(e)}")
                    
            elif format == 'duckdb':
                if not DUCKDB_AVAILABLE:
                    raise ImportError("duckdb not available. Please install duckdb to use DuckDB format.")
                
                # Ensure directory exists
                output_dir = os.path.dirname(file_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                conn = None
                try:
                    conn = duckdb.connect(file_path)
                    self.logger.info(f"Saving data to DuckDB database: {file_path}")
                    
                    if isinstance(data, pd.DataFrame):
                        # Register the DataFrame with DuckDB and create table
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty table")
                        conn.register('temp_data', data)
                        conn.execute("DROP TABLE IF EXISTS tickers_data")
                        conn.execute("CREATE TABLE tickers_data AS SELECT * FROM temp_data")
                        self.logger.info(f"Saved {len(data)} rows to DuckDB")
                        
                    elif POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                        # Register the Polars DataFrame with DuckDB and create table
                        if data.is_empty():
                            self.logger.warning("Polars DataFrame is empty, creating empty table")
                        conn.register('temp_data', data)
                        conn.execute("DROP TABLE IF EXISTS tickers_data")
                        conn.execute("CREATE TABLE tickers_data AS SELECT * FROM temp_data")
                        self.logger.info(f"Saved Polars DataFrame to DuckDB")
                        
                    else:
                        # For other data types, convert to DataFrame first
                        self.logger.info(f"Converting {type(data)} to pandas DataFrame")
                        if hasattr(data, 'to_pandas'):
                            df = data.to_pandas()
                        else:
                            df = pd.DataFrame(data)
                        conn.register('temp_data', df)
                        conn.execute("DROP TABLE IF EXISTS tickers_data")
                        conn.execute("CREATE TABLE tickers_data AS SELECT * FROM temp_data")
                        self.logger.info(f"Saved {len(df)} rows to DuckDB")
                        
                except Exception as e:
                    self.logger.error(f"Error saving to DuckDB database: {str(e)}")
                    self.logger.error(f"Data type: {type(data)}")
                    if hasattr(data, 'shape'):
                        self.logger.error(f"Data shape: {data.shape}")
                    # Ensure connection is closed even on error
                    if conn:
                        try:
                            conn.close()
                        except:
                            pass
                    raise Exception(f"Failed to save to DuckDB: {str(e)}")
                    
                finally:
                    # Always close the connection
                    if conn:
                        try:
                            conn.close()
                            self.logger.debug("Closed DuckDB connection")
                        except Exception as close_error:
                            self.logger.warning(f"Error closing DuckDB connection: {close_error}")
                
            else:
                raise ValueError(f"Unsupported format: {format}")
                
            self.logger.info(f"Saved data to {file_path} in {format} format")
            
        except Exception as e:
            self.logger.error(f"Error saving file {file_path}: {str(e)}")
            raise
    
    def load_file_by_type(self, file_path: str, format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']:
        """
        Load data from file based on format type.
        
        Args:
            file_path: Path to file
            format: Format type
            
        Returns:
            Loaded data
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if format == 'csv':
                return pd.read_csv(file_path)
            elif format == 'parquet':
                try:
                    data = pd.read_parquet(file_path)
                    if data.empty:
                        self.logger.warning(f"Parquet file {file_path} is empty")
                    return data
                except Exception as parquet_error:
                    self.logger.error(f"Error reading parquet file {file_path}: {str(parquet_error)}")
                    # Try to read as CSV if parquet fails
                    try:
                        self.logger.info(f"Attempting to read {file_path} as CSV fallback")
                        return pd.read_csv(file_path)
                    except:
                        raise parquet_error
            elif format == 'feather':
                return pd.read_feather(file_path)
            elif format == 'json':
                return pd.read_json(file_path)
            elif format == 'duckdb':
                import duckdb
                conn = duckdb.connect(file_path)
                try:
                    result = conn.execute("SELECT * FROM tickers_data").fetchdf()
                    return result
                except Exception as e:
                    # Ensure connection is closed even on error
                    try:
                        conn.close()
                    except:
                        pass
                    raise e
                finally:
                    # Always close the connection
                    try:
                        conn.close()
                    except Exception as close_error:
                        self.logger.warning(f"Error closing DuckDB connection: {close_error}")
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            raise
    
    def convert_to_stooq_format(self, data: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
        """
        Convert DataFrame to Stooq format.
        
        Args:
            data: DataFrame to convert
            ticker: Ticker symbol (if not provided, uses first ticker in data)
            
        Returns:
            DataFrame in Stooq format
        """
        try:
            result = data.copy()
            
            # Get ticker if not provided
            if ticker is None and 'ticker' in data.columns:
                ticker = data['ticker'].iloc[0] if not data.empty else 'UNKNOWN'
            elif ticker is None:
                ticker = 'UNKNOWN'
            
            # Handle timestamp conversion
            if 'timestamp' in result.columns:
                try:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], utc=True)
                    result['timestamp'] = result['timestamp'].dt.tz_localize(None)
                    result['<DATE>'] = result['timestamp'].dt.strftime('%Y%m%d')
                except:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], errors='coerce')
                    result['<DATE>'] = result['timestamp'].dt.strftime('%Y%m%d')
            
            # Map columns to Stooq format
            stooq_mapping = {
                'ticker': '<TICKER>',
                'open': '<OPEN>',
                'high': '<HIGH>',
                'low': '<LOW>',
                'close': '<CLOSE>',
                'vol': '<VOL>'
            }
            
            # Create Stooq format DataFrame
            stooq_data = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': result['<DATE>'] if '<DATE>' in result.columns else result['timestamp'].dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': result.get('open', result.get('Open', None)),
                '<HIGH>': result.get('high', result.get('High', None)),
                '<LOW>': result.get('low', result.get('Low', None)),
                '<CLOSE>': result.get('close', result.get('Close', None)),
                '<VOL>': result.get('vol', result.get('Volume', None))
            })
            
            # Clean numeric data
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                stooq_data[col] = pd.to_numeric(stooq_data[col], errors='coerce')
            
            # Remove rows with invalid data
            stooq_data = stooq_data.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            return stooq_data
            
        except Exception as e:
            self.logger.error(f"Error converting to Stooq format: {str(e)}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['csv', 'parquet', 'feather', 'json', 'duckdb']
    
    def detect_format_from_extension(self, file_path: str) -> str:
        """
        Detect format from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected format
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        format_map = {
            '.csv': 'csv',
            '.parquet': 'parquet',
            '.feather': 'feather',
            '.json': 'json',
            '.duckdb': 'duckdb',
            '.db': 'duckdb'
        }
        
        return format_map.get(ext, 'csv')
