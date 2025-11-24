#!/usr/bin/env python3
"""
Window Events Helper for StockAnalyzerGUI
Handles event bindings, keyboard shortcuts, and window events.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class WindowEventsHelper:
    """Helper class for event handling in StockAnalyzerGUI."""
    
    def __init__(self, main_window):
        """Initialize with reference to StockAnalyzerGUI."""
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def setup_bindings(self):
        """Setup event bindings."""
        # Bind notebook tab change event
        self.main_window.notebook.bind("<<NotebookTabChanged>>", self.main_window.tab_manager.on_tab_changed)
        
        # Bind window events
        self.main_window.root.bind("<Configure>", self.on_window_configure)
        
        # Bind focus events
        self.main_window.root.bind("<FocusIn>", self.on_focus_in)
        self.main_window.root.bind("<FocusOut>", self.on_focus_out)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        # File operations
        if hasattr(self.main_window, 'data_tab'):
            self.main_window.root.bind("<Control-o>", lambda e: self.main_window.data_tab.open_file_dialog())
            self.main_window.root.bind("<Control-s>", lambda e: self.main_window.data_tab.save_current_data())
        
        # Navigation (use F2/F3 instead of tab to avoid system conflicts)
        self.main_window.root.bind("<F2>", lambda e: self.main_window.tab_manager.next_tab())
        self.main_window.root.bind("<F3>", lambda e: self.main_window.tab_manager.previous_tab())
        
        # Data operations
        if hasattr(self.main_window, 'data_tab'):
            self.main_window.root.bind("<Control-r>", lambda e: self.main_window.data_tab.refresh_data())
            self.main_window.root.bind("<Control-f>", lambda e: self.main_window.data_tab.open_search_dialog())
        
        # Help
        self.main_window.root.bind("<F1>", lambda e: self.main_window.show_help())
        self.main_window.root.bind("<Control-h>", lambda e: self.main_window.show_help())
        
        # Refresh data
        self.main_window.root.bind("<F5>", lambda e: self.main_window.refresh_all_tabs())
    
    def on_window_configure(self, event):
        """Handle window configuration changes."""
        # Only handle main window resize events
        if event.widget == self.main_window.root:
            # Update window size information
            width = self.main_window.root.winfo_width()
            height = self.main_window.root.winfo_height()
            
            # Update memory label with window size info
            try:
                if hasattr(self.main_window, 'memory_label'):
                    self.main_window.memory_label.config(text=f"Window: {width}x{height}")
            except:
                pass
            
            # Notify tabs of resize event
            self.main_window.tab_manager.notify_tabs_of_resize()
    
    def on_focus_in(self, event):
        """Handle focus in events."""
        # Update UI state when window gains focus
        pass
    
    def on_focus_out(self, event):
        """Handle focus out events."""
        # Update UI state when window loses focus
        pass

