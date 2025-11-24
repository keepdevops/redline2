#!/usr/bin/env python3
"""
REDLINE Base Downloader
Base class for all data downloaders with common functionality.
"""

import logging
import pandas as pd
import requests
import time
import threading
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BaseDownloader(ABC):
    """Base class for all data downloaders."""
    
    def __init__(self, name: str, base_url: str = None):
        """Initialize base downloader."""
        self.name = name
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        self.rate_limit_delay = 1
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'REDLINE Data Downloader/1.0'
        })
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_data_points': 0,
            'last_request_time': None
        }
        
        # Rate limiting attributes (initialized by child classes if needed)
        # Child classes can set: last_request_time, min_request_interval, rate_limit_lock
        self.last_request_time = 0
        self.min_request_interval = None  # Will use rate_limit_delay if not set
        self.rate_limit_lock = None  # Will be created on first use if needed
    
    @abstractmethod
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download data for a single ticker.
        
        Args:
            ticker: Ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with ticker data
        """
        pass
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting download of {len(tickers)} tickers from {self.name}")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
                # Rate limiting
                self._apply_rate_limit()
                
                # Download data
                data = self.download_single_ticker(ticker, start_date, end_date)
                
                if not data.empty:
                    results[ticker] = data
                    self.stats['successful_requests'] += 1
                    self.stats['total_data_points'] += len(data)
                else:
                    failed_tickers.append(ticker)
                    self.stats['failed_requests'] += 1
                
                self.stats['total_requests'] += 1
                self.stats['last_request_time'] = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Failed to download {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
        
        if failed_tickers:
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers: {', '.join(failed_tickers)}")
        
        self.logger.info(f"Download complete: {len(results)} successful, {len(failed_tickers)} failed")
        return results
    
    def download_bulk_data(self, tickers: List[str], start_date: str = None, end_date: str = None, 
                          batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Download data in batches to manage memory and rate limits.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            batch_size: Number of tickers to process in each batch
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        all_results = {}
        
        # Process in batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} tickers)")
            
            batch_results = self.download_multiple_tickers(batch, start_date, end_date)
            all_results.update(batch_results)
            
            # Longer delay between batches
            if i + batch_size < len(tickers):
                time.sleep(self.rate_limit_delay * 2)
        
        return all_results
    
    def _rate_limit(self):
        """
        Enforce rate limiting between requests.
        Uses threading locks for thread safety and time.time() for precision.
        Child classes can override min_request_interval for custom rate limits.
        """
        # Initialize lock if not already created
        if self.rate_limit_lock is None:
            self.rate_limit_lock = threading.Lock()
        
        # Use min_request_interval if set by child class, otherwise use rate_limit_delay
        interval = self.min_request_interval if self.min_request_interval is not None else self.rate_limit_delay
        
        with self.rate_limit_lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < interval:
                sleep_time = interval - time_since_last_request
                self.logger.info(f"{self.name} rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def _apply_rate_limit(self):
        """
        Apply rate limiting between requests.
        Calls _rate_limit() for consistency. Maintains backward compatibility.
        """
        self._rate_limit()
    
    def _make_request(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response object
        """
        for attempt in range(self.max_retries):
            try:
                if headers:
                    response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                else:
                    response = self.session.get(url, params=params, timeout=self.timeout)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    def standardize_data(self, data: pd.DataFrame, ticker: str, source: str = None) -> pd.DataFrame:
        """
        Standardize data format to REDLINE schema.
        
        Args:
            data: Raw data DataFrame
            ticker: Ticker symbol
            source: Data source identifier
            
        Returns:
            Standardized DataFrame
        """
        try:
            # Create standardized DataFrame
            standardized = pd.DataFrame()
            
            # Map columns to standard format
            column_mapping = self._get_column_mapping()
            
            for std_col, source_cols in column_mapping.items():
                if isinstance(source_cols, list):
                    # Try multiple possible column names
                    for source_col in source_cols:
                        if source_col in data.columns:
                            standardized[std_col] = data[source_col]
                            break
                elif source_cols in data.columns:
                    standardized[std_col] = data[source_cols]
                else:
                    # Set default value
                    standardized[std_col] = None
            
            # Ensure ticker column
            standardized['ticker'] = ticker
            
            # Ensure timestamp column
            if 'timestamp' not in standardized.columns and 'date' in standardized.columns:
                standardized['timestamp'] = pd.to_datetime(standardized['date'])
            elif 'timestamp' not in standardized.columns:
                standardized['timestamp'] = pd.to_datetime(data.index) if hasattr(data.index, 'date') else None
            
            # Add source information
            if source:
                standardized['source'] = source
            
            # Clean and validate data
            standardized = self._clean_data(standardized)
            
            return standardized
            
        except Exception as e:
            self.logger.error(f"Error standardizing data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _get_column_mapping(self) -> Dict[str, Union[str, List[str]]]:
        """Get column mapping for data standardization."""
        return {
            'open': ['Open', 'open', 'OPEN'],
            'high': ['High', 'high', 'HIGH'],
            'low': ['Low', 'low', 'LOW'],
            'close': ['Close', 'close', 'CLOSE'],
            'vol': ['Volume', 'volume', 'VOL', 'Vol'],
            'openint': ['OpenInt', 'openint', 'OPENINT'],
            'date': ['Date', 'date', 'DATE']
        }
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data."""
        try:
            # Remove rows with missing critical data
            critical_cols = ['ticker', 'close']
            data = data.dropna(subset=[col for col in critical_cols if col in data.columns])
            
            # Convert numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'vol', 'openint']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # Remove rows with invalid numeric data
            data = data.dropna(subset=['close'])
            
            # Sort by timestamp
            if 'timestamp' in data.columns:
                data = data.sort_values('timestamp')
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            return data
    
    def save_data(self, data: Dict[str, pd.DataFrame], output_dir: str, format: str = 'csv'):
        """
        Save downloaded data to files.
        
        Args:
            data: Dictionary of ticker -> DataFrame
            output_dir: Output directory
            format: File format ('csv', 'parquet', 'json')
        """
        import os
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for ticker, df in data.items():
                if df.empty:
                    continue
                
                filename = f"{ticker}.{format}"
                filepath = os.path.join(output_dir, filename)
                
                if format == 'csv':
                    df.to_csv(filepath, index=False)
                elif format == 'parquet':
                    df.to_parquet(filepath, index=False)
                elif format == 'json':
                    df.to_json(filepath, orient='records', indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                self.logger.info(f"Saved {ticker} data to {filepath}")
            
            self.logger.info(f"Saved {len(data)} tickers to {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get download statistics."""
        stats = self.stats.copy()
        stats['success_rate'] = (
            stats['successful_requests'] / max(stats['total_requests'], 1) * 100
        )
        return stats
    
    def reset_statistics(self):
        """Reset download statistics."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_data_points': 0,
            'last_request_time': None
        }
    
    def close(self):
        """Close the downloader and clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.close()
