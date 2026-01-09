#!/usr/bin/env python3
"""
REDLINE Massive.com Downloader
Uses Massive.com Python client library or REST API for data access.
"""

import logging
import pandas as pd
import requests
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

# Try to import Massive.com client library
try:
    from massive import Client
    MASSIVE_AVAILABLE = True
except ImportError:
    MASSIVE_AVAILABLE = False
    Client = None
    logger.warning("Massive.com client library not available. Install with: pip install massive-client")

class MassiveDownloader(BaseDownloader):
    """Massive.com data downloader using official Python client or REST API."""
    
    def __init__(self, api_key: str, output_dir: str = "data", use_client_library: bool = True):
        """Initialize Massive.com downloader."""
        super().__init__("Massive.com", "https://api.massive.com")
        self.output_dir = output_dir

        # Pre-validation with if-else
        if not api_key:
            logger.error("Massive.com API key is required but not provided")
            raise ValueError("Massive.com API key is required")

        if not isinstance(api_key, str):
            logger.error(f"Massive.com API key must be a string, got {type(api_key)}")
            raise TypeError(f"Massive.com API key must be a string, got {type(api_key)}")

        self.api_key = api_key
        self.use_client_library = use_client_library and MASSIVE_AVAILABLE
        
        # Initialize client if library available
        if self.use_client_library:
            try:
                self.client = Client(api_key=api_key)
                logger.info("Using Massive.com Python client library")
            except Exception as e:
                logger.warning(f"Failed to initialize Massive.com client: {e}. Falling back to REST API.")
                self.use_client_library = False
        
        # REST API configuration
        self.api_base_url = "https://api.massive.com/v1"
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # Rate limiting: Free=5/min, Paid=<100/sec, Default=10/min
        self.rate_limit_delay = 6.0  # 10 requests/minute (conservative default)
        
    def download_single_ticker(self, ticker: str, start_date: str = None,
                              end_date: str = None) -> pd.DataFrame:
        """Download historical data for a single ticker."""
        # Pre-validation with if-else
        if not ticker:
            logger.error("Ticker is empty or None")
            return pd.DataFrame()

        if not isinstance(ticker, str):
            logger.error(f"Ticker must be a string, got {type(ticker)}")
            return pd.DataFrame()

        ticker = ticker.strip().upper()

        if not ticker:
            logger.error("Ticker is empty after strip")
            return pd.DataFrame()

        try:
            self._apply_rate_limit()
            if self.use_client_library:
                return self._download_with_client(ticker, start_date, end_date)
            else:
                return self._download_with_rest_api(ticker, start_date, end_date, 'aggregates')
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout downloading {ticker} from Massive.com: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error downloading {ticker} from Massive.com: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error downloading {ticker} from Massive.com: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error downloading {ticker} from Massive.com: {str(e)}")
            return pd.DataFrame()
    
    def _download_with_client(self, ticker: str, start_date: str = None,
                              end_date: str = None) -> pd.DataFrame:
        """Download using official Python client library."""
        # Convert dates - Note: Date parsing requires try-except
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        except ValueError as e:
            logger.error(f"Invalid date format for {ticker}: {str(e)}")
            return pd.DataFrame()

        try:
            response = self.client.stocks.aggregates(
                ticker=ticker, start_date=start_dt, end_date=end_dt
            )

            if not response or 'data' not in response:
                logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()

            df = pd.DataFrame(response['data'])
            df = self._standardize_columns(df, ticker)
            return self.standardize_data(df, ticker, 'massive')
        except AttributeError as e:
            logger.error(f"Client library error for {ticker}: {str(e)}")
            return self._download_with_rest_api(ticker, start_date, end_date, 'aggregates')
        except KeyError as e:
            logger.error(f"Missing expected data in response for {ticker}: {str(e)}")
            return self._download_with_rest_api(ticker, start_date, end_date, 'aggregates')
        except Exception as e:
            logger.error(f"Unexpected error with client library for {ticker}: {str(e)}")
            return self._download_with_rest_api(ticker, start_date, end_date, 'aggregates')
    
    def _download_with_rest_api(self, ticker: str, start_date: str = None,
                               end_date: str = None, endpoint: str = 'aggregates') -> pd.DataFrame:
        """Download using REST API directly."""
        # Pre-validation with if-else
        if not endpoint:
            logger.error("Endpoint is empty")
            return pd.DataFrame()

        try:
            url = f"{self.api_base_url}/stocks/{endpoint}"
            params = {"ticker": ticker}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = self._make_request(url, params=params)

            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                logger.warning("Rate limit exceeded, backing off for 60 seconds")
                import time
                time.sleep(60)
                # Retry once
                response = self._make_request(url, params=params)

            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code} for {ticker}")
                return pd.DataFrame()

            data = response.json()
            if not data or 'data' not in data:
                logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()

            df = pd.DataFrame(data['data'])
            if endpoint == 'aggregates':
                df = self._standardize_columns(df, ticker)
                return self.standardize_data(df, ticker, 'massive')
            return df
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout with REST API for {ticker}: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error with REST API for {ticker}: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error with REST API for {ticker}: {str(e)}")
            return pd.DataFrame()
        except KeyError as e:
            logger.error(f"Missing expected data in REST API response for {ticker}: {str(e)}")
            return pd.DataFrame()
        except ValueError as e:
            logger.error(f"JSON decode error with REST API for {ticker}: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error with REST API for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def download_trades(self, ticker: str, start_date: str = None, 
                       end_date: str = None) -> pd.DataFrame:
        """Download trade-level data."""
        return self._download_data_type(ticker, start_date, end_date, 'trades')
    
    def download_quotes(self, ticker: str, start_date: str = None, 
                        end_date: str = None) -> pd.DataFrame:
        """Download quote-level data."""
        return self._download_data_type(ticker, start_date, end_date, 'quotes')
    
    def download_fundamentals(self, ticker: str) -> pd.DataFrame:
        """Download fundamental data."""
        # Pre-validation with if-else
        if not ticker:
            logger.error("Ticker is empty or None")
            return pd.DataFrame()

        if not isinstance(ticker, str):
            logger.error(f"Ticker must be a string, got {type(ticker)}")
            return pd.DataFrame()

        try:
            self._apply_rate_limit()
            url = f"{self.api_base_url}/stocks/fundamentals"
            response = self._make_request(url, params={"ticker": ticker})

            if response.status_code != 200 or not response.json():
                logger.warning(f"No fundamentals data returned for {ticker}")
                return pd.DataFrame()

            return pd.DataFrame([response.json()])
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
        except ValueError as e:
            logger.error(f"JSON decode error downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _download_data_type(self, ticker: str, start_date: str = None,
                            end_date: str = None, data_type: str = 'trades') -> pd.DataFrame:
        """Generic method for downloading trades/quotes."""
        # Pre-validation with if-else
        if not ticker:
            logger.error("Ticker is empty or None")
            return pd.DataFrame()

        if not isinstance(ticker, str):
            logger.error(f"Ticker must be a string, got {type(ticker)}")
            return pd.DataFrame()

        if not data_type:
            logger.error("Data type is empty")
            return pd.DataFrame()

        try:
            self._apply_rate_limit()
            return self._download_with_rest_api(ticker, start_date, end_date, data_type)
        except Exception as e:
            logger.error(f"Unexpected error downloading {data_type} for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _standardize_columns(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Standardize column names to REDLINE format."""
        column_mapping = {
            'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume',
            't': 'date', 'timestamp': 'date', 'time': 'date',
            'Open': 'open', 'High': 'high', 'Low': 'low', 
            'Close': 'close', 'Volume': 'volume', 'Date': 'date'
        }
        
        df = df.rename(columns=column_mapping)
        if 'ticker' not in df.columns:
            df['ticker'] = ticker
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
            except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime) as e:
                logger.debug(f"Failed to convert date column to datetime for {ticker}: {str(e)}, keeping original format")
        return df
    
    def query_sql(self, sql: str) -> pd.DataFrame:
        """Execute SQL query against Massive.com data."""
        # Pre-validation with if-else
        if not sql:
            logger.error("SQL query is empty or None")
            return pd.DataFrame()

        if not isinstance(sql, str):
            logger.error(f"SQL query must be a string, got {type(sql)}")
            return pd.DataFrame()

        sql = sql.strip()

        if not sql:
            logger.error("SQL query is empty after strip")
            return pd.DataFrame()

        try:
            self._apply_rate_limit()
            url = f"{self.api_base_url}/sql"
            response = self.session.post(url, json={"query": sql}, timeout=60)
            response.raise_for_status()

            result = response.json()
            return pd.DataFrame(result.get('data', []))
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout executing SQL query: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error executing SQL query: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error executing SQL query: {str(e)}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error executing SQL query: {str(e)}")
            return pd.DataFrame()
        except ValueError as e:
            logger.error(f"JSON decode error in SQL query response: {str(e)}")
            return pd.DataFrame()
        except KeyError as e:
            logger.error(f"Missing expected data in SQL query response: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error executing SQL query: {str(e)}")
            return pd.DataFrame()
    
    def get_websocket_client(self, use_delayed: bool = True, callback: Optional[Callable] = None):
        """Get WebSocket client for streaming data."""
        from .massive_websocket import MassiveWebSocketClient
        return MassiveWebSocketClient(self.api_key, use_delayed, callback)
