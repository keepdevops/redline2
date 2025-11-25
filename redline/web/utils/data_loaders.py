#!/usr/bin/env python3
"""
REDLINE Data Loaders
Functions for loading data files in various formats.
"""

import logging
import os
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def load_data_file(filename, file_path_hint=None):
    """
    Load data file (shared helper).
    Preserves original column names from different API providers for flexibility.
    Only removes malformed columns (Unnamed, empty) via clean_dataframe_columns().
    
    Args:
        filename: Name of the file to load
        file_path_hint: Optional direct path to the file
        
    Returns:
        DataFrame with original column names preserved
        
    Raises:
        FileNotFoundError: If file is not found
        ValueError: If file format is invalid or DataFrame is empty
    """
    from redline.core.format_converter import FormatConverter
    from redline.core.schema import EXT_TO_FORMAT
    from .data_helpers import clean_dataframe_columns
    
    converter = FormatConverter()
    data_dir = os.path.join(os.getcwd(), 'data')
    data_path = None
    
    if file_path_hint and os.path.exists(file_path_hint):
        data_path = file_path_hint
    else:
        search_paths = [
            os.path.join(data_dir, filename),
            os.path.join(data_dir, 'stooq', filename),
            os.path.join(data_dir, 'downloaded', filename),
            os.path.join(data_dir, 'uploads', filename)
        ]
        
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            for root, dirs, files in os.walk(converted_dir):
                if filename in files:
                    search_paths.append(os.path.join(root, filename))
        
        for path in search_paths:
            if os.path.exists(path):
                data_path = path
                break
    
    if not data_path or not os.path.exists(data_path):
        raise FileNotFoundError(f'File not found: {filename}')
    
    ext = os.path.splitext(data_path)[1].lower()
    format_type = EXT_TO_FORMAT.get(ext, 'csv')
    
    if format_type == 'csv':
        df = pd.read_csv(data_path)
    elif format_type == 'parquet':
        df = pd.read_parquet(data_path)
    elif format_type == 'feather':
        df = pd.read_feather(data_path)
    elif format_type == 'json':
        df = pd.read_json(data_path)
    elif format_type == 'duckdb':
        import duckdb
        conn = duckdb.connect(data_path)
        df = conn.execute("SELECT * FROM tickers_data").fetchdf()
        conn.close()
    elif format_type in ('tensorflow', 'npz'):
        # Use allow_pickle=True for .npz files that may contain object arrays
        loaded = np.load(data_path, allow_pickle=True)
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
        else:
            first_key = list(loaded.keys())[0]
            df = pd.DataFrame(loaded[first_key])
            # Convert object columns to numeric where possible
            for col in df.columns:
                if df[col].dtype == 'object':
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if numeric_series.notna().sum() > len(df) * 0.5:
                        df[col] = numeric_series
    elif format_type == 'txt':
        # Handle TXT files (Stooq format or tab-separated)
        try:
            # Try reading as CSV first (Stooq format uses commas)
            df = pd.read_csv(data_path)
        except:
            # Try different separators for TXT files
            for sep in ['\t', ';', ' ', '|']:
                try:
                    df = pd.read_csv(data_path, sep=sep)
                    break
                except:
                    continue
            else:
                # If all separators fail, try reading as fixed-width
                df = pd.read_fwf(data_path)
    elif format_type in ('keras', 'h5'):
        raise ValueError('Keras model files (.h5) cannot be used for data analysis operations. Use the Analysis tab for model operations.')
    elif format_type in ('pyarrow', 'arrow'):
        try:
            import pyarrow as pa
            with pa.ipc.open_file(data_path) as reader:
                df = reader.read_all().to_pandas()
        except ImportError:
            raise ImportError('PyArrow is required to load .arrow files')
        except Exception as e:
            raise Exception(f'Error loading Arrow file: {str(e)}')
    else:
        df = converter.load_file_by_type(data_path, format_type)
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError('Invalid data format')
    
    # Clean malformed columns (Unnamed, empty) but preserve original API provider column names
    df = clean_dataframe_columns(df)
    
    # Check if DataFrame is empty (better validation)
    if df.empty:
        raise ValueError(f'Loaded DataFrame is empty for {filename}')
    
    return df

