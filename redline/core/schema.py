#!/usr/bin/env python3
"""
REDLINE Core Schema Definitions
Defines data schemas and format mappings for financial data processing.
"""

# Check for optional dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import pyarrow as pa
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

# Standard REDLINE data schema
SCHEMA = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']

# File extension to format mapping (base formats always available)
_EXT_TO_FORMAT_BASE = {
    '.csv': 'csv',
    '.json': 'json',
    '.duckdb': 'duckdb',
    '.parquet': 'parquet',
    '.feather': 'feather',
    '.txt': 'txt',
}

# Add optional formats based on availability
if TENSORFLOW_AVAILABLE:
    _EXT_TO_FORMAT_BASE['.h5'] = 'keras'
    _EXT_TO_FORMAT_BASE['.npz'] = 'tensorflow'

if PYARROW_AVAILABLE:
    _EXT_TO_FORMAT_BASE['.arrow'] = 'pyarrow'

EXT_TO_FORMAT = _EXT_TO_FORMAT_BASE

# File dialog information mapping (base formats)
_FORMAT_DIALOG_INFO_BASE = {
    'csv':     ('.csv',     'CSV Files', '*.csv'),
    'txt':     ('.txt',     'TXT Files', '*.txt'),
    'json':    ('.json',    'JSON Files', '*.json'),
    'duckdb':  ('.duckdb',  'DuckDB Files', '*.duckdb'),
    'parquet': ('.parquet', 'Parquet Files', '*.parquet'),
    'feather': ('.feather', 'Feather Files', '*.feather'),
}

# Add optional formats based on availability
if TENSORFLOW_AVAILABLE:
    _FORMAT_DIALOG_INFO_BASE['keras'] = ('.h5', 'Keras Model', '*.h5')
    _FORMAT_DIALOG_INFO_BASE['tensorflow'] = ('.npz', 'TensorFlow NumPy', '*.npz')

if PYARROW_AVAILABLE:
    _FORMAT_DIALOG_INFO_BASE['pyarrow'] = ('.arrow', 'Apache Arrow', '*.arrow')

if POLARS_AVAILABLE:
    _FORMAT_DIALOG_INFO_BASE['polars'] = ('.parquet', 'Polars DataFrame', '*.parquet')

FORMAT_DIALOG_INFO = _FORMAT_DIALOG_INFO_BASE

# Stooq format columns for validation
STOOQ_COLUMNS = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']

# Numeric columns that require type conversion
NUMERIC_COLUMNS = ['open', 'high', 'low', 'close', 'vol', 'openint']

# Required columns for data validation
REQUIRED_COLUMNS = ['ticker', 'timestamp', 'close']

# Default date format
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Default time format for Stooq
STOOQ_TIME_FORMAT = '000000'


def detect_format_from_path(file_path: str) -> str:
    """
    Detect file format from file path extension.
    
    This is the centralized format detection function used across the codebase.
    All format detection should use this function to ensure consistency.
    
    Args:
        file_path: Path to the file (can be full path or just filename)
        
    Returns:
        Detected format type (defaults to 'csv' if extension not recognized)
        
    Examples:
        >>> detect_format_from_path('data.csv')
        'csv'
        >>> detect_format_from_path('/path/to/file.json')
        'json'
        >>> detect_format_from_path('unknown.xyz')
        'csv'
    """
    import os
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_TO_FORMAT.get(ext, 'csv')
