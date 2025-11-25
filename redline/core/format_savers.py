#!/usr/bin/env python3
"""
REDLINE Format Savers
Handles saving data to different file formats.
"""

import logging
import pandas as pd
from typing import Union
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


class FormatSavers:
    """Handles saving data to different file formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
                self._save_csv(data, file_path)
            elif format == 'parquet':
                self._save_parquet(data, file_path)
            elif format == 'feather':
                self._save_feather(data, file_path)
            elif format == 'json':
                self._save_json(data, file_path)
            elif format == 'duckdb':
                self._save_duckdb(data, file_path)
            elif format == 'txt':
                self._save_txt(data, file_path)
            elif format == 'keras' and TENSORFLOW_AVAILABLE:
                self._save_keras(data, file_path)
            elif format in ('tensorflow', 'npz'):
                self._save_tensorflow(data, file_path)
            elif format == 'pyarrow' and PYARROW_AVAILABLE:
                self._save_pyarrow(data, file_path)
            elif format == 'polars' and POLARS_AVAILABLE:
                self._save_polars(data, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
            self.logger.info(f"Saved data to {file_path} in {format} format")
            
        except Exception as e:
            self.logger.error(f"Error saving file {file_path}: {str(e)}")
            raise
    
    def _save_csv(self, data: Union[pd.DataFrame, 'pl.DataFrame'], file_path: str) -> None:
        """Save data to CSV format."""
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
    
    def _save_parquet(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], file_path: str) -> None:
        """Save data to Parquet format."""
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
    
    def _save_feather(self, data: Union[pd.DataFrame, 'pl.DataFrame'], file_path: str) -> None:
        """Save data to Feather format."""
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
    
    def _save_json(self, data: Union[pd.DataFrame, dict], file_path: str) -> None:
        """Save data to JSON format."""
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
    
    def _save_duckdb(self, data: Union[pd.DataFrame, 'pl.DataFrame'], file_path: str) -> None:
        """Save data to DuckDB format."""
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
    
    def _save_txt(self, data: Union[pd.DataFrame, 'pl.DataFrame'], file_path: str) -> None:
        """Save data to TXT format."""
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
    
    def _save_keras(self, data: pd.DataFrame, file_path: str) -> None:
        """Save data to Keras format."""
        if isinstance(data, pd.DataFrame):
            from tensorflow.keras import Sequential, Input
            from tensorflow.keras.layers import Dense
            model = Sequential([Input(shape=(len(data.columns),)), Dense(32, activation='relu'), Dense(1)])
            model.save(file_path)
            self.logger.info(f"Saved Keras model: {file_path}")
        else:
            raise ValueError(f"Cannot save {type(data)} to Keras format")
    
    def _save_tensorflow(self, data: pd.DataFrame, file_path: str) -> None:
        """Save data to TensorFlow NPZ format."""
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for .npz format but is not available. Please install numpy: pip install numpy")
        if isinstance(data, pd.DataFrame):
            try:
                # Save data array and column names to preserve DataFrame structure
                np.savez(file_path, 
                        data=data.to_numpy(),
                        columns=np.array(data.columns.tolist(), dtype=object))
                self.logger.info(f"Saved TensorFlow NPZ: {file_path}")
            except Exception as e:
                self.logger.error(f"Error saving NPZ file: {str(e)}")
                raise Exception(f"Failed to save .npz file: {str(e)}")
        else:
            raise ValueError(f"Cannot save {type(data)} to TensorFlow/NPZ format")
    
    def _save_pyarrow(self, data: Union[pd.DataFrame, 'pa.Table'], file_path: str) -> None:
        """Save data to PyArrow format."""
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
    
    def _save_polars(self, data: Union[pd.DataFrame, 'pl.DataFrame'], file_path: str) -> None:
        """Save data to Polars format."""
        if isinstance(data, pd.DataFrame):
            pl.from_pandas(data).write_parquet(file_path)
            self.logger.info(f"Saved Polars format: {file_path}")
        elif isinstance(data, pl.DataFrame):
            data.write_parquet(file_path)
            self.logger.info(f"Saved Polars format: {file_path}")
        else:
            raise ValueError(f"Cannot save {type(data)} to Polars format")


