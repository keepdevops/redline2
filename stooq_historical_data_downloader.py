#!/usr/bin/env python3
"""
Specialized Stooq Historical Data Downloader
Focuses specifically on historical data with multiple fallback methods
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
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StooqHistoricalDownloader:
    """Specialized downloader for Stooq historical data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Historical data specific URLs
        self.historical_urls = {
            'main': 'https://stooq.com/historical/',
            'direct': 'https://stooq.com/q/d/',
            'daily': 'https://stooq.com/q/d/l/',
            'search': 'https://stooq.com/s/'
        }

    def download_historical_data(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Download historical data for a ticker using multiple methods
        """
        try:
            # Method 1: Try direct historical data URL
            data = self._try_historical_url(ticker, start_date, end_date)
            if data is not None and not data.empty:
                return data
            
            # Method 2: Try CSV download URL
            data = self._try_csv_download(ticker, start_date, end_date)
            if data is not None and not data.empty:
                return data
            
            # Method 3: Try alternative endpoints
            data = self._try_alternative_endpoints(ticker, start_date, end_date)
            if data is not None and not data.empty:
                return data
            
            logger.warning(f"All methods failed for {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading historical data for {ticker}: {str(e)}")
            return None

    def _try_historical_url(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Try the main historical data URL"""
        try:
            # Build URL with parameters
            params = {'s': ticker}
            if start_date:
                params['start'] = start_date
            if end_date:
                params['end'] = end_date
            
            url = f"{self.historical_urls['main']}?{urllib.parse.urlencode(params)}"
            logger.info(f"Trying historical URL: {url}")
            
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return self._parse_historical_response(response, ticker)
            
        except Exception as e:
            logger.warning(f"Historical URL failed: {str(e)}")
        
        return None

    def _try_csv_download(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Try CSV download endpoints"""
        try:
            # Multiple CSV download URLs to try
            csv_urls = [
                f"{self.historical_urls['direct']}?s={ticker}",
                f"{self.historical_urls['direct']}?s={ticker}.US",
                f"{self.historical_urls['daily']}?s={ticker}&i=d",
                f"{self.historical_urls['daily']}?s={ticker}.US&i=d",
                f"http://stooq.com/q/d/?s={ticker}",
                f"http://stooq.com/q/d/l/?s={ticker}&i=d",
            ]
            
            for url in csv_urls:
                try:
                    logger.info(f"Trying CSV URL: {url}")
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200 and 'text/csv' in response.headers.get('content-type', ''):
                        data = self._parse_csv_response(response, ticker)
                        if data is not None and not data.empty:
                            return data
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"CSV URL {url} failed: {str(e)}")
                    continue
            
        except Exception as e:
            logger.warning(f"CSV download failed: {str(e)}")
        
        return None

    def _try_alternative_endpoints(self, ticker: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Try alternative endpoints"""
        try:
            # Alternative endpoints
            alt_urls = [
                f"https://stooq.com/s/?s={ticker}",
                f"https://stooq.com/q/h/?s={ticker}",
                f"https://stooq.com/q/h/?s={ticker}.US",
            ]
            
            for url in alt_urls:
                try:
                    logger.info(f"Trying alternative URL: {url}")
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = self._parse_alternative_response(response, ticker)
                        if data is not None and not data.empty:
                            return data
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Alternative URL {url} failed: {str(e)}")
                    continue
            
        except Exception as e:
            logger.warning(f"Alternative endpoints failed: {str(e)}")
        
        return None

    def _parse_historical_response(self, response: requests.Response, ticker: str) -> Optional[pd.DataFrame]:
        """Parse historical data response"""
        try:
            # Look for CSV data in the response
            content = response.text
            
            # Check if response contains CSV data
            if 'Date,Open,High,Low,Close,Volume' in content or '<TICKER>' in content:
                from io import StringIO
                csv_data = StringIO(content)
                df = pd.read_csv(csv_data)
                
                if not df.empty:
                    return self._convert_to_stooq_format(df, ticker)
            
        except Exception as e:
            logger.warning(f"Error parsing historical response: {str(e)}")
        
        return None

    def _parse_csv_response(self, response: requests.Response, ticker: str) -> Optional[pd.DataFrame]:
        """Parse CSV response"""
        try:
            from io import StringIO
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            if not df.empty:
                return self._convert_to_stooq_format(df, ticker)
                
        except Exception as e:
            logger.warning(f"Error parsing CSV response: {str(e)}")
        
        return None

    def _parse_alternative_response(self, response: requests.Response, ticker: str) -> Optional[pd.DataFrame]:
        """Parse alternative response"""
        try:
            # Try to extract CSV data from HTML response
            content = response.text
            
            # Look for data tables or CSV links
            if 'csv' in content.lower() or 'download' in content.lower():
                # Try to find CSV download link
                import re
                csv_links = re.findall(r'href="([^"]*\.csv[^"]*)"', content)
                
                for link in csv_links:
                    try:
                        if not link.startswith('http'):
                            link = f"https://stooq.com{link}"
                        
                        csv_response = self.session.get(link, timeout=10)
                        if csv_response.status_code == 200:
                            return self._parse_csv_response(csv_response, ticker)
                    except:
                        continue
            
        except Exception as e:
            logger.warning(f"Error parsing alternative response: {str(e)}")
        
        return None

    def _convert_to_stooq_format(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Convert DataFrame to Stooq format"""
        try:
            # Handle different input formats
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['<DATE>'] = df['Date'].dt.strftime('%Y%m%d')
            elif '<DATE>' not in df.columns:
                df['<DATE>'] = datetime.now().strftime('%Y%m%d')
            
            # Map columns to Stooq format
            column_mapping = {
                'Open': '<OPEN>',
                'High': '<HIGH>',
                'Low': '<LOW>',
                'Close': '<CLOSE>',
                'Volume': '<VOL>',
                'Vol': '<VOL>'
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

    def open_stooq_historical_page(self, ticker: str):
        """Open Stooq historical page in browser"""
        url = f"https://stooq.com/q/h/?s={ticker}"
        webbrowser.open(url)

    def download_multiple_historical(self, tickers: List[str], delay: float = 3.0) -> Dict[str, pd.DataFrame]:
        """Download historical data for multiple tickers"""
        results = {}
        
        for ticker in tickers:
            logger.info(f"Downloading historical data for {ticker}...")
            data = self.download_historical_data(ticker)
            
            if data is not None:
                results[ticker] = data
                logger.info(f"Successfully downloaded {len(data)} historical records for {ticker}")
            else:
                logger.warning(f"Failed to download historical data for {ticker}")
            
            # Add delay between requests
            if delay > 0:
                time.sleep(delay)
        
        return results

class StooqHistoricalGUI:
    """GUI for Stooq historical data download"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stooq Historical Data Downloader")
        self.root.geometry("700x600")
        
        self.downloader = StooqHistoricalDownloader()
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = tk.Label(self.root, text="📊 Stooq Historical Data Downloader", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=15)
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Specialized for historical data with multiple fallback methods\n" +
                                  "Automatically tries different Stooq endpoints",
                             justify=tk.CENTER, font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # Ticker input section
        ticker_frame = tk.LabelFrame(self.root, text="📈 Stock Tickers", font=("Arial", 12, "bold"))
        ticker_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(ticker_frame, text="Enter ticker symbols (comma-separated):").pack(pady=5)
        self.ticker_entry = tk.Entry(ticker_frame, width=60, font=("Arial", 11))
        self.ticker_entry.insert(0, "AAPL,MSFT,GOOGL,AMZN,TSLA")
        self.ticker_entry.pack(pady=5)
        
        # Quick select buttons
        quick_frame = tk.Frame(ticker_frame)
        quick_frame.pack(pady=5)
        
        tk.Label(quick_frame, text="Quick select popular stocks:").pack()
        quick_buttons = tk.Frame(quick_frame)
        quick_buttons.pack()
        
        popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        for i, ticker in enumerate(popular_stocks):
            btn = tk.Button(quick_buttons, text=ticker, width=8,
                           command=lambda t=ticker: self.select_ticker(t),
                           bg="#e3f2fd")
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
        
        # Date range section
        date_frame = tk.LabelFrame(self.root, text="📅 Date Range (Optional)", font=("Arial", 12, "bold"))
        date_frame.pack(pady=10, padx=20, fill=tk.X)
        
        date_input_frame = tk.Frame(date_frame)
        date_input_frame.pack(pady=5)
        
        tk.Label(date_input_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.start_date_entry = tk.Entry(date_input_frame, width=15)
        self.start_date_entry.insert(0, "2020-01-01")
        self.start_date_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(date_input_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.end_date_entry = tk.Entry(date_input_frame, width=15)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=0, column=3, padx=5)
        
        # Action buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        # Download button
        download_btn = tk.Button(button_frame, text="🚀 Download Historical Data", 
                                command=self.download_historical_data, 
                                bg="#4caf50", fg="white", font=("Arial", 12, "bold"))
        download_btn.pack(side=tk.LEFT, padx=10)
        
        # Open browser button
        browser_btn = tk.Button(button_frame, text="🌐 Open Stooq in Browser", 
                               command=self.open_browser, 
                               bg="#2196f3", fg="white", font=("Arial", 12))
        browser_btn.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill=tk.X)
        
        # Status text
        status_frame = tk.LabelFrame(self.root, text="📋 Download Status", font=("Arial", 12, "bold"))
        status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=12, width=80, font=("Courier", 9))
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        save_btn = tk.Button(self.root, text="💾 Save Historical Data", 
                            command=self.save_results, 
                            bg="#ff9800", fg="white", font=("Arial", 12))
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
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def download_historical_data(self):
        """Download historical data"""
        tickers_text = self.ticker_entry.get().strip()
        if not tickers_text:
            messagebox.showerror("Error", "Please enter ticker symbols")
            return
        
        tickers = [t.strip().upper() for t in tickers_text.split(',') if t.strip()]
        start_date = self.start_date_entry.get().strip() or None
        end_date = self.end_date_entry.get().strip() or None
        
        self.progress.start()
        self.status_text.delete(1.0, tk.END)
        
        try:
            self.log_status(f"🎯 Starting historical data download for: {', '.join(tickers)}")
            if start_date or end_date:
                self.log_status(f"📅 Date range: {start_date or 'N/A'} to {end_date or 'N/A'}")
            
            self.log_status("🔄 Trying multiple Stooq endpoints...")
            
            self.results = {}
            for ticker in tickers:
                self.log_status(f"\n📊 Processing {ticker}...")
                data = self.downloader.download_historical_data(ticker, start_date, end_date)
                
                if data is not None and not data.empty:
                    self.results[ticker] = data
                    self.log_status(f"✅ {ticker}: {len(data)} historical records downloaded")
                else:
                    self.log_status(f"❌ {ticker}: Failed to download (Stooq may be blocking automated access)")
                    self.log_status(f"   💡 Try manual download: Open browser button above")
                
                time.sleep(2)  # Rate limiting
            
            if self.results:
                self.log_status(f"\n🎉 Successfully downloaded {len(self.results)} tickers!")
                total_records = sum(len(data) for data in self.results.values())
                self.log_status(f"📈 Total historical records: {total_records}")
            else:
                self.log_status(f"\n❌ No data downloaded. Stooq is likely blocking automated access.")
                self.log_status(f"💡 Recommendation: Use the 'Open Stooq in Browser' button for manual download")
            
        except Exception as e:
            self.log_status(f"\n❌ Error: {str(e)}")
        finally:
            self.progress.stop()
    
    def open_browser(self):
        """Open Stooq historical page in browser"""
        ticker = self.ticker_entry.get().strip().split(',')[0].strip().upper()
        if not ticker:
            ticker = "AAPL"
        
        self.downloader.open_stooq_historical_page(ticker)
        self.log_status(f"🌐 Opened Stooq historical page for {ticker} in browser")
        self.log_status("💡 Manual steps:")
        self.log_status("   1. Log in to your Stooq account")
        self.log_status("   2. Complete 2FA if required")
        self.log_status("   3. Navigate to historical data")
        self.log_status("   4. Download CSV files manually")
    
    def save_results(self):
        """Save downloaded results"""
        if not self.results:
            messagebox.showwarning("Warning", "No data to save. Please download data first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"stooq_historical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
                    
                    messagebox.showinfo("Success", f"Historical data saved to {filename}")
                    self.log_status(f"\n💾 Historical data saved to: {filename}")
                    self.log_status(f"📊 Total records: {len(combined_df)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                self.log_status(f"\n❌ Save error: {str(e)}")

def main():
    """Main function"""
    app = StooqHistoricalGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
