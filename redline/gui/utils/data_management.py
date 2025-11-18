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
    
    def open_clean_data_dialog(self):
        """Open data cleaning options dialog."""
        if self.data_tab.current_data is None or self.data_tab.current_data.empty:
            self.data_tab.main_window.show_warning_message("Warning", "No data to clean")
            return
        
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Create cleaning dialog
            clean_window = tk.Toplevel(self.data_tab.frame)
            clean_window.title("Clean Data Options")
            clean_window.geometry("500x400")
            clean_window.resizable(False, False)
            
            # Center the window
            clean_window.transient(self.data_tab.frame)
            clean_window.grab_set()
            
            # Remove duplicates option
            remove_duplicates_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                clean_window,
                text="Remove Duplicate Rows",
                variable=remove_duplicates_var
            ).pack(anchor=tk.W, padx=20, pady=10)
            
            ttk.Label(
                clean_window,
                text="Removes rows that are exact duplicates. If ticker and timestamp\ncolumns exist, duplicates are detected based on those columns.",
                font=("Arial", 8),
                foreground="gray"
            ).pack(anchor=tk.W, padx=40, pady=(0, 10))
            
            # Handle missing values option
            ttk.Label(clean_window, text="Handle Missing Values:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10, 5))
            
            handle_missing_var = tk.StringVar(value="drop")
            missing_frame = ttk.Frame(clean_window)
            missing_frame.pack(fill=tk.X, padx=40, pady=(0, 10))
            
            ttk.Radiobutton(
                missing_frame,
                text="Drop rows with missing values",
                variable=handle_missing_var,
                value="drop"
            ).pack(anchor=tk.W)
            
            ttk.Radiobutton(
                missing_frame,
                text="Forward fill (use previous value)",
                variable=handle_missing_var,
                value="forward_fill"
            ).pack(anchor=tk.W)
            
            ttk.Radiobutton(
                missing_frame,
                text="Backward fill (use next value)",
                variable=handle_missing_var,
                value="backward_fill"
            ).pack(anchor=tk.W)
            
            ttk.Radiobutton(
                missing_frame,
                text="Don't handle missing values",
                variable=handle_missing_var,
                value="none"
            ).pack(anchor=tk.W)
            
            # Clean column names option
            clean_column_names_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                clean_window,
                text="Clean column names (remove unnamed/empty columns)",
                variable=clean_column_names_var
            ).pack(anchor=tk.W, padx=20, pady=10)
            
            # Buttons
            button_frame = ttk.Frame(clean_window)
            button_frame.pack(fill=tk.X, padx=20, pady=20)
            
            def apply_cleaning():
                """Apply cleaning options to data."""
                try:
                    from ...core.data_cleaner import DataCleaner
                    from ...web.utils.data_helpers import clean_dataframe_columns
                    
                    cleaned_data = self.data_tab.current_data.copy()
                    original_rows = len(cleaned_data)
                    stats = {}
                    
                    # Initialize cleaner
                    cleaner = DataCleaner()
                    
                    # Remove duplicates
                    if remove_duplicates_var.get():
                        df_before = len(cleaned_data)
                        subset = None
                        if 'ticker' in cleaned_data.columns and 'timestamp' in cleaned_data.columns:
                            subset = ['ticker', 'timestamp']
                        elif 'timestamp' in cleaned_data.columns:
                            subset = ['timestamp']
                        cleaned_data = cleaner.remove_duplicates(cleaned_data, subset=subset)
                        duplicates_removed = df_before - len(cleaned_data)
                        stats['duplicates_removed'] = duplicates_removed
                    
                    # Handle missing values
                    handle_missing = handle_missing_var.get()
                    if handle_missing and handle_missing != 'none':
                        df_before = len(cleaned_data)
                        cleaned_data = cleaner.handle_missing_values(cleaned_data, strategy=handle_missing)
                        missing_handled = df_before - len(cleaned_data)
                        stats['missing_handled'] = missing_handled
                    
                    # Clean column names
                    if clean_column_names_var.get():
                        cleaned_data = clean_dataframe_columns(cleaned_data)
                    
                    # Update data display
                    self.data_tab.current_data = cleaned_data
                    from .data_display import DataDisplayHelper
                    display_helper = DataDisplayHelper(self.data_tab)
                    display_helper.display_data(cleaned_data)
                    self.data_tab.unsaved_changes = True
                    
                    # Show results
                    stats_msg = f"Data cleaned successfully!\n\n"
                    stats_msg += f"Original rows: {original_rows}\n"
                    stats_msg += f"Final rows: {len(cleaned_data)}\n"
                    if stats.get('duplicates_removed', 0) > 0:
                        stats_msg += f"Duplicates removed: {stats['duplicates_removed']}\n"
                    if stats.get('missing_handled', 0) > 0:
                        stats_msg += f"Missing values handled: {stats['missing_handled']}\n"
                    
                    clean_window.destroy()
                    self.data_tab.main_window.show_info_message("Data Cleaned", stats_msg)
                    
                except Exception as e:
                    self.logger.error(f"Error cleaning data: {str(e)}")
                    self.data_tab.main_window.show_error_message("Error", f"Failed to clean data: {str(e)}")
            
            ttk.Button(button_frame, text="Clean Data", command=apply_cleaning).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Cancel", command=clean_window.destroy).pack(side=tk.LEFT)
            
        except Exception as e:
            self.logger.error(f"Error opening clean data dialog: {str(e)}")
            self.data_tab.main_window.show_error_message("Error", f"Failed to open clean data dialog: {str(e)}")
    
    def _detect_format_from_path(self, file_path: str) -> str:
        """Detect format from file path (uses centralized function)."""
        from ...core.schema import detect_format_from_path
        return detect_format_from_path(file_path)









