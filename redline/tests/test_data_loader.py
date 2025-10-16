#!/usr/bin/env python3
"""
REDLINE Data Loader Tests
Tests for core data loading functionality.
"""

import unittest
import pandas as pd
import tempfile
import os
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from redline.core.data_loader import DataLoader
from redline.core.data_validator import DataValidator
from redline.core.data_cleaner import DataCleaner

class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DataLoader()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'ticker': ['AAPL', 'AAPL', 'MSFT', 'MSFT'],
            'timestamp': [
                datetime(2023, 1, 1),
                datetime(2023, 1, 2),
                datetime(2023, 1, 1),
                datetime(2023, 1, 2)
            ],
            'open': [100.0, 101.0, 200.0, 201.0],
            'high': [105.0, 106.0, 205.0, 206.0],
            'low': [95.0, 96.0, 195.0, 196.0],
            'close': [102.0, 103.0, 202.0, 203.0],
            'vol': [1000, 1100, 2000, 2100],
            'openint': [0, 0, 0, 0],
            'format': ['test', 'test', 'test', 'test']
        })
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_clean_and_select_columns(self):
        """Test column cleaning and selection."""
        cleaned_data = self.loader.clean_and_select_columns(self.sample_data)
        
        # Check that all schema columns are present
        expected_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
        for col in expected_columns:
            self.assertIn(col, cleaned_data.columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data['open']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned_data['timestamp']))
    
    def test_filter_data_by_date_range(self):
        """Test date range filtering."""
        start_date = '2023-01-01'
        end_date = '2023-01-01'
        
        filtered_data = self.loader.filter_data_by_date_range(
            self.sample_data, start_date, end_date
        )
        
        # Should have 2 records for 2023-01-01
        self.assertEqual(len(filtered_data), 2)
        self.assertTrue(all(filtered_data['ticker'].isin(['AAPL', 'MSFT'])))
    
    def test_get_data_stats(self):
        """Test data statistics calculation."""
        stats = self.loader.get_data_stats(self.sample_data)
        
        self.assertEqual(stats['total_records'], 4)
        self.assertEqual(stats['total_tickers'], 2)
        self.assertEqual(stats['avg_records_per_ticker'], 2)
    
    def test_convert_format(self):
        """Test format conversion."""
        # Test pandas to pandas (should return same)
        result = self.loader.convert_format(self.sample_data, 'pandas', 'pandas')
        pd.testing.assert_frame_equal(result, self.sample_data)

class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = DataValidator()
        
        self.valid_data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT'],
            'timestamp': [datetime.now(), datetime.now()],
            'close': [100.0, 200.0]
        })
        
        self.invalid_data = pd.DataFrame({
            'ticker': ['AAPL'],
            'close': [100.0]
            # Missing timestamp column
        })
    
    def test_validate_data_integrity(self):
        """Test data integrity validation."""
        # Test valid data
        issues = self.validator.validate_data_integrity(self.valid_data)
        self.assertEqual(len(issues), 0)
        
        # Test invalid data
        issues = self.validator.validate_data_integrity(self.invalid_data)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('Missing required columns' in issue for issue in issues))
    
    def test_validate_date_range(self):
        """Test date range validation."""
        # Test valid date range
        result = self.validator.validate_date_range(self.valid_data)
        self.assertTrue(result)
        
        # Test with future dates
        future_data = self.valid_data.copy()
        future_data['timestamp'] = pd.to_datetime('2030-01-01')
        result = self.validator.validate_date_range(future_data)
        self.assertFalse(result)

class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = DataCleaner()
        
        self.messy_data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT', None, 'GOOGL'],
            'timestamp': [datetime.now(), datetime.now(), datetime.now(), datetime.now()],
            'open': [100.0, 'invalid', 300.0, 400.0],
            'high': [105.0, 205.0, 305.0, 405.0],
            'low': [95.0, 195.0, 295.0, 395.0],
            'close': [102.0, 202.0, 302.0, 402.0],
            'vol': [1000, 2000, 3000, 4000]
        })
    
    def test_clean_numeric_column(self):
        """Test numeric column cleaning."""
        cleaned_series = self.cleaner._clean_numeric_column(self.messy_data['open'])
        
        # Check that invalid values are converted to NaN
        self.assertTrue(pd.isna(cleaned_series.iloc[1]))
        self.assertTrue(pd.notna(cleaned_series.iloc[0]))
    
    def test_handle_missing_values(self):
        """Test missing value handling."""
        # Test drop strategy
        cleaned_data = self.cleaner.handle_missing_values(self.messy_data, strategy='drop')
        
        # Should remove rows with missing ticker
        self.assertEqual(len(cleaned_data), 3)
        self.assertFalse(cleaned_data['ticker'].isnull().any())
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        duplicate_data = pd.concat([self.messy_data, self.messy_data.iloc[:2]])
        
        cleaned_data = self.cleaner.remove_duplicates(duplicate_data)
        
        # Should have original number of rows
        self.assertEqual(len(cleaned_data), len(self.messy_data))

if __name__ == '__main__':
    unittest.main()
