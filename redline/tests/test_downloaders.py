#!/usr/bin/env python3
"""
REDLINE Downloader Tests
Tests for data downloader functionality.
"""

import unittest
import pandas as pd
import tempfile
import os
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from redline.downloaders.base_downloader import BaseDownloader
from redline.downloaders.yahoo_downloader import YahooDownloader
from redline.downloaders.stooq_downloader import StooqDownloader
from redline.downloaders.multi_source import MultiSourceDownloader

class TestBaseDownloader(unittest.TestCase):
    """Test cases for BaseDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = BaseDownloader("Test Downloader", "https://test.com")
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test downloader initialization."""
        self.assertEqual(self.downloader.name, "Test Downloader")
        self.assertEqual(self.downloader.base_url, "https://test.com")
        self.assertEqual(self.downloader.timeout, 30)
        self.assertEqual(self.downloader.max_retries, 3)
    
    def test_standardize_data(self):
        """Test data standardization."""
        test_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [95.0, 96.0],
            'Close': [102.0, 103.0],
            'Volume': [1000, 1100]
        })
        
        standardized = self.downloader.standardize_data(test_data, 'TEST')
        
        # Check that standard columns are present
        expected_columns = ['ticker', 'open', 'high', 'low', 'close', 'vol']
        for col in expected_columns:
            self.assertIn(col, standardized.columns)
        
        self.assertEqual(standardized['ticker'].iloc[0], 'TEST')
    
    def test_get_statistics(self):
        """Test statistics tracking."""
        # Simulate some operations
        self.downloader.stats['total_requests'] = 10
        self.downloader.stats['successful_requests'] = 8
        self.downloader.stats['failed_requests'] = 2
        
        stats = self.downloader.get_statistics()
        
        self.assertEqual(stats['total_requests'], 10)
        self.assertEqual(stats['success_rate'], 80.0)

class TestYahooDownloader(unittest.TestCase):
    """Test cases for YahooDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = YahooDownloader()
    
    def test_initialization(self):
        """Test Yahoo downloader initialization."""
        self.assertEqual(self.downloader.name, "Yahoo Finance")
        self.assertEqual(self.downloader.base_url, "https://finance.yahoo.com")
    
    def test_standardize_yahoo_data(self):
        """Test Yahoo data standardization."""
        test_data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [95.0, 96.0],
            'Close': [102.0, 103.0],
            'Volume': [1000, 1100]
        })
        
        standardized = self.downloader.standardize_yahoo_data(test_data, 'AAPL')
        
        # Check Stooq format columns
        stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        for col in stooq_columns:
            self.assertIn(col, standardized.columns)
        
        self.assertEqual(standardized['<TICKER>'].iloc[0], 'AAPL')
    
    def test_get_supported_periods(self):
        """Test supported periods."""
        periods = self.downloader.get_supported_periods()
        self.assertIn('1y', periods)
        self.assertIn('max', periods)

class TestStooqDownloader(unittest.TestCase):
    """Test cases for StooqDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = StooqDownloader()
    
    def test_initialization(self):
        """Test Stooq downloader initialization."""
        self.assertEqual(self.downloader.name, "Stooq")
        self.assertEqual(self.downloader.base_url, "https://stooq.com")
        self.assertEqual(self.downloader.timeout, 15)  # Shorter timeout
    
    def test_is_valid_stooq_data(self):
        """Test Stooq data validation."""
        valid_data = pd.DataFrame({
            '<TICKER>': ['AAPL'],
            '<DATE>': ['20230101'],
            '<TIME>': ['000000'],
            '<OPEN>': [100.0],
            '<HIGH>': [105.0],
            '<LOW>': [95.0],
            '<CLOSE>': [102.0],
            '<VOL>': [1000]
        })
        
        self.assertTrue(self.downloader._is_valid_stooq_data(valid_data))
        
        invalid_data = pd.DataFrame({
            '<TICKER>': ['AAPL'],
            '<DATE>': ['20230101']
            # Missing required columns
        })
        
        self.assertFalse(self.downloader._is_valid_stooq_data(invalid_data))
    
    def test_standardize_stooq_data(self):
        """Test Stooq data standardization."""
        test_data = pd.DataFrame({
            '<TICKER>': ['AAPL', 'AAPL'],
            '<DATE>': ['20230101', '20230102'],
            '<OPEN>': [100.0, 101.0],
            '<HIGH>': [105.0, 106.0],
            '<LOW>': [95.0, 96.0],
            '<CLOSE>': [102.0, 103.0],
            '<VOL>': [1000, 1100]
        })
        
        standardized = self.downloader.standardize_stooq_data(test_data, 'AAPL')
        
        # Should have TIME column added
        self.assertIn('<TIME>', standardized.columns)
        self.assertEqual(standardized['<TIME>'].iloc[0], '000000')

class TestMultiSourceDownloader(unittest.TestCase):
    """Test cases for MultiSourceDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = MultiSourceDownloader()
    
    def test_initialization(self):
        """Test multi-source downloader initialization."""
        self.assertEqual(self.downloader.name, "Multi-Source")
        
        # Check that individual downloaders are initialized
        self.assertIn('yahoo', self.downloader.downloaders)
        self.assertIn('stooq', self.downloader.downloaders)
        
        # Check source priority
        self.assertEqual(self.downloader.source_priority[0], 'yahoo')
    
    def test_get_source_order(self):
        """Test source ordering."""
        # Test default order
        default_order = self.downloader._get_source_order()
        self.assertEqual(default_order[0], 'yahoo')
        
        # Test preferred source
        preferred_order = self.downloader._get_source_order('stooq')
        self.assertEqual(preferred_order[0], 'stooq')
    
    def test_get_source_statistics(self):
        """Test source statistics."""
        stats = self.downloader.get_source_statistics()
        
        self.assertIn('yahoo', stats)
        self.assertIn('stooq', stats)
        
        for source, source_stats in stats.items():
            self.assertIn('attempts', source_stats)
            self.assertIn('successes', source_stats)
            self.assertIn('failures', source_stats)
    
    def test_get_available_sources(self):
        """Test available sources."""
        sources = self.downloader.get_available_sources()
        
        self.assertIn('yahoo', sources)
        self.assertIn('stooq', sources)
    
    def test_recommend_source(self):
        """Test source recommendation."""
        recommended = self.downloader.recommend_source()
        self.assertIn(recommended, ['yahoo', 'stooq'])

class TestDownloaderIntegration(unittest.TestCase):
    """Integration tests for downloaders."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_multi_source_fallback(self):
        """Test multi-source fallback behavior."""
        downloader = MultiSourceDownloader(self.temp_dir)
        
        # Test with a ticker that should work with Yahoo
        results = downloader.download_multiple_tickers(['AAPL'])
        
        # Should have some results (depending on network availability)
        self.assertIsInstance(results, dict)
    
    def test_bulk_download_structure(self):
        """Test bulk download structure without actual downloads."""
        from redline.downloaders.bulk_downloader import BulkDownloader
        
        bulk_downloader = BulkDownloader(self.temp_dir)
        
        # Test that it has multi-source downloader
        self.assertIsNotNone(bulk_downloader.multi_source)
        
        # Test progress tracking
        progress = bulk_downloader.get_download_progress()
        self.assertIn('total_requests', progress)
        self.assertIn('success_rate', progress)

if __name__ == '__main__':
    unittest.main()
