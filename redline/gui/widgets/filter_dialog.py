#!/usr/bin/env python3
"""
REDLINE Filter Dialog
Advanced filtering interface for financial data.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
import pandas as pd

logger = logging.getLogger(__name__)

class FilterDialog:
    """Advanced filter dialog for financial data."""
    
    def __init__(self, parent, data: pd.DataFrame, callback: Callable):
        """
        Initialize filter dialog.
        
        Args:
            parent: Parent window
            data: DataFrame to filter
            callback: Function to call with filtered data
        """
        self.parent = parent
        self.data = data
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
        # Filter criteria
        self.filters = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Filter Data")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set dialog size and position
        self.dialog.geometry("900x700+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        self.setup_event_handlers()
        
        # Show initial preview
        self.update_preview()
        
        # Show available columns for debugging
        self.logger.info(f"Filter dialog opened with data columns: {list(self.data.columns)}")
        self.logger.info(f"Data shape: {self.data.shape}")
        self.logger.info(f"Data types: {self.data.dtypes.to_dict()}")
        
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Test button at the top (for debugging)
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill=tk.X, pady=(0, 10))
        
        test_btn = ttk.Button(test_frame, text="🧪 TEST FILTER (Click Me!)", 
                             command=self.test_filter, style="Accent.TButton")
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        apply_btn = ttk.Button(test_frame, text="✅ APPLY FILTER", 
                              command=self.apply_filter, style="Accent.TButton")
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add a simple message to help users
        help_label = ttk.Label(test_frame, text="Click TEST FILTER to apply a 30-day filter, or use APPLY FILTER for custom filters", 
                              font=("Arial", 9), foreground="blue")
        help_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Data Filtering", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create notebook for different filter types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Date/Time filters
        self.create_date_filter_tab()
        
        # Numeric filters
        self.create_numeric_filter_tab()
        
        # Text filters
        self.create_text_filter_tab()
        
        # Advanced filters
        self.create_advanced_filter_tab()
        
        # Column information section
        self.create_column_info_section(main_frame)
        
        # Preview section
        self.create_preview_section(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
    def create_date_filter_tab(self):
        """Create date/time filter tab."""
        date_frame = ttk.Frame(self.notebook)
        self.notebook.add(date_frame, text="Date/Time")
        
        # Date range filter
        date_range_frame = ttk.LabelFrame(date_frame, text="Date Range Filter", padding=10)
        date_range_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start date
        ttk.Label(date_range_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(date_range_frame, textvariable=self.start_date_var, width=15)
        self.start_date_entry.grid(row=0, column=1, padx=(0, 10))
        
        # End date
        ttk.Label(date_range_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(date_range_frame, textvariable=self.end_date_var, width=15)
        self.end_date_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Quick date preset buttons
        quick_date_frame = ttk.Frame(date_range_frame)
        quick_date_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(quick_date_frame, text="Quick Filters:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 7 Days", 
                  command=lambda: self.set_date_preset(7)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 30 Days", 
                  command=lambda: self.set_date_preset(30)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last 90 Days", 
                  command=lambda: self.set_date_preset(90)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Last Year", 
                  command=lambda: self.set_date_preset(365)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_date_frame, text="Clear Dates", 
                  command=self.clear_date_filter).pack(side=tk.LEFT, padx=(5, 0))
        
        # Date format help
        ttk.Label(date_range_frame, text="Format: YYYY-MM-DD (e.g., 2024-01-01)", 
                 font=("Arial", 8)).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Time-based filters
        time_frame = ttk.LabelFrame(date_frame, text="Time-based Filters", padding=10)
        time_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Weekday filter
        self.weekday_var = tk.StringVar()
        weekday_combo = ttk.Combobox(time_frame, textvariable=self.weekday_var, width=15)
        weekday_combo['values'] = ['Any', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_combo.set('Any')
        weekday_combo.grid(row=0, column=1, padx=(0, 10))
        ttk.Label(time_frame, text="Weekday:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Month filter
        self.month_var = tk.StringVar()
        month_combo = ttk.Combobox(time_frame, textvariable=self.month_var, width=15)
        month_combo['values'] = ['Any', 'January', 'February', 'March', 'April', 'May', 'June',
                                'July', 'August', 'September', 'October', 'November', 'December']
        month_combo.set('Any')
        month_combo.grid(row=1, column=1, padx=(0, 10))
        ttk.Label(time_frame, text="Month:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        
    def create_numeric_filter_tab(self):
        """Create numeric filter tab."""
        numeric_frame = ttk.Frame(self.notebook)
        self.notebook.add(numeric_frame, text="Numeric")
        
        # Detect numeric columns
        numeric_columns = self.data.select_dtypes(include=['number']).columns.tolist()
        
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
            self.filters[f"{column}_min"] = min_var
            self.filters[f"{column}_max"] = max_var
            
            # Show column statistics
            stats = self.data[column].describe()
            stats_text = f"Range: {stats['min']:.2f} to {stats['max']:.2f}, Mean: {stats['mean']:.2f}"
            ttk.Label(col_frame, text=stats_text, font=("Arial", 8)).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
            
    def create_text_filter_tab(self):
        """Create text filter tab."""
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Text")
        
        # Detect text columns
        text_columns = self.data.select_dtypes(include=['object', 'string']).columns.tolist()
        
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
            self.filters[f"{column}_contains"] = contains_var
            self.filters[f"{column}_exact"] = exact_var
            
            # Show unique values (limited)
            unique_values = self.data[column].unique()[:10]  # Show first 10 unique values
            if len(self.data[column].unique()) > 10:
                unique_text = f"Sample values: {', '.join(map(str, unique_values))}... (and {len(self.data[column].unique()) - 10} more)"
            else:
                unique_text = f"Values: {', '.join(map(str, unique_values))}"
            ttk.Label(col_frame, text=unique_text, font=("Arial", 8)).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
            
    def create_advanced_filter_tab(self):
        """Create advanced filter tab."""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Custom SQL-like filter
        sql_frame = ttk.LabelFrame(advanced_frame, text="Custom Expression", padding=10)
        sql_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(sql_frame, text="Enter pandas query expression:").pack(anchor=tk.W)
        
        # Show available columns info
        if hasattr(self, 'data') and self.data is not None:
            available_cols = [col for col in self.data.columns if col not in ['format']]
            cols_text = f"Available columns: {', '.join(available_cols)}"
            ttk.Label(sql_frame, text=cols_text, font=("Arial", 8), foreground="blue").pack(anchor=tk.W, pady=(0, 5))
        
        self.custom_filter_var = tk.StringVar()
        self.custom_filter_entry = tk.Text(sql_frame, height=4, width=60)
        self.custom_filter_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
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
        self.row_limit_var = tk.StringVar(value="1000")
        limit_entry = ttk.Entry(limit_frame, textvariable=self.row_limit_var, width=10)
        limit_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(limit_frame, text="rows (0 = no limit)").pack(side=tk.LEFT)
        
    def create_preview_section(self, parent):
        """Create preview section."""
        preview_frame = ttk.LabelFrame(parent, text="Filter Preview", padding=10)
        preview_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Preview info
        self.preview_label = ttk.Label(preview_frame, text=f"Original data: {len(self.data)} rows, {len(self.data.columns)} columns")
        self.preview_label.pack(anchor=tk.W)
        
        # Update preview button
        ttk.Button(preview_frame, text="Update Preview", 
                  command=self.update_preview).pack(anchor=tk.W, pady=(5, 0))
        
        # Preview results
        self.preview_text = tk.Text(preview_frame, height=4, width=70)
        self.preview_text.pack(fill=tk.X, pady=(5, 0))
        
        # Scrollbar for preview
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
    
    def create_column_info_section(self, parent):
        """Create column information section."""
        col_info_frame = ttk.LabelFrame(parent, text="Data Columns", padding=10)
        col_info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Show column names and types
        col_info_text = "Available columns:\n"
        for col in self.data.columns:
            col_type = str(self.data[col].dtype)
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
                              command=self.reset_all_filters)
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        preview_btn = ttk.Button(left_buttons, text="Update Preview", 
                                command=self.update_preview)
        preview_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        cancel_btn = ttk.Button(right_buttons, text="Cancel", 
                               command=self.cancel_filter)
        cancel_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        apply_btn = ttk.Button(right_buttons, text="Apply Filter", 
                              command=self.apply_filter)
        apply_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.logger.info("Filter dialog buttons created successfully")
    
    def test_filter(self):
        """Test filter functionality."""
        self.logger.info("TEST FILTER button clicked!")
        try:
            # Apply a simple filter (last 30 days)
            self.set_date_preset(30)
            self.update_preview()
            
            # Actually apply the filter to the main display
            self.logger.info("Applying test filter to main display...")
            filtered_data = self.apply_filters_to_data(self.data)
            
            if filtered_data is not None and len(filtered_data) > 0:
                self.logger.info(f"Test filter successful: {len(filtered_data)} rows, calling callback")
                # Use the main window's thread-safe method to update GUI
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'run_in_main_thread'):
                    self.main_window.run_in_main_thread(lambda: self.callback(filtered_data))
                else:
                    self.callback(filtered_data)
                self.dialog.destroy()
                self.logger.info("Test filter applied successfully to main display")
            else:
                self.logger.warning("Test filter returned no data")
                
        except Exception as e:
            self.logger.error(f"Test filter failed: {str(e)}")
        
    def setup_event_handlers(self):
        """Setup event handlers."""
        # Auto-update preview when filters change
        self.dialog.bind('<KeyRelease>', lambda e: self.schedule_preview_update())
        
        # Bind to combobox changes
        for widget in self.dialog.winfo_children():
            self._bind_widget_changes(widget)
    
    def _bind_widget_changes(self, widget):
        """Recursively bind to widget changes for auto-preview updates."""
        try:
            if isinstance(widget, ttk.Combobox):
                widget.bind('<<ComboboxSelected>>', lambda e: self.schedule_preview_update())
            elif isinstance(widget, (tk.Entry, tk.Spinbox)):
                widget.bind('<KeyRelease>', lambda e: self.schedule_preview_update())
            elif isinstance(widget, ttk.Checkbutton):
                widget.bind('<Button-1>', lambda e: self.schedule_preview_update())
            
            # Recursively bind to children
            for child in widget.winfo_children():
                self._bind_widget_changes(child)
        except:
            pass  # Ignore binding errors
        
    def schedule_preview_update(self):
        """Schedule preview update to avoid too frequent updates."""
        if hasattr(self, '_preview_timer'):
            self.dialog.after_cancel(self._preview_timer)
        self._preview_timer = self.dialog.after(500, self.update_preview)
        
    def set_date_preset(self, days: int):
        """Set date filter to last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        
    def clear_date_filter(self):
        """Clear date filter."""
        self.start_date_var.set('')
        self.end_date_var.set('')
        
    def update_preview(self):
        """Update filter preview."""
        try:
            filtered_data = self.apply_filters_to_data(self.data, preview=True)
            
            if filtered_data is not None:
                self.preview_label.config(text=f"Original: {len(self.data)} rows → Filtered: {len(filtered_data)} rows")
                
                # Show preview of filtered data
                preview_text = "Preview of filtered data:\n"
                if len(filtered_data) > 0:
                    preview_text += str(filtered_data.head(3).to_string())
                    if len(filtered_data) > 3:
                        preview_text += f"\n... and {len(filtered_data) - 3} more rows"
                else:
                    preview_text += "No data matches the current filters"
                    
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, preview_text)
            else:
                self.preview_label.config(text=f"Original data: {len(self.data)} rows (invalid filter)")
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "Invalid filter expression")
                
        except Exception as e:
            self.preview_label.config(text=f"Original data: {len(self.data)} rows (filter error)")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"Filter error: {str(e)}")
            
    def apply_filters_to_data(self, data: pd.DataFrame, preview: bool = False) -> Optional[pd.DataFrame]:
        """Apply all filters to data."""
        filtered_data = data.copy()
        
        try:
            # Date range filter - try multiple possible date column names
            date_cols = ['date', 'timestamp', '<DATE>', '<TIME>', 'Date', 'Timestamp', 'DATE', 'TIME']
            date_col = None
            for col in date_cols:
                if col in filtered_data.columns:
                    date_col = col
                    break
            
            # If no standard date column found, try to find any column that looks like dates
            if not date_col:
                for col in filtered_data.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                        date_col = col
                        break
                    
            if date_col:
                start_date = self.start_date_var.get().strip()
                end_date = self.end_date_var.get().strip()
                
                self.logger.info(f"Using date column: {date_col}")
                self.logger.info(f"Date column type: {filtered_data[date_col].dtype}")
                
                if start_date:
                    try:
                        start_dt = pd.to_datetime(start_date)
                        
                        # Handle different date column formats
                        if date_col == '<DATE>' and pd.api.types.is_numeric_dtype(filtered_data[date_col]):
                            # Stooq format: YYYYMMDD as integer
                            start_str = start_dt.strftime('%Y%m%d')
                            start_int = int(start_str)
                            filtered_data = filtered_data[filtered_data[date_col] >= start_int]
                            self.logger.info(f"Applied start date filter (Stooq format): {start_date} -> {start_int}")
                        else:
                            # Standard format: convert to datetime if needed
                            if not pd.api.types.is_datetime64_any_dtype(filtered_data[date_col]):
                                filtered_data[date_col] = pd.to_datetime(filtered_data[date_col])
                            filtered_data = filtered_data[filtered_data[date_col] >= start_dt]
                            self.logger.info(f"Applied start date filter (standard format): {start_date}")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply start date filter: {str(e)}")
                        
                if end_date:
                    try:
                        end_dt = pd.to_datetime(end_date)
                        
                        # Handle different date column formats
                        if date_col == '<DATE>' and pd.api.types.is_numeric_dtype(filtered_data[date_col]):
                            # Stooq format: YYYYMMDD as integer
                            end_str = end_dt.strftime('%Y%m%d')
                            end_int = int(end_str)
                            filtered_data = filtered_data[filtered_data[date_col] <= end_int]
                            self.logger.info(f"Applied end date filter (Stooq format): {end_date} -> {end_int}")
                        else:
                            # Standard format: convert to datetime if needed
                            if not pd.api.types.is_datetime64_any_dtype(filtered_data[date_col]):
                                filtered_data[date_col] = pd.to_datetime(filtered_data[date_col])
                            filtered_data = filtered_data[filtered_data[date_col] <= end_dt]
                            self.logger.info(f"Applied end date filter (standard format): {end_date}")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply end date filter: {str(e)}")
            else:
                self.logger.warning("No date column found for filtering")
                        
            # Numeric filters
            numeric_columns = data.select_dtypes(include=['number']).columns
            for column in numeric_columns:
                min_val = self.filters.get(f"{column}_min", tk.StringVar()).get().strip()
                max_val = self.filters.get(f"{column}_max", tk.StringVar()).get().strip()
                
                if min_val:
                    try:
                        filtered_data = filtered_data[filtered_data[column] >= float(min_val)]
                    except:
                        pass
                        
                if max_val:
                    try:
                        filtered_data = filtered_data[filtered_data[column] <= float(max_val)]
                    except:
                        pass
                        
            # Text filters
            text_columns = data.select_dtypes(include=['object', 'string']).columns
            for column in text_columns:
                contains_val = self.filters.get(f"{column}_contains", tk.StringVar()).get().strip()
                exact_val = self.filters.get(f"{column}_exact", tk.StringVar()).get().strip()
                
                if contains_val:
                    filtered_data = filtered_data[filtered_data[column].astype(str).str.contains(contains_val, case=False, na=False)]
                    
                if exact_val:
                    filtered_data = filtered_data[filtered_data[column].astype(str) == exact_val]
                    
            # Custom filter
            try:
                custom_filter = self.custom_filter_entry.get(1.0, tk.END).strip()
                if custom_filter and custom_filter.strip():
                    # Apply advanced custom filter
                    filtered_data = self._apply_custom_filter(filtered_data, custom_filter)
                    self.logger.info(f"Applied custom filter successfully")
                        
            except Exception as e:
                error_msg = f"Error applying custom filter: {str(e)}"
                self.logger.error(error_msg)
                if not preview:
                    raise Exception(error_msg)
                return None
                    
            # Row limit
            if not preview:
                try:
                    limit = int(self.row_limit_var.get())
                    if limit > 0:
                        filtered_data = filtered_data.head(limit)
                except:
                    pass
                    
            return filtered_data
            
        except Exception as e:
            if preview:
                return None
            raise e
    
    def _apply_custom_filter(self, data: pd.DataFrame, filter_expression: str) -> pd.DataFrame:
        """
        Apply advanced custom filter with support for multi-line expressions and complex logic.
        
        Args:
            data: DataFrame to filter
            filter_expression: Multi-line filter expression
            
        Returns:
            Filtered DataFrame
        """
        try:
            # Create a copy of the data to work with
            df = data.copy()
            
            # Log the input data info
            self.logger.info(f"Custom filter input: {len(df)} rows, columns: {list(df.columns)}")
            self.logger.info(f"Filter expression: {repr(filter_expression)}")
            
            # Map standard column names to Stooq format if needed
            column_mapping = {
                'close': '<CLOSE>',
                'volume': '<VOL>',
                'vol': '<VOL>',  # Support both 'volume' and 'vol'
                'ticker': '<TICKER>',
                'high': '<HIGH>',
                'low': '<LOW>',
                'open': '<OPEN>',
                'date': '<DATE>',
                'time': '<TIME>'
            }
            
            # Create reverse mapping for display
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            
            # Parse the filter expression line by line
            lines = [line.strip() for line in filter_expression.split('\n') if line.strip()]
            
            self.logger.info(f"Parsed {len(lines)} filter lines: {lines}")
            
            if not lines:
                return data
            
            # Initialize mask as all True
            mask = pd.Series([True] * len(df), index=df.index)
            
            # Process each line as a separate condition
            for i, line in enumerate(lines):
                # Translate column names in the expression
                translated_line = self._translate_column_names(line, df.columns, column_mapping)
                try:
                    # Use the translated line for evaluation
                    line_to_eval = translated_line
                    
                    # Try to evaluate the entire line as a single expression first
                    # This handles complex expressions like 'vol > vol.mean()' and '(high - low)/close > 0.05'
                    try:
                        # Special handling for expressions with method calls like .mean()
                        if '.mean()' in line_to_eval or '.median()' in line_to_eval or '.std()' in line_to_eval:
                            # These need to be evaluated as a single expression
                            line_mask = df.eval(line_to_eval)
                        else:
                            line_mask = df.eval(line_to_eval)
                        
                        mask = mask & line_mask
                        self.logger.info(f"Applied condition {i+1}: {line} -> {line_to_eval}")
                        continue
                    except Exception as eval_error:
                        self.logger.info(f"Complex eval failed for '{line}', trying simple parsing: {str(eval_error)}")
                    
                    # Fall back to simple condition parsing
                    if '==' in line_to_eval and '!=' not in line_to_eval:
                        # Equality condition
                        parts = line_to_eval.split('==')
                        if len(parts) == 2:
                            col = parts[0].strip()
                            value = parts[1].strip()
                            # Handle string values
                            if value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                                line_mask = df[col] == value
                            elif value.replace('.', '').replace('-', '').isdigit():
                                value = float(value)
                                line_mask = df[col] == value
                            else:
                                # Try to evaluate as expression
                                line_mask = df.eval(f"{col} == {value}")
                            mask = mask & line_mask
                    
                    elif '>' in line_to_eval and '>=' not in line_to_eval:
                        # Greater than condition - try simple parsing
                        parts = line_to_eval.split('>')
                        if len(parts) == 2:
                            left = parts[0].strip()
                            right = parts[1].strip()
                            line_mask = df.eval(f"{left} > {right}")
                            mask = mask & line_mask
                    
                    elif '>=' in line_to_eval:
                        # Greater than or equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '<' in line_to_eval and '<=' not in line_to_eval:
                        # Less than condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '<=' in line_to_eval:
                        # Less than or equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '!=' in line_to_eval:
                        # Not equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    else:
                        # Last resort: try to evaluate as a general expression
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    self.logger.info(f"Applied condition {i+1}: {line} -> {line_to_eval}")
                    
                except Exception as line_error:
                    self.logger.error(f"Error processing line '{line}': {str(line_error)}")
                    raise Exception(f"Invalid filter condition: {line}")
            
            # Apply the combined mask
            filtered_df = df[mask]
            
            self.logger.info(f"Custom filter applied: {len(data)} rows -> {len(filtered_df)} rows")
            return filtered_df
            
        except Exception as e:
            self.logger.error(f"Error in custom filter application: {str(e)}")
            raise Exception(f"Custom filter error: {str(e)}")
    
    def _translate_column_names(self, expression: str, available_columns: list, column_mapping: dict) -> str:
        """
        Translate standard column names to actual column names in the DataFrame.
        
        Args:
            expression: Filter expression
            available_columns: List of available columns in the DataFrame
            column_mapping: Mapping from standard names to actual names
            
        Returns:
            Translated expression
        """
        try:
            translated = expression
            
            # Check if we need to translate (i.e., if standard names are used but Stooq columns exist)
            has_stooq_columns = any(col.startswith('<') and col.endswith('>') for col in available_columns)
            uses_standard_names = any(std_name in expression for std_name in column_mapping.keys())
            
            if has_stooq_columns and uses_standard_names:
                # Translate standard column names to Stooq format
                for std_name, stooq_name in column_mapping.items():
                    if std_name in expression and stooq_name in available_columns:
                        # Replace column names in the expression
                        # Use word boundaries to avoid partial replacements
                        import re
                        pattern = r'\b' + re.escape(std_name) + r'\b'
                        translated = re.sub(pattern, stooq_name, translated)
                        self.logger.info(f"Translated '{std_name}' to '{stooq_name}' in expression")
            
            return translated
            
        except Exception as e:
            self.logger.warning(f"Error translating column names: {str(e)}")
            return expression
            
    def apply_filter(self):
        """Apply filters and close dialog."""
        try:
            self.logger.info("Apply Filter button clicked")
            filtered_data = self.apply_filters_to_data(self.data)
            
            if filtered_data is not None and len(filtered_data) > 0:
                self.logger.info(f"Filter successful: {len(filtered_data)} rows, calling callback")
                # Use the main window's thread-safe method to update GUI
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'run_in_main_thread'):
                    self.main_window.run_in_main_thread(lambda: self.callback(filtered_data))
                else:
                    self.callback(filtered_data)
                self.dialog.destroy()
                self.logger.info("Filter applied successfully and dialog closed")
            else:
                self.logger.warning("No data matches the current filters")
                messagebox.showwarning("No Results", "No data matches the current filters.")
                
        except Exception as e:
            self.logger.error(f"Error applying filters: {str(e)}")
            messagebox.showerror("Filter Error", f"Error applying filters: {str(e)}")
            
    def reset_all_filters(self):
        """Reset all filters to default values."""
        self.start_date_var.set('')
        self.end_date_var.set('')
        
        for var in self.filters.values():
            var.set('')
            
        self.custom_filter_entry.delete(1.0, tk.END)
        self.row_limit_var.set('1000')
        
        self.update_preview()
        
    def cancel_filter(self):
        """Cancel filtering and close dialog."""
        self.dialog.destroy()
