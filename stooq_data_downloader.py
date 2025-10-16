#!/usr/bin/env python3
"""
Stooq Data Downloader for REDLINE
Downloads current historical data from Stooq.pl for specified tickers
"""

import pandas as pd
import pandas_datareader.data as web
import os
import sys
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StooqDataDownloader:
    """Download historical data from Stooq.pl using pandas_datareader"""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def download_ticker_data(self, ticker: str, start_date: datetime = None, 
                           end_date: datetime = None) -> Optional[pd.DataFrame]:
        """
        Download historical data for a specific ticker using pandas_datareader
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date for data (default: 1 year ago)
            end_date: End date for data (default: today)
        
        Returns:
            DataFrame with historical data or None if failed
        """
        try:
            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=365)
            
            logger.info(f"Downloading data for {ticker} from {start_date.date()} to {end_date.date()}")
            
            # Use pandas_datareader to fetch data from Stooq
            df = web.DataReader(ticker, 'stooq', start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data returned for ticker {ticker}")
                return None
            
            # Standardize column names to match REDLINE format
            df = self._standardize_stooq_columns(df, ticker)
            
            logger.info(f"Successfully downloaded {len(df)} records for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None
    
    def _standardize_stooq_columns(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Stooq data columns to match REDLINE format
        
        Args:
            df: Raw DataFrame from Stooq
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame
        """
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Add ticker column
        df['ticker'] = ticker
        
        # pandas_datareader returns data with Date as index, Open, High, Low, Close, Volume as columns
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Map Stooq columns to REDLINE schema
        column_mapping = {
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'vol'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add missing columns with None values
        required_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns to match REDLINE schema
        df = df[required_columns]
        
        # Add format identifier
        df['format'] = 'stooq_download'
        
        return df
    
    def download_multiple_tickers(self, tickers: List[str], start_date: datetime = None,
                                  end_date: datetime = None, delay: float = 1.0) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
        results = {}
        
        for i, ticker in enumerate(tickers):
            logger.info(f"Downloading ticker {i+1}/{len(tickers)}: {ticker}")
            
            df = self.download_ticker_data(ticker, start_date, end_date)
            if df is not None:
                results[ticker] = df
                
                # Save individual file
                filename = f"{ticker}_stooq_data.csv"
                filepath = os.path.join(self.output_dir, filename)
                df.to_csv(filepath, index=False)
                logger.info(f"Saved {ticker} data to {filepath}")
            
            # Add delay to be respectful to the server
            if i < len(tickers) - 1:  # Don't delay after the last ticker
                time.sleep(delay)
        
        return results
    
    def download_popular_stocks(self, start_date: datetime = None, 
                               end_date: datetime = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for a set of popular US stocks
        
        Args:
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
        popular_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
            'CRM', 'NFLX', 'INTC', 'CMCSA', 'PFE', 'TMO', 'ABT', 'COST', 'WMT',
            'MRK', 'PEP', 'KO', 'AVGO', 'ACN', 'TXN', 'NKE', 'DHR', 'VZ', 'CSCO',
            'QCOM', 'T', 'LLY', 'WFC', 'RTX', 'SPGI', 'UNP', 'HON', 'UPS', 'LOW'
        ]
        
        logger.info(f"Downloading data for {len(popular_tickers)} popular stocks")
        return self.download_multiple_tickers(popular_tickers, start_date, end_date)
    
    def save_combined_data(self, data_dict: Dict[str, pd.DataFrame], 
                          filename: str = None) -> str:
        """
        Save combined data from multiple tickers to a single file
        
        Args:
            data_dict: Dictionary mapping tickers to DataFrames
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if not data_dict:
            logger.warning("No data to save")
            return None
        
        # Combine all DataFrames
        combined_df = pd.concat(data_dict.values(), ignore_index=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stooq_combined_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        combined_df.to_csv(filepath, index=False)
        
        logger.info(f"Saved combined data ({len(combined_df)} records) to {filepath}")
        return filepath

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Download Stooq historical data")
    parser.add_argument("--tickers", nargs="+", help="Ticker symbols to download")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", default="data", help="Output directory")
    parser.add_argument("--popular", action="store_true", 
                       help="Download popular US stocks")
    parser.add_argument("--delay", type=float, default=1.0, 
                       help="Delay between requests (seconds)")
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    # Create downloader
    downloader = StooqDataDownloader(args.output)
    
    if args.popular:
        # Download popular stocks
        data = downloader.download_popular_stocks(start_date, end_date)
        if data:
            downloader.save_combined_data(data, "popular_stocks_stooq.csv")
    elif args.tickers:
        # Download specified tickers
        data = downloader.download_multiple_tickers(args.tickers, start_date, end_date, args.delay)
        if data:
            downloader.save_combined_data(data, "custom_tickers_stooq.csv")
    else:
        # Default: download a few popular tickers
        default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        logger.info(f"No tickers specified, downloading default set: {default_tickers}")
        data = downloader.download_multiple_tickers(default_tickers, start_date, end_date, args.delay)
        if data:
            downloader.save_combined_data(data, "default_tickers_stooq.csv")

if __name__ == "__main__":
    main()
