#!/usr/bin/env python3
"""
Download Utilities Helper for DownloadTab
Handles utility functions like date ranges, browser operations, API testing.
"""

import logging
import os
import webbrowser
import subprocess
import platform
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog, simpledialog

logger = logging.getLogger(__name__)


class DownloadUtilsHelper:
    """Helper class for utility functions in DownloadTab."""
    
    def __init__(self, download_tab):
        """Initialize with reference to DownloadTab."""
        self.download_tab = download_tab
        self.logger = logging.getLogger(__name__)
    
    def add_ticker(self, ticker: str):
        """Add a ticker to the input field."""
        current_text = self.download_tab.ticker_entry.get(1.0, "end").strip()
        if current_text:
            new_text = current_text + ", " + ticker
        else:
            new_text = ticker
        self.download_tab.ticker_entry.delete(1.0, "end")
        self.download_tab.ticker_entry.insert(1.0, new_text)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.download_tab.output_dir_var.set(directory)
    
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
        
        # Ensure dates are valid (start <= end, end <= today)
        if start_date > end_date:
            start_date = end_date - timedelta(days=365)  # Fallback to 1 year
        
        # Format dates
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        self.download_tab.start_date_var.set(start_str)
        self.download_tab.end_date_var.set(end_str)
        
        self.logger.info(f"Set date range: {start_str} to {end_str}")
    
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
    
    def test_api_connection(self):
        """Test API connection for the selected source."""
        source = self.download_tab.source_var.get()
        
        self.download_tab.status_label.config(text="Testing API connection...")
        
        def test_connection():
            try:
                if source == "yahoo":
                    # Test Yahoo Finance API
                    import yfinance as yf
                    test_ticker = yf.Ticker("AAPL")
                    info = test_ticker.info
                    if info and 'symbol' in info:
                        self.download_tab.main_window.show_info_message("API Test", "✅ Yahoo Finance API is working")
                    else:
                        self.download_tab.main_window.show_warning_message("API Test", "⚠️ Yahoo Finance API returned limited data")
                        
                elif source == "stooq":
                    self.download_tab.main_window.show_info_message("API Test", "ℹ️ Stooq requires manual authentication. Click 'Open Stooq Website' to authenticate.")
                    
                elif source == "multi":
                    # Test multiple sources
                    self.download_tab.main_window.show_info_message("API Test", "🔄 Multi-Source will try Yahoo Finance as primary source")
                
                self.download_tab.status_label.config(text="API test completed")
                
            except Exception as e:
                self.download_tab.main_window.show_error_message("API Test", f"❌ API test failed: {str(e)}")
                self.download_tab.status_label.config(text="API test failed")
        
        # Run test in thread to avoid blocking UI
        import threading
        test_thread = threading.Thread(target=test_connection)
        test_thread.daemon = True
        test_thread.start()

