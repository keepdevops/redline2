#!/usr/bin/env python3
"""
Yahoo Finance Data Downloader for REDLINE
Alternative data source when Stooq is not accessible
"""

import pandas as pd
import yfinance as yf
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

class YahooDataDownloader:
    """Download historical data from Yahoo Finance as Stooq alternative"""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def download_ticker_data(self, ticker: str, start_date: datetime = None, 
                           end_date: datetime = None, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Download historical data for a specific ticker using yfinance
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date for data (overrides period if provided)
            end_date: End date for data (overrides period if provided)
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
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
            
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Download data
            if start_date and end_date:
                df = stock.history(start=start_date, end=end_date)
            else:
                df = stock.history(period=period)
            
            if df.empty:
                logger.warning(f"No data returned for ticker {ticker}")
                return None
            
            # Standardize column names to match REDLINE format
            df = self._standardize_yahoo_columns(df, ticker)
            
            logger.info(f"Successfully downloaded {len(df)} records for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None
    
    def _standardize_yahoo_columns(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize Yahoo Finance data columns to Stooq format for REDLINE
        
        Args:
            df: Raw DataFrame from Yahoo Finance
            ticker: Ticker symbol
            
        Returns:
            DataFrame in Stooq format
        """
        # Create a copy to avoid modifying original
        df = df.copy()
        
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
    
    def download_multiple_tickers(self, tickers: List[str], start_date: datetime = None,
                                  end_date: datetime = None, period: str = "1y", 
                                  delay: float = 0.1) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            period: Data period if dates not provided
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
        results = {}
        
        for i, ticker in enumerate(tickers):
            logger.info(f"Downloading ticker {i+1}/{len(tickers)}: {ticker}")
            
            df = self.download_ticker_data(ticker, start_date, end_date, period)
            if df is not None:
                results[ticker] = df
                
                # Save individual file
                filename = f"{ticker}_yahoo_data.csv"
                filepath = os.path.join(self.output_dir, filename)
                df.to_csv(filepath, index=False)
                logger.info(f"Saved {ticker} data to {filepath}")
            
            # Add small delay to be respectful
            if i < len(tickers) - 1:
                time.sleep(delay)
        
        return results
    
    def download_popular_stocks(self, start_date: datetime = None, 
                               end_date: datetime = None, period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Download data for a set of popular US stocks
        
        Args:
            start_date: Start date for data
            end_date: End date for data
            period: Data period if dates not provided
            
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
        return self.download_multiple_tickers(popular_tickers, start_date, end_date, period)
    
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
            filename = f"yahoo_combined_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        combined_df.to_csv(filepath, index=False)
        
        logger.info(f"Saved combined data ({len(combined_df)} records) to {filepath}")
        return filepath

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Download Yahoo Finance historical data")
    parser.add_argument("--tickers", nargs="+", help="Ticker symbols to download")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--period", default="1y", 
                       help="Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    parser.add_argument("--output", default="data", help="Output directory")
    parser.add_argument("--popular", action="store_true", 
                       help="Download popular US stocks")
    parser.add_argument("--delay", type=float, default=0.1, 
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
    downloader = YahooDataDownloader(args.output)
    
    if args.popular:
        # Download popular stocks
        data = downloader.download_popular_stocks(start_date, end_date, args.period)
        if data:
            downloader.save_combined_data(data, "popular_stocks_yahoo.csv")
    elif args.tickers:
        # Download specified tickers
        data = downloader.download_multiple_tickers(args.tickers, start_date, end_date, args.period, args.delay)
        if data:
            downloader.save_combined_data(data, "custom_tickers_yahoo.csv")
    else:
        # Default: download a few popular tickers
        default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        logger.info(f"No tickers specified, downloading default set: {default_tickers}")
        data = downloader.download_multiple_tickers(default_tickers, start_date, end_date, args.period, args.delay)
        if data:
            downloader.save_combined_data(data, "default_tickers_yahoo.csv")

if __name__ == "__main__":
    main()
