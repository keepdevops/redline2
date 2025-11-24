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

from .filter_creators import FilterCreatorsHelper
from .filter_logic import FilterLogicHelper
from .filter_preview import FilterPreviewHelper

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
        
        # Initialize helper classes
        self.creators_helper = FilterCreatorsHelper(self)
        self.logic_helper = FilterLogicHelper(self)
        self.preview_helper = FilterPreviewHelper(self)
        
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
        self.preview_helper.update_preview()
        
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
        self.creators_helper.create_date_filter_tab()
        
        # Numeric filters
        self.creators_helper.create_numeric_filter_tab()
        
        # Text filters
        self.creators_helper.create_text_filter_tab()
        
        # Advanced filters
        self.creators_helper.create_advanced_filter_tab()
        
        # Column information section
        self.creators_helper.create_column_info_section(main_frame)
        
        # Preview section
        self.preview_helper.create_preview_section(main_frame)
        
        # Buttons
        self.creators_helper.create_buttons(main_frame)
        
    
    def test_filter(self):
        """Test filter functionality."""
        self.logger.info("TEST FILTER button clicked!")
        try:
            # Apply a simple filter (last 30 days)
            self.set_date_preset(30)
            self.preview_helper.update_preview()
            
            # Actually apply the filter to the main display
            self.logger.info("Applying test filter to main display...")
            filtered_data = self.logic_helper.apply_filters_to_data(self.data)
            
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
        self.dialog.bind('<KeyRelease>', lambda e: self.preview_helper.schedule_preview_update())
        
        # Bind to combobox changes
        for widget in self.dialog.winfo_children():
            self._bind_widget_changes(widget)
    
    def _bind_widget_changes(self, widget):
        """Recursively bind to widget changes for auto-preview updates."""
        try:
            if isinstance(widget, ttk.Combobox):
                widget.bind('<<ComboboxSelected>>', lambda e: self.preview_helper.schedule_preview_update())
            elif isinstance(widget, (tk.Entry, tk.Spinbox)):
                widget.bind('<KeyRelease>', lambda e: self.preview_helper.schedule_preview_update())
            elif isinstance(widget, ttk.Checkbutton):
                widget.bind('<Button-1>', lambda e: self.preview_helper.schedule_preview_update())
            
            # Recursively bind to children
            for child in widget.winfo_children():
                self._bind_widget_changes(child)
        except:
            pass  # Ignore binding errors
        
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
        self.preview_helper.update_preview()
            
    def apply_filter(self):
        """Apply filters and close dialog."""
        try:
            self.logger.info("Apply Filter button clicked")
            filtered_data = self.logic_helper.apply_filters_to_data(self.data)
            
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
        
        self.preview_helper.update_preview()
        
    def cancel_filter(self):
        """Cancel filtering and close dialog."""
        self.dialog.destroy()
