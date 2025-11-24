"""
Analysis helper utilities for REDLINE Web GUI
Shared utility functions for data analysis operations
"""

import logging
import os
import pandas as pd
import numpy as np
import math

logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    # Handle None
    if obj is None:
        return None
    
    # Handle dicts
    if isinstance(obj, dict):
        return {str(k): convert_numpy_types(v) for k, v in obj.items()}
    
    # Handle lists
    if isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    
    # Handle numpy integers
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    
    # Handle numpy floats
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        val = float(obj)
        # Replace NaN and infinity with None or 0
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    
    # Handle regular floats with NaN/inf
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    
    # Handle numpy arrays
    if isinstance(obj, np.ndarray):
        return [convert_numpy_types(item) for item in obj.tolist()]
    
    # Handle pandas objects
    if isinstance(obj, pd.Series):
        return [convert_numpy_types(v) for v in obj.tolist()]
    
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    
    # Handle basic types that are JSON serializable
    if isinstance(obj, (str, int, bool)):
        return obj
    
    # Fallback: convert to string for anything else
    try:
        return str(obj)
    except:
        return None


def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def detect_date_columns(df):
    """
    Detect and return list of columns that are likely dates/timestamps.
    Used to exclude them from numeric analysis.
    """
    date_keywords = ['date', 'time', 'timestamp', 'year', 'month', 'day']
    date_cols = [col for col in df.columns 
                if any(keyword in str(col).lower() for keyword in date_keywords) 
                or pd.api.types.is_datetime64_any_dtype(df[col])]
    
    # Also exclude columns that are likely date components (year, month, day as integers)
    # Check if column values look like dates (years 1900-2100, months 1-12, days 1-31)
    for col in df.columns:
        if col not in date_cols and pd.api.types.is_integer_dtype(df[col]):
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) > 0:
                min_val, max_val = unique_vals.min(), unique_vals.max()
                # Check if values look like years, months, or days
                if (col.lower() == 'year' or (min_val >= 1900 and max_val <= 2100 and len(unique_vals) <= 100)):
                    date_cols.append(col)
                elif (col.lower() == 'month' or (min_val >= 1 and max_val <= 12 and len(unique_vals) <= 12)):
                    date_cols.append(col)
                elif (col.lower() == 'day' or (min_val >= 1 and max_val <= 31 and len(unique_vals) <= 31)):
                    date_cols.append(col)
    
    # Also exclude columns with very large numbers that could be timestamps
    # Unix timestamps (seconds): 1000000000-2000000000 (2001-2033)
    # Unix timestamps (milliseconds): 1000000000000-2000000000000
    # Excel serial dates: 40000-50000 (around 2009-2037)
    for col in df.columns:
        if col not in date_cols and pd.api.types.is_numeric_dtype(df[col]):
            numeric_vals = df[col].dropna()
            if len(numeric_vals) > 0:
                min_val, max_val = numeric_vals.min(), numeric_vals.max()
                # Check for Unix timestamps (seconds) - 1000000000 to 2000000000
                if min_val >= 1000000000 and max_val <= 2000000000:
                    date_cols.append(col)
                    logger.debug(f"Excluding column '{col}' as Unix timestamp (seconds): range {min_val}-{max_val}")
                # Check for Unix timestamps (milliseconds) - 1000000000000 to 2000000000000
                elif min_val >= 1000000000000 and max_val <= 2000000000000:
                    date_cols.append(col)
                    logger.debug(f"Excluding column '{col}' as Unix timestamp (milliseconds): range {min_val}-{max_val}")
                # Check for Excel serial dates - 40000 to 50000
                elif min_val >= 40000 and max_val <= 50000:
                    date_cols.append(col)
                    logger.debug(f"Excluding column '{col}' as Excel serial date: range {min_val}-{max_val}")
                # Check for very large numbers that are suspiciously date-like
                # If values are in millions and look like they could be timestamps
                # Be more aggressive: if all values are in this range and there are many unique values,
                # it's likely a timestamp column (even without date-like name)
                elif min_val > 10000000 and max_val < 1000000000:
                    unique_count = len(numeric_vals.unique())
                    total_count = len(numeric_vals)
                    # If most values are unique and in suspicious range, likely timestamps
                    if unique_count > 50 and (unique_count / total_count) > 0.8:
                        date_cols.append(col)
                        logger.debug(f"Excluding column '{col}' as potential timestamp: range {min_val:.2f}-{max_val:.2f}, {unique_count} unique values")
                    # Also exclude if column name suggests it's a date
                    elif any(keyword in str(col).lower() for keyword in ['time', 'date', 'stamp', 'epoch']):
                        date_cols.append(col)
                        logger.debug(f"Excluding column '{col}' as potential timestamp based on name and value range")
    
    return date_cols


def detect_ticker_column(df):
    """
    Detect ticker/identifier column using multiple heuristics.
    Returns the most likely ticker column name, or None if not found.
    """
    # Priority 1: Column name patterns
    ticker_patterns = [
        'ticker', '<ticker>', 'symbol', 'sym', 'id', 'identifier',
        'stock', 'instrument', 'asset', 'code'
    ]
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in ticker_patterns):
            return col
    
    # Priority 2: Heuristic - find column with characteristics of ticker data
    # Ticker data typically: string/categorical, low cardinality, short values
    best_col = None
    best_score = -1
    
    for col in df.columns:
        try:
            # Ticker columns are usually strings or objects
            if not pd.api.types.is_object_dtype(df[col]):
                continue
            
            values = df[col].dropna()
            if len(values) < 2:
                continue
            
            # Calculate characteristics
            unique_count = values.nunique()
            total_count = len(values)
            avg_length = values.astype(str).str.len().mean()
            
            # Score based on characteristics typical of ticker data
            score = 0
            
            # Low cardinality (few unique values relative to total)
            if unique_count < total_count * 0.1:  # Less than 10% unique
                score += 20
            elif unique_count < total_count * 0.5:  # Less than 50% unique
                score += 10
            
            # Short string values (tickers are usually 1-10 characters)
            if 1 <= avg_length <= 10:
                score += 15
            
            # Mostly uppercase or alphanumeric (typical of ticker symbols)
            sample = values.head(100).astype(str)
            if len(sample) > 0:
                uppercase_ratio = sample.str.isupper().sum() / len(sample)
                alnum_ratio = sample.str.isalnum().sum() / len(sample)
                if uppercase_ratio > 0.5:
                    score += 10
                if alnum_ratio > 0.8:
                    score += 5
            
            if score > best_score:
                best_score = score
                best_col = col
        except:
            continue
    
    return best_col


def detect_timestamp_column(df):
    """
    Detect timestamp/date column using multiple heuristics.
    Returns the most likely timestamp column name, or None if not found.
    """
    # Priority 1: Column name patterns
    timestamp_patterns = [
        'timestamp', 'date', 'time', '<date>', '<time>', '<timestamp>',
        'datetime', 'dt', 'ts', 'epoch', 'stamp'
    ]
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in timestamp_patterns):
            # Check if it's actually a datetime type
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
            # Or if it can be converted to datetime
            try:
                test_convert = pd.to_datetime(df[col].head(10), errors='coerce')
                if test_convert.notna().sum() > 5:  # Most values convertible
                    return col
            except:
                pass
    
    # Priority 2: Check datetime dtypes
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    
    # Priority 3: Heuristic - find numeric column with timestamp-like values
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_vals = df[col].dropna()
            if len(numeric_vals) > 0:
                min_val, max_val = numeric_vals.min(), numeric_vals.max()
                # Check for Unix timestamps (seconds) - 1000000000 to 2000000000
                if min_val >= 1000000000 and max_val <= 2000000000:
                    return col
                # Check for Unix timestamps (milliseconds)
                elif min_val >= 1000000000000 and max_val <= 2000000000000:
                    return col
                # Check for Excel serial dates
                elif min_val >= 40000 and max_val <= 50000:
                    return col
    
    return None


def detect_price_column(df):
    """
    Detect price column using multiple heuristics.
    Returns the most likely price column name.
    """
    # Get all numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return None
    
    # Priority 1: Column name patterns (most common financial data formats)
    price_patterns = [
        'close', 'price', 'adj close', 'px_last', '<close>', 'c',
        'last', 'settle', 'px_settle', 'closing', 'cl'
    ]
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in price_patterns):
            if col in numeric_cols:
                return col
    
    # Priority 1.5: For generic column names (col_0, col_1, etc.), try to infer from position
    # Typical financial data structure: TICKER, DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL
    # CLOSE is usually the 7th column (index 6) or 4th numeric column
    if all(str(col).startswith('col_') for col in df.columns):
        # Count numeric columns and try position-based detection
        numeric_col_list = [col for col in df.columns if col in numeric_cols]
        # CLOSE is typically the 4th numeric column (after OPEN, HIGH, LOW)
        if len(numeric_col_list) >= 4:
            # Try the 4th numeric column as CLOSE
            close_candidate = numeric_col_list[3]
            values = pd.to_numeric(df[close_candidate], errors='coerce').dropna()
            if len(values) > 0 and values.min() > 0 and 0.01 < values.mean() < 1000000:
                return close_candidate
    
    # Priority 2: Heuristic - find numeric column with characteristics of price data
    # Price data typically: positive values, moderate variance, not too large
    best_col = None
    best_score = -1
    
    for col in numeric_cols:
        try:
            values = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(values) < 2:
                continue
            
            # Calculate characteristics
            mean_val = values.mean()
            std_val = values.std()
            min_val = values.min()
            max_val = values.max()
            
            # Skip if all values are negative or zero
            if min_val <= 0:
                continue
            
            # Score based on characteristics typical of price data
            # Price data usually has: positive values, reasonable range, some variance
            score = 0
            
            # Positive values get higher score
            if min_val > 0:
                score += 10
            
            # Moderate coefficient of variation (not too volatile, not too stable)
            if mean_val > 0:
                cv = std_val / mean_val
                if 0.01 < cv < 2.0:  # Reasonable price volatility range
                    score += 20
            
            # Not too large (prices are usually in reasonable ranges)
            if 0.01 < mean_val < 1000000:
                score += 10
            
            # Has variation (not constant)
            if std_val > 0:
                score += 10
            
            if score > best_score:
                best_score = score
                best_col = col
        except:
            continue
    
    return best_col


def detect_volume_column(df):
    """
    Detect volume column using multiple heuristics.
    Returns the most likely volume column name.
    """
    # Get all numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return None
    
    # Priority 1: Column name patterns
    volume_patterns = [
        'volume', 'vol', '<vol>', 'px_volume', 'v',
        'qty', 'quantity', 'turnover', 'shares'
    ]
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in volume_patterns):
            if col in numeric_cols:
                return col
    
    # Priority 2: Heuristic - find numeric column with characteristics of volume data
    # Volume data typically: large positive values, high variance, integer-like
    best_col = None
    best_score = -1
    
    for col in numeric_cols:
        try:
            values = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(values) < 2:
                continue
            
            # Calculate characteristics
            mean_val = values.mean()
            std_val = values.std()
            min_val = values.min()
            
            # Skip if all values are negative or zero
            if min_val <= 0:
                continue
            
            # Score based on characteristics typical of volume data
            score = 0
            
            # Large values (volume is usually large numbers)
            if mean_val > 100:
                score += 10
            
            # High variance (volume varies significantly)
            if std_val > mean_val * 0.5:
                score += 10
            
            # Positive values
            if min_val > 0:
                score += 10
            
            # Integer-like (volume is usually whole numbers)
            # Check if most values are close to integers
            sample = values.head(100)
            if len(sample) > 0:
                integer_like = (sample % 1).abs().mean() < 0.1
                if integer_like:
                    score += 10
            
            if score > best_score:
                best_score = score
                best_col = col
        except:
            continue
    
    return best_col


def _load_data_file(filename, file_path_hint=None):
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
    from ..utils.data_helpers import clean_dataframe_columns
    
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
        import numpy as np
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

