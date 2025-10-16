#!/usr/bin/env python3
"""
REDLINE Data Validator
Handles validation of financial data files and data integrity checks.
"""

import logging
import pandas as pd
from typing import List
from .schema import STOOQ_COLUMNS, REQUIRED_COLUMNS

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates financial data files and data integrity."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_data(self, file_path: str, format: str) -> bool:
        """
        Validate data file format and structure.
        
        Args:
            file_path: Path to the data file
            format: Expected format type
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            if format == 'txt':
                return self._validate_stooq_format(file_path)
            elif format in ['csv', 'json']:
                return self._validate_standard_format(file_path, format)
            else:
                # For other formats like feather, assume valid
                return True
                
        except Exception as e:
            self.logger.error(f"Validation failed for {file_path}: {str(e)}")
            return False
    
    def _validate_stooq_format(self, file_path: str) -> bool:
        """Validate Stooq format files."""
        try:
            with open(file_path, 'r') as f:
                header = f.readline().strip()
                
            # Check for Stooq format header
            header_cols = [col.strip() for col in header.split(',')]
            
            # Validate header columns
            missing_cols = [col for col in STOOQ_COLUMNS if col not in header_cols]
            if missing_cols:
                self.logger.warning(f"Missing required columns in {file_path}: {', '.join(missing_cols)}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating Stooq format: {str(e)}")
            return False
    
    def _validate_standard_format(self, file_path: str, format: str) -> bool:
        """Validate standard CSV/JSON format files."""
        try:
            if format == 'csv':
                df = pd.read_csv(file_path)
            elif format == 'json':
                df = pd.read_json(file_path)
            else:
                return False
                
            # Check for required columns
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                self.logger.warning(f"Missing required columns: {', '.join(missing_cols)}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating {format} format: {str(e)}")
            return False
    
    def validate_data_integrity(self, data: pd.DataFrame) -> List[str]:
        """
        Check data integrity and return list of issues.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check for empty DataFrame
        if data.empty:
            issues.append("DataFrame is empty")
            return issues
        
        # Check for required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Check for null values in critical columns
        if 'ticker' in data.columns:
            null_tickers = data['ticker'].isnull().sum()
            if null_tickers > 0:
                issues.append(f"Found {null_tickers} null ticker values")
        
        if 'close' in data.columns:
            null_closes = data['close'].isnull().sum()
            if null_closes > 0:
                issues.append(f"Found {null_closes} null close price values")
        
        # Check for negative prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in data.columns:
                negative_prices = (data[col] < 0).sum()
                if negative_prices > 0:
                    issues.append(f"Found {negative_prices} negative {col} prices")
        
        # Check for high > low violations
        if 'high' in data.columns and 'low' in data.columns:
            violations = (data['high'] < data['low']).sum()
            if violations > 0:
                issues.append(f"Found {violations} high < low price violations")
        
        # Check for volume issues
        if 'vol' in data.columns:
            negative_vol = (data['vol'] < 0).sum()
            if negative_vol > 0:
                issues.append(f"Found {negative_vol} negative volume values")
        
        return issues
    
    def validate_date_range(self, data: pd.DataFrame) -> bool:
        """
        Validate that data has reasonable date range.
        
        Args:
            data: DataFrame with timestamp column
            
        Returns:
            True if date range is valid
        """
        try:
            if 'timestamp' not in data.columns:
                return False
                
            # Convert to datetime if needed
            timestamps = pd.to_datetime(data['timestamp'], errors='coerce')
            
            # Check for invalid dates
            invalid_dates = timestamps.isnull().sum()
            if invalid_dates > 0:
                self.logger.warning(f"Found {invalid_dates} invalid dates")
                return False
            
            # Check date range (should be within reasonable bounds)
            min_date = timestamps.min()
            max_date = timestamps.max()
            
            # Data should not be from the future
            from datetime import datetime
            if max_date > datetime.now():
                self.logger.warning("Data contains future dates")
                return False
            
            # Data should not be too old (before 1900)
            from datetime import datetime
            if min_date < datetime(1900, 1, 1):
                self.logger.warning("Data contains very old dates (before 1900)")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating date range: {str(e)}")
            return False
