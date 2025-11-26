#!/usr/bin/env python3
"""
Yahoo Finance Data Formatter
Handles standardization of Yahoo Finance data to REDLINE format.
"""

import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


class YahooDataFormatter:
    """Helper class for formatting Yahoo Finance data."""
    
    @staticmethod
    def standardize_data(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Yahoo Finance data to REDLINE format.
        
        Args:
            data: Raw DataFrame from Yahoo Finance
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame in Stooq format
        """
        try:
            # Create a copy to avoid modifying original
            df = data.copy()
            
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Handle timezone-aware timestamps
            try:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
                df['Date'] = df['Date'].dt.tz_localize(None)  # Remove timezone
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            except:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            
            # Map to Stooq format
            df['<TICKER>'] = ticker
            df['<TIME>'] = '000000'  # Default time for daily data
            df['<OPEN>'] = df['Open']
            df['<HIGH>'] = df['High']
            df['<LOW>'] = df['Low']
            df['<CLOSE>'] = df['Close']
            df['<VOL>'] = df['Volume']
            
            # Select Stooq columns in correct order
            stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            df_stooq = df[stooq_columns].copy()
            
            # Handle missing values
            df_stooq = df_stooq.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            # Ensure numeric columns are properly formatted
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
            
            # Remove rows with invalid numeric data
            df_stooq = df_stooq.dropna(subset=numeric_cols)
            
            return df_stooq
            
        except Exception as e:
            logger.error(f"Error standardizing Yahoo data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def normalize_timezone_index(data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize timezone-aware index to timezone-naive.
        
        Args:
            data: DataFrame with potentially timezone-aware index
            
        Returns:
            DataFrame with timezone-naive index
        """
        if not data.empty and hasattr(data.index, 'tz') and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data

