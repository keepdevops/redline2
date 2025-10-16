#!/usr/bin/env python3
"""
Stooq Manual Downloader for REDLINE
Follows the Chartoasis.com guide for accessing Stooq data
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import sys
from datetime import datetime, timedelta
import pandas as pd

class StooqManualDownloader:
    """Manual Stooq downloader following Chartoasis guide"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stooq Manual Downloader - Following Chartoasis Guide")
        self.root.geometry("800x700")
        
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
        title_label = ttk.Label(main_frame, text="Stooq Manual Downloader", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions (Based on Chartoasis.com Guide)", padding="10")
        instructions_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        instructions_text = """This tool helps you download data from Stooq.com following the official guide:

METHOD 1 - Direct Links:
1. Use the direct links below for popular stocks
2. Click the link to open Stooq directly
3. Click "Dane historyczne" (Historical Data)
4. Set date range and click "Download data in .csv file"

METHOD 2 - Search by Name:
1. Click "Open Stooq Search" to open stooq.com
2. Search for your ticker (e.g., AAPL, MSFT)
3. Click on the result
4. Click "Dane historyczne" (Historical Data)
5. Download CSV file

METHOD 3 - Upload Downloaded Files:
1. Download CSV files manually from Stooq
2. Use "Process Downloaded Files" to convert to REDLINE format"""
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT)
        instructions_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Direct Links Section
        links_frame = ttk.LabelFrame(main_frame, text="Direct Links to Popular Stocks", padding="10")
        links_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create buttons for popular stocks
        popular_stocks = [
            ("AAPL", "Apple Inc.", "http://stooq.com/q/d/?s=AAPL"),
            ("MSFT", "Microsoft Corp.", "http://stooq.com/q/d/?s=MSFT"),
            ("GOOGL", "Alphabet Inc.", "http://stooq.com/q/d/?s=GOOGL"),
            ("TSLA", "Tesla Inc.", "http://stooq.com/q/d/?s=TSLA"),
            ("AMZN", "Amazon.com Inc.", "http://stooq.com/q/d/?s=AMZN"),
            ("META", "Meta Platforms Inc.", "http://stooq.com/q/d/?s=META"),
            ("NVDA", "NVIDIA Corp.", "http://stooq.com/q/d/?s=NVDA"),
            ("SPY", "SPDR S&P 500 ETF", "http://stooq.com/q/d/?s=SPY"),
        ]
        
        for i, (ticker, name, url) in enumerate(popular_stocks):
            row = i // 2
            col = (i % 2) * 2
            
            stock_label = ttk.Label(links_frame, text=f"{ticker} - {name}")
            stock_label.grid(row=row, column=col, sticky=tk.W, padx=(0, 10))
            
            stock_button = ttk.Button(links_frame, text=f"Open {ticker}", 
                                    command=lambda u=url: self.open_stooq_link(u))
            stock_button.grid(row=row, column=col+1, padx=(0, 20))
        
        # Search Section
        search_frame = ttk.LabelFrame(main_frame, text="Search for Custom Tickers", padding="10")
        search_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Ticker Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.ticker_entry = ttk.Entry(search_frame, width=20)
        self.ticker_entry.grid(row=0, column=1, padx=(10, 10))
        self.ticker_entry.insert(0, "AAPL")
        
        search_button = ttk.Button(search_frame, text="Search on Stooq", 
                                 command=self.search_ticker)
        search_button.grid(row=0, column=2, padx=(10, 0))
        
        open_stooq_button = ttk.Button(search_frame, text="Open Stooq Main Page", 
                                     command=self.open_stooq_main)
        open_stooq_button.grid(row=0, column=3, padx=(10, 0))
        
        # File Processing Section
        process_frame = ttk.LabelFrame(main_frame, text="Process Downloaded Files", padding="10")
        process_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        process_label = ttk.Label(process_frame, text="Convert manually downloaded CSV files to REDLINE format:")
        process_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.process_button = ttk.Button(process_frame, text="Select and Process CSV Files", 
                                       command=self.process_files)
        self.process_button.grid(row=1, column=0, padx=(0, 10))
        
        self.view_files_button = ttk.Button(process_frame, text="View Processed Files", 
                                          command=self.view_files)
        self.view_files_button.grid(row=1, column=1)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready to help you download Stooq data")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        self.open_redline_button = ttk.Button(button_frame, text="Open REDLINE", 
                                             command=self.open_redline)
        self.open_redline_button.grid(row=0, column=0, padx=(0, 10))
        
        self.open_guide_button = ttk.Button(button_frame, text="Open Chartoasis Guide", 
                                           command=self.open_guide)
        self.open_guide_button.grid(row=0, column=1, padx=(0, 10))
        
        self.help_button = ttk.Button(button_frame, text="Help", 
                                     command=self.show_help)
        self.help_button.grid(row=0, column=2)
    
    def open_stooq_link(self, url):
        """Open direct Stooq link for a ticker"""
        webbrowser.open(url)
        self.status_label.config(text=f"Opened {url}")
        messagebox.showinfo("Stooq Link Opened", 
                           f"Direct link opened in your browser.\n\n"
                           f"Next steps:\n"
                           f"1. Click 'Dane historyczne' (Historical Data)\n"
                           f"2. Set your date range\n"
                           f"3. Select 'Daily' interval\n"
                           f"4. Click 'Download data in .csv file'")
    
    def search_ticker(self):
        """Search for a ticker on Stooq"""
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showerror("Error", "Please enter a ticker symbol!")
            return
        
        # Construct search URL
        search_url = f"http://stooq.com/q/d/?s={ticker}"
        webbrowser.open(search_url)
        self.status_label.config(text=f"Searching for {ticker} on Stooq")
        messagebox.showinfo("Search Opened", 
                           f"Search for {ticker} opened in your browser.\n\n"
                           f"If the ticker is found:\n"
                           f"1. Click 'Dane historyczne' (Historical Data)\n"
                           f"2. Set your date range\n"
                           f"3. Download CSV file\n\n"
                           f"If not found, try searching by company name on the main Stooq page.")
    
    def open_stooq_main(self):
        """Open Stooq main page"""
        webbrowser.open("http://stooq.com/")
        self.status_label.config(text="Opened Stooq main page")
        messagebox.showinfo("Stooq Main Page", 
                           "Stooq main page opened.\n\n"
                           "You can:\n"
                           "1. Search for stocks by name or ticker\n"
                           "2. Browse by category (USA stocks, German stocks, etc.)\n"
                           "3. Use the search box at the top")
    
    def process_files(self):
        """Process manually downloaded CSV files"""
        files = filedialog.askopenfilenames(
            title="Select CSV files downloaded from Stooq",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not files:
            return
        
        processed_count = 0
        for file_path in files:
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Standardize to REDLINE format
                df_standardized = self._standardize_stooq_csv(df, file_path)
                
                # Save processed file
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_redline_ready.csv"
                output_path = os.path.join(self.output_dir, output_filename)
                df_standardized.to_csv(output_path, index=False)
                
                processed_count += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(file_path)}: {str(e)}")
        
        if processed_count > 0:
            messagebox.showinfo("Success", 
                              f"Successfully processed {processed_count} file(s)!\n\n"
                              f"Files saved to: {self.output_dir}\n"
                              f"Ready to load in REDLINE.")
            self.status_label.config(text=f"Processed {processed_count} files successfully")
    
    def _standardize_stooq_csv(self, df, file_path):
        """Standardize Stooq CSV to REDLINE format"""
        df = df.copy()
        
        # Try to detect ticker from filename or data
        filename = os.path.basename(file_path)
        ticker = "UNKNOWN"
        
        # Extract ticker from filename if possible
        for col in df.columns:
            if 'ticker' in col.lower() and not df[col].isna().all():
                ticker = df[col].iloc[0]
                break
        
        # If no ticker found, try to extract from filename
        if ticker == "UNKNOWN":
            parts = filename.upper().split('_')
            for part in parts:
                if len(part) <= 5 and part.isalpha():
                    ticker = part
                    break
        
        # Add ticker column
        df['ticker'] = ticker
        
        # Map common Stooq columns to REDLINE schema
        column_mapping = {
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'vol',
            'Adj Close': 'close',  # Use adjusted close if available
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Add missing columns
        required_columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns
        df = df[required_columns]
        df['format'] = 'stooq_manual'
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        return df
    
    def view_files(self):
        """Open the data directory in file explorer"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.output_dir])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", self.output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.output_dir])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file explorer: {str(e)}")
    
    def open_redline(self):
        """Open REDLINE application"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "main.py"])
            messagebox.showinfo("REDLINE", "REDLINE application started!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start REDLINE: {str(e)}")
    
    def open_guide(self):
        """Open the Chartoasis guide"""
        webbrowser.open("https://www.chartoasis.com/free-data-download-stooq-help-cop3/")
        self.status_label.config(text="Opened Chartoasis guide")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """STOOQ MANUAL DOWNLOADER HELP

This tool helps you download data from Stooq.com following the official Chartoasis guide.

QUICK START:
1. Click a direct link button (e.g., "Open AAPL") for popular stocks
2. On Stooq page, click "Dane historyczne" (Historical Data)
3. Set date range and download CSV
4. Use "Process Downloaded Files" to convert to REDLINE format

SEARCH CUSTOM TICKERS:
1. Enter ticker symbol and click "Search on Stooq"
2. Follow same download process

PROCESS FILES:
1. Download CSV files manually from Stooq
2. Click "Select and Process CSV Files"
3. Files are converted to REDLINE format

INTEGRATION:
- Processed files are saved to the 'data' directory
- Open REDLINE to load and analyze the data
- All files are in REDLINE-compatible format

For detailed instructions, click "Open Chartoasis Guide"."""
        
        messagebox.showinfo("Help", help_text)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = StooqManualDownloader()
    app.run()

if __name__ == "__main__":
    main()
