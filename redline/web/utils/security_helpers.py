#!/usr/bin/env python3
"""
Security helpers for masking sensitive data like API keys.
"""

import re
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

# Patterns to identify API keys
API_KEY_PATTERNS = [
    r'api[_-]?key',
    r'apikey',
    r'api[_-]?token',
    r'access[_-]?token',
    r'secret[_-]?key',
    r'auth[_-]?token',
    r'authorization',
    r'bearer',
]

# Known API key file names
API_KEY_FILES = [
    'api_keys.json',
    'custom_apis.json',
    'data/api_keys.json',
    'data/custom_apis.json',
]

# Known API key column names (case-insensitive)
API_KEY_COLUMNS = [
    'api_key',
    'apikey',
    'api-key',
    'api_token',
    'api-token',
    'access_token',
    'access-token',
    'secret_key',
    'secret-key',
    'auth_token',
    'auth-token',
    'authorization',
    'bearer',
    'token',
]


def mask_api_key(value: Any) -> str:
    """
    Mask an API key value, showing only first 4 and last 4 characters.
    
    Args:
        value: The API key value to mask
        
    Returns:
        Masked string (e.g., "abcd...xyz1")
    """
    if not value:
        return str(value) if value is not None else ''
    
    value_str = str(value).strip()
    
    # If value is too short, mask completely
    if len(value_str) <= 8:
        return '***' * len(value_str) if value_str else ''
    
    # Show first 4 and last 4 characters
    return f"{value_str[:4]}...{value_str[-4:]}"


def is_api_key_column(column_name: str) -> bool:
    """
    Check if a column name indicates it contains API keys.
    
    Args:
        column_name: The column name to check
        
    Returns:
        True if column likely contains API keys
    """
    if not column_name:
        return False
    
    column_lower = str(column_name).lower().strip()
    
    # Check against known API key column names
    if column_lower in [col.lower() for col in API_KEY_COLUMNS]:
        return True
    
    # Check against patterns
    for pattern in API_KEY_PATTERNS:
        if re.search(pattern, column_lower, re.IGNORECASE):
            return True
    
    return False


def is_api_key_value(value: Any) -> bool:
    """
    Check if a value looks like an API key.
    
    Args:
        value: The value to check
        
    Returns:
        True if value looks like an API key
    """
    if not value:
        return False
    
    value_str = str(value).strip()
    
    # API keys are typically:
    # - Long strings (20+ characters)
    # - Alphanumeric with possible special characters
    # - Not dates or numbers
    
    if len(value_str) < 16:
        return False
    
    # Check if it's a date or number
    try:
        float(value_str)
        return False  # It's a number
    except (ValueError, TypeError):
        pass
    
    # Check if it looks like an API key format
    # Common patterns: alphanumeric, base64-like, UUID-like
    if re.match(r'^[A-Za-z0-9_-]{20,}$', value_str):
        # Could be an API key, but also could be other long strings
        # Be conservative - only mask if column name suggests it
        return False
    
    return False  # Default: don't auto-detect, only mask based on column name


def mask_dataframe_columns(df, columns_to_mask: List[str] = None):
    """
    Mask API keys in a DataFrame.
    
    Args:
        df: pandas DataFrame
        columns_to_mask: Optional list of column names to mask. If None, auto-detect.
        
    Returns:
        DataFrame with API keys masked
    """
    try:
        import pandas as pd
        
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Determine which columns to mask
        if columns_to_mask is None:
            columns_to_mask = []
            for col in df.columns:
                if is_api_key_column(str(col)):
                    columns_to_mask.append(col)
        
        # Mask the columns
        for col in columns_to_mask:
            if col in df.columns:
                df[col] = df[col].apply(mask_api_key)
                logger.debug(f"Masked API key column: {col}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error masking DataFrame columns: {str(e)}")
        return df


def mask_dict_data(data: Union[Dict, List], depth: int = 0, max_depth: int = 10) -> Union[Dict, List]:
    """
    Recursively mask API keys in dictionary or list data.
    
    Args:
        data: Dictionary or list to mask
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops
        
    Returns:
        Data with API keys masked
    """
    if depth > max_depth:
        return data
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            key_str = str(key)
            
            # Check if key indicates API key
            if is_api_key_column(key_str):
                masked[key] = mask_api_key(value)
            elif isinstance(value, (dict, list)):
                masked[key] = mask_dict_data(value, depth + 1, max_depth)
            else:
                masked[key] = value
        
        return masked
    
    elif isinstance(data, list):
        return [mask_dict_data(item, depth + 1, max_depth) for item in data]
    
    else:
        return data


def should_mask_file(filename: str) -> bool:
    """
    Check if a file should have its contents masked (e.g., API key files).
    
    Args:
        filename: The filename to check
        
    Returns:
        True if file should be masked
    """
    filename_lower = filename.lower()
    
    # Check against known API key file names
    for api_file in API_KEY_FILES:
        if api_file.lower() in filename_lower or filename_lower.endswith(api_file.lower()):
            return True
    
    # Check if filename contains API key indicators
    if 'api_key' in filename_lower or 'apikey' in filename_lower:
        return True
    
    return False

