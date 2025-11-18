#!/usr/bin/env python3
"""
Legacy GUI file operations extracted from StockAnalyzerGUI class.
Handles file browsing, selection, and analysis.
"""

import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import Counter

logger = logging.getLogger(__name__)


class FileOperations:
    """File operation utilities for legacy GUI."""
    
    @staticmethod
    def browse_files(input_listbox, input_format):
        """Browse and select files, updating the listbox."""
        try:
            from redline.core.data_loader_shared import DataLoader
            
            filetypes = [(desc, pattern) for (_, desc, pattern) in DataLoader.FORMAT_DIALOG_INFO.values()]
            files = filedialog.askopenfilenames(filetypes=filetypes)
            
            input_listbox.delete(0, tk.END)
            detected_types = []
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                fmt = DataLoader.EXT_TO_FORMAT.get(ext, 'unknown')
                detected_types.append(fmt)
                display_name = f"{file} [{fmt}]"
                input_listbox.insert(tk.END, display_name)
            
            # Set input format to the most common detected type
            if detected_types:
                most_common = Counter(detected_types).most_common(1)[0][0]
                if most_common != 'unknown':
                    input_format.set(most_common)
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to browse files: {str(e)}")
            messagebox.showerror("Error", f"Failed to browse files: {str(e)}")
            return []

    @staticmethod
    def select_all_files(input_listbox, selection_info=None):
        """Select all files in the listbox."""
        input_listbox.select_set(0, tk.END)
        if selection_info:
            FileOperations.update_selection_info(input_listbox, selection_info)

    @staticmethod
    def deselect_all_files(input_listbox, selection_info=None):
        """Deselect all files in the listbox."""
        input_listbox.selection_clear(0, tk.END)
        if selection_info:
            FileOperations.update_selection_info(input_listbox, selection_info)

    @staticmethod
    def update_selection_info(input_listbox, selection_info):
        """Update the selection info label."""
        selected_count = len(input_listbox.curselection())
        if selection_info:
            selection_info.config(text=f"Selected: {selected_count} files")

    @staticmethod
    def get_selected_file_paths(input_listbox):
        """Get file paths from selected listbox items."""
        selections = input_listbox.curselection()
        file_paths = [input_listbox.get(idx).split(' [')[0] for idx in selections]
        return file_paths

    @staticmethod
    def refresh_file_list(file_listbox, data_dir='/app/data'):
        """Refresh the file list from data directory."""
        try:
            file_listbox.delete(0, tk.END)
            
            if not os.path.exists(data_dir):
                logger.warning(f"Data directory does not exist: {data_dir}")
                return
            
            # Get all data files
            from redline.core.data_loader_shared import DataLoader
            extensions = list(DataLoader.EXT_TO_FORMAT.keys())
            
            files = []
            for root, dirs, filenames in os.walk(data_dir):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, filename)
                        files.append(file_path)
            
            # Sort files by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Add to listbox
            for file_path in files:
                file_listbox.insert(tk.END, file_path)
            
            logger.info(f"Refreshed file list: {len(files)} files found")
            
        except Exception as e:
            logger.error(f"Failed to refresh file list: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh file list: {str(e)}")

