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
    '.txt': 'txt',
    '.json': 'json',
    '.duckdb': 'duckdb',
    '.parquet': 'parquet',
    '.feather': 'feather',
    '.h5': 'keras'
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
    'tensorflow': ('.npz',  'NumPy Zip', '*.npz')
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
