#!/usr/bin/env python3
"""
Data Management Helper for DataTab
Handles save, clear, search, and filter operations.
"""

import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

from ...core.data_loader import DataLoader

logger = logging.getLogger(__name__)


class DataManagementHelper:
    """Helper class for data management operations in DataTab."""
    
    def __init__(self, data_tab):
        """Initialize with reference to DataTab."""
        self.data_tab = data_tab
        self.logger = logging.getLogger(__name__)
    
    def save_current_data(self):
        """Save current data to file."""
        if self.data_tab.current_data is None or self.data_tab.current_data.empty:
            self.data_tab.main_window.show_warning_message("Warning", "No data to save")
            return
        
        try:
            # Open save dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Data As",
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("JSON files", "*.json"),
                    ("Parquet files", "*.parquet"),
                    ("Feather files", "*.feather"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Detect format from extension
                format_type = self._detect_format_from_path(file_path)
                
                # Save data
                DataLoader.save_file_by_type(self.data_tab.current_data, file_path, format_type)
                
                self.data_tab.unsaved_changes = False
                self.data_tab.main_window.show_info_message("Success", f"Data saved to {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to save data: {str(e)}")
    
    def clear_data(self):
        """Clear the current data."""
        if self.data_tab.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before clearing?"
            )
            
            if result is True:
                self.save_current_data()
            elif result is None:  # Cancel
                return
        
        # Clear data
        self.data_tab.treeview.clear()
        self.data_tab.current_data = None
        self.data_tab.current_format = None
        self.data_tab.unsaved_changes = False
        
        if self.data_tab.current_data_source:
            self.data_tab.current_data_source.close()
            self.data_tab.current_data_source = None
        
        self.data_tab.status_label.config(text="No data loaded")
        self.data_tab.main_window.set_current_file_path(None)
    
    def open_search_dialog(self):
        """Open search dialog."""
        # Create search dialog
        search_window = tk.Toplevel(self.data_tab.frame)
        search_window.title("Search Data")
        search_window.geometry("400x200")
        search_window.resizable(False, False)
        
        # Center the window
        search_window.transient(self.data_tab.frame)
        search_window.grab_set()
        
        # Search entry
        from tkinter import ttk
        ttk.Label(search_window, text="Search term:").pack(pady=5)
        search_entry = ttk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        # Column selection
        ttk.Label(search_window, text="Search in column (optional):").pack(pady=5)
        column_var = tk.StringVar()
        column_combo = ttk.Combobox(search_window, textvariable=column_var, width=37)
        if self.data_tab.current_data is not None:
            column_combo['values'] = list(self.data_tab.current_data.columns)
        column_combo.pack(pady=5)
        
        # Search button
        def perform_search():
            search_term = search_entry.get().strip()
            column = column_var.get().strip() or None
            
            if search_term:
                matching_indices = self.data_tab.treeview.search_and_highlight(search_term, column)
                search_window.destroy()
                
                if matching_indices:
                    self.data_tab.status_label.config(text=f"Found {len(matching_indices)} matches")
                else:
                    self.data_tab.status_label.config(text="No matches found")
        
        ttk.Button(search_window, text="Search", command=perform_search).pack(pady=10)
        
        # Bind Enter key
        search_entry.bind('<Return>', lambda e: perform_search())
    
    def open_filter_dialog(self):
        """Open filter dialog."""
        if self.data_tab.current_data is None or self.data_tab.current_data.empty:
            self.data_tab.main_window.show_warning_message("Warning", "No data to filter")
            return
        
        try:
            from ..widgets.filter_dialog import FilterDialog
            
            def apply_filter(filtered_data):
                """Apply filtered data to display."""
                try:
                    self.logger.info(f"Applying filter: received {len(filtered_data)} rows")
                    self.logger.info(f"Filtered data columns: {list(filtered_data.columns)}")
                    self.logger.info(f"Filtered data shape: {filtered_data.shape}")
                    
                    self.data_tab.current_data = filtered_data
                    from .data_display import DataDisplayHelper
                    display_helper = DataDisplayHelper(self.data_tab)
                    display_helper.display_data(filtered_data)
                    self.data_tab.unsaved_changes = True
                    self.data_tab.main_window.show_info_message("Success", f"Filter applied: {len(filtered_data)} rows remaining")
                    self.logger.info(f"Filter applied successfully: {len(filtered_data)} rows displayed")
                except Exception as e:
                    self.logger.error(f"Error applying filter: {str(e)}")
                    self.data_tab.main_window.show_error_message("Error", f"Failed to apply filter: {str(e)}")
            
            # Create and show filter dialog
            filter_dialog = FilterDialog(self.data_tab.frame, self.data_tab.current_data, apply_filter)
            # Pass main window reference for thread-safe updates
            filter_dialog.main_window = self.data_tab.main_window
            
        except Exception as e:
            self.logger.error(f"Error opening filter dialog: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to open filter dialog: {str(e)}")
    
    def save_unsaved_changes(self):
        """Save any unsaved changes."""
        if self.data_tab.unsaved_changes:
            try:
                self.save_current_data()
            except Exception as e:
                self.logger.error(f"Error saving unsaved changes: {str(e)}")
    
    def _detect_format_from_path(self, file_path: str) -> str:
        """Detect format from file path."""
        import os
        from ...core.schema import EXT_TO_FORMAT
        ext = os.path.splitext(file_path)[1].lower()
        return EXT_TO_FORMAT.get(ext, 'csv')









