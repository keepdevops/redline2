#!/usr/bin/env python3
"""
Stooq GUI Downloader for REDLINE
Provides a GUI interface to access Stooq with manual authentication
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import requests
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
import threading
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StooqGUIDownloader:
    """GUI-based Stooq data downloader with manual authentication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stooq Data Downloader for REDLINE")
        self.root.geometry("800x600")
        
        # Session for maintaining authentication
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Data storage
        self.downloaded_data = {}
        self.output_dir = "data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Stooq Data Downloader", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Authentication Section
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="10")
        auth_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        auth_label = ttk.Label(auth_frame, text="Click the button below to open Stooq and authenticate:")
        auth_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.auth_button = ttk.Button(auth_frame, text="Open Stooq Website", 
                                     command=self.open_stooq_website)
        self.auth_button.grid(row=1, column=0, padx=(0, 10))
        
        self.test_auth_button = ttk.Button(auth_frame, text="Test Authentication", 
                                          command=self.test_authentication)
        self.test_auth_button.grid(row=1, column=1)
        
        self.auth_status = ttk.Label(auth_frame, text="Not authenticated", 
                                    foreground="red")
        self.auth_status.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Data Download Section
        download_frame = ttk.LabelFrame(main_frame, text="Data Download", padding="10")
        download_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Ticker input
        ttk.Label(download_frame, text="Ticker Symbols:").grid(row=0, column=0, sticky=tk.W)
        self.ticker_entry = ttk.Entry(download_frame, width=50)
        self.ticker_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0))
        self.ticker_entry.insert(0, "AAPL,MSFT,GOOGL,TSLA,AMZN")
        
        # Date range
        ttk.Label(download_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.start_date_entry = ttk.Entry(download_frame)
        self.start_date_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
        
        ttk.Label(download_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        self.end_date_entry = ttk.Entry(download_frame)
        self.end_date_entry.grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Download button
        self.download_button = ttk.Button(download_frame, text="Download Data", 
                                         command=self.start_download)
        self.download_button.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(download_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(download_frame, text="Ready to download")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Downloaded Data", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview for results
        columns = ('Ticker', 'Records', 'Date Range', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for results
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.open_redline_button = ttk.Button(button_frame, text="Open REDLINE", 
                                             command=self.open_redline)
        self.open_redline_button.grid(row=0, column=0, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="Export to REDLINE Format", 
                                       command=self.export_to_redline)
        self.export_button.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Results", 
                                      command=self.clear_results)
        self.clear_button.grid(row=0, column=2)
    
    def open_stooq_website(self):
        """Open Stooq website for manual authentication"""
        stooq_url = "https://stooq.com/db/h/"
        webbrowser.open(stooq_url)
        messagebox.showinfo("Authentication", 
                           "Stooq website opened. Please:\n"
                           "1. Log in to your Stooq account\n"
                           "2. Complete any 2FA if required\n"
                           "3. Click 'Test Authentication' when ready")
    
    def test_authentication(self):
        """Test if we can access Stooq data"""
        try:
            # Try to access a simple Stooq page
            response = self.session.get("https://stooq.com/q/d/l/?s=AAPL&i=d", timeout=10)
            
            if response.status_code == 200 and len(response.text) > 100:
                self.auth_status.config(text="Authentication successful!", foreground="green")
                messagebox.showinfo("Success", "Authentication test passed! You can now download data.")
                return True
            else:
                self.auth_status.config(text="Authentication failed", foreground="red")
                messagebox.showerror("Error", "Authentication failed. Please check your login and try again.")
                return False
                
        except Exception as e:
            self.auth_status.config(text="Connection error", foreground="red")
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            return False
    
    def start_download(self):
        """Start downloading data in a separate thread"""
        if self.auth_status.cget("text") != "Authentication successful!":
            messagebox.showerror("Error", "Please authenticate first!")
            return
        
        # Get tickers from input
        tickers_text = self.ticker_entry.get().strip()
        if not tickers_text:
            messagebox.showerror("Error", "Please enter ticker symbols!")
            return
        
        tickers = [t.strip().upper() for t in tickers_text.split(',')]
        
        # Get date range
        try:
            start_date = datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format!")
            return
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_data, args=(tickers, start_date, end_date))
        thread.daemon = True
        thread.start()
    
    def download_data(self, tickers, start_date, end_date):
        """Download data for multiple tickers"""
        total_tickers = len(tickers)
        
        for i, ticker in enumerate(tickers):
            try:
                # Update status
                self.root.after(0, lambda t=ticker: self.status_label.config(text=f"Downloading {t}..."))
                
                # Download data
                df = self.download_ticker_data(ticker, start_date, end_date)
                
                if df is not None and not df.empty:
                    # Store data
                    self.downloaded_data[ticker] = df
                    
                    # Save to file
                    filename = f"{ticker}_stooq_data.csv"
                    filepath = os.path.join(self.output_dir, filename)
                    df.to_csv(filepath, index=False)
                    
                    # Update results
                    date_range = f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}"
                    self.root.after(0, lambda t=ticker, r=len(df), d=date_range: 
                                  self.results_tree.insert('', 'end', values=(t, r, d, "Success")))
                else:
                    self.root.after(0, lambda t=ticker: 
                                  self.results_tree.insert('', 'end', values=(t, 0, "N/A", "Failed")))
                
                # Update progress
                progress = (i + 1) / total_tickers * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error downloading {ticker}: {str(e)}")
                self.root.after(0, lambda t=ticker, e=str(e): 
                              self.results_tree.insert('', 'end', values=(t, 0, "N/A", f"Error: {e}")))
        
        # Update final status
        self.root.after(0, lambda: self.status_label.config(text="Download complete!"))
    
    def download_ticker_data(self, ticker, start_date, end_date):
        """Download data for a single ticker"""
        try:
            # Construct Stooq URL
            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")
            url = f"https://stooq.com/q/d/l/?s={ticker}&i=d&d1={start_str}&d2={end_str}"
            
            logger.info(f"Downloading {ticker} from {url}")
            
            # Download data
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if len(response.text.strip()) < 100:
                logger.warning(f"No data returned for {ticker}")
                return None
            
            # Parse CSV data
            from io import StringIO
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            if df.empty:
                logger.warning(f"Empty data returned for {ticker}")
                return None
            
            # Standardize to REDLINE format
            df = self._standardize_stooq_columns(df, ticker)
            
            logger.info(f"Successfully downloaded {len(df)} records for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None
    
    def _standardize_stooq_columns(self, df, ticker):
        """Standardize Stooq data columns to match REDLINE format"""
        df = df.copy()
        df['ticker'] = ticker
        
        # Map Stooq columns to REDLINE schema
        column_mapping = {
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low', 
            'Close': 'close',
            'Volume': 'vol'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add missing columns
        required_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns
        df = df[required_columns]
        df['format'] = 'stooq_gui_download'
        
        return df
    
    def open_redline(self):
        """Open REDLINE application"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "main.py"])
            messagebox.showinfo("REDLINE", "REDLINE application started!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start REDLINE: {str(e)}")
    
    def export_to_redline(self):
        """Export all downloaded data to a combined REDLINE-compatible file"""
        if not self.downloaded_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        try:
            # Combine all data
            combined_df = pd.concat(self.downloaded_data.values(), ignore_index=True)
            
            # Save combined file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stooq_combined_data_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)
            combined_df.to_csv(filepath, index=False)
            
            messagebox.showinfo("Export Complete", 
                              f"Combined data exported to:\n{filepath}\n\n"
                              f"Total records: {len(combined_df)}\n"
                              f"Tickers: {', '.join(self.downloaded_data.keys())}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.downloaded_data.clear()
        self.progress_var.set(0)
        self.status_label.config(text="Ready to download")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = StooqGUIDownloader()
    app.run()

if __name__ == "__main__":
    main()
