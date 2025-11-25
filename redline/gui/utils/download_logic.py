#!/usr/bin/env python3
"""
Download Logic Helper for DownloadTab
Handles download operations and data processing.
"""

import logging
import threading
import os
import tkinter as tk
from typing import List
from tkinter import messagebox

logger = logging.getLogger(__name__)


class DownloadLogicHelper:
    """Helper class for download logic in DownloadTab."""
    
    def __init__(self, download_tab):
        """Initialize with reference to DownloadTab."""
        self.download_tab = download_tab
        self.logger = logging.getLogger(__name__)
    
    def start_download(self):
        """Start the download process."""
        # Get tickers
        ticker_text = self.download_tab.ticker_entry.get(1.0, tk.END).strip()
        if not ticker_text:
            messagebox.showerror("Error", "Please enter at least one ticker symbol")
            return
        
        tickers = [t.strip().upper() for t in ticker_text.split(',') if t.strip()]
        if not tickers:
            messagebox.showerror("Error", "No valid ticker symbols found")
            return
        
        # Get dates
        start_date = self.download_tab.start_date_var.get()
        end_date = self.download_tab.end_date_var.get()
        
        # Validate dates
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            today = datetime.now()
            
            # Check if end date is in the future
            if end_dt > today:
                messagebox.showwarning(
                    "Invalid Date Range",
                    f"End date ({end_date}) cannot be in the future.\n"
                    f"Please set end date to today ({today.strftime('%Y-%m-%d')}) or earlier."
                )
                # Auto-correct to today
                self.download_tab.end_date_var.set(today.strftime('%Y-%m-%d'))
                end_date = today.strftime('%Y-%m-%d')
                end_dt = today
            
            # Check if start date is after end date
            if start_dt > end_dt:
                messagebox.showerror(
                    "Invalid Date Range",
                    f"Start date ({start_date}) cannot be after end date ({end_date})."
                )
                return
            
            # Check if date range is too large (more than 20 years)
            days_diff = (end_dt - start_dt).days
            if days_diff > 7300:  # ~20 years
                messagebox.showwarning(
                    "Large Date Range",
                    f"Date range is very large ({days_diff} days).\n"
                    f"This may take a long time to download. Continue?"
                )
        except ValueError as e:
            messagebox.showerror(
                "Invalid Date Format",
                f"Invalid date format. Please use YYYY-MM-DD format.\n"
                f"Start: {start_date}, End: {end_date}\n"
                f"Error: {str(e)}"
            )
            return
        
        # Get source
        source = self.download_tab.source_var.get()
        
        # Get output directory
        output_dir = self.download_tab.output_dir_var.get()
        os.makedirs(output_dir, exist_ok=True)
        
        # Update UI
        self.download_tab.download_button.config(state='disabled')
        self.download_tab.stop_button.config(state='normal')
        self.download_tab.progress_var.set(0)
        self.download_tab.status_label.config(text="Starting download...")
        
        # Start download thread
        self.download_tab.download_thread = threading.Thread(
            target=self.download_data_thread,
            args=(tickers, start_date, end_date, source, output_dir)
        )
        self.download_tab.download_thread.daemon = True
        self.download_tab.download_thread.start()
    
    def download_data_thread(self, tickers: List[str], start_date: str, end_date: str, 
                           source: str, output_dir: str):
        """Download data in a separate thread."""
        try:
            total_tickers = len(tickers)
            
            for i, ticker in enumerate(tickers):
                try:
                    # Update status
                    self.download_tab.main_window.run_in_main_thread(
                        lambda t=ticker: self.download_tab.status_label.config(text=f"Downloading {t}...")
                    )
                    
                    # Download data
                    df = None
                    source_name = ""
                    
                    if source == "yahoo":
                        df = self.download_tab.yahoo_downloader.download_single_ticker(ticker, start_date, end_date)
                        source_name = "Yahoo Finance"
                    elif source == "stooq":
                        df = self.download_tab.stooq_downloader.download_single_ticker(ticker, start_date, end_date)
                        source_name = "Stooq"
                    elif source == "multi":
                        df = self.download_tab.multi_downloader.download_from_source("yahoo", ticker, start_date, end_date)
                        source_name = "Multi-Source"
                    
                    # Add delay to avoid rate limiting
                    if i < total_tickers - 1:  # Don't delay after last ticker
                        import time
                        time.sleep(0.5)  # 0.5 second delay
                    
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
                            
                        self.download_tab.main_window.run_in_main_thread(
                            lambda t=ticker, r=len(df), d=date_range, s=source_name, f=filepath:
                            self.add_download_result(t, r, d, s, "Success", f)
                        )
                        
                        self.logger.info(f"Successfully downloaded {ticker}: {len(df)} rows")
                    else:
                        # No data returned - provide helpful error message
                        error_msg = f"No data returned for date range {start_date} to {end_date}"
                        suggestion = ""
                        if source == "yahoo":
                            suggestion = " Try: (1) Different date range, (2) Stooq data source, or (3) Wait and retry (rate limiting)"
                        else:
                            suggestion = " Try a different date range or data source"
                        
                        full_error = f"{error_msg}.{suggestion}"
                        self.download_tab.main_window.run_in_main_thread(
                            lambda t=ticker, s=source_name, e=full_error:
                            self.add_download_result(t, 0, f"{start_date} to {end_date}", s, f"Failed: {e}", "")
                        )
                        self.logger.warning(f"Failed to download {ticker}: {error_msg}")
                    
                    # Update progress
                    progress = ((i + 1) / total_tickers) * 100
                    self.download_tab.main_window.run_in_main_thread(
                        lambda p=progress: self.download_tab.progress_var.set(p)
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error downloading {ticker}: {str(e)}")
                    self.download_tab.main_window.run_in_main_thread(
                        lambda t=ticker, e=str(e):
                        self.add_download_result(t, 0, "N/A", "Error", f"Error: {e}", "")
                    )
            
            # Complete
            self.download_tab.main_window.run_in_main_thread(
                lambda: self.download_tab.status_label.config(text="Download completed")
            )
            
        except Exception as e:
            self.logger.error(f"Download thread error: {str(e)}")
            self.download_tab.main_window.run_in_main_thread(
                lambda: self.download_tab.status_label.config(text=f"Download failed: {str(e)}")
            )
        finally:
            # Reset UI
            self.download_tab.main_window.run_in_main_thread(
                lambda: (
                    self.download_tab.download_button.config(state='normal'),
                    self.download_tab.stop_button.config(state='disabled')
                )
            )
    
    def stop_download(self):
        """Stop the download process."""
        self.download_tab.status_label.config(text="Stopping download...")
        # Note: Thread stopping is complex, this is a basic implementation
        self.download_tab.download_button.config(state='normal')
        self.download_tab.stop_button.config(state='disabled')
        self.download_tab.status_label.config(text="Download stopped")
    
    def add_download_result(self, ticker, rows, date_range, source, status, file_path):
        """Add a download result to the results tree."""
        self.download_tab.results_tree.insert('', 'end', values=(ticker, rows, date_range, source, status, file_path))
    
    def clear_results(self):
        """Clear all download results."""
        for item in self.download_tab.results_tree.get_children():
            self.download_tab.results_tree.delete(item)

