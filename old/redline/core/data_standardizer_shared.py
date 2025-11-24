#!/usr/bin/env python3
"""
Data standardization utilities extracted from data_module_shared.py (shared module)
Handles standardization of Stooq format and other data formats.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataStandardizer:
    """Data standardization utilities."""
    
    SCHEMA = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
    
    @staticmethod
    def standardize_txt_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and formats for txt files (Stooq format)."""
        try:
            df = df.copy()
            required_cols = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
            df['timestamp'] = pd.to_datetime(
                df['<DATE>'].astype(str) + df['<TIME>'].astype(str).str.zfill(6),
                format='%Y%m%d%H%M%S',
                errors='coerce'
            )
            df['ticker'] = df['<TICKER>'] if '<TICKER>' in df.columns else None
            df['open'] = pd.to_numeric(df['<OPEN>'])
            df['high'] = pd.to_numeric(df['<HIGH>'])
            df['low'] = pd.to_numeric(df['<LOW>'])
            df['close'] = pd.to_numeric(df['<CLOSE>'])
            df['vol'] = pd.to_numeric(df['<VOL>'])
            df['openint'] = pd.to_numeric(df['<OPENINT>']) if '<OPENINT>' in df.columns else None
            df['format'] = 'txt'
            df = df[DataStandardizer.SCHEMA]
            df = df.dropna(subset=['timestamp', 'close'])
            if df.empty:
                raise ValueError("No valid data after cleaning")
            return df
        except Exception as e:
            logger.error(f"Error standardizing Stooq columns: {str(e)}")
            raise ValueError(f"Failed to standardize columns: {str(e)}")

