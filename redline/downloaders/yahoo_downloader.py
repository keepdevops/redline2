#!/usr/bin/env python3
"""
REDLINE Yahoo Finance Downloader
Downloads historical data from Yahoo Finance using yfinance library.
"""

import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class YahooDownloader(BaseDownloader):
    """Yahoo Finance data downloader."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize Yahoo downloader."""
        super().__init__("Yahoo Finance", "https://finance.yahoo.com")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with historical data
        """
        try:
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            # Download data using yfinance
            ticker_obj = yf.Ticker(ticker)
            
            if start_dt and end_dt:
                data = ticker_obj.history(start=start_dt, end=end_dt)
            elif start_dt:
                data = ticker_obj.history(start=start_dt)
            else:
                # Default to 1 year if no dates provided
                data = ticker_obj.history(period="1y")
            
            if data.empty:
                self.logger.warning(f"No data found for ticker {ticker}")
                return pd.DataFrame()
            
            # Standardize the data
            standardized_data = self.standardize_yahoo_data(data, ticker)
            
            self.logger.info(f"Downloaded {len(standardized_data)} records for {ticker}")
            return standardized_data
            
        except Exception as e:
            self.logger.error(f"Error downloading {ticker} from Yahoo Finance: {str(e)}")
            return pd.DataFrame()
    
    def standardize_yahoo_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Yahoo Finance data to REDLINE format.
        
        Args:
            data: Raw DataFrame from Yahoo Finance
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame
        """
        try:
            # Create a copy to avoid modifying original
            df = data.copy()
            
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Handle timezone-aware timestamps
            try:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
                df['Date'] = df['Date'].dt.tz_localize(None)  # Remove timezone
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            except:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            
            # Map to Stooq format
            df['<TICKER>'] = ticker
            df['<TIME>'] = '000000'  # Default time for daily data
            df['<OPEN>'] = df['Open']
            df['<HIGH>'] = df['High']
            df['<LOW>'] = df['Low']
            df['<CLOSE>'] = df['Close']
            df['<VOL>'] = df['Volume']
            
            # Select Stooq columns in correct order
            stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            df_stooq = df[stooq_columns].copy()
            
            # Handle missing values
            df_stooq = df_stooq.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
            
            # Ensure numeric columns are properly formatted
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
            
            # Remove rows with invalid numeric data
            df_stooq = df_stooq.dropna(subset=numeric_cols)
            
            return df_stooq
            
        except Exception as e:
            self.logger.error(f"Error standardizing Yahoo data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get additional information about a ticker.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with ticker information
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            return {
                'symbol': info.get('symbol', ticker),
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ticker info for {ticker}: {str(e)}")
            return {}
    
    def search_tickers(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Search for tickers by name or symbol.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of ticker dictionaries
        """
        try:
            # This is a simplified search - in practice, you might need to use
            # a different approach or API for ticker search
            ticker_obj = yf.Ticker(query)
            info = ticker_obj.info
            
            if info and 'symbol' in info:
                return [{
                    'symbol': info.get('symbol', query),
                    'name': info.get('longName', ''),
                    'exchange': info.get('exchange', '')
                }]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error searching tickers: {str(e)}")
            return []
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers with Yahoo-specific optimizations.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting Yahoo Finance download of {len(tickers)} tickers")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
                # Yahoo Finance has rate limits, so we add a small delay
                if i > 0:
                    import time
                    time.sleep(0.5)  # 500ms delay between requests
                
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
        
        self.logger.info(f"Yahoo Finance download complete: {len(results)} successful, {len(failed_tickers)} failed")
        return results
    
    def get_supported_periods(self) -> List[str]:
        """Get list of supported data periods."""
        return ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    def get_available_markets(self) -> List[str]:
        """Get list of available markets."""
        return ['US', 'CA', 'UK', 'DE', 'FR', 'IT', 'ES', 'NL', 'JP', 'AU', 'HK', 'SG']
