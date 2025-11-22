#!/usr/bin/env python3
"""
REDLINE Core Schema Definitions
Defines data schemas and format mappings for financial data processing.
"""

# Standard REDLINE data schema
SCHEMA = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']

# File extension to format mapping
EXT_TO_FORMAT = {
    '.csv': 'csv',
    '.json': 'json',
    '.duckdb': 'duckdb',
    '.parquet': 'parquet',
    '.feather': 'feather',
    '.txt': 'txt',
    '.h5': 'keras',
    '.npz': 'tensorflow',
    '.arrow': 'pyarrow'
}

# File dialog information mapping
FORMAT_DIALOG_INFO = {
    'csv':     ('.csv',     'CSV Files', '*.csv'),
    'txt':     ('.txt',     'TXT Files', '*.txt'),
    'json':    ('.json',    'JSON Files', '*.json'),
    'duckdb':  ('.duckdb',  'DuckDB Files', '*.duckdb'),
    'parquet': ('.parquet', 'Parquet Files', '*.parquet'),
    'feather': ('.feather', 'Feather Files', '*.feather'),
    'keras':   ('.h5',      'Keras Model', '*.h5'),
    'tensorflow': ('.npz',  'TensorFlow NumPy', '*.npz'),
    'pyarrow': ('.arrow',   'Apache Arrow', '*.arrow'),
    'polars':  ('.parquet', 'Polars DataFrame', '*.parquet')
}

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
