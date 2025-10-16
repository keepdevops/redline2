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
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        self.setup_event_handlers()
        
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        # Date format help
        ttk.Label(date_range_frame, text="Format: YYYY-MM-DD (e.g., 2024-01-01)", 
                 font=("Arial", 8)).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Quick date presets
        presets_frame = ttk.Frame(date_range_frame)
        presets_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        ttk.Button(presets_frame, text="Last 30 days", 
                  command=lambda: self.set_date_preset(30)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(presets_frame, text="Last 90 days", 
                  command=lambda: self.set_date_preset(90)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(presets_frame, text="Last Year", 
                  command=lambda: self.set_date_preset(365)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(presets_frame, text="Clear", 
                  command=self.clear_date_filter).pack(side=tk.LEFT, padx=(0, 5))
        
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
        self.custom_filter_var = tk.StringVar()
        self.custom_filter_entry = tk.Text(sql_frame, height=4, width=60)
        self.custom_filter_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Example expressions
        examples_frame = ttk.Frame(sql_frame)
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(examples_frame, text="Examples:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        examples = [
            "close > 100",
            "volume > volume.mean()",
            "ticker == 'AAPL'",
            "(high - low) / close > 0.05"
        ]
        
        for example in examples:
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
        
    def create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply Filter", 
                  command=self.apply_filter).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset All", 
                  command=self.reset_all_filters).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_filter).pack(side=tk.RIGHT, padx=(5, 0))
        
    def setup_event_handlers(self):
        """Setup event handlers."""
        # Auto-update preview when filters change
        self.dialog.bind('<KeyRelease>', lambda e: self.schedule_preview_update())
        
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
            # Date range filter
            date_cols = ['date', 'timestamp', '<DATE>', '<TIME>']
            date_col = None
            for col in date_cols:
                if col in filtered_data.columns:
                    date_col = col
                    break
                    
            if date_col:
                start_date = self.start_date_var.get().strip()
                end_date = self.end_date_var.get().strip()
                
                if start_date:
                    try:
                        start_dt = pd.to_datetime(start_date)
                        filtered_data = filtered_data[filtered_data[date_col] >= start_dt]
                    except:
                        pass
                        
                if end_date:
                    try:
                        end_dt = pd.to_datetime(end_date)
                        filtered_data = filtered_data[filtered_data[date_col] <= end_dt]
                    except:
                        pass
                        
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
            custom_filter = self.custom_filter_entry.get(1.0, tk.END).strip()
            if custom_filter:
                try:
                    filtered_data = filtered_data.query(custom_filter)
                except Exception as e:
                    if not preview:
                        raise e
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
            
    def apply_filter(self):
        """Apply filters and close dialog."""
        try:
            filtered_data = self.apply_filters_to_data(self.data)
            
            if filtered_data is not None and len(filtered_data) > 0:
                self.callback(filtered_data)
                self.dialog.destroy()
            else:
                messagebox.showwarning("No Results", "No data matches the current filters.")
                
        except Exception as e:
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
