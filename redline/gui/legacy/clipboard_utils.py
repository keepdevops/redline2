#!/usr/bin/env python3
"""
Legacy GUI clipboard utilities extracted from StockAnalyzerGUI class.
Handles clipboard operations for treeview and search.
"""

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class ClipboardUtils:
    """Clipboard utility functions for legacy GUI."""
    
    @staticmethod
    def copy_selected_tree_items(root, data_tree):
        """Copy selected tree items to clipboard."""
        selected_items = data_tree.selection()
        if not selected_items:
            return 'break'
        
        columns = data_tree['columns']
        csv_data = '\t'.join(columns) + '\n'
        for item in selected_items:
            values = [data_tree.set(item, col) for col in columns]
            csv_data += '\t'.join(str(v) for v in values) + '\n'
        
        root.clipboard_clear()
        root.clipboard_append(csv_data)
        return 'break'

    @staticmethod
    def select_all_search(search_entry):
        """Select all text in search entry."""
        if search_entry:
            search_entry.select_range(0, tk.END)
        return 'break'

    @staticmethod
    def select_all_tree(data_tree):
        """Select all items in tree."""
        for item in data_tree.get_children():
            data_tree.selection_add(item)
        return 'break'

