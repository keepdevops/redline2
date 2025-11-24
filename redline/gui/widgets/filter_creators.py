#!/usr/bin/env python3
"""
Filter Creators Helper for FilterDialog
Handles creation of filter UI tabs and widgets.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class FilterCreatorsHelper:
    """Helper class for creating filter UI in FilterDialog."""
    
    def __init__(self, filter_dialog):
        """Initialize with reference to FilterDialog."""
        self.filter_dialog = filter_dialog
        self.logger = logging.getLogger(__name__)
    
    def create_date_filter_tab(self):
        """Create date/time filter tab."""
        date_frame = ttk.Frame(self.filter_dialog.notebook)
        self.filter_dialog.notebook.add(date_frame, text="Date/Time")
        
        # Date range filter
        date_range_frame = ttk.LabelFrame(date_frame, text="Date Range Filter", padding=10)
        date_range_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start date
        ttk.Label(date_range_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.filter_dialog.start_date_var = tk.StringVar()
        self.filter_dialog.start_date_entry = ttk.Entry(date_range_frame, textvariable=self.filter_dialog.start_date_var, width=15)
        self.filter_dialog.start_date_entry.grid(row=0, column=1, padx=(0, 10))
        
        # End date
        ttk.Label(date_range_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_dialog.end_date_var = tk.StringVar()
        self.filter_dialog.end_date_entry = ttk.Entry(date_range_frame, textvariable=self.filter_dialog.end_date_var, width=15)
        self.filter_dialog.end_date_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Quick date preset buttons
        quick_date_frame = ttk.Frame(date_range_frame)
        quick_date_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(quick_date_frame, text="Quick Filters:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 7 Days", 
                  command=lambda: self.filter_dialog.set_date_preset(7)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 30 Days", 
                  command=lambda: self.filter_dialog.set_date_preset(30)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 90 Days", 
                  command=lambda: self.filter_dialog.set_date_preset(90)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last Year", 
                  command=lambda: self.filter_dialog.set_date_preset(365)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Clear Dates", 
                  command=self.filter_dialog.clear_date_filter).pack(side=tk.LEFT, padx=(5, 0))
        
        # Date format help
        ttk.Label(date_range_frame, text="Format: YYYY-MM-DD (e.g., 2024-01-01)", 
                 font=("Arial", 8)).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Time-based filters
        time_frame = ttk.LabelFrame(date_frame, text="Time-based Filters", padding=10)
        time_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Weekday filter
        self.filter_dialog.weekday_var = tk.StringVar()
        weekday_combo = ttk.Combobox(time_frame, textvariable=self.filter_dialog.weekday_var, width=15)
        weekday_combo['values'] = ['Any', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_combo.set('Any')
        weekday_combo.grid(row=0, column=1, padx=(0, 10))
        ttk.Label(time_frame, text="Weekday:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Month filter
        self.filter_dialog.month_var = tk.StringVar()
        month_combo = ttk.Combobox(time_frame, textvariable=self.filter_dialog.month_var, width=15)
        month_combo['values'] = ['Any', 'January', 'February', 'March', 'April', 'May', 'June',
                                'July', 'August', 'September', 'October', 'November', 'December']
        month_combo.set('Any')
        month_combo.grid(row=1, column=1, padx=(0, 10))
        ttk.Label(time_frame, text="Month:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
    
    def create_numeric_filter_tab(self):
        """Create numeric filter tab."""
        numeric_frame = ttk.Frame(self.filter_dialog.notebook)
        self.filter_dialog.notebook.add(numeric_frame, text="Numeric")
        
        # Detect numeric columns
        numeric_columns = self.filter_dialog.data.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_columns:
            ttk.Label(numeric_frame, text="No numeric columns found in data.").pack(pady=20)
            return
            
        # Create filters for each numeric column
        for i, column in enumerate(numeric_columns):
            col_frame = ttk.LabelFrame(numeric_frame, text=f"Filter by {column}", padding=10)
            col_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Min value
            ttk.Label(col_frame, text="Min:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            min_var = tk.StringVar()
            min_entry = ttk.Entry(col_frame, textvariable=min_var, width=10)
            min_entry.grid(row=0, column=1, padx=(0, 10))
            
            # Max value
            ttk.Label(col_frame, text="Max:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
            max_var = tk.StringVar()
            max_entry = ttk.Entry(col_frame, textvariable=max_var, width=10)
            max_entry.grid(row=0, column=3, padx=(0, 10))
            
            # Store variables for later use
            self.filter_dialog.filters[f"{column}_min"] = min_var
            self.filter_dialog.filters[f"{column}_max"] = max_var
            
            # Show column statistics
            stats = self.filter_dialog.data[column].describe()
            stats_text = f"Range: {stats['min']:.2f} to {stats['max']:.2f}, Mean: {stats['mean']:.2f}"
            ttk.Label(col_frame, text=stats_text, font=("Arial", 8)).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
    
    def create_text_filter_tab(self):
        """Create text filter tab."""
        text_frame = ttk.Frame(self.filter_dialog.notebook)
        self.filter_dialog.notebook.add(text_frame, text="Text")
        
        # Detect text columns
        text_columns = self.filter_dialog.data.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if not text_columns:
            ttk.Label(text_frame, text="No text columns found in data.").pack(pady=20)
            return
            
        # Create filters for each text column
        for i, column in enumerate(text_columns):
            col_frame = ttk.LabelFrame(text_frame, text=f"Filter by {column}", padding=10)
            col_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Contains filter
            ttk.Label(col_frame, text="Contains:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            contains_var = tk.StringVar()
            contains_entry = ttk.Entry(col_frame, textvariable=contains_var, width=20)
            contains_entry.grid(row=0, column=1, padx=(0, 10))
            
            # Exact match filter
            ttk.Label(col_frame, text="Exact:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
            exact_var = tk.StringVar()
            exact_entry = ttk.Entry(col_frame, textvariable=exact_var, width=20)
            exact_entry.grid(row=0, column=3, padx=(0, 10))
            
            # Store variables for later use
            self.filter_dialog.filters[f"{column}_contains"] = contains_var
            self.filter_dialog.filters[f"{column}_exact"] = exact_var
            
            # Show unique values (limited)
            unique_values = self.filter_dialog.data[column].unique()[:10]  # Show first 10 unique values
            if len(self.filter_dialog.data[column].unique()) > 10:
                unique_text = f"Sample values: {', '.join(map(str, unique_values))}... (and {len(self.filter_dialog.data[column].unique()) - 10} more)"
            else:
                unique_text = f"Values: {', '.join(map(str, unique_values))}"
            ttk.Label(col_frame, text=unique_text, font=("Arial", 8)).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
    
    def create_advanced_filter_tab(self):
        """Create advanced filter tab."""
        advanced_frame = ttk.Frame(self.filter_dialog.notebook)
        self.filter_dialog.notebook.add(advanced_frame, text="Advanced")
        
        # Custom SQL-like filter
        sql_frame = ttk.LabelFrame(advanced_frame, text="Custom Expression", padding=10)
        sql_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(sql_frame, text="Enter pandas query expression:").pack(anchor=tk.W)
        
        # Show available columns info
        if hasattr(self.filter_dialog, 'data') and self.filter_dialog.data is not None:
            available_cols = [col for col in self.filter_dialog.data.columns if col not in ['format']]
            cols_text = f"Available columns: {', '.join(available_cols)}"
            ttk.Label(sql_frame, text=cols_text, font=("Arial", 8), foreground="blue").pack(anchor=tk.W, pady=(0, 5))
        
        self.filter_dialog.custom_filter_var = tk.StringVar()
        self.filter_dialog.custom_filter_entry = tk.Text(sql_frame, height=4, width=60)
        self.filter_dialog.custom_filter_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Example expressions
        examples_frame = ttk.Frame(sql_frame)
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(examples_frame, text="Examples:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        # Examples with correct column names based on actual data structure
        examples = [
            "close > 100",
            "vol > vol.mean()",
            "ticker == 'MSFT'",
            "(high - low) / close > 0.05"
        ]
        
        for example in examples:
            ttk.Label(examples_frame, text=f"  {example}", font=("Arial", 8)).pack(anchor=tk.W)
        
        # Additional helpful examples
        ttk.Label(examples_frame, text="More examples:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 0))
        more_examples = [
            "open > close",
            "vol > 50000000",
            "ticker == 'AAPL'",
            "(high - low) / open * 100 > 2"
        ]
        
        for example in more_examples:
            ttk.Label(examples_frame, text=f"  {example}", font=("Arial", 8)).pack(anchor=tk.W)
            
        # Row limit
        limit_frame = ttk.Frame(advanced_frame)
        limit_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(limit_frame, text="Limit results to:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_dialog.row_limit_var = tk.StringVar(value="1000")
        limit_entry = ttk.Entry(limit_frame, textvariable=self.filter_dialog.row_limit_var, width=10)
        limit_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(limit_frame, text="rows (0 = no limit)").pack(side=tk.LEFT)
    
    def create_column_info_section(self, parent):
        """Create column information section."""
        col_info_frame = ttk.LabelFrame(parent, text="Data Columns", padding=10)
        col_info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Show column names and types
        col_info_text = "Available columns:\n"
        for col in self.filter_dialog.data.columns:
            col_type = str(self.filter_dialog.data[col].dtype)
            col_info_text += f"  • {col} ({col_type})\n"
        
        col_info_label = ttk.Label(col_info_frame, text=col_info_text, 
                                  font=("Courier", 9), justify=tk.LEFT)
        col_info_label.pack(anchor=tk.W)
    
    def create_buttons(self, parent):
        """Create dialog buttons."""
        self.logger.info("Creating filter dialog buttons")
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        reset_btn = ttk.Button(left_buttons, text="Reset All", 
                              command=self.filter_dialog.reset_all_filters)
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        preview_btn = ttk.Button(left_buttons, text="Update Preview", 
                                command=self.filter_dialog.update_preview)
        preview_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        cancel_btn = ttk.Button(right_buttons, text="Cancel", 
                               command=self.filter_dialog.cancel_filter)
        cancel_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        apply_btn = ttk.Button(right_buttons, text="Apply Filter", 
                              command=self.filter_dialog.apply_filter)
        apply_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.logger.info("Filter dialog buttons created successfully")

