#!/usr/bin/env python3
"""
REDLINE Yahoo Finance Downloader
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
from .yahoo_date_handler import YahooDateHandler
from .yahoo_error_handler import YahooErrorHandler
from .yahoo_data_formatter import YahooDataFormatter

logger = logging.getLogger(__name__)

# Disable browser impersonation in yfinance (like tkinter version)
# This prevents "Impersonating chrome136 is not supported" errors
# Set environment variable BEFORE importing yfinance
os.environ['YF_NO_BROWSER_IMPERSONATION'] = '1'
os.environ['CURL_IMPERSONATE'] = ''  # Also disable curl_cffi impersonation

# Import yfinance
# Note: yfinance 0.2.66+ uses curl_cffi by default
# We disable browser impersonation to match tkinter behavior
try:
    import yfinance as yf
    
    # Monkey-patch yfinance to force no impersonation
    # Patch the session creation in yfinance.utils to use impersonate=None
    try:
        import yfinance.utils as yf_utils
        import curl_cffi.requests as curl_requests
        
        # Store original session creation
        _original_session = curl_requests.Session
        
        # Create a wrapper that forces impersonate=None
        class NoImpersonateSession(curl_requests.Session):
            def __init__(self, *args, **kwargs):
                # Force impersonate=None
                kwargs['impersonate'] = None
                super().__init__(*args, **kwargs)
        
        # Patch curl_requests.Session to use our no-impersonate version
        # Only if not already patched
        if not hasattr(curl_requests.Session, '_redline_patched'):
            curl_requests.Session = NoImpersonateSession
            curl_requests.Session._redline_patched = True
            logger.debug("Patched curl_cffi.Session to disable browser impersonation")
    except Exception as patch_error:
        # If patching fails, log but continue - env var should still work
        logger.warning(f"Could not patch yfinance session creation: {patch_error}")
    
except ImportError as e:
    logger.error(f"Failed to import yfinance: {e}")
    logger.error("Install with: pip install yfinance")
    raise

class YahooDownloader(BaseDownloader):
    """Yahoo Finance data downloader."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize Yahoo downloader."""
        super().__init__("Yahoo Finance", "https://finance.yahoo.com")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting - increased delay to avoid rate limiting
        # Yahoo Finance is very aggressive with rate limiting, so we use longer delays
        self.last_request_time = 0
        self.min_request_interval = 60.0  # 60 seconds (1 minute) between requests to avoid rate limiting
        self.rate_limit_backoff_multiplier = 2.0  # Double the delay after each rate limit
        self.max_request_interval = 600.0  # Maximum 10 minutes between requests
        self.initial_delay = 10.0  # Wait 10 seconds before first request
        # rate_limit_lock will be initialized by base class _rate_limit() method
        
        # Note: yfinance 0.2.66+ uses curl_cffi by default
        # Browser impersonation is disabled via YF_NO_BROWSER_IMPERSONATION=1 (set before import)
        # This matches the tkinter version behavior and prevents impersonation errors
        self.logger.debug("yfinance using curl_cffi without browser impersonation (YF_NO_BROWSER_IMPERSONATION=1)")
        
        # Initialize helper classes
        self.date_handler = YahooDateHandler()
        self.error_handler = YahooErrorHandler()
        self.data_formatter = YahooDataFormatter()
    
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
            # Apply rate limiting
            # Add initial delay if this is the first request
            if self.last_request_time == 0:
                self.logger.info(f"Initial delay of {self.initial_delay} seconds before first Yahoo Finance request")
                time.sleep(self.initial_delay)
            
            self._rate_limit()
            
            # Parse and validate dates using helper
            start_dt, end_dt, start_date, end_date = self.date_handler.parse_and_validate_dates(start_date, end_date)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Normalize to midnight
            
            # Download data using yfinance
            # yfinance 0.2.66+ uses curl_cffi by default (not requests)
            # We removed CURL_IMPERSONATE=0 to avoid curl error 43
            ticker_obj = yf.Ticker(ticker)
            
            try:
                # Download historical data
                # Note: yfinance's end parameter is exclusive, so we need to handle it carefully
                if start_dt and end_dt:
                    # If end date is today, use period-based approach to avoid future date issues
                    if end_dt.date() == today.date():
                        # End date is today - use period-based download to avoid future date issues
                        days_diff = (end_dt - start_dt).days
                        period = self.date_handler.calculate_period(days_diff)
                        
                        self.logger.debug(f"Using period-based download: {period} (date range: {days_diff} days)")
                        data = ticker_obj.history(period=period)
                        
                        # If period-based fails, try using yesterday as end date (safer for yfinance)
                        if data.empty:
                            self.logger.debug(f"Period-based download returned empty, trying with yesterday as end date")
                            yesterday = today - timedelta(days=1)
                            end_dt_yesterday = yesterday
                            end_dt_inclusive = end_dt_yesterday + timedelta(days=1)
                            if end_dt_inclusive > today:
                                end_dt_inclusive = today
                            try:
                                data = ticker_obj.history(start=start_dt, end=end_dt_inclusive)
                                self.logger.debug(f"Date range download with yesterday end date succeeded")
                            except Exception as fallback_error:
                                self.logger.debug(f"Fallback to yesterday end date also failed: {fallback_error}")
                        
                        # Filter to the requested date range using helper
                        data = self.date_handler.normalize_timezone(data, start_dt, end_dt)
                    else:
                        # End date is in the past - safe to add 1 day for inclusive end
                        end_dt_inclusive = self.date_handler.get_inclusive_end_date(end_dt, today)
                        data = ticker_obj.history(start=start_dt, end=end_dt_inclusive)
                elif start_dt:
                    data = ticker_obj.history(start=start_dt)
                else:
                    # Default to 1 year if no dates provided
                    data = ticker_obj.history(period="1y")
            except Exception as history_error:
                # Use error handler to detect and handle errors
                error_msg = str(history_error)
                error_type, is_rate_limit = self.error_handler.detect_error_type(history_error, error_msg)
                
                if is_rate_limit:
                    # Increase delay for next request with exponential backoff
                    self.min_request_interval = min(
                        self.min_request_interval * self.rate_limit_backoff_multiplier,
                        self.max_request_interval
                    )
                    self.logger.warning(
                        f"Rate limit detected for {ticker}. "
                        f"Increasing delay to {self.min_request_interval:.1f} seconds"
                    )
                    # Raise RateLimitError with retry information
                    raise self.error_handler.handle_rate_limit_error(ticker, self.min_request_interval)
                elif error_type in ('yfinance_error', 'curl_error'):
                    # yfinance/curl library error - raise with descriptive message
                    self.logger.error(f"{error_type} for {ticker}: {error_msg}")
                    helpful_msg = self.error_handler.create_error_message(error_type, error_msg, ticker)
                    raise Exception(helpful_msg)
                else:
                    # Re-raise other errors
                    raise
            
            # Normalize timezone-aware index to timezone-naive for consistency
            data = self.data_formatter.normalize_timezone_index(data)
            
            # Check if data is empty - this could indicate rate limiting or no data
            if data.empty:
                # Check if this might be due to rate limiting or invalid date range
                date_range_info = ""
                if start_dt and end_dt:
                    days_diff = (end_dt - start_dt).days
                    date_range_info = f" for date range {start_date} to {end_date} ({days_diff} days)"
                
                # Check if date range might be the issue
                if start_dt and end_dt:
                    if days_diff < 7:
                        self.logger.warning(
                            f"No data found for ticker {ticker}{date_range_info}. "
                            f"Date range is very short ({days_diff} days). "
                            f"Try a longer date range (e.g., 1 year)."
                        )
                    elif end_dt > today:
                        self.logger.warning(
                            f"No data found for ticker {ticker}{date_range_info}. "
                            f"End date is in the future. Try setting end date to today or earlier."
                        )
                    elif end_dt.date() == today.date():
                        # End date is today - likely rate limiting or API issue
                        self.logger.warning(
                            f"No data found for ticker {ticker}{date_range_info}. "
                            f"End date is today - this often indicates Yahoo Finance rate limiting. "
                            f"Suggestions: (1) Wait 5-10 minutes and retry, (2) Use end date of yesterday, "
                            f"(3) Try a shorter date range, or (4) Use Stooq data source instead."
                        )
                    else:
                        self.logger.warning(
                            f"No data found for ticker {ticker}{date_range_info}. "
                            f"This might be due to: (1) Rate limiting, (2) Ticker delisted/no data, "
                            f"or (3) Yahoo Finance API issues. Try a different date range or data source (e.g., Stooq)."
                        )
                else:
                    self.logger.warning(
                        f"No data found for ticker {ticker}. "
                        f"This might be due to rate limiting or the ticker having no data. "
                        f"Try a different date range or data source (e.g., Stooq)."
                    )
                return pd.DataFrame()
            
            # Standardize the data using formatter
            standardized_data = self.data_formatter.standardize_data(data, ticker)
            
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
            if self.error_handler.is_yfinance_related_error(error_msg):
                self.logger.error(f"yfinance/curl error for {ticker}: {error_msg}")
                raise  # Re-raise so route can handle it properly
            
            # For other errors, log and return empty DataFrame
            self.logger.error(f"Error downloading {ticker} from Yahoo Finance: {error_msg}")
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
                
            except RateLimitError as e:
                # Rate limit error - propagate to caller
                self.logger.warning(f"Rate limited while downloading {ticker}: {e.message}")
                failed_tickers.append(ticker)
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
                # If this is the first rate limit error, raise it to stop batch processing
                # Otherwise, continue with other tickers
                if len(failed_tickers) == 1:
                    raise
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
