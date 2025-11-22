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

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    TENSORFLOW_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

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
                        # Replace NaN values in dict before saving
                        def replace_nan(obj):
                            if isinstance(obj, dict):
                                return {k: replace_nan(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [replace_nan(item) for item in obj]
                            elif isinstance(obj, float) and (pd.isna(obj) or pd.isnull(obj)):
                                return None
                            return obj
                        cleaned_data = replace_nan(data)
                        with open(file_path, 'w') as f:
                            json.dump(cleaned_data, f, indent=2, default=str)
                        self.logger.info(f"Successfully saved JSON file: {file_path}")
                    elif isinstance(data, pd.DataFrame):
                        self.logger.info(f"Saving {len(data)} rows to JSON: {file_path}")
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty JSON file")
                        # Replace NaN/NaT values with None before saving to JSON
                        # This ensures valid JSON output (NaN is not valid JSON)
                        from ..utils.json_utils import clean_dataframe_for_json
                        # Convert to dict and clean NaN values using centralized utility
                        cleaned_data = clean_dataframe_for_json(data)
                        # Write JSON directly
                        with open(file_path, 'w') as f:
                            json.dump(cleaned_data, f, indent=2, default=str)
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
                
            elif format == 'txt':
                try:
                    if isinstance(data, pd.DataFrame):
                        self.logger.info(f"Saving {len(data)} rows to TXT: {file_path}")
                        if data.empty:
                            self.logger.warning("DataFrame is empty, creating empty TXT file")
                        data.to_csv(file_path, index=False, sep='\t')
                        self.logger.info(f"Successfully saved TXT file: {file_path}")
                    elif POLARS_AVAILABLE and isinstance(data, pl.DataFrame):
                        self.logger.info(f"Saving Polars DataFrame to TXT: {file_path}")
                        if data.is_empty():
                            self.logger.warning("Polars DataFrame is empty, creating empty TXT file")
                        data.write_csv(file_path, separator='\t')
                        self.logger.info(f"Successfully saved TXT file: {file_path}")
                    else:
                        raise ValueError(f"Cannot save {type(data)} to TXT format")
                except Exception as e:
                    self.logger.error(f"Error saving TXT file: {str(e)}")
                    raise Exception(f"Failed to save TXT file: {str(e)}")
            elif format == 'keras' and TENSORFLOW_AVAILABLE:
                if isinstance(data, pd.DataFrame):
                    from tensorflow.keras import Sequential, Input
                    from tensorflow.keras.layers import Dense
                    model = Sequential([Input(shape=(len(data.columns),)), Dense(32, activation='relu'), Dense(1)])
                    model.save(file_path)
                    self.logger.info(f"Saved Keras model: {file_path}")
                else:
                    raise ValueError(f"Cannot save {type(data)} to Keras format")
            elif format in ('tensorflow', 'npz'):
                if not NUMPY_AVAILABLE:
                    raise ImportError("NumPy is required for .npz format but is not available. Please install numpy: pip install numpy")
                if isinstance(data, pd.DataFrame):
                    try:
                        np.savez(file_path, data=data.to_numpy())
                        self.logger.info(f"Saved TensorFlow NPZ: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error saving NPZ file: {str(e)}")
                        raise Exception(f"Failed to save .npz file: {str(e)}")
                else:
                    raise ValueError(f"Cannot save {type(data)} to TensorFlow/NPZ format")
            elif format == 'pyarrow' and PYARROW_AVAILABLE:
                if isinstance(data, pd.DataFrame):
                    table = pa.Table.from_pandas(data)
                    with pa.OSFile(file_path, 'wb') as sink:
                        with pa.ipc.new_file(sink, table.schema) as writer:
                            writer.write_table(table)
                    self.logger.info(f"Saved PyArrow format: {file_path}")
                elif isinstance(data, pa.Table):
                    with pa.OSFile(file_path, 'wb') as sink:
                        with pa.ipc.new_file(sink, data.schema) as writer:
                            writer.write_table(data)
                    self.logger.info(f"Saved PyArrow format: {file_path}")
                else:
                    raise ValueError(f"Cannot save {type(data)} to PyArrow format")
            elif format == 'polars' and POLARS_AVAILABLE:
                if isinstance(data, pd.DataFrame):
                    pl.from_pandas(data).write_parquet(file_path)
                    self.logger.info(f"Saved Polars format: {file_path}")
                elif isinstance(data, pl.DataFrame):
                    data.write_parquet(file_path)
                    self.logger.info(f"Saved Polars format: {file_path}")
                else:
                    raise ValueError(f"Cannot save {type(data)} to Polars format")
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
                    try:
                        conn.close()
                    except:
                        pass
                    raise e
                finally:
                    try:
                        conn.close()
                    except Exception as close_error:
                        self.logger.warning(f"Error closing DuckDB connection: {close_error}")
            elif format == 'keras' and TENSORFLOW_AVAILABLE:
                return tf.keras.models.load_model(file_path)
            elif format == 'tensorflow' and NUMPY_AVAILABLE:
                loaded = np.load(file_path)
                return pd.DataFrame(loaded['data']) if 'data' in loaded else pd.DataFrame(loaded[list(loaded.keys())[0]])
            elif format == 'pyarrow' and PYARROW_AVAILABLE:
                return pa.ipc.open_file(file_path).read_all().to_pandas()
            elif format == 'polars' and POLARS_AVAILABLE:
                return pl.read_parquet(file_path).to_pandas()
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
        formats = ['csv', 'parquet', 'feather', 'json', 'duckdb', 'txt']
        if TENSORFLOW_AVAILABLE:
            formats.extend(['keras', 'tensorflow'])
        if PYARROW_AVAILABLE:
            formats.append('pyarrow')
        if POLARS_AVAILABLE:
            formats.append('polars')
        return formats
    
    def detect_format_from_extension(self, file_path: str) -> str:
        """
        Detect format from file extension (uses centralized function).
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected format
        """
        from .schema import detect_format_from_path
        return detect_format_from_path(file_path)
