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

