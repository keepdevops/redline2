#!/usr/bin/env python3
"""
JSON utilities for handling NaN values and data cleaning.
Centralized functions for JSON serialization of pandas DataFrames.
"""

import logging
from typing import Any, Union, Dict, List

logger = logging.getLogger(__name__)


def replace_nan_in_dict(obj: Any) -> Any:
    """
    Recursively replace NaN, NaT, and None values with None for JSON serialization.
    
    This function ensures that pandas NaN/NaT values are converted to None,
    which is valid JSON. This is necessary because NaN is not valid JSON.
    
    Args:
        obj: The object to clean (dict, list, or primitive value)
        
    Returns:
        Object with NaN/NaT values replaced with None
        
    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> data = {'value': np.nan, 'nested': {'x': pd.NaT}}
        >>> cleaned = replace_nan_in_dict(data)
        >>> cleaned
        {'value': None, 'nested': {'x': None}}
    """
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        # If pandas/numpy not available, just return the object
        logger.warning("pandas/numpy not available, skipping NaN replacement")
        return obj
    
    if isinstance(obj, dict):
        return {k: replace_nan_in_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_in_dict(item) for item in obj]
    else:
        # Check for NaN/NaT/NA values using pandas
        try:
            if pd.isna(obj) or pd.isnull(obj):
                return None
        except (TypeError, ValueError):
            # If pd.isna fails, try other checks
            pass
        
        # Check numpy NaN (NaN != NaN)
        try:
            if isinstance(obj, float) and (obj != obj):
                return None
        except (TypeError, ValueError):
            pass
        
        # For other types (str, int, None, etc.), return as-is
        return obj


def clean_dataframe_for_json(df) -> List[Dict]:
    """
    Convert a pandas DataFrame to a list of dictionaries with NaN values cleaned.
    
    This is a convenience function that combines DataFrame.to_dict() with
    replace_nan_in_dict() to ensure valid JSON output.
    
    Args:
        df: pandas DataFrame to convert
        
    Returns:
        List of dictionaries with NaN values replaced with None
        
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2, None], 'b': [3.0, pd.NA, 5.0]})
        >>> cleaned = clean_dataframe_for_json(df)
        >>> cleaned
        [{'a': 1, 'b': 3.0}, {'a': None, 'b': None}, {'a': None, 'b': 5.0}]
    """
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas not available for DataFrame cleaning")
        return []
    
    if df is None or df.empty:
        return []
    
    # Convert DataFrame to list of dictionaries
    data_dict = df.to_dict(orient='records')
    
    # Clean NaN values
    cleaned_data = [replace_nan_in_dict(record) for record in data_dict]
    
    return cleaned_data

