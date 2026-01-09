#!/usr/bin/env python3
"""
VarioSync Data Validator
Handles validation of financial data files and data integrity checks.
"""

import logging
import pandas as pd
from typing import List, Dict, Any
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
        # Pre-validation with if-else
        if not file_path:
            self.logger.error("File path is empty or None")
            return False

        if not isinstance(file_path, str):
            self.logger.error(f"File path must be a string, got {type(file_path)}")
            return False

        if not format:
            self.logger.error("Format is empty or None")
            return False

        if not isinstance(format, str):
            self.logger.error(f"Format must be a string, got {type(format)}")
            return False

        import os
        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return False

        if not os.path.isfile(file_path):
            self.logger.error(f"Path is not a file: {file_path}")
            return False

        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File is not readable: {file_path}")
            return False

        try:
            if format == 'txt':
                return self._validate_stooq_format(file_path)
            elif format in ['csv', 'json']:
                # First try to detect if it's Stooq format
                if self._is_stooq_format(file_path):
                    return self._validate_stooq_format(file_path)
                else:
                    return self._validate_standard_format(file_path, format)
            else:
                # For other formats like feather, assume valid
                return True

        except FileNotFoundError as e:
            self.logger.error(f"File not found during validation {file_path}: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied during validation {file_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during validation of {file_path}: {type(e).__name__}: {str(e)}")
            return False
    
    def _is_stooq_format(self, file_path: str) -> bool:
        """Detect if a file is in Stooq format by checking column names."""
        # Pre-validation with if-else
        if not file_path:
            self.logger.debug("File path is empty - not Stooq format")
            return False

        if not isinstance(file_path, str):
            self.logger.debug(f"File path must be a string, got {type(file_path)} - not Stooq format")
            return False

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=1)  # Read only header
                # Check if columns match Stooq format
                stooq_cols = set(STOOQ_COLUMNS)
                file_cols = set(df.columns)
                return len(stooq_cols.intersection(file_cols)) >= 3  # At least 3 Stooq columns
            return False
        except FileNotFoundError:
            self.logger.debug(f"File not found checking Stooq format: {file_path}")
            return False
        except pd.errors.EmptyDataError:
            self.logger.debug(f"Empty file checking Stooq format: {file_path}")
            return False
        except pd.errors.ParserError:
            self.logger.debug(f"Parse error checking Stooq format: {file_path}")
            return False
        except Exception:
            return False
    
    def _validate_stooq_format(self, file_path: str) -> bool:
        """Validate Stooq format files."""
        # Pre-validation with if-else
        if not file_path:
            self.logger.error("File path is empty or None")
            return False

        if not isinstance(file_path, str):
            self.logger.error(f"File path must be a string, got {type(file_path)}")
            return False

        import os
        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return False

        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File is not readable: {file_path}")
            return False

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

        except FileNotFoundError as e:
            self.logger.error(f"File not found validating Stooq format {file_path}: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied validating Stooq format {file_path}: {str(e)}")
            return False
        except UnicodeDecodeError as e:
            self.logger.error(f"Unicode decode error validating Stooq format {file_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error validating Stooq format: {type(e).__name__}: {str(e)}")
            return False
    
    def _validate_standard_format(self, file_path: str, format: str) -> bool:
        """Validate standard CSV/JSON format files."""
        # Pre-validation with if-else
        if not file_path:
            self.logger.error("File path is empty or None")
            return False

        if not isinstance(file_path, str):
            self.logger.error(f"File path must be a string, got {type(file_path)}")
            return False

        if not format:
            self.logger.error("Format is empty or None")
            return False

        if not isinstance(format, str):
            self.logger.error(f"Format must be a string, got {type(format)}")
            return False

        valid_formats = ['csv', 'json']
        if format not in valid_formats:
            self.logger.error(f"Invalid format: {format}. Must be one of {valid_formats}")
            return False

        import os
        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return False

        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File is not readable: {file_path}")
            return False

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

        except FileNotFoundError as e:
            self.logger.error(f"File not found validating standard format {file_path}: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied validating standard format {file_path}: {str(e)}")
            return False
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Empty file validating standard format {file_path}: {str(e)}")
            return False
        except pd.errors.ParserError as e:
            self.logger.error(f"Parse error validating standard format {file_path}: {str(e)}")
            return False
        except ValueError as e:
            self.logger.error(f"Value error validating standard format {file_path}: {str(e)}")
            return False
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
    
    def validate_required_columns(self, data: pd.DataFrame, columns: List[str] = None) -> bool:
        """
        Validate that all required columns are present in the data.
        
        Args:
            data: DataFrame to validate
            columns: List of required columns (uses REQUIRED_COLUMNS if None)
            
        Returns:
            True if all required columns are present
        """
        if columns is None:
            columns = REQUIRED_COLUMNS
        
        missing_cols = [col for col in columns if col not in data.columns]
        if missing_cols:
            self.logger.warning(f"Missing required columns: {', '.join(missing_cols)}")
            return False
        
        return True
    
    def validate_data_types(self, data: pd.DataFrame, schema: Dict[str, str] = None) -> bool:
        """
        Validate data types against expected schema.
        
        Args:
            data: DataFrame to validate
            schema: Dictionary mapping column names to expected types
            
        Returns:
            True if data types match expected schema
        """
        if schema is None:
            # Default schema for financial data
            schema = {
                'ticker': 'object',
                'timestamp': 'datetime64[ns]',
                'open': 'float64',
                'high': 'float64',
                'low': 'float64',
                'close': 'float64',
                'vol': 'int64'
            }
        
        issues = []
        for col, expected_type in schema.items():
            if col in data.columns:
                actual_type = str(data[col].dtype)
                if actual_type != expected_type:
                    issues.append(f"Column {col}: expected {expected_type}, got {actual_type}")
        
        if issues:
            self.logger.warning(f"Data type validation issues: {issues}")
            return False
        
        return True
    
    def validate_price_consistency(self, data: pd.DataFrame) -> List[str]:
        """
        Validate price data consistency (high >= low, etc.).
        
        Args:
            data: DataFrame with price columns
            
        Returns:
            List of consistency issues found
        """
        issues = []
        
        # Check high >= low
        if 'high' in data.columns and 'low' in data.columns:
            violations = (data['high'] < data['low']).sum()
            if violations > 0:
                issues.append(f"Found {violations} high < low price violations")
        
        # Check high >= open and high >= close
        if 'high' in data.columns:
            if 'open' in data.columns:
                violations = (data['high'] < data['open']).sum()
                if violations > 0:
                    issues.append(f"Found {violations} high < open price violations")
            
            if 'close' in data.columns:
                violations = (data['high'] < data['close']).sum()
                if violations > 0:
                    issues.append(f"Found {violations} high < close price violations")
        
        # Check low <= open and low <= close
        if 'low' in data.columns:
            if 'open' in data.columns:
                violations = (data['low'] > data['open']).sum()
                if violations > 0:
                    issues.append(f"Found {violations} low > open price violations")
            
            if 'close' in data.columns:
                violations = (data['low'] > data['close']).sum()
                if violations > 0:
                    issues.append(f"Found {violations} low > close price violations")
        
        return issues
    
    def comprehensive_validation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive validation of financial data.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Dictionary with validation results and issues
        """
        results = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'summary': {}
        }
        
        # Basic data validation
        if data.empty:
            results['is_valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Required columns validation
        if not self.validate_required_columns(data):
            results['is_valid'] = False
        
        # Data integrity validation
        integrity_issues = self.validate_data_integrity(data)
        results['issues'].extend(integrity_issues)
        
        # Price consistency validation
        price_issues = self.validate_price_consistency(data)
        results['issues'].extend(price_issues)
        
        # Data type validation
        if not self.validate_data_types(data):
            results['warnings'].append("Data type validation failed")
        
        # Update validity
        if results['issues']:
            results['is_valid'] = False
        
        # Create summary
        results['summary'] = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'total_issues': len(results['issues']),
            'total_warnings': len(results['warnings']),
            'columns': list(data.columns)
        }
        
        return results