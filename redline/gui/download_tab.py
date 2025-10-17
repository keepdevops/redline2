#!/usr/bin/env python3
"""
REDLINE Download Tab
GUI tab for downloading financial data from various sources.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import os
import webbrowser
from typing import Optional, List, Dict, Any

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector
from ..downloaders.yahoo_downloader import YahooDownloader
from ..downloaders.stooq_downloader import StooqDownloader
from ..downloaders.multi_source import MultiSourceDownloader
from ..downloaders.bulk_downloader import BulkDownloader

logger = logging.getLogger(__name__)

class DownloadTab:
    """Download tab for acquiring financial data from various sources."""
    
    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        """Initialize download tab."""
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Downloaders
        self.yahoo_downloader = YahooDownloader()
        self.stooq_downloader = StooqDownloader()
        self.multi_downloader = MultiSourceDownloader()
        self.bulk_downloader = BulkDownloader(max_workers=1)  # Use only 1 worker to avoid rate limiting
        
        # Variables
        self.ticker_input = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value='data/downloads')
        self.api_key_var = tk.StringVar()
        self.bulk_mode_var = tk.BooleanVar()
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Create widgets
        self.create_widgets()
        
        # Setup event handlers
        self.setup_event_handlers()
        
        # Set default date range
        self.set_date_range(365)  # Default to 1 year
    
    def create_widgets(self):
        """Create the download tab widgets."""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - API & Download controls
        left_panel = ttk.LabelFrame(main_container, text="API & Download Controls", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel - Results and status
        right_panel = ttk.LabelFrame(main_container, text="Download Results", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_download_controls(left_panel)
        self.create_results_display(right_panel)
    
    def create_download_controls(self, parent):
        """Create download control widgets."""
        # API Data source selection
        source_frame = ttk.LabelFrame(parent, text="API Data Sources", padding=5)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_var = tk.StringVar(value="yahoo")
        ttk.Radiobutton(source_frame, text="📊 Yahoo Finance API (Free, Reliable, No Auth)", 
                       variable=self.source_var, value="yahoo").pack(anchor=tk.W)
        ttk.Radiobutton(source_frame, text="🏢 Stooq.com API (High Quality, Manual Auth)", 
                       variable=self.source_var, value="stooq").pack(anchor=tk.W)
        ttk.Radiobutton(source_frame, text="🔄 Multi-Source API (Fallback System)", 
                       variable=self.source_var, value="multi").pack(anchor=tk.W)
        
        # API status info
        api_info_frame = ttk.Frame(source_frame)
        api_info_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(api_info_frame, text="💡 Yahoo Finance is recommended for most users", 
                 font=("Arial", 8), foreground="blue").pack(anchor=tk.W)
        ttk.Label(api_info_frame, text="⚠️ Yahoo Finance: 2 second delay between requests (rate limited)", 
                 font=("Arial", 8), foreground="orange").pack(anchor=tk.W)
        ttk.Label(api_info_frame, text="📊 Bulk downloads use sequential processing to avoid rate limits", 
                 font=("Arial", 8), foreground="green").pack(anchor=tk.W)
        
        # Ticker input
        ticker_frame = ttk.LabelFrame(parent, text="Ticker Symbols", padding=5)
        ticker_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ticker_frame, text="Enter ticker symbols (comma-separated):").pack(anchor=tk.W)
        self.ticker_entry = tk.Text(ticker_frame, height=4, wrap=tk.WORD)
        self.ticker_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Quick ticker buttons
        quick_frame = ttk.Frame(ticker_frame)
        quick_frame.pack(fill=tk.X, pady=(5, 0))
        
        quick_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"]
        for i, ticker in enumerate(quick_tickers):
            btn = ttk.Button(quick_frame, text=ticker, width=8,
                           command=lambda t=ticker: self.add_ticker(t))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky='ew')
        
        # Date range
        date_frame = ttk.LabelFrame(parent, text="Date Range", padding=5)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start date
        start_frame = ttk.Frame(date_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Date:").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar(value="2020-01-01")
        ttk.Entry(start_frame, textvariable=self.start_date_var, width=12).pack(side=tk.RIGHT)
        
        # End date
        end_frame = ttk.Frame(date_frame)
        end_frame.pack(fill=tk.X, pady=2)
        ttk.Label(end_frame, text="End Date:").pack(side=tk.LEFT)
        self.end_date_var = tk.StringVar(value="2024-12-31")
        ttk.Entry(end_frame, textvariable=self.end_date_var, width=12).pack(side=tk.RIGHT)
        
        # Quick date buttons
        quick_date_frame = ttk.Frame(date_frame)
        quick_date_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(quick_date_frame, text="1Y", 
                  command=lambda: self.set_date_range("1y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="2Y", 
                  command=lambda: self.set_date_range("2y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="5Y", 
                  command=lambda: self.set_date_range("5y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="Max", 
                  command=lambda: self.set_date_range("max")).pack(side=tk.LEFT, padx=2)
        
        # Output options
        output_frame = ttk.LabelFrame(parent, text="Output Options", padding=5)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value="data/downloaded")
        ttk.Entry(dir_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.RIGHT)
        
        # Format options
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=2)
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="stooq")
        ttk.Radiobutton(format_frame, text="Stooq (REDLINE Compatible)", 
                       variable=self.format_var, value="stooq").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="Standard", 
                       variable=self.format_var, value="standard").pack(side=tk.LEFT, padx=(10, 0))
        
        # Output options
        output_frame = ttk.LabelFrame(parent, text="Output Options", padding=5)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output format
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_format_var = tk.StringVar(value='csv')
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format_var, 
                                   values=['csv', 'json', 'parquet', 'duckdb'], 
                                   state='readonly', width=10)
        format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Output directory
        ttk.Label(format_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))
        output_dir_entry = ttk.Entry(format_frame, textvariable=self.output_dir_var, width=20)
        output_dir_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Browse", 
                  command=self.browse_output_dir).pack(side=tk.LEFT)
        
        # API Key input (for services that need it)
        api_key_frame = ttk.Frame(output_frame)
        api_key_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(api_key_frame, text="API Key (if required):").pack(side=tk.LEFT, padx=(0, 5))
        api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, 
                                 show="*", width=30)
        api_key_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(api_key_frame, text="Clear", 
                  command=lambda: self.api_key_var.set("")).pack(side=tk.LEFT)
        
        # Download mode options
        mode_frame = ttk.LabelFrame(parent, text="Download Mode", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(mode_frame, text="Bulk Download Mode (Parallel Processing)", 
                       variable=self.bulk_mode_var).pack(anchor=tk.W)
        
        # Download buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.download_button = ttk.Button(button_frame, text="Start Download", 
                                        command=self.start_download, style="Accent.TButton")
        self.download_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                    command=self.stop_download, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Open Stooq Website", 
                  command=self.open_stooq_website).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Open Browser", 
                  command=self.open_browser_menu).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Test API", 
                  command=self.test_api_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(parent, text="Ready to download")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_results_display(self, parent):
        """Create results display widgets."""
        # Results treeview
        columns = ("Ticker", "Rows", "Date Range", "Source", "Status", "File")
        self.results_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu
        self.create_context_menu()
    
    def create_context_menu(self):
        """Create context menu for results tree."""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Open File", command=self.open_selected_file)
        self.context_menu.add_command(label="Load in REDLINE", command=self.load_selected_data)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete File", command=self.delete_selected_file)
        
        self.results_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_event_handlers(self):
        """Setup event handlers."""
        pass
    
    def add_ticker(self, ticker: str):
        """Add a ticker to the input field."""
        current_text = self.ticker_entry.get(1.0, tk.END).strip()
        if current_text:
            new_text = current_text + ", " + ticker
        else:
            new_text = ticker
        self.ticker_entry.delete(1.0, tk.END)
        self.ticker_entry.insert(1.0, new_text)
    
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def start_download(self):
        """Start the download process."""
        # Get tickers
        ticker_text = self.ticker_entry.get(1.0, tk.END).strip()
        if not ticker_text:
            messagebox.showerror("Error", "Please enter at least one ticker symbol")
            return
        
        tickers = [t.strip().upper() for t in ticker_text.split(',') if t.strip()]
        if not tickers:
            messagebox.showerror("Error", "No valid ticker symbols found")
            return
        
        # Get dates
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        # Get source
        source = self.source_var.get()
        
        # Get output directory
        output_dir = self.output_dir_var.get()
        os.makedirs(output_dir, exist_ok=True)
        
        # Update UI
        self.download_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_var.set(0)
        self.status_label.config(text="Starting download...")
        
        # Start download thread
        self.download_thread = threading.Thread(
            target=self.download_data_thread,
            args=(tickers, start_date, end_date, source, output_dir)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def download_data_thread(self, tickers: List[str], start_date: str, end_date: str, 
                           source: str, output_dir: str):
        """Download data in a separate thread."""
        try:
            total_tickers = len(tickers)
            
            for i, ticker in enumerate(tickers):
                try:
                    # Update status
                    self.main_window.run_in_main_thread(
                        lambda t=ticker: self.status_label.config(text=f"Downloading {t}...")
                    )
                    
                    # Download data
                    df = None
                    source_name = ""
                    
                    if source == "yahoo":
                        df = self.yahoo_downloader.download_single_ticker(ticker, start_date, end_date)
                        source_name = "Yahoo Finance"
                    elif source == "stooq":
                        df = self.stooq_downloader.download_single_ticker(ticker, start_date, end_date)
                        source_name = "Stooq"
                    elif source == "multi":
                        df = self.multi_downloader.download_from_source("yahoo", ticker, start_date, end_date)
                        source_name = "Multi-Source"
                    
                    # Add delay to avoid rate limiting
                    if i < total_tickers - 1:  # Don't delay after last ticker
                        import time
                        time.sleep(3)  # 3 second delay between requests to avoid rate limiting
                    
                    # Process results
                    if df is not None and not df.empty:
                        # Save file
                        filename = f"{ticker}_{source}_data_{start_date}_{end_date}.csv"
                        filepath = os.path.join(output_dir, filename)
                        df.to_csv(filepath, index=False)
                        
                        # Add to results
                        if hasattr(df, 'index') and len(df.index) > 0:
                            try:
                                date_range = f"{df.index.min().date()} to {df.index.max().date()}"
                            except:
                                date_range = "N/A"
                        else:
                            date_range = "N/A"
                            
                        self.main_window.run_in_main_thread(
                            lambda t=ticker, r=len(df), d=date_range, s=source_name, f=filepath:
                            self.results_tree.insert('', 'end', values=(t, r, d, s, "Success", f))
                        )
                        
                        self.logger.info(f"Successfully downloaded {ticker}: {len(df)} rows")
                    else:
                        error_msg = "No data returned"
                        self.main_window.run_in_main_thread(
                            lambda t=ticker, s=source_name, e=error_msg:
                            self.results_tree.insert('', 'end', values=(t, 0, "N/A", s, f"Failed: {e}", ""))
                        )
                        self.logger.warning(f"Failed to download {ticker}: {error_msg}")
                    
                    # Update progress
                    progress = ((i + 1) / total_tickers) * 100
                    self.main_window.run_in_main_thread(
                        lambda p=progress: self.progress_var.set(p)
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error downloading {ticker}: {str(e)}")
                    self.main_window.run_in_main_thread(
                        lambda t=ticker, e=str(e):
                        self.results_tree.insert('', 'end', values=(t, 0, "N/A", "Error", f"Error: {e}", ""))
                    )
            
            # Complete
            self.main_window.run_in_main_thread(
                lambda: self.status_label.config(text="Download completed")
            )
            
        except Exception as e:
            self.logger.error(f"Download thread error: {str(e)}")
            self.main_window.run_in_main_thread(
                lambda: self.status_label.config(text=f"Download failed: {str(e)}")
            )
        finally:
            # Reset UI
            self.main_window.run_in_main_thread(
                lambda: (
                    self.download_button.config(state='normal'),
                    self.stop_button.config(state='disabled')
                )
            )
    
    def stop_download(self):
        """Stop the download process."""
        self.status_label.config(text="Stopping download...")
        # Note: Thread stopping is complex, this is a basic implementation
        self.download_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Download stopped")
    
    def open_stooq_website(self):
        """Open Stooq website for manual download."""
        try:
            # Open Stooq.com with a sample ticker
            stooq_url = "https://stooq.com/q/d/?s=AAPL&i=d"
            webbrowser.open(stooq_url)
            
            # Show helpful instructions
            messagebox.showinfo("Stooq Manual Download", 
                               "🌐 Stooq.com opened in your default browser!\n\n"
                               "📋 Instructions:\n"
                               "1. 🔐 Log in to your Stooq account\n"
                               "2. 🔒 Complete 2FA authentication if required\n"
                               "3. 📊 Navigate to historical data section\n"
                               "4. 📈 Search for your desired ticker symbols\n"
                               "5. 💾 Download CSV files manually\n"
                               "6. 📁 Use 'Browse Files' in REDLINE Data tab to load them\n\n"
                               "💡 Tip: Stooq provides high-quality financial data\n"
                               "with detailed historical information.")
                               
            self.logger.info(f"Opened Stooq website: {stooq_url}")
            
        except Exception as e:
            error_msg = f"Failed to open browser: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Browser Error", error_msg)
    
    def open_browser_menu(self):
        """Open a menu with browser options."""
        try:
            from tkinter import simpledialog
            
            # Get ticker symbol from user
            ticker = simpledialog.askstring("Custom Ticker", 
                                          "Enter ticker symbol for Stooq (e.g., AAPL, MSFT):",
                                          initialvalue="AAPL")
            
            if ticker:
                ticker = ticker.upper().strip()
                stooq_url = f"https://stooq.com/q/d/?s={ticker}&i=d"
                
                # Ask which browser to use
                browser_choice = messagebox.askyesnocancel("Browser Choice", 
                                                         f"Open Stooq for {ticker} in:\n\n"
                                                         "YES = Default Browser\n"
                                                         "NO = Try to specify browser\n"
                                                         "CANCEL = Cancel")
                
                if browser_choice is True:
                    # Use default browser
                    webbrowser.open(stooq_url)
                    messagebox.showinfo("Success", f"Opened Stooq for {ticker} in default browser!")
                    
                elif browser_choice is False:
                    # Try to specify browser
                    self._open_with_specific_browser(stooq_url, ticker)
                    
                self.logger.info(f"Opened Stooq for {ticker}: {stooq_url}")
                
        except Exception as e:
            error_msg = f"Failed to open browser menu: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Browser Menu Error", error_msg)
    
    def _open_with_specific_browser(self, url, ticker):
        """Try to open URL with a specific browser."""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Try Safari first, then Chrome, then Firefox
                browsers = ["safari", "google chrome", "firefox"]
                for browser in browsers:
                    try:
                        subprocess.run(["open", "-a", browser, url], check=True)
                        messagebox.showinfo("Success", f"Opened Stooq for {ticker} in {browser.title()}!")
                        return
                    except subprocess.CalledProcessError:
                        continue
                        
            elif system == "Windows":
                # Try Chrome, Edge, Firefox
                browsers = ["chrome", "msedge", "firefox"]
                for browser in browsers:
                    try:
                        subprocess.run([browser, url], check=True)
                        messagebox.showinfo("Success", f"Opened Stooq for {ticker} in {browser.title()}!")
                        return
                    except subprocess.CalledProcessError:
                        continue
                        
            # Fallback to default browser
            webbrowser.open(url)
            messagebox.showinfo("Success", f"Opened Stooq for {ticker} in default browser!")
            
        except Exception as e:
            # Ultimate fallback
            webbrowser.open(url)
            messagebox.showinfo("Success", f"Opened Stooq for {ticker} in default browser!")
    
    def clear_results(self):
        """Clear the results tree."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def show_context_menu(self, event):
        """Show context menu for results tree."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def open_selected_file(self):
        """Open the selected file."""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                os.system(f"open '{filepath}'")
    
    def load_selected_data(self):
        """Load the selected data into REDLINE."""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                # Load the data in the data tab
                self.main_window.data_tab.load_files([filepath])
                messagebox.showinfo("Data Loaded", f"Data from {filepath} has been loaded into REDLINE")
    
    def delete_selected_file(self):
        """Delete the selected file."""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                if messagebox.askyesno("Delete File", f"Delete {filepath}?"):
                    os.remove(filepath)
                    self.results_tree.delete(selection[0])
    
    def test_api_connection(self):
        """Test API connection for the selected source."""
        source = self.source_var.get()
        
        self.status_label.config(text="Testing API connection...")
        
        def test_connection():
            try:
                if source == "yahoo":
                    # Test Yahoo Finance API
                    import yfinance as yf
                    test_ticker = yf.Ticker("AAPL")
                    info = test_ticker.info
                    if info and 'symbol' in info:
                        self.main_window.show_info_message("API Test", "✅ Yahoo Finance API is working")
                    else:
                        self.main_window.show_warning_message("API Test", "⚠️ Yahoo Finance API returned limited data")
                        
                elif source == "stooq":
                    self.main_window.show_info_message("API Test", "ℹ️ Stooq requires manual authentication. Click 'Open Stooq Website' to authenticate.")
                    
                elif source == "multi":
                    # Test multiple sources
                    self.main_window.show_info_message("API Test", "🔄 Multi-Source will try Yahoo Finance as primary source")
                
                self.status_label.config(text="API test completed")
                
            except Exception as e:
                self.main_window.show_error_message("API Test", f"❌ API test failed: {str(e)}")
                self.status_label.config(text="API test failed")
        
        # Run test in thread to avoid blocking UI
        import threading
        test_thread = threading.Thread(target=test_connection)
        test_thread.daemon = True
        test_thread.start()
    
    def set_date_range(self, days):
        """Set date range to last N days or specific period."""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        
        # Handle both string periods and integer days
        if isinstance(days, str):
            if days == "1y":
                start_date = end_date - timedelta(days=365)
            elif days == "2y":
                start_date = end_date - timedelta(days=730)
            elif days == "5y":
                start_date = end_date - timedelta(days=1825)
            elif days == "max":
                start_date = datetime(2000, 1, 1)
            else:
                # Try to convert to int
                try:
                    days_int = int(days)
                    start_date = end_date - timedelta(days=days_int)
                except ValueError:
                    start_date = end_date - timedelta(days=365)  # Default to 1 year
        else:
            # Handle integer days
            start_date = end_date - timedelta(days=int(days))
        
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def on_tab_activated(self):
        """Handle tab activation."""
        # Refresh any necessary data when tab becomes active
        pass
