#!/usr/bin/env python3
"""
REDLINE Format Converter
Handles conversion between different data formats and file I/O operations.
"""

import logging
import pandas as pd
from typing import Union, List

# Optional dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    TENSORFLOW_AVAILABLE = False

try:
    import pyarrow as pa
    PYARROW_AVAILABLE = True
except ImportError:
    pa = None
    PYARROW_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False

from .format_loaders import FormatLoaders
from .format_savers import FormatSavers
from .format_converters import FormatConverters

logger = logging.getLogger(__name__)

class FormatConverter:
    """Handles format conversion and file I/O operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Initialize helper classes
        self.loaders = FormatLoaders()
        self.savers = FormatSavers()
        self.converters = FormatConverters()
    
    def convert_format(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table'], 
                      from_format: str, to_format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict]:
        """
        Convert data between different formats.
        
        Args:
            data: Data to convert
            from_format: Source format
            to_format: Target format
            
        Returns:
            Converted data in target format
        """
        return self.converters.convert_format(data, from_format, to_format)
    
    def save_file_by_type(self, data: Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table', dict], 
                          file_path: str, format: str) -> None:
        """
        Save data to file based on format type.
        
        Args:
            data: Data to save
            file_path: Path to save file
            format: Format type
        """
        self.savers.save_file_by_type(data, file_path, format)
    
    def load_file_by_type(self, file_path: str, format: str) -> Union[pd.DataFrame, 'pl.DataFrame', 'pa.Table']:
        """
        Load data from file based on format type.
        
        Args:
            file_path: Path to file
            format: Format type
            
        Returns:
            Loaded data
        """
        return self.loaders.load_file_by_type(file_path, format)
    
    def convert_to_stooq_format(self, data: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
        """
        Convert DataFrame to Stooq format.
        
        Args:
            data: DataFrame to convert
            ticker: Ticker symbol (if not provided, uses first ticker in data)
            
        Returns:
            DataFrame in Stooq format
        """
        return self.converters.convert_to_stooq_format(data, ticker)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        formats = ['csv', 'parquet', 'feather', 'json', 'duckdb', 'txt']
        if TENSORFLOW_AVAILABLE:
            formats.extend(['keras', 'tensorflow'])
        if PYARROW_AVAILABLE:
            formats.append('pyarrow')
        if POLARS_AVAILABLE:
            formats.append('polars')
        return formats
    
    def detect_format_from_extension(self, file_path: str) -> str:
        """
        Detect format from file extension (uses centralized function).
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected format
        """
        from .schema import detect_format_from_path
        return detect_format_from_path(file_path)
