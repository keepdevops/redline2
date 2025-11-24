#!/usr/bin/env python3
"""
Download File Operations Helper for DownloadTab
Handles file operations like opening, loading, and deleting downloaded files.
"""

import logging
import os
from tkinter import messagebox

logger = logging.getLogger(__name__)


class DownloadFileOpsHelper:
    """Helper class for file operations in DownloadTab."""
    
    def __init__(self, download_tab):
        """Initialize with reference to DownloadTab."""
        self.download_tab = download_tab
        self.logger = logging.getLogger(__name__)
    
    def open_selected_file(self):
        """Open the selected file."""
        selection = self.download_tab.results_tree.selection()
        if selection:
            item = self.download_tab.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(filepath)
                    elif os.name == 'posix':  # macOS and Linux
                        os.system(f"open '{filepath}'")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            else:
                messagebox.showwarning("Warning", "File not found or no file selected")
    
    def load_selected_data(self):
        """Load the selected data into REDLINE."""
        selection = self.download_tab.results_tree.selection()
        if selection:
            item = self.download_tab.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                try:
                    # Load the data in the data tab
                    self.download_tab.main_window.data_tab.load_file(filepath)
                    messagebox.showinfo("Data Loaded", f"Data from {os.path.basename(filepath)} has been loaded into REDLINE")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            else:
                messagebox.showwarning("Warning", "File not found or no file selected")
        else:
            messagebox.showwarning("Warning", "No file selected")
    
    def delete_selected_file(self):
        """Delete the selected file."""
        selection = self.download_tab.results_tree.selection()
        if selection:
            item = self.download_tab.results_tree.item(selection[0])
            filepath = item['values'][5]  # File column
            if filepath and os.path.exists(filepath):
                if messagebox.askyesno("Delete File", f"Delete {os.path.basename(filepath)}?"):
                    try:
                        os.remove(filepath)
                        self.download_tab.results_tree.delete(selection[0])
                        messagebox.showinfo("Success", "File deleted successfully")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete file: {str(e)}")
            else:
                messagebox.showwarning("Warning", "File not found")
        else:
            messagebox.showwarning("Warning", "No file selected")

