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
from .data_tab import DataTab
from .analysis_tab import AnalysisTab
from .settings_tab import SettingsTab

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
        
        # Setup main window
        self.setup_main_window()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew')
        
        # Create tabs
        self.create_tabs()
        
        # Setup event bindings
        self.setup_bindings()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Setup performance monitoring
        self.setup_performance_monitoring()
    
    def setup_main_window(self):
        """Configure the main window."""
        # Configure root window
        self.root.title("REDLINE Data Analyzer")
        self.root.geometry("1200x800")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set minimum size
        self.root.minsize(800, 600)
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_tabs(self):
        """Create the main tabs."""
        # Data tab
        self.data_tab = DataTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.data_tab.frame, text="Data")
        
        # Analysis tab
        self.analysis_tab = AnalysisTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.analysis_tab.frame, text="Analysis")
        
        # Settings tab
        self.settings_tab = SettingsTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.settings_tab.frame, text="Settings")
    
    def setup_bindings(self):
        """Setup event bindings."""
        # Bind notebook tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Bind window events
        self.root.bind("<Configure>", self.on_window_configure)
        
        # Bind focus events
        self.root.bind("<FocusIn>", self.on_focus_in)
        self.root.bind("<FocusOut>", self.on_focus_out)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        # File operations
        self.root.bind("<Control-o>", lambda e: self.data_tab.open_file_dialog())
        self.root.bind("<Control-s>", lambda e: self.data_tab.save_current_data())
        
        # Navigation (use F2/F3 instead of tab to avoid system conflicts)
        self.root.bind("<F2>", lambda e: self.next_tab())
        self.root.bind("<F3>", lambda e: self.previous_tab())
        
        # Data operations
        self.root.bind("<Control-r>", lambda e: self.data_tab.refresh_data())
        self.root.bind("<Control-f>", lambda e: self.data_tab.open_search_dialog())
        
        # Help
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<Control-h>", lambda e: self.show_help())
    
    def setup_performance_monitoring(self):
        """Setup performance monitoring."""
        # This could include memory usage monitoring, performance metrics, etc.
        self.performance_stats = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'data_loaded': False,
            'last_refresh': None
        }
    
    def on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            self.logger.info(f"Switched to tab: {current_tab}")
            
            # Notify the active tab of the change
            if current_tab == "Data":
                self.data_tab.on_tab_activated()
            elif current_tab == "Analysis":
                self.analysis_tab.on_tab_activated()
            elif current_tab == "Settings":
                self.settings_tab.on_tab_activated()
                
        except Exception as e:
            self.logger.error(f"Error handling tab change: {str(e)}")
    
    def on_window_configure(self, event):
        """Handle window configuration changes."""
        # Update scrollbars and layouts as needed
        pass
    
    def on_focus_in(self, event):
        """Handle focus in events."""
        # Update UI state when window gains focus
        pass
    
    def on_focus_out(self, event):
        """Handle focus out events."""
        # Update UI state when window loses focus
        pass
    
    def next_tab(self):
        """Switch to next tab."""
        current_index = self.notebook.index(self.notebook.select())
        next_index = (current_index + 1) % self.notebook.index("end")
        self.notebook.select(next_index)
    
    def previous_tab(self):
        """Switch to previous tab."""
        current_index = self.notebook.index(self.notebook.select())
        prev_index = (current_index - 1) % self.notebook.index("end")
        self.notebook.select(prev_index)
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
REDLINE Data Analyzer - Keyboard Shortcuts

File Operations:
  Ctrl+O  - Open file
  Ctrl+S  - Save current data

Navigation:
  F2            - Next tab
  F3            - Previous tab

Data Operations:
  Ctrl+R  - Refresh data
  Ctrl+F  - Search data

Help:
  F1      - Show this help
  Ctrl+H  - Show this help
        """
        
        # Create help dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("400x300")
        help_window.resizable(False, False)
        
        # Center the window
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Create text widget
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        # Add close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
    
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
    
    def on_closing(self):
        """Handle window closing."""
        try:
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
