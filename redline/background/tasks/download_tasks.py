#!/usr/bin/env python3
"""
REDLINE Download Tasks
Background tasks for downloading financial data.
"""

import os
import logging
import pandas as pd
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def process_data_download_impl(ticker: str, start_date: str, end_date: str, 
                               source: str = 'yahoo', options: Dict[str, Any] = None, 
                               progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of data download."""
    try:
        logger.info(f"Starting data download: {ticker} from {source}")
        
        if progress_callback:
            progress_callback({'step': 'initializing', 'progress': 5})
        
        # Import downloaders
        downloader = None
        if source == 'yahoo':
            from ...downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
        elif source == 'stooq':
            from ...downloaders.stooq_downloader import StooqDownloader
            downloader = StooqDownloader()
        elif source == 'alpha_vantage':
            from ...downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            downloader = AlphaVantageDownloader()
        elif source == 'massive':
            from ...downloaders.massive_downloader import MassiveDownloader
            api_key = options.get('api_key') if options else None
            api_key = api_key or os.environ.get('MASSIVE_API_KEY')
            if not api_key:
                raise ValueError("Massive.com API key is required")
            downloader = MassiveDownloader(api_key=api_key)
        else:
            raise ValueError(f"Unsupported source: {source}")
        
        if progress_callback:
            progress_callback({'step': 'downloading', 'progress': 30})
        
        # Download data
        df = downloader.download_single_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        if progress_callback:
            progress_callback({'step': 'saving', 'progress': 80})
        
        # Save to file
        filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
        downloaded_dir = "data/downloaded"
        os.makedirs(downloaded_dir, exist_ok=True)
        filepath = os.path.join(downloaded_dir, filename)
        
        df.to_csv(filepath, index=True)
        
        if progress_callback:
            progress_callback({'step': 'completed', 'progress': 100})
        
        result = {
            'status': 'success',
            'ticker': ticker,
            'source': source,
            'filename': filename,
            'filepath': filepath,
            'records': len(df),
            'columns': list(df.columns),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data download completed: {len(df)} records for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Data download failed: {str(e)}")
        raise

