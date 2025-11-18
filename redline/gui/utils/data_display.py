#!/usr/bin/env python3
"""
Data Display Helper for DataTab
Handles data display, refresh, and selection events.
"""

import logging
import pandas as pd

from ...core.data_loader import DataLoader
from ..widgets.data_source import DataSource

logger = logging.getLogger(__name__)


class DataDisplayHelper:
    """Helper class for data display in DataTab."""
    
    def __init__(self, data_tab):
        """Initialize with reference to DataTab."""
        self.data_tab = data_tab
        self.logger = logging.getLogger(__name__)
    
    def display_data(self, data):
        """Display data in the treeview."""
        try:
            import pandas as pd
            
            self.logger.info(f"Starting data display: {len(data)} rows, columns: {list(data.columns)}")
            
            # Create data source
            if self.data_tab.current_data_source:
                self.data_tab.current_data_source.close()
            
            # Check if data is empty
            if data is None or data.empty:
                self.logger.warning("No data to display - empty DataFrame")
                self.data_tab.main_window.show_warning_message("No Data", "The loaded file contains no data.")
                return
            
            # Apply date formatting if date format is set
            data = self._apply_date_formatting(data.copy())
            
            # Mask API keys before display
            data = self._mask_api_keys(data.copy())
            
            # Clean data before display - ensure numeric columns are numeric
            try:
                # Auto-convert common numeric columns to numeric type
                numeric_cols = ['open', 'high', 'low', 'close', 'vol', 'volume', 'openint']
                for col in data.columns:
                    if col.lower() in [n.lower() for n in numeric_cols]:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
            except Exception as e:
                self.logger.warning(f"Could not clean data types: {str(e)}")
            
            # Try to use database if available, otherwise use direct pandas display
            try:
                # Try database approach first
                # Use the same database file as the connector
                db_path = self.data_tab.connector.db_path
                self.logger.info(f"Attempting database display with path: {db_path}")
                self.data_tab.connector.write_shared_data("temp_display_data", data, "display")
                self.data_tab.current_data_source = DataSource(db_path, "duckdb", "temp_display_data")
                self.logger.info(f"Database data source created: {self.data_tab.current_data_source.total_rows} rows")
                self.data_tab.treeview.set_data_source(self.data_tab.current_data_source)
                self.logger.info("Treeview data source set successfully")
            except Exception as db_error:
                # Fallback to direct pandas display if database not available, locked, or data invalid
                self.logger.warning(f"Database not available or locked, using direct pandas display: {db_error}")
                self.data_tab.current_data_source = DataSource(None, "pandas")
                self.data_tab.current_data_source.data = data
                self.data_tab.current_data_source.total_rows = len(data)
                self.logger.info(f"Pandas data source created: {self.data_tab.current_data_source.total_rows} rows")
                self.data_tab.treeview.set_data_source(self.data_tab.current_data_source)
                self.logger.info("Treeview pandas data source set successfully")
            
            # Store current data
            self.data_tab.current_data = data
            self.data_tab.current_format = "display"
            self.data_tab.unsaved_changes = False
            
            # Update main window
            self.data_tab.main_window.set_current_file_path("Multiple files")
            
            # Force treeview refresh
            self.data_tab.treeview.refresh()
            self.logger.info("Data display completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error displaying data: {str(e)}")
            raise
    
    def refresh_data(self):
        """Refresh the current data display."""
        if self.data_tab.current_data is not None:
            self.data_tab.treeview.refresh()
            self.data_tab.status_label.config(text="Data refreshed")
    
    def on_data_selection(self, event):
        """Handle data selection events."""
        selected_items = self.data_tab.treeview.get_selected_items()
        if selected_items:
            self.data_tab.status_label.config(text=f"{len(selected_items)} items selected")
    
    def on_data_double_click(self, event):
        """Handle data double-click events."""
        # Could open detailed view or edit dialog
        pass
    
    def _apply_date_formatting(self, data):
        """Apply date formatting based on selected format."""
        if not hasattr(self.data_tab, 'date_format_var'):
            return data
        
        date_format = self.data_tab.date_format_var.get()
        if date_format == 'raw' or not date_format:
            return data
        
        try:
            import pandas as pd
            from datetime import datetime
            
            # Find date columns
            date_columns = []
            for col in data.columns:
                col_lower = str(col).lower()
                if 'date' in col_lower or 'time' in col_lower or 'timestamp' in col_lower:
                    date_columns.append(col)
                # Also check if column contains YYYYMMDD format
                elif data[col].dtype in ['int64', 'float64']:
                    sample = data[col].dropna().head(10)
                    if len(sample) > 0:
                        # Check if values look like YYYYMMDD (8 digits, 19000101-21001231)
                        first_val = int(sample.iloc[0]) if pd.notna(sample.iloc[0]) else None
                        if first_val and 19000101 <= first_val <= 21001231:
                            date_columns.append(col)
            
            if not date_columns:
                return data
            
            # Apply formatting to date columns
            for col in date_columns:
                try:
                    # Convert to string, remove commas
                    data[col] = data[col].astype(str).str.replace(',', '')
                    
                    # Try to parse as YYYYMMDD
                    def format_date(val):
                        if pd.isna(val) or val == '' or val == 'nan':
                            return val
                        try:
                            val_str = str(val).replace(',', '')
                            if len(val_str) == 8 and val_str.isdigit():
                                year = int(val_str[:4])
                                month = int(val_str[4:6])
                                day = int(val_str[6:8])
                                
                                if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                                    if date_format == 'auto' or date_format == 'YYYY-MM-DD':
                                        return f"{year:04d}-{month:02d}-{day:02d}"
                                    elif date_format == 'MM/DD/YYYY':
                                        return f"{month:02d}/{day:02d}/{year:04d}"
                                    elif date_format == 'DD/MM/YYYY':
                                        return f"{day:02d}/{month:02d}/{year:04d}"
                                    elif date_format == 'YYYY/MM/DD':
                                        return f"{year:04d}/{month:02d}/{day:02d}"
                                    elif date_format == 'DD-MM-YYYY':
                                        return f"{day:02d}-{month:02d}-{year:04d}"
                                    elif date_format == 'MM-DD-YYYY':
                                        return f"{month:02d}-{day:02d}-{year:04d}"
                        except:
                            pass
                        return val
                    
                    data[col] = data[col].apply(format_date)
                except Exception as e:
                    self.logger.warning(f"Could not format date column {col}: {str(e)}")
            
            return data
        except Exception as e:
            self.logger.warning(f"Error applying date formatting: {str(e)}")
            return data
    
    def _mask_api_keys(self, data):
        """Mask API keys in the data."""
        try:
            import pandas as pd
            from ...web.utils.security_helpers import mask_dataframe_columns, should_mask_file
            
            # Check if current file is an API key file
            current_file = getattr(self.data_tab, 'current_file', None)
            if current_file and should_mask_file(str(current_file)):
                data = mask_dataframe_columns(data)
                self.logger.info(f"Masked API keys in file: {current_file}")
            else:
                # Still check for API key columns
                data = mask_dataframe_columns(data)
            
            return data
        except Exception as e:
            self.logger.warning(f"Error masking API keys: {str(e)}")
            return data

