#!/usr/bin/env python3
"""
REDLINE Converter Tab
GUI tab for data format conversion utilities.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from typing import List, Dict, Any, Optional
import pandas as pd

from redline.core.data_loader import DataLoader
from redline.core.format_converter import FormatConverter
from redline.database.connector import DatabaseConnector
from redline.gui.widgets.progress_tracker import ProgressTracker
from redline.core.schema import EXT_TO_FORMAT, FORMAT_DIALOG_INFO

logger = logging.getLogger(__name__)

class ConverterTab:
    """Converter tab for data format conversion."""

    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

        self.frame = ttk.Frame(parent)
        self.converter = FormatConverter()
        
        # Conversion state
        self.conversion_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.converted_files: List[str] = []
        
        self.create_widgets()
        self.setup_event_handlers()
        
        # Validate that only supported formats are available
        self._validate_supported_formats()
        
    def _validate_supported_formats(self):
        """Validate that only supported formats are available in the GUI."""
        try:
            supported_formats = self.converter.get_supported_formats()
            schema_formats = list(FORMAT_DIALOG_INFO.keys())
            
            # Check for formats in schema that are not supported
            unsupported_in_schema = [f for f in schema_formats if f not in supported_formats]
            if unsupported_in_schema:
                self.logger.warning(f"Found unsupported formats in schema: {unsupported_in_schema}")
                self.logger.warning("These formats will be removed from GUI dropdowns")
            
            # Check for supported formats not in schema
            missing_in_schema = [f for f in supported_formats if f not in schema_formats]
            if missing_in_schema:
                self.logger.warning(f"Supported formats missing from schema: {missing_in_schema}")
                
            self.logger.info(f"Format validation complete. Supported: {supported_formats}")
            
        except Exception as e:
            self.logger.error(f"Error validating supported formats: {str(e)}")
        
    def create_widgets(self):
        """Create converter tab widgets."""
        # Main container with scrollbar
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Data Format Converter", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Input section
        self.create_input_section(scrollable_frame)
        
        # Output section
        self.create_output_section(scrollable_frame)
        
        # Conversion options
        self.create_conversion_options(scrollable_frame)
        
        # Batch conversion
        self.create_batch_section(scrollable_frame)
        
        # Progress section
        self.create_progress_section(scrollable_frame)
        
        # Results section
        self.create_results_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_input_section(self, parent):
        """Create input file selection section."""
        input_frame = ttk.LabelFrame(parent, text="Input Files", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # File selection
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_files_var = tk.StringVar()
        self.input_files_entry = ttk.Entry(file_frame, textvariable=self.input_files_var, 
                                          state='readonly', width=50)
        self.input_files_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse Files", 
                  command=self.browse_input_files).pack(side=tk.RIGHT)
        
        # Input format detection
        format_frame = ttk.Frame(input_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Input Format:").pack(side=tk.LEFT, padx=(0, 10))
        self.input_format_var = tk.StringVar()
        self.input_format_combo = ttk.Combobox(format_frame, textvariable=self.input_format_var,
                                              state='readonly', width=15)
        self.input_format_combo['values'] = list(FORMAT_DIALOG_INFO.keys())
        self.input_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(format_frame, text="Auto-detect", 
                  command=self.auto_detect_format).pack(side=tk.LEFT)
        
        # Preview button
        ttk.Button(input_frame, text="Preview Input File", 
                  command=self.preview_input_file).pack(anchor=tk.W)
        
    def create_output_section(self, parent):
        """Create output configuration section."""
        output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 10))
        self.output_dir_var = tk.StringVar(value="data/converted")
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=30)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.browse_output_directory).pack(side=tk.RIGHT)
        
        # Output format
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 10))
        self.output_format_var = tk.StringVar(value="csv")
        self.output_format_combo = ttk.Combobox(format_frame, textvariable=self.output_format_var,
                                               state='readonly', width=15)
        self.output_format_combo['values'] = list(FORMAT_DIALOG_INFO.keys())
        self.output_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Output options
        options_frame = ttk.Frame(output_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.overwrite_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.create_subdir_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create subdirectory by format", 
                       variable=self.create_subdir_var).pack(side=tk.LEFT)
        
    def create_conversion_options(self, parent):
        """Create conversion options section."""
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Data cleaning options
        cleaning_frame = ttk.Frame(options_frame)
        cleaning_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cleaning_frame, text="Data Cleaning:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cleaning_frame, text="Remove duplicate rows", 
                       variable=self.remove_duplicates_var).pack(anchor=tk.W, padx=(20, 0))
        
        self.fill_missing_var = tk.BooleanVar()
        ttk.Checkbutton(cleaning_frame, text="Fill missing values", 
                       variable=self.fill_missing_var).pack(anchor=tk.W, padx=(20, 0))
        
        self.normalize_dates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cleaning_frame, text="Normalize date formats", 
                       variable=self.normalize_dates_var).pack(anchor=tk.W, padx=(20, 0))
        
        # Schema options
        schema_frame = ttk.Frame(options_frame)
        schema_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(schema_frame, text="Schema Options:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.standardize_columns_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(schema_frame, text="Standardize column names", 
                       variable=self.standardize_columns_var).pack(anchor=tk.W, padx=(20, 0))
        
        self.validate_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(schema_frame, text="Validate data integrity", 
                       variable=self.validate_data_var).pack(anchor=tk.W, padx=(20, 0))
        
    def create_batch_section(self, parent):
        """Create batch conversion section."""
        batch_frame = ttk.LabelFrame(parent, text="Batch Conversion", padding=10)
        batch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Batch options
        options_frame = ttk.Frame(batch_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.batch_convert_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Convert all files in directory", 
                       variable=self.batch_convert_var, 
                       command=self.toggle_batch_mode).pack(anchor=tk.W)
        
        # Batch directory selection
        self.batch_dir_frame = ttk.Frame(batch_frame)
        self.batch_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.batch_dir_frame, text="Batch Directory:").pack(side=tk.LEFT, padx=(0, 10))
        self.batch_dir_var = tk.StringVar()
        self.batch_dir_entry = ttk.Entry(self.batch_dir_frame, textvariable=self.batch_dir_var, 
                                        state='disabled', width=30)
        self.batch_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.batch_browse_btn = ttk.Button(self.batch_dir_frame, text="Browse", 
                                          command=self.browse_batch_directory, state='disabled')
        self.batch_browse_btn.pack(side=tk.RIGHT)
        
        # File pattern
        pattern_frame = ttk.Frame(batch_frame)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pattern_frame, text="File Pattern:").pack(side=tk.LEFT, padx=(0, 10))
        self.file_pattern_var = tk.StringVar(value="*.csv")
        self.file_pattern_entry = ttk.Entry(pattern_frame, textvariable=self.file_pattern_var, 
                                           state='disabled', width=20)
        self.file_pattern_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(pattern_frame, text="(e.g., *.csv, *.json, data_*.parquet)", 
                 font=("Arial", 8)).pack(side=tk.LEFT)
        
    def create_progress_section(self, parent):
        """Create progress tracking section."""
        progress_frame = ttk.LabelFrame(parent, text="Conversion Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to convert")
        self.status_label.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(progress_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.convert_btn = ttk.Button(button_frame, text="Start Conversion", 
                                     command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_conversion, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Results", 
                                   command=self.clear_results)
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Add tooltips to buttons
        self.add_tooltip(self.convert_btn, "Start converting selected files to the chosen format")
        self.add_tooltip(self.stop_btn, "Stop the current conversion process")
        self.add_tooltip(self.clear_btn, "Clear all conversion results from the display")
        
    def create_results_section(self, parent):
        """Create results display section."""
        results_frame = ttk.LabelFrame(parent, text="Conversion Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results tree
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('File', 'Input Format', 'Output Format', 'Status', 'Output File')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Results actions
        actions_frame = ttk.Frame(results_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        open_file_btn = ttk.Button(actions_frame, text="Open Output File", 
                                  command=self.open_output_file)
        open_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        open_dir_btn = ttk.Button(actions_frame, text="Open Output Directory", 
                                 command=self.open_output_directory)
        open_dir_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_data_btn = ttk.Button(actions_frame, text="Load to Data Tab", 
                                  command=self.load_to_data_tab)
        load_data_btn.pack(side=tk.RIGHT)
        
        # Add tooltips to action buttons
        self.add_tooltip(open_file_btn, "Open the selected converted file in default application")
        self.add_tooltip(open_dir_btn, "Open the output directory in file explorer")
        self.add_tooltip(load_data_btn, "Load the selected converted file into the Data tab")
        
    def setup_event_handlers(self):
        """Setup event handlers."""
        self.batch_convert_var.trace('w', lambda *args: self.toggle_batch_mode())
        
    def toggle_batch_mode(self):
        """Toggle batch conversion mode."""
        if self.batch_convert_var.get():
            self.batch_dir_entry.config(state='normal')
            self.file_pattern_entry.config(state='normal')
            self.batch_browse_btn.config(state='normal')
        else:
            self.batch_dir_entry.config(state='disabled')
            self.file_pattern_entry.config(state='disabled')
            self.batch_browse_btn.config(state='disabled')
            
    def browse_input_files(self):
        """Browse for input files."""
        filetypes = [
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("Parquet files", "*.parquet"),
            ("Feather files", "*.feather"),
            ("DuckDB files", "*.duckdb"),
            ("All files", "*.*")
        ]
        
        try:
            files = filedialog.askopenfilenames(
                title="Select Input Files",
                filetypes=filetypes
            )
        except Exception as e:
            self.logger.error(f"Error opening file dialog: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to open file dialog: {str(e)}")
            return
        
        if files:
            self.input_files_var.set(f"{len(files)} file(s) selected")
            self.input_files = list(files)
            
            # Auto-detect format from first file
            if len(files) == 1:
                self.auto_detect_format()
                
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def browse_batch_directory(self):
        """Browse for batch directory."""
        directory = filedialog.askdirectory(title="Select Batch Directory")
        if directory:
            self.batch_dir_var.set(directory)
            
    def auto_detect_format(self):
        """Auto-detect input format from file extension."""
        if hasattr(self, 'input_files') and self.input_files:
            first_file = self.input_files[0]
            ext = os.path.splitext(first_file)[1].lower()
            format_type = EXT_TO_FORMAT.get(ext, 'csv')
            self.input_format_var.set(format_type)
            
    def preview_input_file(self):
        """Preview input file contents."""
        if not hasattr(self, 'input_files') or not self.input_files:
            messagebox.showwarning("Warning", "No input files selected")
            return
            
        try:
            # Load first file for preview
            file_path = self.input_files[0]
            input_format = self.input_format_var.get()
            
            if not input_format:
                messagebox.showwarning("Warning", "Please select input format")
                return
                
            # Load data
            data = self.loader.load_file_by_type(file_path, input_format)
            
            # Show preview dialog
            self.show_preview_dialog(file_path, data)
            
        except Exception as e:
            self.logger.error(f"Error previewing file: {str(e)}")
            messagebox.showerror("Error", f"Failed to preview file: {str(e)}")
            
    def show_preview_dialog(self, file_path: str, data):
        """Show data preview dialog."""
        preview_window = tk.Toplevel(self.frame)
        preview_window.title(f"Preview: {os.path.basename(file_path)}")
        preview_window.geometry("800x600")
        
        # Info frame
        info_frame = ttk.Frame(preview_window)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"File: {os.path.basename(file_path)}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Shape: {data.shape[0]} rows × {data.shape[1]} columns").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Columns: {list(data.columns)}").pack(anchor=tk.W)
        
        # Data preview
        preview_frame = ttk.Frame(preview_window)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for preview
        preview_tree = ttk.Treeview(preview_frame, columns=list(data.columns), show='headings')
        
        # Configure columns
        for col in data.columns:
            preview_tree.heading(col, text=str(col))
            preview_tree.column(col, width=100)
            
        # Add data (first 100 rows)
        preview_data = data.head(100)
        for idx, row in preview_data.iterrows():
            preview_tree.insert('', 'end', values=list(row))
            
        # Scrollbars
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_tree.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=preview_tree.xview)
        
        preview_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
        
    def start_conversion(self):
        """Start conversion process."""
        if self.batch_convert_var.get():
            if not self.batch_dir_var.get():
                messagebox.showwarning("Warning", "Please select batch directory")
                return
        else:
            if not hasattr(self, 'input_files') or not self.input_files:
                messagebox.showwarning("Warning", "Please select input files")
                return
                
        if not self.output_format_var.get():
            messagebox.showwarning("Warning", "Please select output format")
            return
            
        # Clear previous results
        self.clear_results()
        
        # Start conversion in thread
        self.stop_event.clear()
        self.conversion_thread = threading.Thread(target=self._conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
        # Update UI
        self.convert_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Conversion in progress...")
        
    def _conversion_worker(self):
        """Worker thread for conversion process."""
        try:
            if self.batch_convert_var.get():
                self._batch_conversion_worker()
            else:
                self._single_conversion_worker()
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Conversion error: {error_msg}")
            self.main_window.run_in_main_thread(
                lambda: self.main_window.show_error_message("Error", f"Conversion failed: {error_msg}")
            )
        finally:
            self.main_window.run_in_main_thread(self._conversion_complete)
            
    def _single_conversion_worker(self):
        """Single file conversion worker."""
        total_files = len(self.input_files)
        
        for i, input_file in enumerate(self.input_files):
            if self.stop_event.is_set():
                break
                
            try:
                # Update progress
                progress = (i / total_files) * 100
                self.main_window.run_in_main_thread(
                    lambda p=progress: self.progress_var.set(p)
                )
                
                self.main_window.run_in_main_thread(
                    lambda f=input_file: self.status_label.config(text=f"Converting: {os.path.basename(f)}")
                )
                
                # Perform conversion
                output_file = self._convert_single_file(input_file)
                
                if output_file:
                    self.converted_files.append(output_file)
                    
                    # Add to results
                    self.main_window.run_in_main_thread(
                        lambda: self._add_conversion_result(
                            input_file, self.input_format_var.get(),
                            self.output_format_var.get(), "Success", output_file
                        )
                    )
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Error converting {input_file}: {error_msg}")
                self.main_window.run_in_main_thread(
                    lambda: self._add_conversion_result(
                        input_file, self.input_format_var.get(),
                        self.output_format_var.get(), f"Error: {error_msg}", ""
                    )
                )
                
    def _batch_conversion_worker(self):
        """Batch conversion worker."""
        import glob
        
        batch_dir = self.batch_dir_var.get()
        pattern = self.file_pattern_var.get()
        
        # Find files matching pattern
        search_pattern = os.path.join(batch_dir, pattern)
        files = glob.glob(search_pattern)
        
        if not files:
            raise ValueError(f"No files found matching pattern: {search_pattern}")
            
        total_files = len(files)
        
        for i, input_file in enumerate(files):
            if self.stop_event.is_set():
                break
                
            try:
                # Update progress
                progress = (i / total_files) * 100
                self.main_window.run_in_main_thread(
                    lambda p=progress: self.progress_var.set(p)
                )
                
                self.main_window.run_in_main_thread(
                    lambda f=input_file: self.status_label.config(text=f"Converting: {os.path.basename(f)}")
                )
                
                # Auto-detect input format
                ext = os.path.splitext(input_file)[1].lower()
                input_format = EXT_TO_FORMAT.get(ext, 'csv')
                
                # Perform conversion
                result = self._convert_single_file(input_file, input_format)
                
                if result and not result.startswith("Skipped:"):
                    # Successful conversion
                    self.converted_files.append(result)
                    
                    # Add to results
                    self.main_window.run_in_main_thread(
                        lambda: self._add_conversion_result(
                            input_file, input_format,
                            self.output_format_var.get(), "Success", result
                        )
                    )
                elif result and result.startswith("Skipped:"):
                    # File was skipped
                    self.main_window.run_in_main_thread(
                        lambda: self._add_conversion_result(
                            input_file, input_format,
                            self.output_format_var.get(), result, ""
                        )
                    )
                    
            except Exception as e:
                error_msg = str(e)  # Capture exception message
                self.logger.error(f"Error converting {input_file}: {error_msg}")
                self.main_window.run_in_main_thread(
                    lambda: self._add_conversion_result(
                        input_file, input_format,
                        self.output_format_var.get(), f"Error: {error_msg}", ""
                    )
                )
                
    def _convert_single_file(self, input_file: str, input_format: str = None) -> str:
        """Convert a single file."""
        if input_format is None:
            input_format = self.input_format_var.get()
            
        output_format = self.output_format_var.get()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_ext = FORMAT_DIALOG_INFO[output_format][0]  # First element is extension
        output_filename = f"{base_name}_converted{output_ext}"
        
        # Create output directory
        output_dir = self.output_dir_var.get()
        if self.create_subdir_var.get():
            output_dir = os.path.join(output_dir, output_format)
            
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, output_filename)
        
        # Check if file exists
        if os.path.exists(output_file) and not self.overwrite_var.get():
            # Instead of raising an error, skip the file and log a warning
            self.logger.warning(f"Skipping {input_file}: Output file already exists: {output_file}")
            return f"Skipped: File already exists"
            
        # Load input data
        data = self.loader.load_file_by_type(input_file, input_format)
        
        # Apply data cleaning options
        if self.remove_duplicates_var.get():
            data = data.drop_duplicates()
            
        if self.fill_missing_var.get():
            data = data.fillna(method='ffill').fillna(method='bfill')
            
        if self.normalize_dates_var.get():
            # Try to normalize date columns
            date_cols = ['date', 'timestamp', '<DATE>', '<TIME>']
            for col in date_cols:
                if col in data.columns:
                    try:
                        data[col] = pd.to_datetime(data[col], utc=True)
                    except:
                        pass
                        
        if self.standardize_columns_var.get():
            # Standardize column names
            data.columns = [col.strip().replace(' ', '_').replace('<', '').replace('>', '') 
                           for col in data.columns]
                           
        if self.validate_data_var.get():
            # Basic validation
            if data.empty:
                raise ValueError("Data is empty after processing")
                
        # Save output data
        self.converter.save_file_by_type(data, output_file, output_format)
        
        return output_file
        
    def _add_conversion_result(self, input_file: str, input_format: str, 
                              output_format: str, status: str, output_file: str):
        """Add conversion result to results tree."""
        self.results_tree.insert('', 'end', values=(
            os.path.basename(input_file),
            input_format,
            output_format,
            status,
            os.path.basename(output_file) if output_file else ""
        ))
        
    def stop_conversion(self):
        """Stop conversion process."""
        self.stop_event.set()
        self.status_label.config(text="Stopping conversion...")
        
    def _conversion_complete(self):
        """Handle conversion completion."""
        self.convert_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_var.set(100)
        
        if self.stop_event.is_set():
            self.status_label.config(text="Conversion stopped")
        else:
            self.status_label.config(text=f"Conversion complete: {len(self.converted_files)} files converted")
            
    def clear_results(self):
        """Clear conversion results."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.converted_files.clear()
        self.progress_var.set(0)
        
    def open_output_file(self):
        """Open selected output file."""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return
            
        item = self.results_tree.item(selected[0])
        output_file = item['values'][4]
        
        if output_file:
            import subprocess
            import platform
            
            output_path = os.path.join(self.output_dir_var.get(), output_file)
            if os.path.exists(output_path):
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_path])
                    elif platform.system() == 'Windows':
                        os.startfile(output_path)
                    else:  # Linux/Container
                        # Try xdg-open first, fallback to showing file path
                        try:
                            subprocess.run(['xdg-open', output_path], check=True)
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            # xdg-open not available (common in Docker containers)
                            messagebox.showinfo(
                                "Output File", 
                                f"File location:\n{output_path}\n\n"
                                "Note: File opener not available in this environment.\n"
                                "You can access the file through the file system."
                            )
                except Exception as e:
                    self.logger.error(f"Error opening file: {str(e)}")
                    # Show file path instead of error
                    messagebox.showinfo(
                        "Output File", 
                        f"File location:\n{output_path}\n\n"
                        "File opener not available in this environment."
                    )
            else:
                messagebox.showwarning("Warning", "Output file not found")
        else:
            messagebox.showwarning("Warning", "No output file available")
            
    def open_output_directory(self):
        """Open output directory."""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            import subprocess
            import platform
            
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', output_dir])
                elif platform.system() == 'Windows':
                    os.startfile(output_dir)
                else:  # Linux/Container
                    # Try xdg-open first, fallback to showing path in message
                    try:
                        subprocess.run(['xdg-open', output_dir], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # xdg-open not available (common in Docker containers)
                        import tkinter as tk
                        from tkinter import messagebox
                        messagebox.showinfo(
                            "Output Directory", 
                            f"Output directory location:\n{output_dir}\n\n"
                            "Note: File explorer not available in this environment.\n"
                            "You can access the files through the file system."
                        )
            except Exception as e:
                self.logger.error(f"Error opening directory: {str(e)}")
                # Show directory path instead of error
                import tkinter as tk
                from tkinter import messagebox
                messagebox.showinfo(
                    "Output Directory", 
                    f"Output directory location:\n{output_dir}\n\n"
                    "File explorer not available in this environment."
                )
        else:
            messagebox.showwarning("Warning", "Output directory does not exist")
            
    def load_to_data_tab(self):
        """Load selected converted file to data tab."""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return
            
        item = self.results_tree.item(selected[0])
        output_file = item['values'][4]
        
        if output_file and item['values'][3] == "Success":
            output_path = os.path.join(self.output_dir_var.get(), output_file)
            if os.path.exists(output_path):
                # Switch to data tab and load file
                self.main_window.switch_to_tab("Data")
                self.main_window.data_tab.load_file(output_path)
            else:
                messagebox.showwarning("Warning", "Output file not found")
        else:
            messagebox.showwarning("Warning", "No successful conversion available")
    
    def add_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0",
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
            
    def on_tab_activated(self):
        """Handle tab activation."""
        # Refresh any necessary data when tab becomes active
        pass
    
    def on_window_resize(self):
        """Handle window resize events."""
        try:
            # Update results tree layout if needed
            if hasattr(self, 'results_tree') and self.results_tree:
                # Could update tree column widths or refresh display
                pass
                
        except Exception as e:
            self.logger.error(f"Error handling window resize in ConverterTab: {str(e)}")
