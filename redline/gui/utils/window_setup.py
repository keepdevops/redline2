#!/usr/bin/env python3
"""
Window Setup Helper for StockAnalyzerGUI
Handles main window configuration and toolbar creation.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class WindowSetupHelper:
    """Helper class for window setup in StockAnalyzerGUI."""
    
    def __init__(self, main_window):
        """Initialize with reference to StockAnalyzerGUI."""
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def setup_main_window(self):
        """Configure the main window."""
        # Configure root window
        self.main_window.root.title("REDLINE Data Analyzer")
        
        # Try to restore previous window geometry
        self.restore_window_geometry()
        
        # Configure grid weights for proper resizing
        self.main_window.root.grid_rowconfigure(0, weight=0)  # Toolbar (fixed height)
        self.main_window.root.grid_rowconfigure(1, weight=1)  # Main content area (expandable)
        self.main_window.root.grid_columnconfigure(0, weight=1)  # Full width
        
        # Set minimum and maximum sizes
        self.main_window.root.minsize(800, 600)
        self.main_window.root.maxsize(2400, 1600)  # Prevent excessive window sizes
        
        # Enable resizing
        self.main_window.root.resizable(True, True)
        
        # Create toolbar with help button
        self.create_toolbar()
        
        # Setup window close handler
        self.main_window.root.protocol("WM_DELETE_WINDOW", self.main_window.on_closing)
    
    def create_toolbar(self):
        """Create toolbar with help button."""
        self.main_window.toolbar = ttk.Frame(self.main_window.root)
        self.main_window.toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Help button
        self.main_window.help_btn = ttk.Button(self.main_window.toolbar, text="?", 
                                  command=self.main_window.show_help, width=3)
        self.main_window.help_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add tooltip to help button
        self.create_tooltip(self.main_window.help_btn, "Click for help and documentation")
        
        # Status label
        self.main_window.status_label = ttk.Label(self.main_window.toolbar, text="Ready")
        self.main_window.status_label.pack(side=tk.LEFT)
        
        # Memory usage label
        self.main_window.memory_label = ttk.Label(self.main_window.toolbar, text="")
        self.main_window.memory_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def restore_window_geometry(self):
        """Restore window geometry from settings."""
        try:
            # Default geometry
            default_geometry = "1200x800+100+100"
            
            # Try to load from a settings file (could be implemented later)
            # For now, use default geometry
            self.main_window.root.geometry(default_geometry)
            
        except Exception as e:
            self.main_window.logger.error(f"Error restoring window geometry: {str(e)}")
            # Fallback to default
            self.main_window.root.geometry("1200x800+100+100")
    
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

