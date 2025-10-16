#!/usr/bin/env python3
"""
REDLINE Stooq Format Handler
Handles conversion to and from Stooq data format.
"""

import logging
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class StooqFormatHandler:
    """Handler for Stooq data format conversion."""
    
    def __init__(self):
        """Initialize Stooq format handler."""
        self.logger = logging.getLogger(__name__)
        
        # Stooq format column definitions
        self.stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        
        # Column mappings for different input formats
        self.column_mappings = {
            'yahoo': {
                'Open': '<OPEN>',
                'High': '<HIGH>',
                'Low': '<LOW>',
                'Close': '<CLOSE>',
                'Volume': '<VOL>'
            },
            'generic': {
                'open': '<OPEN>',
                'high': '<HIGH>',
                'low': '<LOW>',
                'close': '<CLOSE>',
                'vol': '<VOL>',
                'volume': '<VOL>'
            }
        }
    
    def convert_to_stooq_format(self, data: pd.DataFrame, ticker: str, source_format: str = 'generic') -> pd.DataFrame:
        """
        Convert DataFrame to Stooq format.
        
        Args:
            data: Input DataFrame
            ticker: Ticker symbol
            source_format: Source format ('yahoo', 'generic')
            
        Returns:
            DataFrame in Stooq format
        """
        try:
            # Create copy to avoid modifying original
            result = data.copy()
            
            # Handle timestamp conversion
            if 'timestamp' in result.columns:
                result = self._convert_timestamp_column(result)
            elif 'date' in result.columns:
                result = self._convert_date_column(result)
            elif 'Date' in result.columns:
                result = self._convert_date_column(result, 'Date')
            
            # Map columns based on source format
            if source_format in self.column_mappings:
                mapping = self.column_mappings[source_format]
                for source_col, stooq_col in mapping.items():
                    if source_col in result.columns:
                        result[stooq_col] = result[source_col]
            
            # Create Stooq format DataFrame
            stooq_data = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': result.get('<DATE>', self._generate_default_date(result)),
                '<TIME>': '000000',
                '<OPEN>': result.get('<OPEN>', None),
                '<HIGH>': result.get('<HIGH>', None),
                '<LOW>': result.get('<LOW>', None),
                '<CLOSE>': result.get('<CLOSE>', None),
                '<VOL>': result.get('<VOL>', None)
            })
            
            # Clean and validate data
            stooq_data = self._clean_stooq_data(stooq_data)
            
            return stooq_data
            
        except Exception as e:
            self.logger.error(f"Error converting to Stooq format: {str(e)}")
            return pd.DataFrame()
    
    def _convert_timestamp_column(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convert timestamp column to Stooq date format."""
        try:
            # Handle timezone-aware timestamps
            data['timestamp'] = pd.to_datetime(data['timestamp'], utc=True)
            data['timestamp'] = data['timestamp'].dt.tz_localize(None)
            data['<DATE>'] = data['timestamp'].dt.strftime('%Y%m%d')
            return data
        except:
            # Fallback for timezone issues
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
            data['<DATE>'] = data['timestamp'].dt.strftime('%Y%m%d')
            return data
    
    def _convert_date_column(self, data: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
        """Convert date column to Stooq date format."""
        try:
            data['timestamp'] = pd.to_datetime(data[date_col], errors='coerce')
            data['<DATE>'] = data['timestamp'].dt.strftime('%Y%m%d')
            return data
        except Exception as e:
            self.logger.error(f"Error converting date column {date_col}: {str(e)}")
            return data
    
    def _generate_default_date(self, data: pd.DataFrame) -> str:
        """Generate default date if no date column found."""
        try:
            if hasattr(data.index, 'date'):
                return data.index.date[0].strftime('%Y%m%d')
            else:
                return datetime.now().strftime('%Y%m%d')
        except:
            return datetime.now().strftime('%Y%m%d')
    
    def _clean_stooq_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate Stooq format data."""
        try:
            # Ensure numeric columns are properly formatted
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # Remove rows with invalid data
            data = data.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            # Validate OHLC relationships
            data = self._validate_ohlc_relationships(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error cleaning Stooq data: {str(e)}")
            return data
    
    def _validate_ohlc_relationships(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate OHLC price relationships."""
        try:
            # Check high >= low
            if '<HIGH>' in data.columns and '<LOW>' in data.columns:
                invalid_mask = data['<HIGH>'] < data['<LOW>']
                if invalid_mask.any():
                    self.logger.warning(f"Found {invalid_mask.sum()} rows with high < low")
                    data = data[~invalid_mask]
            
            # Check high >= open, close and low <= open, close
            if all(col in data.columns for col in ['<HIGH>', '<LOW>', '<OPEN>', '<CLOSE>']):
                invalid_high = (data['<HIGH>'] < data['<OPEN>']) | (data['<HIGH>'] < data['<CLOSE>'])
                invalid_low = (data['<LOW>'] > data['<OPEN>']) | (data['<LOW>'] > data['<CLOSE>'])
                
                if invalid_high.any() or invalid_low.any():
                    self.logger.warning(f"Found invalid OHLC relationships")
                    data = data[~(invalid_high | invalid_low)]
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error validating OHLC relationships: {str(e)}")
            return data
    
    def convert_from_stooq_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert from Stooq format to standard format.
        
        Args:
            data: DataFrame in Stooq format
            
        Returns:
            DataFrame in standard format
        """
        try:
            result = data.copy()
            
            # Map Stooq columns to standard columns
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
            
            # Rename columns
            for stooq_col, std_col in column_mapping.items():
                if stooq_col in result.columns:
                    result[std_col] = result[stooq_col]
            
            # Create timestamp from date and time
            if 'date_str' in result.columns:
                if 'time_str' in result.columns:
                    result['timestamp'] = pd.to_datetime(
                        result['date_str'] + ' ' + result['time_str'],
                        format='%Y%m%d %H%M%S',
                        errors='coerce'
                    )
                else:
                    result['timestamp'] = pd.to_datetime(
                        result['date_str'],
                        format='%Y%m%d',
                        errors='coerce'
                    )
            
            # Select standard columns
            standard_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol']
            final_columns = [col for col in standard_columns if col in result.columns]
            
            return result[final_columns]
            
        except Exception as e:
            self.logger.error(f"Error converting from Stooq format: {str(e)}")
            return pd.DataFrame()
    
    def validate_stooq_format(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate Stooq format data.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_columns': [],
            'data_quality_issues': []
        }
        
        try:
            # Check required columns
            missing_cols = [col for col in self.stooq_columns if col not in data.columns]
            if missing_cols:
                validation_results['missing_columns'] = missing_cols
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Missing required columns: {missing_cols}")
            
            # Check data types
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                if col in data.columns:
                    if not pd.api.types.is_numeric_dtype(data[col]):
                        validation_results['errors'].append(f"Column {col} should be numeric")
                        validation_results['is_valid'] = False
            
            # Check for missing values in critical columns
            critical_cols = ['<TICKER>', '<DATE>', '<CLOSE>']
            for col in critical_cols:
                if col in data.columns:
                    null_count = data[col].isnull().sum()
                    if null_count > 0:
                        validation_results['data_quality_issues'].append(f"{null_count} null values in {col}")
            
            # Check date format
            if '<DATE>' in data.columns:
                try:
                    pd.to_datetime(data['<DATE>'], format='%Y%m%d')
                except:
                    validation_results['errors'].append("Invalid date format in <DATE> column")
                    validation_results['is_valid'] = False
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating Stooq format: {str(e)}")
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
            return validation_results
    
    def get_stooq_columns(self) -> List[str]:
        """Get list of Stooq format columns."""
        return self.stooq_columns.copy()
    
    def get_supported_source_formats(self) -> List[str]:
        """Get list of supported source formats."""
        return list(self.column_mappings.keys())
