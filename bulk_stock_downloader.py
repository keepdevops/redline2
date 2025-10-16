#!/usr/bin/env python3
"""
Bulk Stock Data Downloader
Downloads historical data for multiple stocks at once
"""

import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulkStockDownloader:
    """Download historical data for multiple stocks"""
    
    def __init__(self):
        # Popular stock lists
        self.stock_lists = {
            'SP500': self.get_sp500_tickers(),
            'NASDAQ100': self.get_nasdaq100_tickers(),
            'DOW30': self.get_dow30_tickers(),
            'FAANG': ['AAPL', 'AMZN', 'NFLX', 'GOOGL', 'META'],
            'TECH_GIANTS': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX'],
            'BANKING': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC'],
            'HEALTHCARE': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR'],
            'ENERGY': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO'],
            'CUSTOM': []
        }

    def get_sp500_tickers(self) -> List[str]:
        """Get S&P 500 ticker list"""
        try:
            # Try to get from Wikipedia
            import requests
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url, timeout=10)
            df = pd.read_html(response.text)[0]
            return df['Symbol'].tolist()[:50]  # Limit to first 50 for demo
        except:
            # Fallback list of major S&P 500 stocks
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 
                   'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA', 'PFE', 'ABBV', 'CVX', 
                   'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'WMT', 'DHR', 'ABT', 
                   'ACN', 'VZ', 'NFLX', 'ADBE', 'TXN', 'NKE', 'CRM', 'RTX', 'QCOM',
                   'PM', 'T', 'LIN', 'UNP', 'SPGI', 'HON', 'IBM', 'AMAT', 'GE', 'LOW',
                   'CAT', 'AXP', 'AMD', 'INTU']

    def get_nasdaq100_tickers(self) -> List[str]:
        """Get NASDAQ 100 ticker list"""
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 
               'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'PYPL', 'CMCSA', 'TXN', 'QCOM',
               'AMAT', 'CSCO', 'AVGO', 'INTU', 'BKNG', 'ISRG', 'GILD', 'ADP', 'VRTX',
               'REGN', 'MDLZ', 'FISV', 'CHTR', 'ATVI', 'ILMN', 'BIIB', 'CTSH', 'EXC',
               'WBA', 'SBUX', 'KHC', 'CSX', 'TMUS', 'LRCX', 'AMGN', 'MRNA', 'XEL',
               'NFLX', 'GOOGL', 'AMZN', 'AAPL', 'MSFT', 'META', 'TSLA', 'NVDA']

    def get_dow30_tickers(self) -> List[str]:
        """Get Dow 30 ticker list"""
        return ['AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'CAT', 'AMGN', 'CRM', 'MCD', 'V',
               'AXP', 'TRV', 'JPM', 'JNJ', 'PG', 'WMT', 'NKE', 'IBM', 'CVX', 'MRK',
               'BA', 'KO', 'DIS', 'DOW', 'CSCO', 'VZ', 'INTC', 'WBA', 'MMM', 'HON']

    def convert_to_stooq_format(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
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
            logger.error(f"Error converting {ticker} to Stooq format: {str(e)}")
            return pd.DataFrame()

    def download_single_stock(self, ticker: str, start_date: str = None, end_date: str = None, period: str = "2y") -> Optional[pd.DataFrame]:
        """Download data for a single stock"""
        try:
            stock = yf.Ticker(ticker)
            
            if start_date and end_date:
                data = stock.history(start=start_date, end=end_date)
            else:
                data = stock.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            return self.convert_to_stooq_format(data, ticker)
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None

    def download_multiple_stocks(self, tickers: List[str], start_date: str = None, end_date: str = None, 
                               period: str = "2y", max_workers: int = 5, delay: float = 0.1) -> Dict[str, pd.DataFrame]:
        """Download data for multiple stocks with threading"""
        results = {}
        failed_tickers = []
        
        def download_worker(ticker):
            """Worker function for downloading single stock"""
            try:
                time.sleep(delay)  # Rate limiting
                data = self.download_single_stock(ticker, start_date, end_date, period)
                return ticker, data
            except Exception as e:
                logger.error(f"Worker error for {ticker}: {str(e)}")
                return ticker, None
        
        logger.info(f"Starting bulk download for {len(tickers)} stocks...")
        logger.info(f"Using {max_workers} threads with {delay}s delay between requests")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_ticker = {executor.submit(download_worker, ticker): ticker for ticker in tickers}
            
            # Process completed downloads
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    ticker, data = future.result()
                    if data is not None and not data.empty:
                        results[ticker] = data
                        logger.info(f"✅ Downloaded {ticker}: {len(data)} records")
                    else:
                        failed_tickers.append(ticker)
                        logger.warning(f"❌ Failed {ticker}")
                except Exception as e:
                    failed_tickers.append(ticker)
                    logger.error(f"❌ Error processing {ticker}: {str(e)}")
        
        logger.info(f"Bulk download complete: {len(results)} successful, {len(failed_tickers)} failed")
        if failed_tickers:
            logger.warning(f"Failed tickers: {failed_tickers[:10]}...")  # Show first 10
        
        return results

class BulkDownloaderGUI:
    """GUI for bulk stock download"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bulk Stock Data Downloader")
        self.root.geometry("900x800")
        
        self.downloader = BulkStockDownloader()
        self.results = {}
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = tk.Label(self.root, text="📊 Bulk Stock Data Downloader", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=15)
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Download historical data for multiple stocks at once\n" +
                                  "Perfect for building comprehensive datasets",
                             justify=tk.CENTER, font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # Stock list selection
        list_frame = tk.LabelFrame(self.root, text="📈 Stock Lists", font=("Arial", 12, "bold"))
        list_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.list_var = tk.StringVar(value="TECH_GIANTS")
        
        stock_lists = [
            ("FAANG Stocks (5 stocks)", "FAANG"),
            ("Tech Giants (8 stocks)", "TECH_GIANTS"),
            ("Dow 30 (30 stocks)", "DOW30"),
            ("S&P 500 (50 stocks)", "SP500"),
            ("NASDAQ 100 (50 stocks)", "NASDAQ100"),
            ("Banking Sector (8 stocks)", "BANKING"),
            ("Healthcare Sector (8 stocks)", "HEALTHCARE"),
            ("Energy Sector (8 stocks)", "ENERGY"),
            ("Custom List", "CUSTOM")
        ]
        
        for text, value in stock_lists:
            rb = tk.Radiobutton(list_frame, text=text, variable=self.list_var, 
                               value=value, font=("Arial", 10))
            rb.pack(anchor=tk.W, padx=20)
        
        # Custom ticker input
        custom_frame = tk.LabelFrame(self.root, text="✏️ Custom Ticker List", font=("Arial", 12, "bold"))
        custom_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(custom_frame, text="Enter ticker symbols (comma-separated):").pack(pady=5)
        self.custom_entry = tk.Entry(custom_frame, width=80, font=("Arial", 10))
        self.custom_entry.insert(0, "AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,NFLX")
        self.custom_entry.pack(pady=5)
        
        # Date range and settings
        settings_frame = tk.LabelFrame(self.root, text="⚙️ Download Settings", font=("Arial", 12, "bold"))
        settings_frame.pack(pady=10, padx=20, fill=tk.X)
        
        settings_grid = tk.Frame(settings_frame)
        settings_grid.pack(pady=10)
        
        # Date range
        tk.Label(settings_grid, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.start_date_entry = tk.Entry(settings_grid, width=15)
        self.start_date_entry.insert(0, "2020-01-01")
        self.start_date_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(settings_grid, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.end_date_entry = tk.Entry(settings_grid, width=15)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=0, column=3, padx=5)
        
        # Threading settings
        tk.Label(settings_grid, text="Max Threads:").grid(row=1, column=0, padx=5)
        self.threads_entry = tk.Entry(settings_grid, width=10)
        self.threads_entry.insert(0, "5")
        self.threads_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(settings_grid, text="Delay (seconds):").grid(row=1, column=2, padx=5)
        self.delay_entry = tk.Entry(settings_grid, width=10)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.grid(row=1, column=3, padx=5)
        
        # Download button
        download_btn = tk.Button(self.root, text="🚀 Start Bulk Download", 
                                command=self.start_bulk_download, 
                                bg="#4caf50", fg="white", font=("Arial", 14, "bold"))
        download_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill=tk.X)
        
        # Progress label
        self.progress_label = tk.Label(self.root, text="Ready to download", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        # Status text
        status_frame = tk.LabelFrame(self.root, text="📋 Download Status", font=("Arial", 12, "bold"))
        status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=15, width=100, font=("Courier", 9))
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        save_btn = tk.Button(self.root, text="💾 Save All Data", 
                            command=self.save_all_data, 
                            bg="#ff9800", fg="white", font=("Arial", 12))
        save_btn.pack(pady=10)
    
    def get_selected_tickers(self) -> List[str]:
        """Get the list of tickers to download"""
        selected_list = self.list_var.get()
        
        if selected_list == "CUSTOM":
            custom_text = self.custom_entry.get().strip()
            if not custom_text:
                return []
            return [ticker.strip().upper() for ticker in custom_text.split(',') if ticker.strip()]
        else:
            return self.downloader.stock_lists.get(selected_list, [])
    
    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def start_bulk_download(self):
        """Start bulk download in a separate thread"""
        tickers = self.get_selected_tickers()
        if not tickers:
            messagebox.showerror("Error", "No tickers selected. Please choose a stock list or enter custom tickers.")
            return
        
        # Get settings
        start_date = self.start_date_entry.get().strip() or None
        end_date = self.end_date_entry.get().strip() or None
        max_workers = int(self.threads_entry.get() or 5)
        delay = float(self.delay_entry.get() or 0.1)
        
        # Start download in background thread
        self.progress.start()
        self.progress_label.config(text=f"Downloading {len(tickers)} stocks...")
        self.status_text.delete(1.0, tk.END)
        
        # Run download in separate thread
        thread = threading.Thread(target=self.bulk_download_worker, 
                                args=(tickers, start_date, end_date, max_workers, delay))
        thread.daemon = True
        thread.start()
    
    def bulk_download_worker(self, tickers, start_date, end_date, max_workers, delay):
        """Worker function for bulk download"""
        try:
            self.log_status(f"🎯 Starting bulk download for {len(tickers)} stocks...")
            self.log_status(f"📊 Tickers: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
            self.log_status(f"⚙️ Settings: {max_workers} threads, {delay}s delay")
            
            self.results = self.downloader.download_multiple_stocks(
                tickers, start_date, end_date, "2y", max_workers, delay
            )
            
            if self.results:
                total_records = sum(len(data) for data in self.results.values())
                self.log_status(f"\n🎉 Bulk download complete!")
                self.log_status(f"✅ Successfully downloaded: {len(self.results)} stocks")
                self.log_status(f"❌ Failed: {len(tickers) - len(self.results)} stocks")
                self.log_status(f"📊 Total records: {total_records:,}")
                self.log_status(f"\n💾 Click 'Save All Data' to export to CSV")
            else:
                self.log_status(f"\n❌ No data downloaded. Check your internet connection.")
            
        except Exception as e:
            self.log_status(f"\n❌ Bulk download error: {str(e)}")
        finally:
            self.progress.stop()
            self.progress_label.config(text="Download complete")
    
    def save_all_data(self):
        """Save all downloaded data"""
        if not self.results:
            messagebox.showwarning("Warning", "No data to save. Please download data first.")
            return
        
        # Ask for directory
        directory = filedialog.askdirectory(title="Select directory to save stock data")
        if not directory:
            return
        
        try:
            saved_files = []
            for ticker, data in self.results.items():
                filename = os.path.join(directory, f"{ticker}_historical_data.csv")
                data.to_csv(filename, index=False)
                saved_files.append(filename)
            
            # Also save combined file
            all_data = pd.concat(list(self.results.values()), ignore_index=True)
            combined_filename = os.path.join(directory, f"all_stocks_historical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            all_data.to_csv(combined_filename, index=False)
            
            messagebox.showinfo("Success", f"Saved {len(saved_files)} individual files + 1 combined file to:\n{directory}")
            self.log_status(f"\n💾 Saved {len(saved_files)} individual files + 1 combined file")
            self.log_status(f"📁 Directory: {directory}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            self.log_status(f"\n❌ Save error: {str(e)}")

def main():
    """Main function"""
    app = BulkDownloaderGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
