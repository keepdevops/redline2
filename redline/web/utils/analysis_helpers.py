"""
Analysis helper utilities for REDLINE Web GUI
Shared utility functions for data analysis operations.

This module now serves as a compatibility layer that re-exports functions
from specialized modules for backward compatibility.
"""

import logging

# Import from specialized modules
from .data_loaders import load_data_file
from .column_detectors import (
    detect_date_columns,
    detect_ticker_column,
    detect_timestamp_column,
    detect_price_column,
    detect_volume_column
)
from .analysis_utils import (
    convert_numpy_types,
    flatten_dict
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
# Keep the old function name with underscore for internal use
_load_data_file = load_data_file

# Public API - all functions are available directly
__all__ = [
    'convert_numpy_types',
    'flatten_dict',
    'detect_date_columns',
    'detect_ticker_column',
    'detect_timestamp_column',
    'detect_price_column',
    'detect_volume_column',
    'load_data_file',
    '_load_data_file'  # Keep for backward compatibility
]

