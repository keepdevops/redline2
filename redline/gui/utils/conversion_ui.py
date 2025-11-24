#!/usr/bin/env python3
"""
Conversion UI Helper for ConverterTab
Handles UI creation and event handlers for the converter tab.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from redline.core.schema import FORMAT_DIALOG_INFO

logger = logging.getLogger(__name__)


class ConversionUIHelper:
    """Helper class for UI creation in ConverterTab."""
    
    def __init__(self, converter_tab):
        """Initialize with reference to ConverterTab."""
        self.converter_tab = converter_tab
        self.logger = logging.getLogger(__name__)
    
    def create_input_section(self, parent):
        """Create input file selection section."""
        input_frame = ttk.LabelFrame(parent, text="Input Files", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # File selection
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.converter_tab.input_files_var = tk.StringVar()
        self.converter_tab.input_files_entry = ttk.Entry(file_frame, textvariable=self.converter_tab.input_files_var, 
                                          state='readonly', width=50)
        self.converter_tab.input_files_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse Files", 
                  command=self.converter_tab.browser_helper.browse_input_files).pack(side=tk.RIGHT)
        
        # Input format detection
        format_frame = ttk.Frame(input_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Input Format:").pack(side=tk.LEFT, padx=(0, 10))
        self.converter_tab.input_format_var = tk.StringVar()
        self.converter_tab.input_format_combo = ttk.Combobox(format_frame, textvariable=self.converter_tab.input_format_var,
                                              state='readonly', width=15)
        self.converter_tab.input_format_combo['values'] = list(FORMAT_DIALOG_INFO.keys())
        self.converter_tab.input_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(format_frame, text="Auto-detect", 
                  command=self.converter_tab.browser_helper.auto_detect_format).pack(side=tk.LEFT)
        
        # Preview button
        ttk.Button(input_frame, text="Preview Input File", 
                  command=self.converter_tab.browser_helper.preview_input_file).pack(anchor=tk.W)
    
    def create_output_section(self, parent):
        """Create output configuration section."""
        output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 10))
        self.converter_tab.output_dir_var = tk.StringVar(value="data/converted")
        self.converter_tab.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.converter_tab.output_dir_var, width=30)
        self.converter_tab.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.converter_tab.browser_helper.browse_output_directory).pack(side=tk.RIGHT)
        
        # Output format
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 10))
        self.converter_tab.output_format_var = tk.StringVar(value="csv")
        self.converter_tab.output_format_combo = ttk.Combobox(format_frame, textvariable=self.converter_tab.output_format_var,
                                               state='readonly', width=15)
        self.converter_tab.output_format_combo['values'] = list(FORMAT_DIALOG_INFO.keys())
        self.converter_tab.output_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Output options
        options_frame = ttk.Frame(output_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.converter_tab.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.converter_tab.overwrite_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.converter_tab.create_subdir_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create subdirectory by format", 
                       variable=self.converter_tab.create_subdir_var).pack(side=tk.LEFT)
    
    def create_conversion_options(self, parent):
        """Create conversion options section."""
        options_frame = ttk.LabelFrame(parent, text="Data Cleaning Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Data cleaning options
        cleaning_frame = ttk.Frame(options_frame)
        cleaning_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cleaning_frame, text="Data Cleaning (Applied before conversion):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Remove duplicates
        self.converter_tab.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            cleaning_frame,
            text="Remove Duplicate Rows",
            variable=self.converter_tab.remove_duplicates_var
        ).pack(anchor=tk.W, padx=(20, 0), pady=5)
        
        ttk.Label(
            cleaning_frame,
            text="Removes rows that are exact duplicates. If ticker and timestamp columns exist,\nduplicates are detected based on those columns.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(40, 0), pady=(0, 10))
        
        # Handle missing values
        ttk.Label(cleaning_frame, text="Handle Missing Values:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=(20, 0), pady=(5, 5))
        
        self.converter_tab.handle_missing_var = tk.StringVar(value="drop")
        missing_frame = ttk.Frame(cleaning_frame)
        missing_frame.pack(fill=tk.X, padx=(40, 0), pady=(0, 10))
        
        ttk.Radiobutton(
            missing_frame,
            text="Drop rows with missing values",
            variable=self.converter_tab.handle_missing_var,
            value="drop"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            missing_frame,
            text="Forward fill (use previous value)",
            variable=self.converter_tab.handle_missing_var,
            value="forward_fill"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            missing_frame,
            text="Backward fill (use next value)",
            variable=self.converter_tab.handle_missing_var,
            value="backward_fill"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            missing_frame,
            text="Don't handle missing values",
            variable=self.converter_tab.handle_missing_var,
            value="none"
        ).pack(anchor=tk.W)
        
        # Clean column names
        self.converter_tab.clean_column_names_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            cleaning_frame,
            text="Clean column names (remove unnamed/empty columns)",
            variable=self.converter_tab.clean_column_names_var
        ).pack(anchor=tk.W, padx=(20, 0), pady=10)
    
    def create_batch_section(self, parent):
        """Create batch conversion section."""
        batch_frame = ttk.LabelFrame(parent, text="Batch Conversion", padding=10)
        batch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Batch options
        options_frame = ttk.Frame(batch_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.converter_tab.batch_convert_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Convert all files in directory", 
                       variable=self.converter_tab.batch_convert_var, 
                       command=self.converter_tab.events_helper.toggle_batch_mode).pack(anchor=tk.W)
        
        # Batch directory selection
        self.converter_tab.batch_dir_frame = ttk.Frame(batch_frame)
        self.converter_tab.batch_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.converter_tab.batch_dir_frame, text="Batch Directory:").pack(side=tk.LEFT, padx=(0, 10))
        self.converter_tab.batch_dir_var = tk.StringVar()
        self.converter_tab.batch_dir_entry = ttk.Entry(self.converter_tab.batch_dir_frame, textvariable=self.converter_tab.batch_dir_var, 
                                        state='disabled', width=30)
        self.converter_tab.batch_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.converter_tab.batch_browse_btn = ttk.Button(self.converter_tab.batch_dir_frame, text="Browse", 
                                          command=self.converter_tab.browser_helper.browse_batch_directory, state='disabled')
        self.converter_tab.batch_browse_btn.pack(side=tk.RIGHT)
        
        # File pattern
        pattern_frame = ttk.Frame(batch_frame)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pattern_frame, text="File Pattern:").pack(side=tk.LEFT, padx=(0, 10))
        self.converter_tab.file_pattern_var = tk.StringVar(value="*.csv")
        self.converter_tab.file_pattern_entry = ttk.Entry(pattern_frame, textvariable=self.converter_tab.file_pattern_var, 
                                           state='disabled', width=20)
        self.converter_tab.file_pattern_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(pattern_frame, text="(e.g., *.csv, *.json, data_*.parquet)", 
                 font=("Arial", 8)).pack(side=tk.LEFT)
    
    def create_progress_section(self, parent):
        """Create progress tracking section."""
        progress_frame = ttk.LabelFrame(parent, text="Conversion Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress bar
        self.converter_tab.progress_var = tk.DoubleVar()
        self.converter_tab.progress_bar = ttk.Progressbar(progress_frame, variable=self.converter_tab.progress_var, 
                                           maximum=100, length=400)
        self.converter_tab.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.converter_tab.status_label = ttk.Label(progress_frame, text="Ready to convert")
        self.converter_tab.status_label.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(progress_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.converter_tab.convert_btn = ttk.Button(button_frame, text="Start Conversion", 
                                     command=self.converter_tab.events_helper.start_conversion)
        self.converter_tab.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.converter_tab.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.converter_tab.events_helper.stop_conversion, state='disabled')
        self.converter_tab.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.converter_tab.clear_btn = ttk.Button(button_frame, text="Clear Results", 
                                   command=self.converter_tab.events_helper.clear_results)
        self.converter_tab.clear_btn.pack(side=tk.RIGHT)
        
        # Add tooltips to buttons
        self.add_tooltip(self.converter_tab.convert_btn, "Start converting selected files to the chosen format")
        self.add_tooltip(self.converter_tab.stop_btn, "Stop the current conversion process")
        self.add_tooltip(self.converter_tab.clear_btn, "Clear all conversion results from the display")
    
    def create_results_section(self, parent):
        """Create results display section."""
        results_frame = ttk.LabelFrame(parent, text="Conversion Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results tree
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('File', 'Input Format', 'Output Format', 'Status', 'Output File')
        self.converter_tab.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.converter_tab.results_tree.heading(col, text=col)
            self.converter_tab.results_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.converter_tab.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.converter_tab.results_tree.xview)
        
        self.converter_tab.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.converter_tab.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Results actions
        actions_frame = ttk.Frame(results_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        open_file_btn = ttk.Button(actions_frame, text="Open Output File", 
                                  command=self.converter_tab.browser_helper.open_output_file)
        open_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        open_dir_btn = ttk.Button(actions_frame, text="Open Output Directory", 
                                 command=self.converter_tab.browser_helper.open_output_directory)
        open_dir_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_data_btn = ttk.Button(actions_frame, text="Load to Data Tab", 
                                  command=self.converter_tab.events_helper.load_to_data_tab)
        load_data_btn.pack(side=tk.RIGHT)
        
        # Add tooltips to action buttons
        self.add_tooltip(open_file_btn, "Open the selected converted file in default application")
        self.add_tooltip(open_dir_btn, "Open the output directory in file explorer")
        self.add_tooltip(load_data_btn, "Load the selected converted file into the Data tab")
    
    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        def on_enter(e):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{e.x_root + 10}+{e.y_root + 10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            def on_leave(e):
                tooltip.destroy()
            
            widget.bind('<Leave>', on_leave)
        
        widget.bind('<Enter>', on_enter)


