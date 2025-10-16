#!/usr/bin/env python3
"""
Enhanced Stooq downloader using Chartoasis direct link approach
Based on: https://www.chartoasis.com/free-data-download-stooq-help-cop3/
"""

import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartoasisStooqDownloader:
    """Download Stooq data using Chartoasis direct link approach"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Chartoasis-style direct URLs for popular stocks
        self.direct_links = {
            'AAPL': 'http://stooq.com/q/d/?s=AAPL',
            'MSFT': 'http://stooq.com/q/d/?s=MSFT', 
            'GOOGL': 'http://stooq.com/q/d/?s=GOOGL',
            'AMZN': 'http://stooq.com/q/d/?s=AMZN',
            'TSLA': 'http://stooq.com/q/d/?s=TSLA',
            'META': 'http://stooq.com/q/d/?s=META',
            'NVDA': 'http://stooq.com/q/d/?s=NVDA',
            'NFLX': 'http://stooq.com/q/d/?s=NFLX'
        }

    def download_ticker_via_chartoasis_link(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Download ticker data using Chartoasis direct link approach
        """
        try:
            # Try the direct Chartoasis-style link first
            if ticker in self.direct_links:
                url = self.direct_links[ticker]
                logger.info(f"Trying Chartoasis direct link for {ticker}: {url}")
                
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    return self._parse_stooq_response(response, ticker)
            
            # Fallback to multiple URL formats
            urls_to_try = [
                f"http://stooq.com/q/d/?s={ticker}",
                f"http://stooq.com/q/d/?s={ticker}.US",
                f"http://stooq.com/q/d/l/?s={ticker}&i=d",
                f"http://stooq.com/q/d/l/?s={ticker}.US&i=d",
                f"https://stooq.com/q/d/?s={ticker}",
                f"https://stooq.com/q/d/?s={ticker}.US",
                f"https://stooq.com/q/d/l/?s={ticker}&i=d",
                f"https://stooq.com/q/d/l/?s={ticker}.US&i=d",
            ]
            
            for url in urls_to_try:
                try:
                    logger.info(f"Trying URL: {url}")
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = self._parse_stooq_response(response, ticker)
                        if data is not None and not data.empty:
                            return data
                    
                    # Add delay between requests
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Failed to access {url}: {str(e)}")
                    continue
            
            logger.error(f"All URL attempts failed for {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None

    def _parse_stooq_response(self, response: requests.Response, ticker: str) -> Optional[pd.DataFrame]:
        """Parse Stooq response and convert to DataFrame"""
        try:
            # Try to parse as CSV
            from io import StringIO
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            if df.empty:
                return None
            
            # Convert to Stooq format
            return self._convert_to_stooq_format(df, ticker)
            
        except Exception as e:
            logger.error(f"Error parsing response for {ticker}: {str(e)}")
            return None

    def _convert_to_stooq_format(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Convert DataFrame to Stooq format"""
        try:
            # Handle different input formats
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            elif '<DATE>' in df.columns:
                # Already in Stooq format
                pass
            else:
                # Try to find date column
                date_cols = [col for col in df.columns if 'date' in col.lower()]
                if date_cols:
                    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                    df['<DATE>'] = df[date_cols[0]].dt.strftime('%Y%m%d')
                else:
                    df['<DATE>'] = datetime.now().strftime('%Y%m%d')
            
            # Map columns to Stooq format
            column_mapping = {
                'Open': '<OPEN>',
                'High': '<HIGH>',
                'Low': '<LOW>',
                'Close': '<CLOSE>',
                'Volume': '<VOL>',
                '<OPEN>': '<OPEN>',
                '<HIGH>': '<HIGH>',
                '<LOW>': '<LOW>',
                '<CLOSE>': '<CLOSE>',
                '<VOL>': '<VOL>'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and new_col not in df.columns:
                    df[new_col] = df[old_col]
            
            # Ensure required columns exist
            df['<TICKER>'] = ticker
            if '<TIME>' not in df.columns:
                df['<TIME>'] = '000000'
            
            # Select Stooq columns
            stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            available_cols = [col for col in stooq_columns if col in df.columns]
            df_stooq = df[available_cols].copy()
            
            # Clean numeric data
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                if col in df_stooq.columns:
                    df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
            
            # Remove rows with invalid data
            df_stooq = df_stooq.dropna(subset=['<TICKER>', '<DATE>'])
            
            return df_stooq
            
        except Exception as e:
            logger.error(f"Error converting to Stooq format: {str(e)}")
            return df

    def open_chartoasis_guide(self):
        """Open Chartoasis guide for manual reference"""
        webbrowser.open("https://www.chartoasis.com/free-data-download-stooq-help-cop3/")

    def download_multiple_tickers(self, tickers: List[str], delay: float = 2.0) -> Dict[str, pd.DataFrame]:
        """Download multiple tickers with delay"""
        results = {}
        
        for ticker in tickers:
            logger.info(f"Downloading {ticker}...")
            data = self.download_ticker_via_chartoasis_link(ticker)
            
            if data is not None:
                results[ticker] = data
                logger.info(f"Successfully downloaded {len(data)} records for {ticker}")
            else:
                logger.warning(f"Failed to download {ticker}")
            
            # Add delay between requests
            if delay > 0:
                time.sleep(delay)
        
        return results

class ChartoasisStooqGUI:
    """GUI for Chartoasis-style Stooq downloading"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chartoasis Stooq Downloader")
        self.root.geometry("600x500")
        
        self.downloader = ChartoasisStooqDownloader()
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = tk.Label(self.root, text="Chartoasis Stooq Downloader", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Uses Chartoasis direct link approach for Stooq data\n" +
                                  "More reliable than generic Stooq endpoints",
                             justify=tk.CENTER)
        desc_label.pack(pady=5)
        
        # Open Chartoasis Guide button
        guide_btn = tk.Button(self.root, text="📖 Open Chartoasis Guide", 
                             command=self.downloader.open_chartoasis_guide,
                             bg="#e1f5fe")
        guide_btn.pack(pady=10)
        
        # Ticker input
        ticker_frame = tk.Frame(self.root)
        ticker_frame.pack(pady=10)
        
        tk.Label(ticker_frame, text="Tickers (comma-separated):").pack()
        self.ticker_entry = tk.Entry(ticker_frame, width=50)
        self.ticker_entry.insert(0, "AAPL,MSFT,GOOGL,AMZN,TSLA")
        self.ticker_entry.pack()
        
        # Quick ticker buttons
        quick_frame = tk.Frame(self.root)
        quick_frame.pack(pady=5)
        
        tk.Label(quick_frame, text="Quick select:").pack()
        quick_buttons = tk.Frame(quick_frame)
        quick_buttons.pack()
        
        for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']:
            btn = tk.Button(quick_buttons, text=ticker, width=8,
                           command=lambda t=ticker: self.select_ticker(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Download button
        download_btn = tk.Button(self.root, text="🚀 Download via Chartoasis Links", 
                                command=self.download_data, bg="#4caf50", fg="white")
        download_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill=tk.X)
        
        # Status text
        self.status_text = tk.Text(self.root, height=15, width=70)
        self.status_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Save button
        save_btn = tk.Button(self.root, text="💾 Save Results", 
                            command=self.save_results, bg="#ff9800", fg="white")
        save_btn.pack(pady=10)
        
        self.results = {}
    
    def select_ticker(self, ticker):
        """Select a ticker"""
        current = self.ticker_entry.get()
        if current:
            self.ticker_entry.delete(0, tk.END)
            self.ticker_entry.insert(0, current + f",{ticker}")
        else:
            self.ticker_entry.insert(0, ticker)
    
    def log_status(self, message):
        """Log status message"""
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def download_data(self):
        """Download data using Chartoasis approach"""
        tickers_text = self.ticker_entry.get().strip()
        if not tickers_text:
            messagebox.showerror("Error", "Please enter ticker symbols")
            return
        
        tickers = [t.strip().upper() for t in tickers_text.split(',') if t.strip()]
        
        self.progress.start()
        self.status_text.delete(1.0, tk.END)
        
        try:
            self.log_status(f"Starting download for: {', '.join(tickers)}")
            self.log_status("Using Chartoasis direct link approach...")
            
            self.results = self.downloader.download_multiple_tickers(tickers, delay=2.0)
            
            if self.results:
                self.log_status(f"\n✅ Successfully downloaded {len(self.results)} tickers:")
                for ticker, data in self.results.items():
                    self.log_status(f"  - {ticker}: {len(data)} records")
            else:
                self.log_status("\n❌ No data downloaded. Stooq may be blocking automated access.")
                self.log_status("Try manual download using the Chartoasis guide.")
            
        except Exception as e:
            self.log_status(f"\n❌ Error: {str(e)}")
        finally:
            self.progress.stop()
    
    def save_results(self):
        """Save downloaded results"""
        if not self.results:
            messagebox.showwarning("Warning", "No data to save. Please download data first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"chartoasis_stooq_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                # Combine all ticker data
                all_data = []
                for ticker, data in self.results.items():
                    all_data.append(data)
                
                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    combined_df.to_csv(filename, index=False)
                    
                    messagebox.showinfo("Success", f"Data saved to {filename}")
                    self.log_status(f"\n💾 Data saved to: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                self.log_status(f"\n❌ Save error: {str(e)}")

def main():
    """Main function"""
    app = ChartoasisStooqGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
