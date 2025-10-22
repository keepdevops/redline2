#!/usr/bin/env python3
"""
REDLINE CSV Data Downloader
Downloads data from local CSV files or creates sample data.
"""

import logging
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .base_downloader import BaseDownloader

logger = logging.getLogger(__name__)

class CSVDownloader(BaseDownloader):
    """CSV-based data downloader for local files and sample data."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize CSV downloader."""
        super().__init__("CSV Data", "Local Files")
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # CSV-specific configuration
        self.data_dir = "data"
        self.sample_data_dir = "data/sample"
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.sample_data_dir, exist_ok=True)
    
    def download_single_ticker(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker from CSV files or create sample data.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with historical data
        """
        try:
            # Try to find existing CSV file
            csv_file = self._find_csv_file(ticker)
            
            if csv_file and os.path.exists(csv_file):
                self.logger.info(f"Loading {ticker} from existing CSV file: {csv_file}")
                return self._load_from_csv(csv_file, start_date, end_date)
            else:
                self.logger.info(f"No CSV file found for {ticker}, creating sample data")
                return self._create_sample_data(ticker, start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"Error downloading {ticker} from CSV: {str(e)}")
            return pd.DataFrame()
    
    def _find_csv_file(self, ticker: str) -> Optional[str]:
        """Find CSV file for the given ticker."""
        possible_files = [
            f"{self.data_dir}/{ticker}_yahoo_data.csv",
            f"{self.data_dir}/{ticker}_data.csv",
            f"{self.data_dir}/{ticker}.csv",
            f"{self.data_dir}/downloaded/{ticker}_yahoo_*.csv",
            f"{self.data_dir}/downloaded/{ticker}_*.csv"
        ]
        
        for file_pattern in possible_files:
            if '*' in file_pattern:
                # Handle wildcard patterns
                import glob
                matches = glob.glob(file_pattern)
                if matches:
                    return matches[0]  # Return first match
            else:
                if os.path.exists(file_pattern):
                    return file_pattern
        
        return None
    
    def _load_from_csv(self, csv_file: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Load data from CSV file."""
        try:
            # Try different CSV formats
            df = None
            
            # Try with index column
            try:
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
            except:
                pass
            
            # Try without index column
            if df is None:
                try:
                    df = pd.read_csv(csv_file, parse_dates=True)
                    # Try to set date column as index
                    date_columns = ['Date', 'date', 'DATE', 'timestamp', 'Timestamp']
                    for col in date_columns:
                        if col in df.columns:
                            df.set_index(col, inplace=True)
                            break
                except:
                    pass
            
            if df is None:
                self.logger.error(f"Could not parse CSV file: {csv_file}")
                return pd.DataFrame()
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Filter by date range if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df.index >= start_dt]
            
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df.index <= end_dt]
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file {csv_file}: {str(e)}")
            return pd.DataFrame()
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names."""
        column_mapping = {
            'open': 'Open',
            'OPEN': 'Open',
            'high': 'High',
            'HIGH': 'High',
            'low': 'Low',
            'LOW': 'Low',
            'close': 'Close',
            'CLOSE': 'Close',
            'volume': 'Volume',
            'VOLUME': 'Volume',
            'vol': 'Volume',
            'VOL': 'Volume'
        }
        
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                if col == 'Volume':
                    df[col] = 1000000  # Default volume
                else:
                    df[col] = df['Close'] if 'Close' in df.columns else 100
        
        return df
    
    def _create_sample_data(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Create sample data for the ticker."""
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Create date range
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Create sample data with ticker-specific seed
            np.random.seed(hash(ticker) % 2**32)
            
            # Generate realistic stock data
            base_price = 100 + (hash(ticker) % 200)  # Base price between 100-300
            
            # Generate price movements
            returns = np.random.normal(0, 0.02, len(dates))  # 2% daily volatility
            prices = base_price * np.exp(np.cumsum(returns))
            
            # Create OHLC data
            df = pd.DataFrame({
                'Open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
                'High': prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
                'Low': prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
                'Close': prices,
                'Volume': np.random.randint(1000000, 10000000, len(dates))
            }, index=dates)
            
            # Ensure High >= Low and High >= Open, Close
            df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
            df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
            
            # Round to 2 decimal places
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].round(2)
            
            self.logger.info(f"Created sample data for {ticker} with {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error creating sample data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def standardize_csv_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Standardize CSV data format.
        
        Args:
            data: Raw DataFrame from CSV
            ticker: Ticker symbol
            
        Returns:
            Standardized DataFrame
        """
        try:
            df = data.copy()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return pd.DataFrame()
            
            # Clean numeric data
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['Close'])
            
            # Sort by date
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error standardizing CSV data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available tickers from CSV files."""
        tickers = []
        
        # Scan data directory for CSV files
        for file in os.listdir(self.data_dir):
            if file.endswith('.csv'):
                # Extract ticker from filename
                ticker = file.replace('.csv', '').split('_')[0]
                if ticker not in tickers:
                    tickers.append(ticker)
        
        return sorted(tickers)
    
    def download_multiple_tickers(self, tickers: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers from CSV files.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        failed_tickers = []
        
        self.logger.info(f"Starting batch download of {len(tickers)} tickers from CSV files")
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Downloading {ticker} ({i+1}/{len(tickers)})")
                
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
                
            except Exception as e:
                self.logger.error(f"Failed to download {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
        
        if failed_tickers:
            self.logger.warning(f"Failed to download {len(failed_tickers)} tickers from CSV: {', '.join(failed_tickers)}")
        
        return results
