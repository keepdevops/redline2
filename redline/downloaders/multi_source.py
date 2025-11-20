#!/usr/bin/env python3
"""
REDLINE Multi-Source Downloader
Downloads data from multiple sources with fallback capabilities.
"""

import logging
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime
from .base_downloader import BaseDownloader
from .yahoo_downloader import YahooDownloader
from .stooq_downloader import StooqDownloader
import os

logger = logging.getLogger(__name__)

class MultiSourceDownloader(BaseDownloader):
    """Multi-source data downloader with fallback capabilities."""
    
    def __init__(self, output_dir: str = "data", massive_api_key: str = None):
        """
        Initialize multi-source downloader.
        
        Args:
            output_dir: Output directory for downloaded files
            massive_api_key: Optional Massive.com API key. If provided, Massive.com will be added as primary source.
        """
        super().__init__("Multi-Source", None)
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Initialize individual downloaders
        self.downloaders = {
            'yahoo': YahooDownloader(output_dir),
            'stooq': StooqDownloader(output_dir)
        }
        
        # Source priority order (first is preferred)
        self.source_priority = ['yahoo', 'stooq']
        
        # Source statistics
        self.source_stats = {
            'yahoo': {'attempts': 0, 'successes': 0, 'failures': 0},
            'stooq': {'attempts': 0, 'successes': 0, 'failures': 0}
        }
        
        # Add Massive.com if API key is available
        massive_key = massive_api_key or os.environ.get('MASSIVE_API_KEY')
        if massive_key:
            try:
                from .massive_downloader import MassiveDownloader
                self.downloaders['massive'] = MassiveDownloader(api_key=massive_key, output_dir=output_dir)
                self.source_stats['massive'] = {'attempts': 0, 'successes': 0, 'failures': 0}
                # Set Massive.com as primary source
                self.source_priority = ['massive', 'yahoo', 'stooq']
                self.logger.info("Massive.com downloader added as primary source")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Massive.com downloader: {str(e)}")
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None, 
                             preferred_source: str = None) -> pd.DataFrame:
        """
        Download data for a single ticker from multiple sources with fallback.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            preferred_source: Preferred source ('massive', 'yahoo', 'stooq')
            
        Returns:
            DataFrame with historical data
        """
        # Determine source order
        sources_to_try = self._get_source_order(preferred_source)
        
        for source_name in sources_to_try:
            try:
                self.logger.info(f"Trying {source_name} for ticker {ticker}")
                
                # Update source statistics
                self.source_stats[source_name]['attempts'] += 1
                
                # Get downloader
                downloader = self.downloaders[source_name]
                
                # Download data
                data = downloader.download_single_ticker(ticker, start_date, end_date)
                
                if not data.empty:
                    self.logger.info(f"Successfully downloaded {ticker} from {source_name}")
                    self.source_stats[source_name]['successes'] += 1
                    self.stats['successful_requests'] += 1
                    self.stats['total_data_points'] += len(data)
                    
                    # Add source metadata
                    data['data_source'] = source_name
                    
                    return data
                else:
                    self.logger.warning(f"No data received from {source_name} for {ticker}")
                    self.source_stats[source_name]['failures'] += 1
                
            except Exception as e:
                self.logger.error(f"Error downloading {ticker} from {source_name}: {str(e)}")
                self.source_stats[source_name]['failures'] += 1
        
        # All sources failed
        self.logger.error(f"Failed to download {ticker} from all sources")
        self.stats['failed_requests'] += 1
        self.stats['total_requests'] += 1
        
        return pd.DataFrame()
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None,
                                preferred_source: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers from multiple sources.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            preferred_source: Preferred source ('yahoo', 'stooq')
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting multi-source download of {len(tickers)} tickers")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
                # Download data with fallback
                data = self.download_single_ticker(ticker, start_date, end_date, preferred_source)
                
                if not data.empty:
                    results[ticker] = data
                else:
                    failed_tickers.append(ticker)
                
                self.stats['total_requests'] += 1
                self.stats['last_request_time'] = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Failed to download {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
        
        if failed_tickers:
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers: {', '.join(failed_tickers)}")
        
        self.logger.info(f"Multi-source download complete: {len(results)} successful, {len(failed_tickers)} failed")
        return results
    
    def _get_source_order(self, preferred_source: str = None) -> List[str]:
        """Get ordered list of sources to try."""
        if preferred_source and preferred_source in self.source_priority:
            # Move preferred source to front
            sources = [preferred_source] + [s for s in self.source_priority if s != preferred_source]
        else:
            sources = self.source_priority.copy()
        
        return sources
    
    def download_from_source(self, source: str, ticker: str, start_date: str = None, 
                           end_date: str = None) -> pd.DataFrame:
        """
        Download data from a specific source.
        
        Args:
            source: Source name ('yahoo', 'stooq')
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with stock data
        """
        if source not in self.downloaders:
            self.logger.error(f"Unknown source: {source}")
            return pd.DataFrame()
        
        try:
            self.source_stats[source]['attempts'] += 1
            downloader = self.downloaders[source]
            data = downloader.download_single_ticker(ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                self.source_stats[source]['successes'] += 1
                self.logger.info(f"Successfully downloaded {ticker} from {source}")
                return data
            else:
                self.source_stats[source]['failures'] += 1
                self.logger.warning(f"No data returned for {ticker} from {source}")
                return pd.DataFrame()
                
        except Exception as e:
            self.source_stats[source]['failures'] += 1
            self.logger.error(f"Error downloading {ticker} from {source}: {str(e)}")
            return pd.DataFrame()
    
    def get_source_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for each source."""
        return self.source_stats.copy()
    
    def get_source_success_rates(self) -> Dict[str, float]:
        """Get success rates for each source."""
        success_rates = {}
        
        for source, stats in self.source_stats.items():
            total_attempts = stats['attempts']
            if total_attempts > 0:
                success_rate = stats['successes'] / total_attempts * 100
            else:
                success_rate = 0.0
            
            success_rates[source] = success_rate
        
        return success_rates
    
    def recommend_source(self) -> str:
        """Recommend the best source based on success rates."""
        success_rates = self.get_source_success_rates()
        
        if not success_rates:
            return 'yahoo'  # Default recommendation
        
        # Return source with highest success rate
        best_source = max(success_rates, key=success_rates.get)
        return best_source
    
    def set_source_priority(self, priority_list: List[str]):
        """
        Set the priority order for sources.
        
        Args:
            priority_list: List of source names in priority order
        """
        if all(source in self.downloaders for source in priority_list):
            self.source_priority = priority_list
            self.logger.info(f"Updated source priority: {priority_list}")
        else:
            self.logger.error("Invalid source names in priority list")
    
    def add_downloader(self, name: str, downloader: BaseDownloader):
        """
        Add a new downloader to the multi-source system.
        
        Args:
            name: Name for the downloader
            downloader: Downloader instance
        """
        self.downloaders[name] = downloader
        self.source_stats[name] = {'attempts': 0, 'successes': 0, 'failures': 0}
        
        if name not in self.source_priority:
            self.source_priority.append(name)
        
        self.logger.info(f"Added downloader: {name}")
    
    def remove_downloader(self, name: str):
        """
        Remove a downloader from the multi-source system.
        
        Args:
            name: Name of the downloader to remove
        """
        if name in self.downloaders:
            del self.downloaders[name]
            del self.source_stats[name]
            
            if name in self.source_priority:
                self.source_priority.remove(name)
            
            self.logger.info(f"Removed downloader: {name}")
    
    def get_available_sources(self) -> List[str]:
        """Get list of available sources."""
        return list(self.downloaders.keys())
    
    def test_source_connectivity(self, source_name: str) -> bool:
        """
        Test connectivity to a specific source.
        
        Args:
            source_name: Name of the source to test
            
        Returns:
            True if source is accessible, False otherwise
        """
        if source_name not in self.downloaders:
            return False
        
        try:
            # Try downloading a common ticker
            test_ticker = 'AAPL'
            downloader = self.downloaders[source_name]
            data = downloader.download_single_ticker(test_ticker)
            
            return not data.empty
            
        except Exception as e:
            self.logger.error(f"Connectivity test failed for {source_name}: {str(e)}")
            return False
    
    def close(self):
        """Close all downloaders and clean up resources."""
        for downloader in self.downloaders.values():
            if hasattr(downloader, 'close'):
                downloader.close()
        
        super().close()
