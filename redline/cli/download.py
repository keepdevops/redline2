#!/usr/bin/env python3
"""
REDLINE CLI Download Tool
Command-line interface for downloading financial data.
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from redline.downloaders.yahoo_downloader import YahooDownloader
from redline.downloaders.stooq_downloader import StooqDownloader
from redline.downloaders.multi_source import MultiSourceDownloader
from redline.downloaders.bulk_downloader import BulkDownloader
from redline.utils.logging_config import setup_logging

def main():
    """Main CLI entry point for data downloading."""
    parser = argparse.ArgumentParser(description='REDLINE Data Downloader CLI')
    
    # Data source selection
    parser.add_argument('--source', choices=['yahoo', 'stooq', 'multi'], 
                       default='multi', help='Data source to use')
    
    # Ticker specification
    parser.add_argument('--tickers', nargs='+', required=True,
                       help='Ticker symbols to download (e.g., AAPL MSFT GOOGL)')
    
    # Date range
    parser.add_argument('--start-date', type=str,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--period', type=str, choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                       default='1y', help='Data period (for Yahoo Finance)')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='data',
                       help='Output directory for downloaded data')
    parser.add_argument('--format', choices=['csv', 'parquet', 'json'], 
                       default='csv', help='Output file format')
    
    # Download options
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Batch size for bulk downloads')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum number of worker threads')
    
    # Logging options
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress console output')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file='download.log',
        console_output=not args.quiet
    )
    
    try:
        # Determine date range
        start_date, end_date = _determine_date_range(args)
        
        # Initialize downloader based on source
        downloader = _create_downloader(args)
        
        # Download data
        if len(args.tickers) == 1:
            # Single ticker download
            _download_single_ticker(downloader, args.tickers[0], start_date, end_date, args)
        else:
            # Multiple tickers download
            _download_multiple_tickers(downloader, args.tickers, start_date, end_date, args)
        
        print("Download completed successfully!")
        
    except KeyboardInterrupt:
        print("\nDownload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Download failed: {str(e)}")
        sys.exit(1)

def _determine_date_range(args):
    """Determine start and end dates from arguments."""
    if args.start_date and args.end_date:
        return args.start_date, args.end_date
    elif args.start_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        return args.start_date, end_date
    elif args.end_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        return start_date, args.end_date
    else:
        # Use period for Yahoo Finance or default to 1 year
        if args.period == 'max':
            return None, None
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            return start_date, end_date

def _create_downloader(args):
    """Create appropriate downloader based on source."""
    if args.source == 'yahoo':
        return YahooDownloader(args.output_dir)
    elif args.source == 'stooq':
        return StooqDownloader(args.output_dir)
    elif args.source == 'multi':
        return MultiSourceDownloader(args.output_dir)
    else:
        raise ValueError(f"Unknown source: {args.source}")

def _download_single_ticker(downloader, ticker, start_date, end_date, args):
    """Download data for a single ticker."""
    print(f"Downloading {ticker}...")
    
    data = downloader.download_single_ticker(ticker, start_date, end_date)
    
    if data.empty:
        print(f"No data found for {ticker}")
        return
    
    # Save data
    output_file = os.path.join(args.output_dir, f"{ticker}.{args.format}")
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.format == 'csv':
        data.to_csv(output_file, index=False)
    elif args.format == 'parquet':
        data.to_parquet(output_file, index=False)
    elif args.format == 'json':
        data.to_json(output_file, orient='records', indent=2)
    
    print(f"Saved {len(data)} records to {output_file}")

def _download_multiple_tickers(downloader, tickers, start_date, end_date, args):
    """Download data for multiple tickers."""
    print(f"Downloading {len(tickers)} tickers...")
    
    if isinstance(downloader, BulkDownloader):
        # Use bulk downloader for efficiency
        results = downloader.download_bulk_tickers(
            tickers, start_date, end_date, 
            batch_size=args.batch_size
        )
    else:
        # Use regular multi-ticker download
        results = downloader.download_multiple_tickers(tickers, start_date, end_date)
    
    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    
    saved_count = 0
    for ticker, data in results.items():
        if not data.empty:
            output_file = os.path.join(args.output_dir, f"{ticker}.{args.format}")
            
            if args.format == 'csv':
                data.to_csv(output_file, index=False)
            elif args.format == 'parquet':
                data.to_parquet(output_file, index=False)
            elif args.format == 'json':
                data.to_json(output_file, orient='records', indent=2)
            
            saved_count += 1
            print(f"Saved {len(data)} records for {ticker}")
    
    print(f"Downloaded {saved_count} out of {len(tickers)} tickers")

if __name__ == '__main__':
    main()
