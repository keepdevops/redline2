#!/usr/bin/env python3
"""
REDLINE Bulk Downloader
Downloads data for large numbers of tickers efficiently.
"""

import logging
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from .base_downloader import BaseDownloader
from .multi_source import MultiSourceDownloader

logger = logging.getLogger(__name__)

class BulkDownloader(BaseDownloader):
    """Bulk data downloader for large-scale data acquisition."""
    
    def __init__(self, output_dir: str = "data", max_workers: int = 4):
        """Initialize bulk downloader."""
        super().__init__("Bulk Downloader", None)
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # Initialize multi-source downloader
        self.multi_source = MultiSourceDownloader(output_dir)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Progress tracking
        self.progress_callback = None
        self.cancel_requested = False
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download data for a single ticker (delegates to multi-source).
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with historical data
        """
        return self.multi_source.download_single_ticker(ticker, start_date, end_date)
    
    def download_bulk_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None,
                            batch_size: int = 50, progress_callback = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for a large number of tickers using parallel processing.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            batch_size: Number of tickers to process in each batch
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        self.progress_callback = progress_callback
        self.cancel_requested = False
        
        results = {}
        failed_tickers = []
        
        total_tickers = len(tickers)
        self.logger.info(f"Starting bulk download of {total_tickers} tickers")
        
        # Process in batches to manage memory and rate limits
        for batch_start in range(0, total_tickers, batch_size):
            if self.cancel_requested:
                self.logger.info("Bulk download cancelled by user")
                break
            
            batch_end = min(batch_start + batch_size, total_tickers)
            batch_tickers = tickers[batch_start:batch_end]
            
            self.logger.info(f"Processing batch {batch_start//batch_size + 1}: {batch_start+1}-{batch_end} of {total_tickers}")
            
            # Process batch with parallel downloads
            batch_results = self._download_batch_parallel(batch_tickers, start_date, end_date)
            
            # Merge results
            results.update(batch_results['successful'])
            failed_tickers.extend(batch_results['failed'])
            
            # Update progress
            if self.progress_callback:
                progress = (batch_end / total_tickers) * 100
                self.progress_callback(progress, f"Processed {batch_end} of {total_tickers} tickers")
            
            # Rate limiting between batches
            if batch_end < total_tickers:
                import time
                time.sleep(2)  # 2 second delay between batches
        
        self.logger.info(f"Bulk download complete: {len(results)} successful, {len(failed_tickers)} failed")
        return results
    
    def _download_batch_parallel(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, Union[Dict[str, pd.DataFrame], List[str]]]:
        """
        Download a batch of tickers in parallel.
        
        Args:
            tickers: List of ticker symbols for this batch
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with 'successful' and 'failed' keys
        """
        successful = {}
        failed = []
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_ticker = {
                executor.submit(self._download_with_error_handling, ticker, start_date, end_date): ticker
                for ticker in tickers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ticker):
                if self.cancel_requested:
                    break
                
                ticker = future_to_ticker[future]
                
                try:
                    result = future.result()
                    if not result.empty:
                        successful[ticker] = result
                        
                        with self.lock:
                            self.stats['successful_requests'] += 1
                            self.stats['total_data_points'] += len(result)
                    else:
                        failed.append(ticker)
                        
                        with self.lock:
                            self.stats['failed_requests'] += 1
                
                except Exception as e:
                    self.logger.error(f"Error in parallel download for {ticker}: {str(e)}")
                    failed.append(ticker)
                    
                    with self.lock:
                        self.stats['failed_requests'] += 1
                
                with self.lock:
                    self.stats['total_requests'] += 1
                    self.stats['last_request_time'] = datetime.now()
        
        return {'successful': successful, 'failed': failed}
    
    def _download_with_error_handling(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Download a single ticker with error handling."""
        try:
            return self.multi_source.download_single_ticker(ticker, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error downloading {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def download_sector_data(self, sectors: List[str], start_date: str = None, end_date: str = None) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Download data for all tickers in specified sectors.
        
        Args:
            sectors: List of sector names
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping sector to ticker to DataFrame
        """
        results = {}
        
        for sector in sectors:
            self.logger.info(f"Downloading sector: {sector}")
            
            # Get tickers for sector (this would need to be implemented based on available data)
            sector_tickers = self._get_sector_tickers(sector)
            
            if sector_tickers:
                sector_results = self.download_bulk_tickers(sector_tickers, start_date, end_date)
                results[sector] = sector_results
            else:
                self.logger.warning(f"No tickers found for sector: {sector}")
                results[sector] = {}
        
        return results
    
    def _get_sector_tickers(self, sector: str) -> List[str]:
        """
        Get list of tickers for a sector.
        This is a placeholder - in practice, you'd need to implement
        sector-to-ticker mapping based on available data sources.
        """
        # Placeholder implementation
        sector_mappings = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
            'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'KMI', 'PXD']
        }
        
        return sector_mappings.get(sector.lower(), [])
    
    def download_market_data(self, market: str, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for all major tickers in a market.
        
        Args:
            market: Market identifier ('US', 'EU', 'ASIA')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        market_tickers = self._get_market_tickers(market)
        
        if market_tickers:
            return self.download_bulk_tickers(market_tickers, start_date, end_date)
        else:
            self.logger.warning(f"No tickers found for market: {market}")
            return {}
    
    def _get_market_tickers(self, market: str) -> List[str]:
        """Get list of major tickers for a market."""
        market_mappings = {
            'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'BAC', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA'],
            'EU': ['ASML', 'SAP', 'NOVN', 'UL', 'NESN', 'RHHBY', 'TSM', 'TM', 'HDB', 'BABA'],
            'ASIA': ['TSM', 'TM', 'HDB', 'BABA', 'JD', 'BIDU', 'NIO', 'XPEV', 'LI']
        }
        
        return market_mappings.get(market.upper(), [])
    
    def cancel_download(self):
        """Cancel the current bulk download operation."""
        self.cancel_requested = True
        self.logger.info("Bulk download cancellation requested")
    
    def get_download_progress(self) -> Dict[str, Any]:
        """Get current download progress information."""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'total_data_points': self.stats['total_data_points'],
            'cancel_requested': self.cancel_requested,
            'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1) * 100
        }
    
    def close(self):
        """Close the bulk downloader and clean up resources."""
        self.cancel_download()
        
        if hasattr(self, 'multi_source'):
            self.multi_source.close()
        
        super().close()
