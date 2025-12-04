#!/usr/bin/env python3
"""
REDLINE Stooq Downloader
Downloads historical data from Stooq.com with multiple access methods.
"""

import logging
import pandas as pd
import requests
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class StooqDownloader(BaseDownloader):
    """Stooq.com data downloader with multiple access methods."""
    
    def __init__(self, output_dir: str = None):
        """Initialize Stooq downloader."""
        super().__init__("Stooq", "https://stooq.com")
        # Use REDLINE data directory if not specified
        if output_dir is None:
            import os
            # Check for data directory in common locations
            base_dir = os.getcwd()
            data_dir = os.path.join(base_dir, 'data')
            self.output_dir = os.path.join(data_dir, 'stooq')
        else:
            self.output_dir = output_dir
        
        # Ensure output directory exists
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Stooq-specific configuration
        self.timeout = 15  # Shorter timeout for Stooq
        self.max_retries = 2  # Fewer retries due to 2FA issues
        
        # Multiple endpoints to try
        self.endpoints = [
            "https://stooq.com/q/d/l/?s={ticker}&i=d",
            "https://stooq.com/q/d/l/?s={ticker}&i=w",
            "https://stooq.com/historical/{ticker}/",
            "https://stooq.com/db/h/?s={ticker}"
        ]
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker from Stooq.
        First checks local cache before attempting download.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD) - filters data after loading
            end_date: End date (YYYY-MM-DD) - filters data after loading

        Returns:
            DataFrame with historical data
        """
        try:
            # First, check if data already exists locally in the REDLINE data directory
            import os
            import glob

            # Look for existing files in multiple locations
            data_dir = os.path.join(os.getcwd(), 'data')
            possible_files = [
                os.path.join(data_dir, f'{ticker}_stooq_data.csv'),
                os.path.join(data_dir, f'{ticker}_stooq_data.txt'),
                os.path.join(self.output_dir, f'{ticker}.csv'),
                os.path.join(self.output_dir, f'{ticker}.txt'),
                os.path.join(self.output_dir, f'{ticker}_stooq.csv'),
            ]

            # Also search for any file containing the ticker
            search_patterns = [
                os.path.join(data_dir, f'*{ticker}*stooq*.csv'),
                os.path.join(data_dir, f'*{ticker}*stooq*.txt'),
                os.path.join(self.output_dir, f'*{ticker}*.csv'),
                os.path.join(self.output_dir, f'*{ticker}*.txt'),
            ]

            for pattern in search_patterns:
                possible_files.extend(glob.glob(pattern))

            # Try to load from existing files
            for filepath in possible_files:
                if os.path.exists(filepath):
                    try:
                        self.logger.info(f"Found existing Stooq data for {ticker} at {filepath}")
                        data = pd.read_csv(filepath)

                        # Check if it's valid Stooq format
                        if self._is_valid_stooq_data(data):
                            self.logger.info(f"Successfully loaded {ticker} from local cache: {filepath}")
                            # Filter by date if specified
                            if start_date or end_date:
                                data = self._filter_by_date_range(data, start_date, end_date)
                            return data
                        else:
                            self.logger.debug(f"File {filepath} is not in valid Stooq format, trying next")
                    except Exception as e:
                        self.logger.debug(f"Could not load {filepath}: {str(e)}")
                        continue

            self.logger.info(f"No local cache found for {ticker}, attempting download from Stooq")

            # No local data found, proceed with download
            # Try multiple endpoints
            for endpoint in self.endpoints:
                try:
                    url = endpoint.format(ticker=ticker)
                    self.logger.info(f"Trying Stooq endpoint: {url}")
                    
                    # Make request with Stooq-specific headers
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    response = self._make_request(url, headers=headers)
                    
                    # Check for bandwidth limit errors
                    if response.status_code == 200:
                        response_text_lower = response.text.lower()
                        if 'bandwidth' in response_text_lower and 'limit' in response_text_lower:
                            error_msg = "Stooq daily bandwidth limit exceeded. Please try again tomorrow or use manual download."
                            self.logger.error(error_msg)
                            print(f"\n⚠️  {error_msg}")
                            print("   You can manually download from: https://stooq.com/q/d/l/?s={ticker}")
                            print("   Files will auto-copy from your Downloads folder.\n")
                            return pd.DataFrame()
                    
                    if response.status_code == 200:
                        # Try to parse as CSV
                        try:
                            from io import StringIO
                            csv_data = StringIO(response.text)
                            data = pd.read_csv(csv_data)
                            
                            if not data.empty and self._is_valid_stooq_data(data):
                                standardized_data = self.standardize_stooq_data(data, ticker)
                                self.logger.info(f"Successfully downloaded {ticker} from Stooq")
                                return standardized_data
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to parse CSV from {url}: {str(e)}")
                            continue
                    elif response.status_code == 429:
                        # Rate limiting
                        error_msg = "Stooq rate limit exceeded. Please wait a few minutes before trying again."
                        self.logger.warning(error_msg)
                        print(f"\n⚠️  {error_msg}\n")
                        return pd.DataFrame()
                    
                except Exception as e:
                    self.logger.warning(f"Failed to access {url}: {str(e)}")
                    continue
            
            # If all direct methods fail, suggest manual download
            self._suggest_manual_download(ticker)
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error downloading {ticker} from Stooq: {str(e)}")
            return pd.DataFrame()
    
    def _is_valid_stooq_data(self, data: pd.DataFrame) -> bool:
        """Check if the downloaded data is valid Stooq format."""
        required_columns = ['<TICKER>', '<DATE>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        return all(col in data.columns for col in required_columns)

    def _filter_by_date_range(self, data: pd.DataFrame, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Filter DataFrame by date range.

        Args:
            data: DataFrame with <DATE> column
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Filtered DataFrame
        """
        try:
            if data.empty:
                return data

            df = data.copy()

            # Convert <DATE> column to datetime if it's not already
            if '<DATE>' in df.columns:
                df['<DATE>'] = pd.to_datetime(df['<DATE>'], format='%Y%m%d', errors='coerce')

                # Filter by date range
                if start_date:
                    start = pd.to_datetime(start_date)
                    df = df[df['<DATE>'] >= start]

                if end_date:
                    end = pd.to_datetime(end_date)
                    df = df[df['<DATE>'] <= end]

                # Convert back to original format (YYYYMMDD)
                df['<DATE>'] = df['<DATE>'].dt.strftime('%Y%m%d')

            return df

        except Exception as e:
            self.logger.error(f"Error filtering by date range: {str(e)}")
            return data
    
    def standardize_stooq_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Stooq data format.
        
        Args:
            data: Raw DataFrame from Stooq
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame
        """
        try:
            # Stooq data is already in the correct format
            # Just ensure it's clean and valid
            df = data.copy()
            
            # Validate required columns
            required_columns = ['<TICKER>', '<DATE>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return pd.DataFrame()
            
            # Ensure TIME column exists
            if '<TIME>' not in df.columns:
                df['<TIME>'] = '000000'
            
            # Clean numeric data
            numeric_columns = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            # Sort by date
            df = df.sort_values('<DATE>')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error standardizing Stooq data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _suggest_manual_download(self, ticker: str):
        """Suggest manual download when automated methods fail."""
        try:
            self.logger.info(f"Automated download failed for {ticker}. Opening Stooq website for manual download.")
            
            # Open Stooq historical page for the ticker
            stooq_url = f"https://stooq.com/q/d/l/?s={ticker}"
            
            # Try to open in browser
            try:
                webbrowser.open(stooq_url)
                self.logger.info(f"Opened browser to {stooq_url}")
            except Exception as e:
                self.logger.warning(f"Could not open browser: {str(e)}")
            
            # Print instructions
            instructions = f"""
Manual Download Instructions for {ticker}:

1. Go to: {stooq_url}
2. If prompted, complete 2FA authentication
3. Click "Download historical data" or similar button
4. Save the CSV file
5. Use the file with REDLINE's file loading functionality

Alternative URL: https://stooq.com/historical/{ticker}/
            """
            
            print(instructions)
            self.logger.info(instructions)
            
        except Exception as e:
            self.logger.error(f"Error suggesting manual download: {str(e)}")
    
    def open_stooq_website(self, ticker: str = None):
        """
        Open Stooq website for manual data access.
        
        Args:
            ticker: Optional ticker symbol to open specific page
        """
        try:
            if ticker:
                url = f"https://stooq.com/q/d/l/?s={ticker}"
            else:
                url = "https://stooq.com"
            
            webbrowser.open(url)
            self.logger.info(f"Opened Stooq website: {url}")
            
        except Exception as e:
            self.logger.error(f"Error opening Stooq website: {str(e)}")
    
    def get_stooq_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get information about ticker availability on Stooq.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with ticker information
        """
        try:
            info = {
                'ticker': ticker,
                'stooq_url': f"https://stooq.com/q/d/l/?s={ticker}",
                'historical_url': f"https://stooq.com/historical/{ticker}/",
                'available_endpoints': len(self.endpoints),
                'requires_2fa': True,
                'manual_download_recommended': True
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting Stooq info for {ticker}: {str(e)}")
            return {}
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers from Stooq.
        Note: Due to Stooq's 2FA requirements, this may not work reliably.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (not used for Stooq)
            end_date: End date (not used for Stooq)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.warning("Stooq download may fail due to 2FA requirements. Consider using manual download.")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
                # Longer delay for Stooq to avoid rate limiting
                if i > 0:
                    import time
                    time.sleep(2)  # 2 second delay between requests
                
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
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers from Stooq: {', '.join(failed_tickers)}")
            self.logger.info("Consider using manual download or alternative data sources like Yahoo Finance.")
        
        return results
