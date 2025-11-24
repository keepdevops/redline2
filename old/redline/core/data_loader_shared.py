#!/usr/bin/env python3
"""
DataLoader class extracted from data_module_shared.py (shared module)
Main data loading functionality - Part 1: Core loading and validation.
"""

import logging
import configparser
import pandas as pd
from typing import Union, List, Any
import os

# Optional dependencies
try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None

try:
    import duckdb
except ImportError:
    duckdb = None

logger = logging.getLogger(__name__)


class DataLoader:
    """Legacy data loader for stock market data management."""
    
    SCHEMA = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
    EXT_TO_FORMAT = {
        '.csv': 'csv',
        '.txt': 'txt',
        '.json': 'json',
        '.duckdb': 'duckdb',
        '.parquet': 'parquet',
        '.feather': 'feather',
        '.h5': 'keras'
    }
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

    @staticmethod
    def clean_and_select_columns(data: pd.DataFrame) -> pd.DataFrame:
        """Clean and select columns according to schema."""
        try:
            data = data.copy()
            for col in DataLoader.SCHEMA:
                if col not in data.columns:
                    data[col] = None
            data = data[DataLoader.SCHEMA]
            numeric_cols = ['open', 'high', 'low', 'close', 'vol', 'openint']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                    data[col] = data[col].apply(
                        lambda x: float(x) if pd.notnull(x) and not isinstance(x, (list, tuple, dict)) else None
                    )
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
            return data
        except Exception as e:
            logger.error(f"Error in clean_and_select_columns: {str(e)}")
            raise

    def __init__(self, config_path: str = 'data_config.ini'):
        """Initialize DataLoader with configuration."""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.db_path = self.config['Data'].get('db_path', '/app/redline_data.duckdb')
        self.csv_dir = self.config['Data'].get('csv_dir', '/app/data')
        self.json_dir = self.config['Data'].get('json_dir', '/app/data/json')
        self.parquet_dir = self.config['Data'].get('parquet_dir', '/app/data/parquet')

    def validate_data(self, file_path: str, format: str) -> bool:
        """Validate data file format."""
        try:
            if format == 'txt':
                with open(file_path, 'r') as f:
                    header = f.readline().strip()
                required_cols = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
                header_cols = [col.strip() for col in header.split(',')]
                missing_cols = [col for col in required_cols if col not in header_cols]
                if missing_cols:
                    logger.warning(f"Missing required columns in {file_path}: {', '.join(missing_cols)}")
                    return False
                return True
            elif format in ['csv', 'json']:
                df = pd.read_csv(file_path) if format == 'csv' else pd.read_json(file_path)
                required = ['ticker', 'timestamp', 'close']
                return all(col in df.columns for col in required)
            return True
        except Exception as e:
            logger.error(f"Validation failed for {file_path}: {str(e)}")
            return False

    def load_data(self, file_paths: List[str], format: str, delete_empty: bool = False) -> List[Union[pd.DataFrame, Any, Any]]:
        """Load data from multiple files."""
        data = []
        skipped_files = []
        for path in file_paths:
            try:
                relative_path = path.replace('/app/', '')
                if not self.validate_data(relative_path, format):
                    skipped_files.append({'file': os.path.basename(path), 'reason': 'Failed validation'})
                    continue
                df = pd.read_csv(relative_path)
                df = self._standardize_txt_columns(df)
                if not all(col in df.columns for col in ['ticker', 'timestamp', 'close']):
                    skipped_files.append({'file': os.path.basename(path), 'reason': 'Missing required columns after standardization'})
                    continue
                data.append(df)
                logger.info(f"Successfully loaded {path}")
            except Exception as e:
                logger.error(f"Failed to load {path}: {str(e)}")
                skipped_files.append({'file': os.path.basename(path), 'reason': str(e)})
        if not data:
            raise ValueError(f"No valid data could be loaded. Skipped files: {', '.join([f['file'] for f in skipped_files])}")
        return data

