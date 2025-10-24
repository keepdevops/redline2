#!/usr/bin/env python3
"""
REDLINE Alpha Vantage Downloader
Downloads historical data from Alpha Vantage API.
"""

import logging
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class AlphaVantageDownloader(BaseDownloader):
    """Alpha Vantage data downloader."""
    
    def __init__(self, output_dir: str = "data", api_key: str = None):
        """Initialize Alpha Vantage downloader."""
        super().__init__("Alpha Vantage", "https://www.alphavantage.co")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Alpha Vantage configuration
        self.api_key = api_key or "demo"  # Use demo key if none provided
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 30
        
        # Rate limiting - Alpha Vantage allows 5 calls per minute for free
        self.last_request_time = 0
        self.min_request_interval = 12.0  # 12 seconds between requests (5 per minute)
        self.rate_limit_lock = None
        
        # Import threading for rate limiting
        import threading
        self.rate_limit_lock = threading.Lock()
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        with self.rate_limit_lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                self.logger.info(f"Alpha Vantage rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker from Alpha Vantage.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD) - Alpha Vantage returns all available data
            end_date: End date (YYYY-MM-DD) - Alpha Vantage returns all available data
            
        Returns:
            DataFrame with historical data
        """
        try:
            # Apply rate limiting
            self._rate_limit()
            
            # Alpha Vantage API parameters
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': 'full',  # Get all available data
                'apikey': self.api_key
            }
            
            self.logger.info(f"Downloading {ticker} from Alpha Vantage...")
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    self.logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                    return pd.DataFrame()
                
                if 'Note' in data:
                    self.logger.warning(f"Alpha Vantage API note: {data['Note']}")
                    return pd.DataFrame()
                
                # Extract time series data
                if 'Time Series (Daily)' in data:
                    time_series = data['Time Series (Daily)']
                    
                    # Convert to DataFrame
                    df = pd.DataFrame.from_dict(time_series, orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    
                    # Rename columns to standard format
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    
                    # Convert to numeric
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Filter by date range if provided
                    if start_date:
                        start_dt = pd.to_datetime(start_date)
                        df = df[df.index >= start_dt]
                    
                    if end_date:
                        end_dt = pd.to_datetime(end_date)
                        df = df[df.index <= end_dt]
                    
                    if df.empty:
                        self.logger.warning(f"No data found for {ticker} in specified date range")
                        return pd.DataFrame()
                    
                    # Standardize the data
                    standardized_data = self.standardize_alpha_vantage_data(df, ticker)
                    
                    self.logger.info(f"Downloaded {len(standardized_data)} records for {ticker}")
                    return standardized_data
                    
                else:
                    self.logger.error(f"No time series data found for {ticker}")
                    return pd.DataFrame()
                    
            else:
                self.logger.error(f"HTTP error {response.status_code} for {ticker}")
                return pd.DataFrame()
                
        except Exception as e:
            error_msg = str(e)
            if "API call frequency" in error_msg or "rate limit" in error_msg.lower():
                self.logger.warning(f"Rate limited for {ticker} from Alpha Vantage. Please wait before trying again.")
                # Increase delay for next request
                self.min_request_interval = min(self.min_request_interval * 1.5, 60.0)
            else:
                self.logger.error(f"Error downloading {ticker} from Alpha Vantage: {error_msg}")
            return pd.DataFrame()
    
    def standardize_alpha_vantage_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Alpha Vantage data format.
        
        Args:
            data: Raw DataFrame from Alpha Vantage
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame
        """
        try:
            df = data.copy()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return pd.DataFrame()
            
            # Clean numeric data
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['Close'])
            
            # Sort by date
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error standardizing Alpha Vantage data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get information about Alpha Vantage API usage."""
        return {
            'name': 'Alpha Vantage',
            'website': 'https://www.alphavantage.co',
            'free_tier': '5 calls per minute',
            'api_key_required': True,
            'api_key_url': 'https://www.alphavantage.co/support/#api-key',
            'rate_limit': '5 calls per minute',
            'data_coverage': 'US and international stocks',
            'historical_data': True,
            'real_time_data': False
        }
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers from Alpha Vantage.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting batch download of {len(tickers)} tickers from Alpha Vantage")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
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
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers from Alpha Vantage: {', '.join(failed_tickers)}")
        
        return results


