#!/usr/bin/env python3
"""
REDLINE Format Converters
Handles conversion between different data formats.
"""

import logging
import pandas as pd
from typing import Union

# Optional dependencies
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False

try:
    import pyarrow as pa
    PYARROW_AVAILABLE = True
except ImportError:
    pa = None
    PYARROW_AVAILABLE = False

logger = logging.getLogger(__name__)


class FormatConverters:
    """Handles conversion between different data formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
        if from_format == to_format:
            return data
            
        if isinstance(data, list):
            return [self.convert_format(d, from_format, to_format) for d in data]
            
        try:
            if from_format == 'pandas':
                if to_format == 'polars':
                    if not POLARS_AVAILABLE:
                        raise ImportError("polars not available")
                    return pl.from_pandas(data)
                elif to_format == 'pyarrow':
                    if not PYARROW_AVAILABLE:
                        raise ImportError("pyarrow not available")
                    return pa.Table.from_pandas(data)
            elif from_format == 'polars':
                if not POLARS_AVAILABLE:
                    raise ImportError("polars not available")
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'pyarrow':
                    if not PYARROW_AVAILABLE:
                        raise ImportError("pyarrow not available")
                    return data.to_arrow()
            elif from_format == 'pyarrow':
                if not PYARROW_AVAILABLE:
                    raise ImportError("pyarrow not available")
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'polars':
                    if not POLARS_AVAILABLE:
                        raise ImportError("polars not available")
                    return pl.from_arrow(data)
                    
            self.logger.info(f"Converted from {from_format} to {to_format}")
            return data
            
        except Exception as e:
            self.logger.error(f"Conversion failed from {from_format} to {to_format}: {str(e)}")
            raise
    
    def convert_to_stooq_format(self, data: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
        """
        Convert DataFrame to Stooq format.
        
        Args:
            data: DataFrame to convert
            ticker: Ticker symbol (if not provided, uses first ticker in data)
            
        Returns:
            DataFrame in Stooq format
        """
        try:
            result = data.copy()
            
            # Get ticker if not provided
            if ticker is None and 'ticker' in data.columns:
                ticker = data['ticker'].iloc[0] if not data.empty else 'UNKNOWN'
            elif ticker is None:
                ticker = 'UNKNOWN'
            
            # Handle timestamp conversion
            if 'timestamp' in result.columns:
                try:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], utc=True)
                    result['timestamp'] = result['timestamp'].dt.tz_localize(None)
                    result['<DATE>'] = result['timestamp'].dt.strftime('%Y%m%d')
                except:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], errors='coerce')
                    result['<DATE>'] = result['timestamp'].dt.strftime('%Y%m%d')
            
            # Map columns to Stooq format
            stooq_mapping = {
                'ticker': '<TICKER>',
                'open': '<OPEN>',
                'high': '<HIGH>',
                'low': '<LOW>',
                'close': '<CLOSE>',
                'vol': '<VOL>'
            }
            
            # Create Stooq format DataFrame
            stooq_data = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': result['<DATE>'] if '<DATE>' in result.columns else result['timestamp'].dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': result.get('open', result.get('Open', None)),
                '<HIGH>': result.get('high', result.get('High', None)),
                '<LOW>': result.get('low', result.get('Low', None)),
                '<CLOSE>': result.get('close', result.get('Close', None)),
                '<VOL>': result.get('vol', result.get('Volume', None))
            })
            
            # Clean numeric data
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                stooq_data[col] = pd.to_numeric(stooq_data[col], errors='coerce')
            
            # Remove rows with invalid data
            stooq_data = stooq_data.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            return stooq_data
            
        except Exception as e:
            self.logger.error(f"Error converting to Stooq format: {str(e)}")
            raise


