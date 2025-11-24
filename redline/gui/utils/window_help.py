#!/usr/bin/env python3
"""
Window Help Helper for StockAnalyzerGUI
Handles help dialog creation and content.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class WindowHelpHelper:
    """Helper class for help functionality in StockAnalyzerGUI."""
    
    def __init__(self, main_window):
        """Initialize with reference to StockAnalyzerGUI."""
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def show_help(self):
        """Show help dialog with context-sensitive information."""
        try:
            # Get current tab
            current_tab = self.main_window.notebook.select()
            tab_text = self.main_window.notebook.tab(current_tab, "text")
            
            # Create help window
            help_window = tk.Toplevel(self.main_window.root)
            help_window.title("REDLINE Help")
            help_window.geometry("800x600")
            help_window.resizable(True, True)
            
            # Make window modal
            help_window.transient(self.main_window.root)
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
            
            # Close button with proper cleanup
            def close_help():
                try:
                    for widget in help_window.winfo_children():
                        if hasattr(widget, '_help_window'):
                            try:
                                widget.unbind("<MouseWheel>")
                            except:
                                pass
                    help_window.destroy()
                except:
                    pass
            
            close_btn = ttk.Button(main_frame, text="Close", command=close_help)
            close_btn.pack(pady=(10, 0))
            
            # Center the window
            help_window.update_idletasks()
            x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
            y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
            help_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            self.main_window.logger.error(f"Error showing help: {str(e)}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Could not show help: {str(e)}")
    
    def create_help_content(self, parent, content):
        """Create help content in a frame."""
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
            title_label = ttk.Label(scrollable_frame, text=section_title, 
                                   font=("Arial", 12, "bold"))
            title_label.pack(anchor=tk.W, pady=(10, 5))
            
            content_text = tk.Text(scrollable_frame, wrap=tk.WORD, height=6,
                                  font=("Arial", 10), bg="#f0f0f0")
            content_text.pack(fill=tk.X, pady=(0, 10), padx=(20, 0))
            content_text.insert(tk.END, section_content)
            content_text.config(state=tk.DISABLED)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        help_window = canvas.winfo_toplevel()
        canvas._help_window = help_window
        
        def _on_mousewheel(event):
            try:
                if not canvas.winfo_exists():
                    return
                canvas.update_idletasks()
                delta = event.delta
                if delta > 0:
                    canvas.yview_scroll(-1, "units")
                else:
                    canvas.yview_scroll(1, "units")
            except (tk.TclError, AttributeError, RuntimeError):
                try:
                    canvas.unbind("<MouseWheel>")
                    if hasattr(canvas, '_help_window'):
                        canvas._help_window.unbind("<MouseWheel>")
                except:
                    pass
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        def _on_window_close():
            try:
                canvas.unbind("<MouseWheel>")
                help_window.unbind("<MouseWheel>")
            except:
                pass
        
        help_window.protocol("WM_DELETE_WINDOW", _on_window_close)
    
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

