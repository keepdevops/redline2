#!/usr/bin/env python3
"""
REDLINE Main Window
Main GUI window setup and coordination for the REDLINE application.
"""

import logging
import tkinter as tk
from tkinter import ttk
import threading
from typing import Optional

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector
from .utils.window_setup import WindowSetupHelper
from .utils.tab_manager import TabManagerHelper
from .utils.window_events import WindowEventsHelper
from .utils.window_help import WindowHelpHelper

logger = logging.getLogger(__name__)

class StockAnalyzerGUI:
    """Main GUI class for the REDLINE Stock Analyzer."""
    
    def __init__(self, root: tk.Tk, loader: DataLoader, connector: DatabaseConnector):
        """Initialize the main GUI."""
        self.root = root
        self.loader = loader
        self.connector = connector
        self.logger = logging.getLogger(__name__)
        
        # Initialize variables
        self.current_file_path: Optional[str] = None
        self.scrollbars = {}  # Dictionary to keep track of scrollbars
        
        # Thread safety
        self.ui_lock = threading.Lock()
        
        # Initialize helper classes
        self.setup_helper = WindowSetupHelper(self)
        self.tab_manager = TabManagerHelper(self)
        self.events_helper = WindowEventsHelper(self)
        self.help_helper = WindowHelpHelper(self)
        
        # Setup main window
        self.setup_helper.setup_main_window()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=(0, 5))
        
        # Configure notebook to expand with window
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create tabs
        self.tab_manager.create_tabs()
        
        # Setup event bindings
        self.events_helper.setup_bindings()
        
        # Setup keyboard shortcuts
        self.events_helper.setup_keyboard_shortcuts()
        
        # Setup performance monitoring
        self.setup_performance_monitoring()
    
    def show_help(self):
        """Show help dialog."""
        self.help_helper.show_help()
    
    def setup_performance_monitoring(self):
        """Setup performance monitoring."""
        self.performance_stats = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'data_loaded': False,
            'last_refresh': None
        }
    
    def cleanup_scrollbars(self, frame_name: str):
        """Clean up scrollbars for a given frame."""
        if frame_name in self.scrollbars:
            for scrollbar in self.scrollbars[frame_name]:
                try:
                    if scrollbar.winfo_exists():
                        scrollbar.destroy()
                except:
                    pass  # Ignore errors if widget is already destroyed
            del self.scrollbars[frame_name]
    
    def safe_update_widget(self, widget_name: str, update_func):
        """Safely update a widget from background thread."""
        if hasattr(self, widget_name):
            widget = getattr(self, widget_name)
            if widget and widget.winfo_exists():
                def safe_update():
                    with self.ui_lock:
                        update_func()
                self.run_in_main_thread(safe_update)
            else:
                self.logger.warning(f"Widget {widget_name} does not exist or has been destroyed")
        else:
            self.logger.warning(f"Widget {widget_name} not found")
    
    def run_in_main_thread(self, func):
        """Run a function in the main thread."""
        self.root.after(0, func)
    
    def get_current_file_path(self) -> Optional[str]:
        """Get the current file path."""
        return self.current_file_path
    
    def set_current_file_path(self, file_path: str):
        """Set the current file path."""
        self.current_file_path = file_path
        self.root.title(f"REDLINE Data Analyzer - {file_path}")
    
    def update_performance_stats(self, stats: dict):
        """Update performance statistics."""
        self.performance_stats.update(stats)
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics."""
        return self.performance_stats.copy()
    
    def save_window_geometry(self):
        """Save current window geometry to settings."""
        try:
            geometry = self.root.geometry()
            self.logger.info(f"Window geometry: {geometry}")
        except Exception as e:
            self.logger.error(f"Error saving window geometry: {str(e)}")
    
    def on_closing(self):
        """Handle window closing."""
        try:
            # Save window geometry
            self.save_window_geometry()
            
            # Save any unsaved data
            if hasattr(self, 'data_tab'):
                self.data_tab.save_unsaved_changes()
            
            # Clean up resources
            self.cleanup_resources()
            
            # Close the window
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during window closing: {str(e)}")
            self.root.destroy()
    
    def cleanup_resources(self):
        """Clean up resources before closing."""
        try:
            # Clean up scrollbars
            for frame_name in list(self.scrollbars.keys()):
                self.cleanup_scrollbars(frame_name)
            
            # Close database connections
            if hasattr(self.connector, 'close'):
                self.connector.close()
            
            # Close data sources
            if hasattr(self, 'data_tab'):
                self.data_tab.cleanup_resources()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up resources: {str(e)}")
    
    def refresh_all_tabs(self):
        """Refresh all tabs with current data."""
        try:
            self.data_tab.refresh_data()
            self.analysis_tab.refresh_data()
            self.settings_tab.refresh_settings()
            
        except Exception as e:
            self.logger.error(f"Error refreshing tabs: {str(e)}")
    
    def show_status_message(self, message: str, duration: int = 3000):
        """Show a status message."""
        # This could be implemented with a status bar
        self.logger.info(f"Status: {message}")
    
    def switch_to_tab(self, tab_name: str):
        """Switch to a specific tab by name."""
        try:
            tab_names = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
            if tab_name in tab_names:
                tab_index = tab_names.index(tab_name)
                self.notebook.select(tab_index)
        except Exception as e:
            self.logger.error(f"Error switching to tab {tab_name}: {str(e)}")
    
    def show_error_message(self, title: str, message: str):
        """Show an error message dialog."""
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, message)
    
    def show_info_message(self, title: str, message: str):
        """Show an info message dialog."""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(title, message)
    
    def show_warning_message(self, title: str, message: str):
        """Show a warning message dialog."""
        import tkinter.messagebox as messagebox
        messagebox.showwarning(title, message)
