#!/usr/bin/env python3
"""
Multi-Source Historical Data Downloader
Supports multiple free data services for historical stock data
"""

import yfinance as yf
import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSourceDownloader:
    """Download historical data from multiple free sources"""
    
    def __init__(self):
        self.api_keys = self.load_api_keys()
        
    def load_api_keys(self):
        """Load API keys from config file"""
        try:
            with open('api_keys.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_api_keys(self):
        """Save API keys to config file"""
        with open('api_keys.json', 'w') as f:
            json.dump(self.api_keys, f, indent=2)

    # YAHOO FINANCE (No API key needed)
    def download_yahoo(self, ticker: str, start_date: str = None, end_date: str = None, period: str = "5y") -> Optional[pd.DataFrame]:
        """Download data from Yahoo Finance"""
        try:
            logger.info(f"Downloading {ticker} from Yahoo Finance...")
            
            stock = yf.Ticker(ticker)
            
            if start_date and end_date:
                data = stock.history(start=start_date, end=end_date)
            else:
                data = stock.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for {ticker} on Yahoo Finance")
                return None
            
            # Convert to Stooq format
            return self._convert_to_stooq_format(data, ticker)
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {ticker}: {str(e)}")
            return None

    # ALPHA VANTAGE (Requires free API key)
    def download_alpha_vantage(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Download data from Alpha Vantage"""
        try:
            if 'alpha_vantage' not in self.api_keys:
                logger.warning("Alpha Vantage API key not found")
                return None
            
            logger.info(f"Downloading {ticker} from Alpha Vantage...")
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': 'full',
                'apikey': self.api_keys['alpha_vantage']
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            # Parse Alpha Vantage data
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                logger.warning(f"No data found for {ticker} on Alpha Vantage")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Filter by date range if provided
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            return self._convert_to_stooq_format(df, ticker)
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {str(e)}")
            return None

    # IEX CLOUD (Requires free API key)
    def download_iex_cloud(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Download data from IEX Cloud"""
        try:
            if 'iex_cloud' not in self.api_keys:
                logger.warning("IEX Cloud API key not found")
                return None
            
            logger.info(f"Downloading {ticker} from IEX Cloud...")
            
            # Calculate date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            url = f"https://cloud.iexapis.com/stable/stock/{ticker}/chart/5y"
            params = {
                'token': self.api_keys['iex_cloud']
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 402:
                logger.warning("IEX Cloud quota exceeded")
                return None
            
            data = response.json()
            
            if not data:
                logger.warning(f"No data found for {ticker} on IEX Cloud")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.sort_index()
            
            # Rename columns
            column_mapping = {
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Filter by date range if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df.index >= start_dt]
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df.index <= end_dt]
            
            return self._convert_to_stooq_format(df, ticker)
            
        except Exception as e:
            logger.error(f"IEX Cloud error for {ticker}: {str(e)}")
            return None

    # FINNHUB (Requires free API key)
    def download_finnhub(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Download data from Finnhub"""
        try:
            if 'finnhub' not in self.api_keys:
                logger.warning("Finnhub API key not found")
                return None
            
            logger.info(f"Downloading {ticker} from Finnhub...")
            
            # Convert dates to timestamps
            if start_date:
                start_ts = int(pd.to_datetime(start_date).timestamp())
            else:
                start_ts = int((datetime.now() - timedelta(days=365*5)).timestamp())
            
            if end_date:
                end_ts = int(pd.to_datetime(end_date).timestamp())
            else:
                end_ts = int(datetime.now().timestamp())
            
            url = f"https://finnhub.io/api/v1/stock/candle"
            params = {
                'symbol': ticker,
                'resolution': 'D',
                'from': start_ts,
                'to': end_ts,
                'token': self.api_keys['finnhub']
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('s') == 'no_data':
                logger.warning(f"No data found for {ticker} on Finnhub")
                return None
            
            if 'error' in data:
                logger.error(f"Finnhub error: {data['error']}")
                return None
            
            # Convert to DataFrame
            timestamps = data['t']
            df = pd.DataFrame({
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c'],
                'Volume': data['v']
            })
            
            df.index = pd.to_datetime(timestamps, unit='s')
            df = df.sort_index()
            
            return self._convert_to_stooq_format(df, ticker)
            
        except Exception as e:
            logger.error(f"Finnhub error for {ticker}: {str(e)}")
            return None

    def _convert_to_stooq_format(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Convert DataFrame to Stooq format"""
        try:
            # Handle timezone-aware timestamps
            if hasattr(df.index, 'tz') and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            # Create Stooq format DataFrame
            df_stooq = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': df.index.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['Open'].values,
                '<HIGH>': df['High'].values,
                '<LOW>': df['Low'].values,
                '<CLOSE>': df['Close'].values,
                '<VOL>': df['Volume'].values
            })
            
            # Clean numeric data
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
            
            # Remove rows with invalid data
            df_stooq = df_stooq.dropna()
            
            return df_stooq
            
        except Exception as e:
            logger.error(f"Error converting to Stooq format: {str(e)}")
            return df

    def download_from_source(self, source: str, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Download data from specified source"""
        if source == 'yahoo':
            return self.download_yahoo(ticker, start_date, end_date)
        elif source == 'alpha_vantage':
            return self.download_alpha_vantage(ticker, start_date, end_date)
        elif source == 'iex_cloud':
            return self.download_iex_cloud(ticker, start_date, end_date)
        elif source == 'finnhub':
            return self.download_finnhub(ticker, start_date, end_date)
        else:
            logger.error(f"Unknown source: {source}")
            return None

class MultiSourceGUI:
    """GUI for multi-source data download"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multi-Source Historical Data Downloader")
        self.root.geometry("800x700")
        
        self.downloader = MultiSourceDownloader()
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = tk.Label(self.root, text="🆓 Multi-Source Historical Data Downloader", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=15)
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Download historical stock data from multiple free sources\n" +
                                  "Yahoo Finance (no key) | Alpha Vantage | IEX Cloud | Finnhub",
                             justify=tk.CENTER, font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # API Keys section
        api_frame = tk.LabelFrame(self.root, text="🔑 API Keys (Optional)", font=("Arial", 12, "bold"))
        api_frame.pack(pady=10, padx=20, fill=tk.X)
        
        api_button = tk.Button(api_frame, text="⚙️ Configure API Keys", 
                              command=self.configure_api_keys, bg="#e3f2fd")
        api_button.pack(pady=10)
        
        # Data source selection
        source_frame = tk.LabelFrame(self.root, text="📊 Data Source", font=("Arial", 12, "bold"))
        source_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.source_var = tk.StringVar(value="yahoo")
        
        sources = [
            ("Yahoo Finance (Free, No Key)", "yahoo"),
            ("Alpha Vantage (Free API Key)", "alpha_vantage"),
            ("IEX Cloud (Free Tier)", "iex_cloud"),
            ("Finnhub (Free Tier)", "finnhub")
        ]
        
        for text, value in sources:
            rb = tk.Radiobutton(source_frame, text=text, variable=self.source_var, 
                               value=value, font=("Arial", 10))
            rb.pack(anchor=tk.W, padx=20)
        
        # Ticker input
        ticker_frame = tk.LabelFrame(self.root, text="📈 Stock Ticker", font=("Arial", 12, "bold"))
        ticker_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(ticker_frame, text="Enter ticker symbol:").pack(pady=5)
        self.ticker_entry = tk.Entry(ticker_frame, width=30, font=("Arial", 12))
        self.ticker_entry.insert(0, "AAPL")
        self.ticker_entry.pack(pady=5)
        
        # Date range
        date_frame = tk.LabelFrame(self.root, text="📅 Date Range", font=("Arial", 12, "bold"))
        date_frame.pack(pady=10, padx=20, fill=tk.X)
        
        date_input_frame = tk.Frame(date_frame)
        date_input_frame.pack(pady=10)
        
        tk.Label(date_input_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.start_date_entry = tk.Entry(date_input_frame, width=15)
        self.start_date_entry.insert(0, "2020-01-01")
        self.start_date_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(date_input_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.end_date_entry = tk.Entry(date_input_frame, width=15)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=0, column=3, padx=5)
        
        # Download button
        download_btn = tk.Button(self.root, text="🚀 Download Historical Data", 
                                command=self.download_data, 
                                bg="#4caf50", fg="white", font=("Arial", 14, "bold"))
        download_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill=tk.X)
        
        # Status text
        status_frame = tk.LabelFrame(self.root, text="📋 Download Status", font=("Arial", 12, "bold"))
        status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=15, width=90, font=("Courier", 9))
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        save_btn = tk.Button(self.root, text="💾 Save Data", 
                            command=self.save_data, 
                            bg="#ff9800", fg="white", font=("Arial", 12))
        save_btn.pack(pady=10)
        
        self.downloaded_data = None
    
    def configure_api_keys(self):
        """Configure API keys"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API Keys Configuration")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="🔑 API Keys Configuration", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="Alpha Vantage (alphavantage.co):").pack(pady=5)
        alpha_entry = tk.Entry(dialog, width=50)
        alpha_entry.insert(0, self.downloader.api_keys.get('alpha_vantage', ''))
        alpha_entry.pack(pady=5)
        
        tk.Label(dialog, text="IEX Cloud (iexcloud.io):").pack(pady=5)
        iex_entry = tk.Entry(dialog, width=50)
        iex_entry.insert(0, self.downloader.api_keys.get('iex_cloud', ''))
        iex_entry.pack(pady=5)
        
        tk.Label(dialog, text="Finnhub (finnhub.io):").pack(pady=5)
        finnhub_entry = tk.Entry(dialog, width=50)
        finnhub_entry.insert(0, self.downloader.api_keys.get('finnhub', ''))
        finnhub_entry.pack(pady=5)
        
        def save_keys():
            self.downloader.api_keys['alpha_vantage'] = alpha_entry.get().strip()
            self.downloader.api_keys['iex_cloud'] = iex_entry.get().strip()
            self.downloader.api_keys['finnhub'] = finnhub_entry.get().strip()
            self.downloader.save_api_keys()
            messagebox.showinfo("Success", "API keys saved!")
            dialog.destroy()
        
        tk.Button(dialog, text="💾 Save Keys", command=save_keys, 
                 bg="#4caf50", fg="white").pack(pady=20)
    
    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def download_data(self):
        """Download data from selected source"""
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showerror("Error", "Please enter a ticker symbol")
            return
        
        source = self.source_var.get()
        start_date = self.start_date_entry.get().strip() or None
        end_date = self.end_date_entry.get().strip() or None
        
        self.progress.start()
        self.status_text.delete(1.0, tk.END)
        
        try:
            source_names = {
                'yahoo': 'Yahoo Finance',
                'alpha_vantage': 'Alpha Vantage',
                'iex_cloud': 'IEX Cloud',
                'finnhub': 'Finnhub'
            }
            
            self.log_status(f"🎯 Downloading {ticker} from {source_names[source]}...")
            if start_date or end_date:
                self.log_status(f"📅 Date range: {start_date or 'N/A'} to {end_date or 'N/A'}")
            
            self.downloaded_data = self.downloader.download_from_source(source, ticker, start_date, end_date)
            
            if self.downloaded_data is not None and not self.downloaded_data.empty:
                self.log_status(f"✅ Success! Downloaded {len(self.downloaded_data)} records")
                self.log_status(f"📊 Columns: {list(self.downloaded_data.columns)}")
                self.log_status(f"📅 Date range: {self.downloaded_data['<DATE>'].min()} to {self.downloaded_data['<DATE>'].max()}")
                self.log_status(f"💰 Price range: ${self.downloaded_data['<LOW>'].min():.2f} - ${self.downloaded_data['<HIGH>'].max():.2f}")
                self.log_status("\n💾 Click 'Save Data' to export to CSV")
            else:
                self.log_status(f"❌ Failed to download data for {ticker}")
                if source != 'yahoo':
                    self.log_status(f"💡 Try Yahoo Finance (no API key required)")
                else:
                    self.log_status(f"💡 Check ticker symbol or try a different date range")
            
        except Exception as e:
            self.log_status(f"❌ Error: {str(e)}")
        finally:
            self.progress.stop()
    
    def save_data(self):
        """Save downloaded data"""
        if self.downloaded_data is None:
            messagebox.showwarning("Warning", "No data to save. Please download data first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"historical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                self.downloaded_data.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Data saved to {filename}")
                self.log_status(f"\n💾 Data saved to: {filename}")
                self.log_status(f"📊 Total records: {len(self.downloaded_data)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                self.log_status(f"\n❌ Save error: {str(e)}")

def main():
    """Main function"""
    app = MultiSourceGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
