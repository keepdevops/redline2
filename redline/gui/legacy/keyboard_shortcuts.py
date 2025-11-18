#!/usr/bin/env python3
"""
Legacy GUI keyboard shortcuts extracted from StockAnalyzerGUI class.
Handles keyboard shortcut setup and tooltips.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class KeyboardShortcuts:
    """Keyboard shortcuts manager for legacy GUI."""
    
    @staticmethod
    def setup_keyboard_shortcuts(root, callbacks):
        """Setup keyboard shortcuts for common actions.
        
        Args:
            root: Root window
            callbacks: Dict of callback functions:
                - focus_search: Focus search entry
                - export_data: Export data
                - refresh_file_list: Refresh file list
                - show_view_statistics: Show statistics
                - view_selected_file: View selected file
                - remove_selected_file: Remove selected file
                - clear_search: Clear search
        """
        if 'focus_search' in callbacks:
            root.bind('<Control-f>', lambda e: callbacks['focus_search']())
        if 'export_data' in callbacks:
            root.bind('<Control-e>', lambda e: callbacks['export_data']())
        if 'refresh_file_list' in callbacks:
            root.bind('<Control-r>', lambda e: callbacks['refresh_file_list']())
            root.bind('<F5>', lambda e: callbacks['refresh_file_list']())
        if 'show_view_statistics' in callbacks:
            root.bind('<Control-s>', lambda e: callbacks['show_view_statistics']())
        if 'view_selected_file' in callbacks:
            root.bind('<Control-v>', lambda e: callbacks['view_selected_file']())
        if 'remove_selected_file' in callbacks:
            root.bind('<Control-d>', lambda e: callbacks['remove_selected_file']())
        if 'clear_search' in callbacks:
            root.bind('<Escape>', lambda e: callbacks['clear_search']())

    @staticmethod
    def add_shortcut_tooltips():
        """Add tooltips with shortcut hints to buttons."""
        # This is a simplified version - in a full implementation,
        # you'd traverse the widget tree and add tooltips to specific buttons
        pass

    @staticmethod
    def create_tooltip(widget, text):
        """Create a tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1)
            label.pack()
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Button-1>', hide_tooltip)
        
        widget.bind('<Enter>', show_tooltip)

