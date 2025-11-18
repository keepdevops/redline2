"""
Analysis helper utilities for REDLINE Web GUI
Shared utility functions for data analysis operations
"""

import logging
import pandas as pd
import numpy as np
import math

logger = logging.getLogger(__name__)


def clean_dataframe_columns(df):
    """Clean up malformed CSV headers - remove unnamed/empty columns."""
    columns_to_drop = []
    cleaned_columns = []
    
    for i, col in enumerate(df.columns):
        # Drop columns with empty names or typical pandas unnamed column patterns
        if (col == '' or 
            str(col).strip() == '' or 
            str(col).startswith('Unnamed:') or
            (str(col) == '0' and i == 0 and len(df.columns) > 1)):  # First column named '0' usually indicates index issue
            columns_to_drop.append(col)
        else:
            # Clean column name
            clean_col = str(col).strip()
            # If still empty after cleaning, give it a meaningful name
            if clean_col == '':
                clean_col = f'Column_{i}'
            cleaned_columns.append(clean_col)
    
    # Drop the problematic columns
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        
    # Rename columns to cleaned versions
    if len(cleaned_columns) == len(df.columns):
        df.columns = cleaned_columns
        
    return df


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

