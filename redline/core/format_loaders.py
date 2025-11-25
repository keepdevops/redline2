#!/usr/bin/env python3
"""
REDLINE Format Loaders
Handles loading data from different file formats.
"""

import logging
import pandas as pd
from typing import Union
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


class FormatLoaders:
    """Handles loading data from different file formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
                return self._load_parquet(file_path)
            elif format == 'feather':
                return pd.read_feather(file_path)
            elif format == 'json':
                return pd.read_json(file_path)
            elif format == 'txt':
                return self._load_txt(file_path)
            elif format == 'duckdb':
                return self._load_duckdb(file_path)
            elif format == 'keras' and TENSORFLOW_AVAILABLE:
                return tf.keras.models.load_model(file_path)
            elif format == 'tensorflow' and NUMPY_AVAILABLE:
                return self._load_tensorflow(file_path)
            elif format == 'pyarrow' and PYARROW_AVAILABLE:
                return pa.ipc.open_file(file_path).read_all().to_pandas()
            elif format == 'polars' and POLARS_AVAILABLE:
                return pl.read_parquet(file_path).to_pandas()
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            raise
    
    def _load_parquet(self, file_path: str) -> pd.DataFrame:
        """Load parquet file with fallback handling."""
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
    
    def _load_txt(self, file_path: str) -> pd.DataFrame:
        """Load TXT file with format detection."""
        try:
            # Try to detect TXT format (Stooq format is comma-separated, others may be tab-separated)
            # First, try to read first line to detect format
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
            
            # Check if it's Stooq format (comma-separated with <TICKER> header)
            if '<TICKER>' in first_line or '<DATE>' in first_line:
                # Stooq format - comma-separated
                self.logger.info(f"Detected Stooq format (comma-separated) for {file_path}")
                return pd.read_csv(file_path, sep=',')
            else:
                # Try tab-separated first (common for TXT files)
                try:
                    self.logger.info(f"Attempting tab-separated format for {file_path}")
                    return pd.read_csv(file_path, sep='\t')
                except:
                    # Fallback to comma-separated
                    self.logger.info(f"Falling back to comma-separated format for {file_path}")
                    return pd.read_csv(file_path, sep=',')
        except Exception as txt_error:
            self.logger.error(f"Error reading TXT file {file_path}: {str(txt_error)}")
            # Last resort: try reading as CSV with default settings
            try:
                self.logger.info(f"Attempting CSV fallback for {file_path}")
                return pd.read_csv(file_path)
            except:
                raise txt_error
    
    def _load_duckdb(self, file_path: str) -> pd.DataFrame:
        """Load data from DuckDB database."""
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
    
    def _load_tensorflow(self, file_path: str) -> pd.DataFrame:
        """Load TensorFlow NPZ file."""
        # Use allow_pickle=True for .npz files that may contain object arrays
        loaded = np.load(file_path, allow_pickle=True)
        if 'data' in loaded:
            data_array = loaded['data']
            # Restore column names if they were saved
            if 'columns' in loaded:
                columns = loaded['columns'].tolist()
                df = pd.DataFrame(data_array, columns=columns)
            else:
                # Fallback: create generic column names
                df = pd.DataFrame(data_array, columns=[f'col_{i}' for i in range(data_array.shape[1])])
            
            # Convert object columns to numeric where possible (important for .npz files with mixed types)
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    # If most values converted successfully, use numeric type
                    if numeric_series.notna().sum() > len(df) * 0.5:  # More than 50% numeric
                        df[col] = numeric_series
            
            return df
        else:
            first_key = list(loaded.keys())[0]
            df = pd.DataFrame(loaded[first_key])
            # Convert object columns to numeric where possible
            for col in df.columns:
                if df[col].dtype == 'object':
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if numeric_series.notna().sum() > len(df) * 0.5:
                        df[col] = numeric_series
            return df
