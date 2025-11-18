#!/usr/bin/env python3
"""
Legacy GUI UI utilities extracted from StockAnalyzerGUI class.
Handles error dialogs, clipboard operations, and UI helpers.
"""

import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox

logger = logging.getLogger(__name__)


class UIUtilities:
    """UI utility functions for legacy GUI."""
    
    @staticmethod
    def show_enhanced_error(root, title, message, file_path=None):
        """Show enhanced error message with suggestions."""
        error_window = tk.Toplevel(root)
        error_window.title(title)
        error_window.geometry("500x300")
        error_window.resizable(True, True)
        
        error_frame = ttk.Frame(error_window)
        error_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(error_frame, text="Error Details:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        error_text = tk.Text(error_frame, height=8, wrap='word')
        error_text.pack(fill='both', expand=True, pady=(5, 10))
        error_text.insert('1.0', message)
        error_text.config(state='disabled')
        
        if file_path:
            ttk.Label(error_frame, text=f"File: {file_path}", foreground='gray').pack(anchor='w')
        
        suggestions_frame = ttk.LabelFrame(error_frame, text="Suggestions")
        suggestions_frame.pack(fill='x', pady=(10, 0))
        
        suggestions = UIUtilities.get_error_suggestions(message, file_path)
        for suggestion in suggestions:
            ttk.Label(suggestions_frame, text=f"• {suggestion}", wraplength=450).pack(anchor='w', padx=5, pady=2)
        
        button_frame = ttk.Frame(error_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Copy Error", 
                  command=lambda: UIUtilities.copy_to_clipboard(root, message)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=error_window.destroy).pack(side='right', padx=5)

    @staticmethod
    def get_error_suggestions(error_message, file_path=None):
        """Get suggestions based on error message."""
        suggestions = []
        
        if "File not found" in error_message:
            suggestions.extend([
                "Check if the file path is correct",
                "Verify the file exists in the specified location",
                "Try using the file browser to select the file"
            ])
        elif "File is empty" in error_message:
            suggestions.extend([
                "Check if the file contains data",
                "Verify the file wasn't corrupted during transfer",
                "Try opening the file in a text editor to verify content"
            ])
        elif "format" in error_message.lower():
            suggestions.extend([
                "Check if the file format is supported",
                "Verify the file extension matches the content",
                "Try converting the file to a supported format"
            ])
        elif "permission" in error_message.lower():
            suggestions.extend([
                "Check file permissions",
                "Try running the application with elevated privileges",
                "Verify you have read access to the file"
            ])
        else:
            suggestions.extend([
                "Check the file format and content",
                "Verify all required dependencies are installed",
                "Try refreshing the file list"
            ])
        
        return suggestions

    @staticmethod
    def copy_to_clipboard(root, text):
        """Copy text to clipboard."""
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Copied", "Error message copied to clipboard")

    @staticmethod
    def validate_data_file(file_path, format_type):
        """Validate data file before loading."""
        try:
            from redline.core.data_loader_shared import DataLoader
            
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            if os.path.getsize(file_path) == 0:
                raise ValueError(f"File is empty: {file_path}")
            
            ext = os.path.splitext(file_path)[1].lower()
            expected_ext = DataLoader.EXT_TO_FORMAT.get(ext, None)
            if expected_ext and expected_ext != format_type:
                raise ValueError(f"File extension '{ext}' doesn't match format '{format_type}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise

