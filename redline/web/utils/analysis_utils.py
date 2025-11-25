#!/usr/bin/env python3
"""
REDLINE Analysis Utilities
Utility functions for data analysis operations.
"""

import logging
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

