#!/usr/bin/env python3
"""
REDLINE Generic API Downloader
Downloads historical data from any financial API with configurable rate limiting.
"""

import logging
import pandas as pd
import requests
import time
import threading
from datetime import datetime
from typing import Dict, Any
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class GenericAPIDownloader(BaseDownloader):
    """Generic API downloader for any financial data source."""
    
    def __init__(self, api_config: Dict[str, Any], output_dir: str = "data"):
        """Initialize generic API downloader with configuration dict."""
        name = api_config.get('name', 'Generic API')
        super().__init__(name, api_config.get('base_url', ''))
        
        self.output_dir = output_dir
        self.api_config = api_config
        self.base_url = api_config.get('base_url', '')
        self.endpoint = api_config.get('endpoint', '')
        self.api_key = api_config.get('api_key')
        self.api_key_param = api_config.get('api_key_param', 'apikey')
        self.ticker_param = api_config.get('ticker_param', 'symbol')
        self.start_date_param = api_config.get('start_date_param', 'from')
        self.end_date_param = api_config.get('end_date_param', 'to')
        self.date_format = api_config.get('date_format', 'YYYY-MM-DD')
        self.response_format = api_config.get('response_format', 'json')
        self.data_path = api_config.get('data_path', 'data')
        self.column_mapping = api_config.get('column_mapping', {})
        self.timeout = api_config.get('timeout', 30)
        
        if not self.api_key or not self.base_url or not self.endpoint:
            raise ValueError(f"{name} requires api_key, base_url, and endpoint")
        
        # Rate limiting
        rate_limit_per_minute = api_config.get('rate_limit_per_minute', 60)
        self.min_request_interval = 60.0 / rate_limit_per_minute
        self.last_request_time = 0
        # rate_limit_lock will be initialized by base class _rate_limit() method
        
        # Custom headers
        if api_config.get('headers'):
            self.session.headers.update(api_config['headers'])
    
    def _format_date(self, date_str: str) -> Any:
        """Format date according to API requirements."""
        if self.date_format == 'timestamp':
            return int(datetime.strptime(date_str, '%Y-%m-%d').timestamp())
        elif self.date_format == 'iso':
            return datetime.strptime(date_str, '%Y-%m-%d').isoformat()
        elif self.date_format == 'YYYY-MM-DD':
            return date_str
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime(self.date_format)
        except:
            return date_str
    
    def _extract_data(self, response_data: Dict) -> pd.DataFrame:
        """Extract data array from API response."""
        data = response_data
        if self.data_path:
            for key in self.data_path.split('.'):
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return pd.DataFrame()
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    return pd.DataFrame(value)
            return pd.DataFrame([data])
        return pd.DataFrame()
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Download historical data for a single ticker."""
        try:
            self._rate_limit()
            url = f"{self.base_url.rstrip('/')}/{self.endpoint.lstrip('/')}"
            params = {self.ticker_param: ticker, self.api_key_param: self.api_key}
            
            if start_date:
                params[self.start_date_param] = self._format_date(start_date)
            if end_date:
                params[self.end_date_param] = self._format_date(end_date)
            
            params.update(self.api_config.get('additional_params', {}))
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            if self.response_format == 'csv':
                import io
                df = pd.read_csv(io.StringIO(response.text))
            else:
                df = self._extract_data(response.json())
            
            if df.empty:
                return pd.DataFrame()
            
            # Map columns if configured
            if self.column_mapping:
                rename_dict = {v: k for k, v in self.column_mapping.items() if v in df.columns}
                if rename_dict:
                    df = df.rename(columns=rename_dict)
            
            return self.standardize_data(df, ticker, self.name)
            
        except Exception as e:
            self.logger.error(f"Error downloading {ticker}: {str(e)}")
            return pd.DataFrame()
