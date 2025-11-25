#!/usr/bin/env python3
"""
REDLINE Column Detectors
Functions for detecting column types in financial data.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def _is_repeated_pattern(s):
    """Check if string is a repetition of a shorter substring (e.g., 'IBMIBM', 'AAPLAAPL')."""
    if not isinstance(s, str) or len(s) < 2:
        return False
    # Check if string is repetition of first N characters
    for i in range(1, len(s) // 2 + 1):
        substring = s[:i]
        if len(s) % len(substring) == 0:
            repetitions = len(s) // len(substring)
            if substring * repetitions == s:
                return True
    return False


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
            # Check if column contains repeated string patterns before converting
            sample = df[close_candidate].dropna().head(10)
            if len(sample) > 0 and all(isinstance(x, str) for x in sample):
                first_val = str(sample.iloc[0])
                if _is_repeated_pattern(first_val):
                    logger.warning(f"Skipping column '{close_candidate}' - contains repeated pattern: '{first_val[:20]}...'")
                else:
                    # Not a repeated pattern, try numeric conversion
                    values = pd.to_numeric(df[close_candidate], errors='coerce').dropna()
                    if len(values) > 0 and values.min() > 0 and 0.01 < values.mean() < 1000000:
                        return close_candidate
            else:
                # Not all strings, try numeric conversion
                values = pd.to_numeric(df[close_candidate], errors='coerce').dropna()
                if len(values) > 0 and values.min() > 0 and 0.01 < values.mean() < 1000000:
                    return close_candidate
    
    # Priority 2: Heuristic - find numeric column with characteristics of price data
    # Price data typically: positive values, moderate variance, not too large
    best_col = None
    best_score = -1
    
    for col in numeric_cols:
        try:
            # Check if column contains repeated string patterns before converting
            sample = df[col].dropna().head(10)
            if len(sample) > 0 and all(isinstance(x, str) for x in sample):
                first_val = str(sample.iloc[0])
                if _is_repeated_pattern(first_val):
                    logger.warning(f"Skipping column '{col}' - contains repeated pattern: '{first_val[:20]}...'")
                    continue
            
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
            # Check if column contains repeated string patterns before converting
            sample = df[col].dropna().head(10)
            if len(sample) > 0 and all(isinstance(x, str) for x in sample):
                first_val = str(sample.iloc[0])
                if _is_repeated_pattern(first_val):
                    logger.warning(f"Skipping column '{col}' - contains repeated pattern: '{first_val[:20]}...'")
                    continue
            
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

