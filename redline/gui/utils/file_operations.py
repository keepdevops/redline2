#!/usr/bin/env python3
"""
File Operations Helper for DataTab
Handles file loading, format detection, and parallel processing.
"""

import logging
import tkinter as tk
from tkinter import filedialog
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from typing import Optional, List

from ...core.schema import EXT_TO_FORMAT

logger = logging.getLogger(__name__)


class FileOperationsHelper:
    """Helper class for file operations in DataTab."""
    
    def __init__(self, data_tab):
        """Initialize with reference to DataTab."""
        self.data_tab = data_tab
        self.logger = logging.getLogger(__name__)
    
    def open_file_dialog(self):
        """Open file dialog to select data files."""
        try:
            # Create file dialog
            file_paths = filedialog.askopenfilenames(
                title="Select Data Files",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("Parquet files", "*.parquet"),
                    ("Feather files", "*.feather"),
                    ("DuckDB files", "*.duckdb"),
                    ("All files", "*.*")
                ]
            )
            
            if file_paths:
                self.data_tab.load_files(file_paths)
                
        except Exception as e:
            self.logger.error(f"Error opening file dialog: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to open file dialog: {str(e)}")
    
    def load_converted_files(self):
        """Load converted files from the converter output directory."""
        try:
            import glob
            
            # Get the converter output directory
            converted_dir = "data/converted"
            
            if not os.path.exists(converted_dir):
                self.data_tab.main_window.show_warning_message("No Converted Files", 
                    "No converted files directory found. Please run conversions first.")
                return
            
            # Find all converted files in subdirectories
            converted_files = []
            for root, dirs, files in os.walk(converted_dir):
                for file in files:
                    if file.endswith(('.csv', '.txt', '.feather', '.parquet', '.json', '.duckdb')):
                        converted_files.append(os.path.join(root, file))
            
            if not converted_files:
                self.data_tab.main_window.show_warning_message("No Converted Files", 
                    "No converted files found in the converted directory.")
                return
            
            # Ask user which files to load
            if len(converted_files) == 1:
                # Only one file, load it directly
                self.data_tab.load_files([converted_files[0]])
            else:
                # Multiple files, show selection dialog
                self.show_converted_files_dialog(converted_files)
                
        except Exception as e:
            self.logger.error(f"Error loading converted files: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to load converted files: {str(e)}")
    
    def show_converted_files_dialog(self, files: List[str]):
        """Show dialog to select which converted files to load."""
        try:
            from tkinter import messagebox
            from tkinter import ttk
            
            # Create a simple selection dialog
            dialog = tk.Toplevel(self.data_tab.frame)
            dialog.title("Select Converted Files to Load")
            dialog.geometry("600x400")
            dialog.transient(self.data_tab.frame)
            dialog.grab_set()
            
            # Create frame for listbox and scrollbar
            list_frame = ttk.Frame(dialog)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Label
            ttk.Label(list_frame, text="Select files to load:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Listbox with scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Add files to listbox
            for file_path in files:
                # Show relative path for better readability
                rel_path = os.path.relpath(file_path, "data/converted")
                listbox.insert(tk.END, rel_path)
            
            # Buttons frame
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # Load selected button
            def load_selected():
                selected_indices = listbox.curselection()
                if selected_indices:
                    selected_files = [files[i] for i in selected_indices]
                    dialog.destroy()
                    self.data_tab.load_files(selected_files)
                else:
                    messagebox.showwarning("No Selection", "Please select at least one file to load.")
            
            # Load all button
            def load_all():
                dialog.destroy()
                self.data_tab.load_files(files)
            
            # Cancel button
            def cancel():
                dialog.destroy()
            
            ttk.Button(button_frame, text="Load Selected", command=load_selected).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Load All", command=load_all).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
            
            # Instructions
            ttk.Label(button_frame, text="Hold Ctrl/Cmd to select multiple files", 
                     font=("Arial", 9), foreground="gray").pack(side=tk.RIGHT, padx=(0, 10))
            
        except Exception as e:
            self.logger.error(f"Error showing converted files dialog: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to show file selection dialog: {str(e)}")
    
    def load_files(self, file_paths: List[str]):
        """Load multiple files."""
        try:
            # Load files in background thread
            self.data_tab.loading_thread = threading.Thread(target=self._load_files_thread, args=(file_paths,))
            self.data_tab.loading_thread.daemon = True
            self.data_tab.loading_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting file loading: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to start file loading: {str(e)}")
    
    def _load_files_thread(self, file_paths: List[str]):
        """Load files in background thread."""
        try:
            loaded_data = []
            skipped_files = []
            large_files = []
            
            # Check file sizes first
            for file_path in file_paths:
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        large_files.append((file_path, file_size))
                except:
                    pass
            
            # Warn about large files
            if large_files:
                large_file_names = [os.path.basename(f[0]) for f in large_files]
                large_files_text = "\n".join(large_file_names)
                self.data_tab.main_window.run_in_main_thread(
                    lambda: self.data_tab.main_window.show_warning_message(
                        "Large Files Detected",
                        f"Large files detected: {large_files_text}\n\n"
                        "Loading may be slow. Consider using chunked loading for better performance."
                    )
                )
            
            # Use parallel processing for file loading (I/O bound, so more workers)
            with ThreadPoolExecutor(max_workers=8) as executor:
                # Submit all file loading tasks
                future_to_file = {
                    executor.submit(self._load_single_file_parallel, file_path): file_path
                    for file_path in file_paths
                }
                
                # Process completed loads
                completed = 0
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    completed += 1
                    
                    try:
                        data = future.result()
                        if data is not None and not data.empty:
                            loaded_data.append(data)
                            self.logger.info(f"Successfully loaded {file_path}: {len(data)} rows")
                        else:
                            skipped_files.append(file_path)
                            self.logger.warning(f"Skipped empty file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error loading {file_path}: {str(e)}")
                        skipped_files.append(file_path)
            
            # Combine loaded data with memory optimization
            if loaded_data:
                try:
                    # Store count before clearing
                    files_loaded_count = len(loaded_data)
                    
                    # Combine data with memory management
                    if len(loaded_data) == 1:
                        combined_data = loaded_data[0]
                    else:
                        combined_data = pd.concat(loaded_data, ignore_index=True)
                    
                    # Clear the list to free memory
                    loaded_data.clear()
                    
                    # Display the combined data
                    from .data_display import DataDisplayHelper
                    display_helper = DataDisplayHelper(self.data_tab)
                    display_helper.display_data(combined_data)
                    
                    # Clear the combined data after display setup
                    del combined_data
                    
                except MemoryError as mem_error:
                    self.logger.error(f"Memory error combining data: {str(mem_error)}")
                    self.data_tab.main_window.run_in_main_thread(
                        lambda: self.data_tab.main_window.show_error_message(
                            "Memory Error", 
                            "File too large to load. Try loading smaller files or use chunked processing."
                        )
                    )
                except Exception as e:
                    self.logger.error(f"Error combining data: {str(e)}")
                    raise
                
                # Update status with correct count
                self.logger.info(f"Updating status: {files_loaded_count} files loaded, {len(skipped_files)} skipped")
                self.data_tab.main_window.run_in_main_thread(
                    lambda: self.data_tab.status_label.config(
                        text=f"Loaded {files_loaded_count} files, {len(skipped_files)} skipped"
                    )
                )
            else:
                self.data_tab.main_window.run_in_main_thread(
                    lambda: self.data_tab.status_label.config(text="No data loaded")
                )
            
            # Show skipped files if any
            if skipped_files:
                self.data_tab.main_window.show_warning_message(
                    "Skipped Files",
                    f"The following files could not be loaded:\n" + "\n".join(skipped_files)
                )
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in load files thread: {error_msg}")
            self.data_tab.main_window.run_in_main_thread(
                lambda: self.data_tab.main_window.show_error_message("Error", f"Failed to load files: {error_msg}")
            )
    
    def _load_single_file_parallel(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load a single file - optimized for speed with parallel processing."""
        try:
            # Detect format from extension
            format_type = self._detect_format_from_path(file_path)
            
            # Use direct pandas loading for speed (skip validation/cleaning for display)
            if format_type == 'csv':
                data = pd.read_csv(file_path)
            elif format_type == 'txt':
                # Try different separators for TXT files
                data = None
                for sep in [',', '\t', ';', ' ', '|']:
                    try:
                        test_data = pd.read_csv(file_path, sep=sep)
                        # Check if we got multiple columns (good parsing)
                        if len(test_data.columns) > 1:
                            data = test_data
                            break
                    except:
                        continue
                
                if data is None:
                    # If all separators fail, try reading as fixed-width
                    data = pd.read_fwf(file_path)
            elif format_type == 'parquet':
                data = pd.read_parquet(file_path)
            elif format_type == 'feather':
                data = pd.read_feather(file_path)
            elif format_type == 'json':
                data = pd.read_json(file_path)
            elif format_type == 'duckdb':
                import duckdb
                conn = duckdb.connect(file_path)
                data = conn.execute("SELECT * FROM tickers_data").fetchdf()
                conn.close()
            else:
                # Fallback to loader for unsupported formats
                data = self.data_tab.loader.load_file_by_type(file_path, format_type)
            
            # Clean data after loading - ensure numeric columns are numeric
            if data is not None and not data.empty:
                try:
                    # Protect ticker column from being converted
                    has_ticker = 'ticker' in data.columns
                    
                    # Convert common numeric columns to numeric type
                    # BUT exclude ticker column even if it contains numeric-looking values
                    numeric_keywords = ['open', 'high', 'low', 'close', 'vol', 'volume', 'openint']
                    for col in data.columns:
                        col_lower = col.lower().strip()
                        # Skip ticker column - keep it as string
                        if col_lower == 'ticker':
                            data[col] = data[col].astype(str)
                            continue
                        # Check if column name contains numeric indicators
                        if any(numeric_keyword in col_lower for numeric_keyword in numeric_keywords):
                            data[col] = pd.to_numeric(data[col], errors='coerce')
                        # Handle Stooq format columns
                        elif col in ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']:
                            data[col] = pd.to_numeric(data[col], errors='coerce')
                    
                    # Ensure ticker is always string (handle various ticker column formats)
                    ticker_columns = ['ticker', '<TICKER>', 'Ticker', 'TICKER']
                    for ticker_col in ticker_columns:
                        if ticker_col in data.columns:
                            data[ticker_col] = data[ticker_col].astype(str)
                            # Clean any concatenated tickers (e.g., "LW.USLW.US..." -> "LW.US")
                            # This happens when data gets improperly concatenated
                            if data[ticker_col].dtype == 'object':
                                # Limit ticker length to prevent weird concatenations
                                data[ticker_col] = data[ticker_col].str[:20]  # Limit to 20 chars
                                
                except Exception as e:
                    self.logger.warning(f"Could not clean data types: {str(e)}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    def _detect_format_from_path(self, file_path: str) -> str:
        """Detect format from file path."""
        ext = os.path.splitext(file_path)[1].lower()
        return EXT_TO_FORMAT.get(ext, 'csv')
    
    def _load_large_file_chunked(self, file_path: str, format_type: str, chunk_size: int = 10000) -> pd.DataFrame:
        """Load large files in chunks to prevent memory issues."""
        try:
            self.logger.info(f"Loading large file {file_path} in chunks of {chunk_size} rows")
            
            if format_type == 'csv':
                # Load CSV in chunks
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    chunks.append(chunk)
                    if len(chunks) >= 10:  # Limit memory usage
                        combined = pd.concat(chunks, ignore_index=True)
                        chunks = [combined]
                
                if chunks:
                    return pd.concat(chunks, ignore_index=True)
                else:
                    return pd.DataFrame()
            
            elif format_type == 'txt':
                # Try different separators for TXT files in chunks
                chunks = []
                for sep in [',', '\t', ';', ' ', '|']:
                    try:
                        for chunk in pd.read_csv(file_path, sep=sep, chunksize=chunk_size):
                            chunks.append(chunk)
                            if len(chunks) >= 10:  # Limit memory usage
                                combined = pd.concat(chunks, ignore_index=True)
                                chunks = [combined]
                        
                        if chunks:
                            return pd.concat(chunks, ignore_index=True)
                        break
                    except:
                        continue
                
                # If all separators fail, try reading as fixed-width
                try:
                    return pd.read_fwf(file_path)
                except Exception as e:
                    self.logger.warning(f"Error in chunked text loading: {str(e)}")
                    return pd.DataFrame()
            
            else:
                # For other formats, use regular loading
                return self.data_tab.loader.load_file_by_type(file_path, format_type)
                
        except Exception as e:
            self.logger.error(f"Error in chunked loading: {str(e)}")
            return pd.DataFrame()

