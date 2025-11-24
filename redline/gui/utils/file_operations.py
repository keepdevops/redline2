#!/usr/bin/env python3
"""
File Operations Helper for DataTab
Handles file loading, browsing, and file-related operations.
"""

import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

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
            # Supported file types
            filetypes = [
                ("CSV files", "*.csv"),
                ("TXT files", "*.txt"),
                ("JSON files", "*.json"),
                ("Parquet files", "*.parquet"),
                ("Feather files", "*.feather"),
                ("DuckDB files", "*.duckdb"),
                ("All supported files", "*.csv;*.txt;*.json;*.parquet;*.feather;*.duckdb"),
                ("All files", "*.*")
            ]
            
            # Open file dialog
            file_paths = filedialog.askopenfilenames(
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
            
            # Use the data tab's loader
            loader = self.data_tab.loader
            
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
            data = loader.load_file(file_path, format_type)
            
            if data is None or (hasattr(data, 'empty') and data.empty):
                messagebox.showwarning("Warning", f"No data loaded from: {file_path}")
                return None
            
            # Store in data tab
            self.data_tab.current_data = data
            self.data_tab.current_data_source = file_path
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
            
            self.logger.info(f"Successfully loaded {num_rows} rows from {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading files: {str(e)}")
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
