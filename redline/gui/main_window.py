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
from .download_tab import DownloadTab
from .converter_tab import ConverterTab
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
        self.notebook.grid(row=1, column=0, sticky='nsew')
        
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
        self.root.grid_rowconfigure(1, weight=1)  # Main content area
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set minimum size
        self.root.minsize(800, 600)
        
        # Create toolbar with help button
        self.create_toolbar()
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_toolbar(self):
        """Create toolbar with help button."""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Help button
        self.help_btn = ttk.Button(self.toolbar, text="?", 
                                  command=self.show_help, width=3)
        self.help_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add tooltip to help button
        self.create_tooltip(self.help_btn, "Click for help and documentation")
        
        # Status label
        self.status_label = ttk.Label(self.toolbar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Memory usage label
        self.memory_label = ttk.Label(self.toolbar, text="")
        self.memory_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def setup_bindings(self):
        """Setup event bindings."""
        # Bind tab change events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Bind window events
        self.root.bind("<Configure>", self.on_window_configure)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        # F1 for help
        self.root.bind("<F1>", lambda e: self.show_help())
        
        # Ctrl+H for help
        self.root.bind("<Control-h>", lambda e: self.show_help())
        
        # Tab navigation
        self.root.bind("<Control-Tab>", lambda e: self.next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self.previous_tab())
        
        # Refresh data
        self.root.bind("<F5>", lambda e: self.refresh_all_tabs())
    
    def on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")
            self.status_label.config(text=f"Active: {tab_text}")
            
            # Update help button tooltip
            self.create_tooltip(self.help_btn, f"Help for {tab_text} tab")
            
        except Exception as e:
            self.logger.error(f"Error handling tab change: {str(e)}")
    
    def on_window_configure(self, event):
        """Handle window configuration events."""
        # Update window size in settings if needed
        pass
    
    def next_tab(self):
        """Go to next tab."""
        try:
            current_index = self.notebook.index(self.notebook.select())
            next_index = (current_index + 1) % self.notebook.index("end")
            self.notebook.select(next_index)
        except Exception as e:
            self.logger.error(f"Error switching to next tab: {str(e)}")
    
    def previous_tab(self):
        """Go to previous tab."""
        try:
            current_index = self.notebook.index(self.notebook.select())
            prev_index = (current_index - 1) % self.notebook.index("end")
            self.notebook.select(prev_index)
        except Exception as e:
            self.logger.error(f"Error switching to previous tab: {str(e)}")
    
    def create_tabs(self):
        """Create the main tabs."""
        # Data tab
        self.data_tab = DataTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.data_tab.frame, text="Data")
        
        # Analysis tab
        self.analysis_tab = AnalysisTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.analysis_tab.frame, text="Analysis")

        # Download/API tab
        self.download_tab = DownloadTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.download_tab.frame, text="Download/API")
        
        # Converter tab
        self.converter_tab = ConverterTab(self.notebook, self.loader, self.connector, self)
        self.notebook.add(self.converter_tab.frame, text="Converter")

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
            elif current_tab == "Download/API":
                self.download_tab.on_tab_activated()
            elif current_tab == "Converter":
                self.converter_tab.on_tab_activated()
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

Available Tabs:
  Data          - Load, view, and filter financial data
  Analysis      - Statistical and trend analysis tools
  Download/API  - Download data from various APIs (Yahoo, Stooq, etc.)
  Converter     - Convert between different data formats
  Settings      - Application configuration

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
    
    def show_help(self):
        """Show help dialog with context-sensitive information."""
        try:
            # Get current tab
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")
            
            # Create help window
            help_window = tk.Toplevel(self.root)
            help_window.title("REDLINE Help")
            help_window.geometry("800x600")
            help_window.resizable(True, True)
            
            # Make window modal
            help_window.transient(self.root)
            help_window.grab_set()
            
            # Create main frame
            main_frame = ttk.Frame(help_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create notebook for help sections
            help_notebook = ttk.Notebook(main_frame)
            help_notebook.pack(fill=tk.BOTH, expand=True)
            
            # Current tab help
            current_frame = ttk.Frame(help_notebook)
            help_notebook.add(current_frame, text=f"{tab_text} Tab")
            
            # Get help content for current tab
            help_content = self.get_tab_help_content(tab_text)
            self.create_help_content(current_frame, help_content)
            
            # General help
            general_frame = ttk.Frame(help_notebook)
            help_notebook.add(general_frame, text="General Help")
            
            general_content = self.get_general_help_content()
            self.create_help_content(general_frame, general_content)
            
            # Keyboard shortcuts
            shortcuts_frame = ttk.Frame(help_notebook)
            help_notebook.add(shortcuts_frame, text="Keyboard Shortcuts")
            
            shortcuts_content = self.get_shortcuts_help_content()
            self.create_help_content(shortcuts_frame, shortcuts_content)
            
            # Troubleshooting
            troubleshooting_frame = ttk.Frame(help_notebook)
            help_notebook.add(troubleshooting_frame, text="Troubleshooting")
            
            troubleshooting_content = self.get_troubleshooting_help_content()
            self.create_help_content(troubleshooting_frame, troubleshooting_content)
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Close", 
                                  command=help_window.destroy)
            close_btn.pack(pady=(10, 0))
            
            # Center the window
            help_window.update_idletasks()
            x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
            y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
            help_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            self.logger.error(f"Error showing help: {str(e)}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Could not show help: {str(e)}")
    
    def create_help_content(self, parent, content):
        """Create help content in a frame."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add content
        for section_title, section_content in content.items():
            # Section title
            title_label = ttk.Label(scrollable_frame, text=section_title, 
                                   font=("Arial", 12, "bold"))
            title_label.pack(anchor=tk.W, pady=(10, 5))
            
            # Section content
            content_text = tk.Text(scrollable_frame, wrap=tk.WORD, height=6,
                                  font=("Arial", 10), bg="#f0f0f0")
            content_text.pack(fill=tk.X, pady=(0, 10), padx=(20, 0))
            content_text.insert(tk.END, section_content)
            content_text.config(state=tk.DISABLED)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0",
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def get_tab_help_content(self, tab_name):
        """Get help content for specific tab."""
        help_content = {
            "Data Tab": {
                "Overview": "Load, view, and manage financial data files. This tab is your main workspace for data operations.",
                "Load Data": "Click 'Load Data' to browse and select files. Supported formats: CSV, Parquet, JSON, DuckDB, Feather.",
                "Data View": "View your loaded data with virtual scrolling for large datasets. Use pagination controls to navigate.",
                "Filtering": "Apply advanced filters using date ranges, numeric values, and text search. Use SQL-like queries for complex filtering.",
                "Export": "Export current data to various formats. Choose from CSV, Parquet, JSON, DuckDB, or Feather formats."
            },
            "Analysis Tab": {
                "Overview": "Perform statistical analysis and generate insights from your financial data.",
                "Statistical Analysis": "View basic statistics including mean, median, standard deviation, min/max values for all numeric columns.",
                "Trend Analysis": "Analyze price trends and volume patterns. View correlation between different assets.",
                "Data Quality": "Check data quality metrics including missing values, outliers, and data completeness.",
                "Performance Metrics": "Calculate returns, volatility, Sharpe ratio, and other investment performance indicators."
            },
            "Download/API Tab": {
                "Overview": "Download financial data from various sources including Yahoo Finance and Stooq.",
                "Yahoo Finance": "Free, reliable financial data. Enter ticker symbols (e.g., AAPL, MSFT) and select date ranges.",
                "Stooq Data": "High-quality historical data. Requires manual authentication setup.",
                "Batch Download": "Download multiple tickers simultaneously. Use comma-separated ticker symbols.",
                "Date Ranges": "Choose from preset ranges (1Y, 2Y, 5Y) or set custom date ranges."
            },
            "Converter Tab": {
                "Overview": "Convert data between different file formats efficiently.",
                "File Selection": "Select input files or directories for batch conversion. Supports all REDLINE formats.",
                "Format Options": "Choose output format: CSV (compatibility), Parquet (large datasets), DuckDB (analysis), JSON (web), Feather (speed).",
                "Data Cleaning": "Remove duplicates, fill missing values, standardize column names, and validate data integrity.",
                "Batch Processing": "Convert multiple files simultaneously with progress tracking and error handling."
            },
            "Settings Tab": {
                "Overview": "Configure application preferences and system settings.",
                "Data Paths": "Set default directories for data storage and downloads.",
                "Performance": "Configure memory usage, virtual scrolling, and processing options.",
                "Display": "Customize appearance, themes, and window settings.",
                "Logging": "Control debug output and error reporting levels."
            }
        }
        
        return help_content.get(tab_name, {
            "Information": f"Help content for {tab_name} is not available. Please check the general help section."
        })
    
    def get_general_help_content(self):
        """Get general help content."""
        return {
            "Getting Started": "1. Start by downloading data in the Download/API tab\n2. Load your data in the Data tab\n3. Use the Analysis tab for insights\n4. Convert formats in the Converter tab",
            "Supported Formats": "Input: CSV, Parquet, JSON, DuckDB, Feather, TXT (Stooq)\nOutput: CSV, Parquet, JSON, DuckDB, Feather\nRecommended: Parquet for large datasets, DuckDB for analysis",
            "Performance Tips": "• Use Parquet format for large datasets (10x smaller than CSV)\n• Enable virtual scrolling for 10M+ rows\n• Monitor memory usage in the status bar\n• Close unused tabs to free memory",
            "Data Sources": "• Yahoo Finance: Free, reliable data (recommended)\n• Stooq: High-quality data, requires setup\n• Multi-source: Fallback system for reliability",
            "Best Practices": "• Start with small datasets for testing\n• Use batch operations for multiple files\n• Regular data validation and cleaning\n• Keep backups of important data"
        }
    
    def get_shortcuts_help_content(self):
        """Get keyboard shortcuts help content."""
        return {
            "General Shortcuts": "• Ctrl+O: Open file\n• Ctrl+S: Save data\n• Ctrl+Q: Quit application\n• F1: Show help\n• F5: Refresh data",
            "Data Navigation": "• Ctrl+F: Search in data\n• Ctrl+A: Select all\n• Ctrl+C: Copy selection\n• Page Up/Down: Navigate pages\n• Home/End: Go to first/last row",
            "Tab Navigation": "• Ctrl+Tab: Next tab\n• Ctrl+Shift+Tab: Previous tab\n• Ctrl+1-5: Go to specific tab",
            "Filtering": "• Enter: Apply filter\n• Escape: Clear filter\n• Ctrl+R: Reset all filters\n• Ctrl+Shift+R: Reset view"
        }
    
    def get_troubleshooting_help_content(self):
        """Get troubleshooting help content."""
        return {
            "GUI Won't Start": "• Check Python version (3.11+ recommended)\n• Verify dependencies: conda activate stock\n• Try: python main.py --task=gui",
            "Data Loading Issues": "• Check file format is supported\n• Verify file is not corrupted\n• Ensure file has proper headers\n• Try converting to CSV first",
            "Performance Issues": "• Use Parquet format for large datasets\n• Enable virtual scrolling\n• Close unused applications\n• Monitor memory usage",
            "Conversion Errors": "• Check input file format\n• Verify output directory permissions\n• Ensure sufficient disk space\n• Try single file conversion first",
            "Download Failures": "• Check internet connection\n• Verify ticker symbols are valid\n• Try Yahoo Finance first\n• Reduce date range for testing",
            "Getting Help": "• Check logs for error messages\n• Use Docker environment as fallback\n• Report issues with detailed logs\n• Check documentation files"
        }
    
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
