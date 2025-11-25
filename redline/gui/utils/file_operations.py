#!/usr/bin/env python3
"""
File Operations Helper for DataTab
Handles file loading, browsing, and file-related operations.
"""

import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from .safe_file_dialog import safe_askopenfilenames

logger = logging.getLogger(__name__)


class FileOperationsHelper:
    """Helper class for file operations in DataTab."""
    
    def __init__(self, data_tab):
        """Initialize with reference to DataTab."""
        self.data_tab = data_tab
        self.logger = logging.getLogger(__name__)
    
    def open_file_dialog(self):
        """Open file dialog to select data files."""
        import traceback
        self.logger.info(f"🔍 FileOperationsHelper.open_file_dialog() called")
        self.logger.debug(f"   Call stack:\n{''.join(traceback.format_stack()[-5:-1])}")
        try:
            # Supported file types - let safe wrapper handle all validation
            # Note: Avoid semicolon-separated patterns on macOS - they can cause crashes
            filetypes = [
                ("CSV files", "*.csv"),
                ("TXT files", "*.txt"),
                ("JSON files", "*.json"),
                ("Parquet files", "*.parquet"),
                ("Feather files", "*.feather"),
                ("DuckDB files", "*.duckdb"),
                ("All files", "*.*")
            ]
            
            # Open file dialog using macOS-safe wrapper (handles all validation)
            file_paths = safe_askopenfilenames(
                title="Select Data Files",
                filetypes=filetypes,
                initialdir=os.path.expanduser("~")
            )
            
            if file_paths:
                return self.load_files(list(file_paths))
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error opening file dialog: {str(e)}")
            messagebox.showerror("Error", f"Failed to open file dialog: {str(e)}")
            return None
    
    def load_converted_files(self):
        """Load converted files from the converter output directory."""
        try:
            # Default converter output directory
            converter_output = os.path.join(os.getcwd(), "data", "converted")
            
            if not os.path.exists(converter_output):
                messagebox.showinfo(
                    "Info",
                    f"Converter output directory not found: {converter_output}\n"
                    "Please convert some files first."
                )
                return None
            
            # Get list of files in converter output
            files = []
            for ext in ['.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb']:
                files.extend(Path(converter_output).glob(f"*{ext}"))
            
            if not files:
                messagebox.showinfo(
                    "Info",
                    f"No converted files found in: {converter_output}"
                )
                return None
            
            # Convert Path objects to strings
            file_paths = [str(f) for f in files]
            
            # Load the files
            return self.load_files(file_paths)
            
        except Exception as e:
            self.logger.error(f"Error loading converted files: {str(e)}")
            messagebox.showerror("Error", f"Failed to load converted files: {str(e)}")
            return None
    
    def load_files(self, file_paths):
        """Load multiple files."""
        try:
            if not file_paths:
                return None
            
            # Load the first file (for now, support single file loading)
            # TODO: Support multiple file loading/merging
            file_path = file_paths[0] if isinstance(file_paths, list) else file_paths
            
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return None
            
            # Use the data tab's converter (FormatConverter)
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
            
            # Detect file format
            ext = os.path.splitext(file_path)[1].lower()
            format_map = {
                '.csv': 'csv',
                '.txt': 'txt',
                '.json': 'json',
                '.parquet': 'parquet',
                '.feather': 'feather',
                '.duckdb': 'duckdb'
            }
            format_type = format_map.get(ext, 'csv')
            
            # Load the data
            self.logger.info(f"Loading file: {file_path} (format: {format_type})")
            data = converter.load_file_by_type(file_path, format_type)
            
            if data is None or (hasattr(data, 'empty') and data.empty):
                messagebox.showwarning("Warning", f"No data loaded from: {file_path}")
                return None
            
            # Store in data tab
            # Note: current_data_source will be set by _display_data() as a DataSource object
            # Don't set it here as a string, as cleanup_resources() expects an object with .close()
            self.data_tab.current_data = data
            self.data_tab.current_format = format_type
            self.data_tab.unsaved_changes = False
            
            # Update status
            if hasattr(self.data_tab, 'status_label'):
                num_rows = len(data) if hasattr(data, '__len__') else 0
                self.data_tab.status_label.config(
                    text=f"Loaded: {os.path.basename(file_path)} ({num_rows} rows)"
                )
            
            # Display the data
            self.data_tab._display_data(data)
            
            # Update main window title
            if hasattr(self.data_tab, 'main_window'):
                self.data_tab.main_window.set_current_file_path(file_path)
            
            # Get num_rows for logging
            num_rows = len(data) if hasattr(data, '__len__') else 0
            self.logger.info(f"Successfully loaded {num_rows} rows from {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading files: {str(e)}")
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
