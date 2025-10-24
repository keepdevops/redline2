#!/usr/bin/env python3
"""
REDLINE Finnhub Downloader
Downloads historical data from Finnhub API.
"""

import logging
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class FinnhubDownloader(BaseDownloader):
    """Finnhub data downloader."""
    
    def __init__(self, output_dir: str = "data", api_key: str = None):
        """Initialize Finnhub downloader."""
        super().__init__("Finnhub", "https://finnhub.io")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Finnhub configuration
        self.api_key = api_key or os.environ.get('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("Finnhub API key is required. Set FINNHUB_API_KEY environment variable or pass api_key parameter.")
        self.base_url = "https://finnhub.io/api/v1"
        self.timeout = 30
        
        # Rate limiting - Finnhub allows 60 calls per minute for free
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
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
                self.logger.info(f"Finnhub rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker from Finnhub.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with historical data
        """
        try:
            # Apply rate limiting
            self._rate_limit()
            
            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp()) if start_date else None
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) if end_date else None
            
            # Finnhub API parameters
            params = {
                'symbol': ticker,
                'resolution': 'D',  # Daily resolution
                'token': self.api_key
            }
            
            if start_timestamp:
                params['from'] = start_timestamp
            if end_timestamp:
                params['to'] = end_timestamp
            
            self.logger.info(f"Downloading {ticker} from Finnhub...")
            
            # Make API request
            url = f"{self.base_url}/stock/candle"
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if data.get('s') == 'no_data':
                    self.logger.warning(f"No data available for {ticker}")
                    return pd.DataFrame()
                
                if 'error' in data:
                    self.logger.error(f"Finnhub API error: {data['error']}")
                    return pd.DataFrame()
                
                # Extract candle data
                if 'c' in data and len(data['c']) > 0:
                    # Create DataFrame from candle data
                    df = pd.DataFrame({
                        'Open': data['o'],
                        'High': data['h'],
                        'Low': data['l'],
                        'Close': data['c'],
                        'Volume': data['v']
                    })
                    
                    # Convert timestamps to dates
                    df.index = pd.to_datetime(data['t'], unit='s')
                    df = df.sort_index()
                    
                    # Convert to numeric
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    if df.empty:
                        self.logger.warning(f"No data found for {ticker}")
                        return pd.DataFrame()
                    
                    # Standardize the data
                    standardized_data = self.standardize_finnhub_data(df, ticker)
                    
                    self.logger.info(f"Downloaded {len(standardized_data)} records for {ticker}")
                    return standardized_data
                    
                else:
                    self.logger.error(f"No candle data found for {ticker}")
                    return pd.DataFrame()
                    
            else:
                self.logger.error(f"HTTP error {response.status_code} for {ticker}")
                return pd.DataFrame()
                
        except Exception as e:
            error_msg = str(e)
            if "API call frequency" in error_msg or "rate limit" in error_msg.lower():
                self.logger.warning(f"Rate limited for {ticker} from Finnhub. Please wait before trying again.")
                # Increase delay for next request
                self.min_request_interval = min(self.min_request_interval * 1.5, 10.0)
            else:
                self.logger.error(f"Error downloading {ticker} from Finnhub: {error_msg}")
            return pd.DataFrame()
    
    def standardize_finnhub_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Finnhub data format.
        
        Args:
            data: Raw DataFrame from Finnhub
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
            self.logger.error(f"Error standardizing Finnhub data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get information about Finnhub API usage."""
        return {
            'name': 'Finnhub',
            'website': 'https://finnhub.io',
            'free_tier': '60 calls per minute',
            'api_key_required': True,
            'api_key_url': 'https://finnhub.io/register',
            'rate_limit': '60 calls per minute',
            'data_coverage': 'Global stocks, forex, crypto',
            'historical_data': True,
            'real_time_data': True
        }
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers from Finnhub.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting batch download of {len(tickers)} tickers from Finnhub")
        
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
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers from Finnhub: {', '.join(failed_tickers)}")
        
        return results


