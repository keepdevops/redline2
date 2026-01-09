#!/usr/bin/env python3
"""
VarioSync Yahoo Finance Downloader
Downloads historical data from Yahoo Finance using yfinance library.
"""

import logging
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .base_downloader import BaseDownloader
from .exceptions import RateLimitError

# Import yfinance - it will use curl_cffi if available (required for Yahoo Finance API)
# Do not pass a session parameter to yf.Ticker() - let yfinance handle session creation internally
import yfinance as yf

logger = logging.getLogger(__name__)

class YahooDownloader(BaseDownloader):
    """Yahoo Finance data downloader."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize Yahoo downloader."""
        super().__init__("Yahoo Finance", "https://finance.yahoo.com")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting - optimized for batch downloads
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests (reduced from 15s for better throughput)
        # rate_limit_lock will be initialized by base class _rate_limit() method
        
        # Session management for batch downloads
        self._session = None
        
        # Browser impersonation is disabled at module level (before yfinance import)
        # CURL_IMPERSONATE=0 is set to prevent browser impersonation errors
        self.logger.debug("Browser impersonation disabled via CURL_IMPERSONATE=0 (set at module level)")
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None, use_session: bool = True) -> pd.DataFrame:
        """
        Download historical data for a single ticker.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_session: Whether to reuse session for batch downloads

        Returns:
            DataFrame with historical data
        """
        # Pre-validation with if-else
        if not ticker:
            self.logger.error("Ticker is empty or None")
            return pd.DataFrame()

        if not isinstance(ticker, str):
            self.logger.error(f"Ticker must be a string, got {type(ticker)}")
            return pd.DataFrame()

        ticker = ticker.strip().upper()

        if not ticker:
            self.logger.error("Ticker is empty after strip")
            return pd.DataFrame()

        # Validate dates if provided
        if start_date and not isinstance(start_date, str):
            self.logger.error(f"start_date must be a string, got {type(start_date)}")
            return pd.DataFrame()

        if end_date and not isinstance(end_date, str):
            self.logger.error(f"end_date must be a string, got {type(end_date)}")
            return pd.DataFrame()

        self.logger.debug(f"Downloading {ticker} from Yahoo Finance (start={start_date}, end={end_date})")

        try:
            # Apply rate limiting (only if not in batch mode)
            if use_session:
                # In batch mode, rate limiting is handled at batch level
                time.sleep(0.5)  # Small delay to avoid overwhelming Yahoo
            else:
                self._rate_limit()

            # Parse dates - Note: Date parsing requires try-except for invalid formats
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError as e:
                self.logger.error(f"Invalid date format for {ticker}: {str(e)}")
                return pd.DataFrame()
            
            # Download data using yfinance
            # For batch downloads, reuse session if available
            if use_session and self._session is None:
                # Create a session for batch downloads
                try:
                    import requests
                    self._session = requests.Session()
                    self._session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    self.logger.debug(f"Created requests session for batch downloads")
                except ImportError as e:
                    self.logger.debug(f"requests library not available: {str(e)}")
                    self._session = None
                except Exception as e:
                    self.logger.warning(f"Failed to create session for batch downloads: {str(e)}")
                    self._session = None
            
            ticker_obj = yf.Ticker(ticker)
            
            try:
                # Download historical data
                if start_dt and end_dt:
                    data = ticker_obj.history(start=start_dt, end=end_dt)
                elif start_dt:
                    data = ticker_obj.history(start=start_dt)
                else:
                    # Default to 1 year if no dates provided
                    data = ticker_obj.history(period="1y")
            except Exception as history_error:
                # Check if this is a rate limit error from yfinance
                error_msg = str(history_error)
                error_lower = error_msg.lower()
                
                # Detect rate limiting indicators
                is_rate_limit = (
                    "too many requests" in error_lower or
                    "rate limit" in error_lower or
                    "429" in error_msg or
                    "throttled" in error_lower or
                    "exceeded" in error_lower and "request" in error_lower
                )
                
                # Detect yfinance library errors (not "no data" errors)
                is_yfinance_error = (
                    "impersonating" in error_lower or
                    "user-agent" in error_lower or
                    "not supported" in error_lower or
                    "yfinance" in error_lower or
                    "curl_cffi" in error_lower or
                    "setopt" in error_lower
                )
                
                # Check for HTTPError with 429 status
                if hasattr(history_error, 'response'):
                    try:
                        if hasattr(history_error.response, 'status_code'):
                            if history_error.response.status_code == 429:
                                is_rate_limit = True
                    except (AttributeError, TypeError) as e:
                        logger.debug(f"Error checking response status code: {str(e)}")
                
                if is_rate_limit:
                    self.logger.warning(f"Rate limited for {ticker} from Yahoo Finance")
                    # Increase delay for next request
                    self.min_request_interval = min(self.min_request_interval * 1.5, 30.0)
                    # Raise RateLimitError with retry information
                    retry_after = int(self.min_request_interval * 12)  # Suggest waiting ~12x the interval
                    raise RateLimitError(
                        f'Rate limit exceeded for Yahoo Finance while downloading {ticker}',
                        retry_after=retry_after,
                        source='yahoo'
                    )
                elif is_yfinance_error:
                    # yfinance library error - raise with descriptive message
                    self.logger.error(f"yfinance library error for {ticker}: {error_msg}")
                    # Raise exception so route can return 503, not 404
                    raise Exception(f'yfinance library error: {error_msg}. This may be a temporary issue with Yahoo Finance. Please try again in a few moments or use a different data source (e.g., Stooq).')
                elif 'curl' in error_lower or 'setopt' in error_lower or 'curl_cffi' in error_lower:
                    # curl_cffi errors (like "Failed to setopt") - also yfinance issues
                    self.logger.error(f"curl_cffi error for {ticker}: {error_msg}")
                    raise Exception(f'Yahoo Finance connection error: {error_msg}. This may be a temporary issue. Please try again in a few moments or use a different data source (e.g., Stooq).')
                else:
                    # Re-raise other errors
                    raise
            
            # Check if data is empty - this could indicate rate limiting or no data
            if data.empty:
                # Check if this might be due to rate limiting
                # Yahoo Finance sometimes returns empty data when rate limited
                # We'll log a warning but return empty DataFrame (let route handler decide)
                self.logger.warning(f"No data found for ticker {ticker} - this might be due to rate limiting")
                return pd.DataFrame()
            
            # Standardize the data
            standardized_data = self.standardize_yahoo_data(data, ticker)
            
            self.logger.info(f"Downloaded {len(standardized_data)} records for {ticker}")
            return standardized_data
            
        except RateLimitError:
            # Re-raise RateLimitError to be handled by route
            raise
        except Exception as e:
            # Check if this is a yfinance/curl error that should be propagated
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            # If it's a yfinance/curl error, re-raise so route can return 503
            if ('yfinance' in error_lower or 'impersonating' in error_lower or 
                'curl' in error_lower or 'setopt' in error_lower or 'curl_cffi' in error_lower):
                self.logger.error(f"yfinance/curl error for {ticker}: {error_msg}")
                raise  # Re-raise so route can handle it properly
            
            # For other errors, log and return empty DataFrame
            self.logger.error(f"Error downloading {ticker} from Yahoo Finance: {error_msg}")
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
        # Pre-validation with if-else
        if data is None or not isinstance(data, pd.DataFrame):
            self.logger.error(f"Invalid data type for standardization: {type(data)}")
            return pd.DataFrame()

        if data.empty:
            self.logger.debug(f"Empty DataFrame for {ticker}, nothing to standardize")
            return pd.DataFrame()

        if not ticker or not isinstance(ticker, str):
            self.logger.error(f"Invalid ticker for standardization: {ticker}")
            return pd.DataFrame()

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
            except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime) as e:
                logger.debug(f"Failed to parse timezone-aware dates for {ticker}: {str(e)}, using fallback")
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
        
        # Initialize session for batch downloads
        try:
            import requests
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        except (ImportError, AttributeError, Exception) as e:
            logger.warning(f"Failed to initialize requests session: {str(e)}, continuing without session")
            self._session = None
        
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
                # Adaptive delay based on recent failures
                if i > 0:
                    if consecutive_failures > 0:
                        delay = min(2.0 + (consecutive_failures * 1.0), 10.0)  # Increase delay if failures
                        self.logger.info(f"Using adaptive delay of {delay}s due to recent failures")
                    else:
                        delay = 2.0  # Normal delay between requests
                    time.sleep(delay)
                
                # Download data with session reuse
                data = self.download_single_ticker(ticker, start_date, end_date, use_session=True)
                
                if not data.empty:
                    results[ticker] = data
                    self.stats['successful_requests'] += 1
                    self.stats['total_data_points'] += len(data)
                    consecutive_failures = 0  # Reset failure counter on success
                else:
                    failed_tickers.append(ticker)
                    self.stats['failed_requests'] += 1
                    consecutive_failures += 1
                    
                    # If too many consecutive failures, increase delay and log warning
                    if consecutive_failures >= max_consecutive_failures:
                        self.logger.warning(f"Multiple consecutive failures ({consecutive_failures}). This may indicate rate limiting.")
                        time.sleep(5.0)  # Extra delay before continuing
                
                self.stats['total_requests'] += 1
                self.stats['last_request_time'] = datetime.now()
                
            except RateLimitError as e:
                # Rate limit error - log and continue with increased delay
                self.logger.warning(f"Rate limited while downloading {ticker}: {e.message}")
                failed_tickers.append(ticker)
                consecutive_failures += 1
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
                
                # Wait longer before next request
                if i < len(tickers) - 1:  # Don't wait after last ticker
                    retry_delay = e.retry_after if hasattr(e, 'retry_after') and e.retry_after else 30
                    self.logger.info(f"Waiting {retry_delay}s before next request due to rate limit...")
                    time.sleep(min(retry_delay, 60))  # Cap at 60 seconds
                
                # Only raise if this is the first rate limit and we have many tickers remaining
                if len(failed_tickers) == 1 and len(tickers) > 5:
                    # For large batches, continue but with longer delays
                    self.logger.warning("Rate limit encountered. Continuing with increased delays...")
                elif len(failed_tickers) <= 3:
                    # For small batches or first few failures, continue
                    continue
                else:
                    # Too many rate limit errors, stop batch
                    raise
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Failed to download {ticker}: {error_msg}")
                failed_tickers.append(ticker)
                consecutive_failures += 1
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
                
                # Check if it's a yfinance/curl error that might be temporary
                if any(keyword in error_msg.lower() for keyword in ['yfinance', 'curl', 'impersonating', 'setopt']):
                    self.logger.warning(f"yfinance/curl error for {ticker}. Waiting before continuing...")
                    time.sleep(3.0)  # Wait before continuing
        
        # Clean up session
        if self._session:
            try:
                self._session.close()
            except (AttributeError, Exception) as e:
                logger.debug(f"Error closing session: {str(e)}")
            self._session = None
        
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
