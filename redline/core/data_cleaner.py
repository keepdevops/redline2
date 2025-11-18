#!/usr/bin/env python3
"""
REDLINE Data Cleaner
Handles data cleaning, standardization, and preprocessing operations.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any
from .schema import SCHEMA, NUMERIC_COLUMNS

logger = logging.getLogger(__name__)

class DataCleaner:
    """Handles data cleaning and standardization operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_and_select_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize DataFrame columns to match REDLINE schema.
        
        Args:
            data: Raw DataFrame to clean
            
        Returns:
            Cleaned DataFrame with standardized columns
        """
        try:
            # Make a copy to avoid modifying original
            data = data.copy()
            
            # Ensure all schema columns are present
            for col in SCHEMA:
                if col not in data.columns:
                    data[col] = None
            
            # Select only schema columns in correct order
            data = data[SCHEMA]
            
            # Clean numeric columns and handle type conversion safely
            for col in NUMERIC_COLUMNS:
                if col in data.columns:
                    data[col] = self._clean_numeric_column(data[col])
            
            # Ensure timestamp is datetime
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
                
            return data
            
        except Exception as e:
            self.logger.error(f"Error in clean_and_select_columns: {str(e)}")
            raise
    
    def _clean_numeric_column(self, series: pd.Series) -> pd.Series:
        """Clean a numeric column by converting types and handling errors."""
        try:
            # Convert to numeric, coerce errors to NaN
            cleaned = pd.to_numeric(series, errors='coerce')
            
            # Clean any remaining non-numeric values
            cleaned = cleaned.apply(
                lambda x: float(x) if pd.notnull(x) and not isinstance(x, (list, tuple, dict)) else None
            )
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error cleaning numeric column: {str(e)}")
            return series
    
    def standardize_txt_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize columns from Stooq TXT format to REDLINE schema.
        
        Args:
            df: DataFrame with Stooq format columns
            
        Returns:
            DataFrame with standardized columns
        """
        try:
            # Create a copy to avoid modifying original
            result = df.copy()
            
            # Map Stooq columns to REDLINE schema
            column_mapping = {
                '<TICKER>': 'ticker',
                '<DATE>': 'date_str',
                '<TIME>': 'time_str',
                '<OPEN>': 'open',
                '<HIGH>': 'high',
                '<LOW>': 'low',
                '<CLOSE>': 'close',
                '<VOL>': 'vol'
            }
            
            # Rename columns if they exist
            for stooq_col, redline_col in column_mapping.items():
                if stooq_col in result.columns:
                    result[redline_col] = result[stooq_col]
            
            # Combine date and time into timestamp
            if 'date_str' in result.columns and 'time_str' in result.columns:
                result['timestamp'] = pd.to_datetime(
                    result['date_str'] + ' ' + result['time_str'], 
                    format='%Y%m%d %H%M%S', 
                    errors='coerce'
                )
            elif 'date_str' in result.columns:
                result['timestamp'] = pd.to_datetime(
                    result['date_str'], 
                    format='%Y%m%d', 
                    errors='coerce'
                )
            
            # Clean numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'vol']
            for col in numeric_cols:
                if col in result.columns:
                    result[col] = self._clean_numeric_column(result[col])
            
            # Add missing columns
            result['openint'] = None
            result['format'] = 'stooq_txt'
            
            # Select and reorder columns to match schema
            final_columns = []
            for col in SCHEMA:
                if col in result.columns:
                    final_columns.append(col)
                else:
                    final_columns.append(col)
                    result[col] = None
            
            result = result[SCHEMA]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error standardizing TXT columns: {str(e)}")
            raise
    
    def balance_ticker_data(self, data: pd.DataFrame, target_records_per_ticker: int = None) -> pd.DataFrame:
        """
        Balance data by ensuring each ticker has approximately the same number of records.
        
        Args:
            data: DataFrame with ticker column
            target_records_per_ticker: Target number of records per ticker
            
        Returns:
            Balanced DataFrame
        """
        try:
            if 'ticker' not in data.columns:
                self.logger.warning("No ticker column found, returning original data")
                return data
            
            # Calculate records per ticker
            ticker_counts = data['ticker'].value_counts()
            
            if target_records_per_ticker is None:
                # Use median as target
                target_records_per_ticker = int(ticker_counts.median())
            
            self.logger.info(f"Balancing data to {target_records_per_ticker} records per ticker")
            
            balanced_data = []
            
            for ticker in ticker_counts.index:
                ticker_data = data[data['ticker'] == ticker]
                
                if len(ticker_data) > target_records_per_ticker:
                    # Sample down to target
                    balanced_data.append(
                        ticker_data.sample(n=target_records_per_ticker, random_state=42)
                    )
                else:
                    # Keep all data if less than target
                    balanced_data.append(ticker_data)
            
            if balanced_data:
                result = pd.concat(balanced_data, ignore_index=True)
                
                # Log statistics
                original_stats = {
                    'total_records': len(data),
                    'total_tickers': len(ticker_counts),
                    'avg_records_per_ticker': len(data) // len(ticker_counts)
                }
                
                balanced_stats = {
                    'total_records': len(result),
                    'total_tickers': len(result['ticker'].unique()),
                    'avg_records_per_ticker': len(result) // len(result['ticker'].unique())
                }
                
                self.logger.info(f"Original data: {original_stats['total_records']} records across {original_stats['total_tickers']} tickers")
                self.logger.info(f"Balanced data: {balanced_stats['total_records']} records across {balanced_stats['total_tickers']} tickers")
                
                return result
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"Error balancing ticker data: {str(e)}")
            raise
    
    def remove_duplicates(self, data: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        """
        Remove duplicate records from data.
        
        Args:
            data: DataFrame to deduplicate
            subset: Columns to consider for duplicate detection
            
        Returns:
            DataFrame with duplicates removed
        """
        try:
            if subset is None:
                subset = ['ticker', 'timestamp'] if 'ticker' in data.columns and 'timestamp' in data.columns else None
            
            original_count = len(data)
            result = data.drop_duplicates(subset=subset)
            removed_count = original_count - len(result)
            
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} duplicate records")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}")
            return data
    
    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            data: DataFrame with potential missing values
            strategy: Strategy to handle missing values ('drop', 'forward_fill', 'backward_fill')
            
        Returns:
            DataFrame with missing values handled
        """
        try:
            original_count = len(data)
            
            if strategy == 'drop':
                result = data.dropna(subset=['ticker', 'timestamp', 'close'])
            elif strategy == 'forward_fill':
                result = data.ffill()
            elif strategy == 'backward_fill':
                result = data.bfill()
            else:
                self.logger.warning(f"Unknown strategy '{strategy}', returning original data")
                return data
            
            removed_count = original_count - len(result)
            if removed_count > 0:
                self.logger.info(f"Handled {removed_count} missing value records using {strategy} strategy")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling missing values: {str(e)}")
            return data
