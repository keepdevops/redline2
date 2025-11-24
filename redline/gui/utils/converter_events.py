#!/usr/bin/env python3
"""
Converter Event Handlers Helper for ConverterTab
Handles event handlers and UI interactions for the converter tab.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import os

logger = logging.getLogger(__name__)


class ConverterEventsHelper:
    """Helper class for event handlers in ConverterTab."""
    
    def __init__(self, converter_tab):
        """Initialize with reference to ConverterTab."""
        self.converter_tab = converter_tab
        self.logger = logging.getLogger(__name__)
    
    def setup_event_handlers(self):
        """Setup event handlers."""
        self.converter_tab.batch_convert_var.trace('w', lambda *args: self.toggle_batch_mode())
    
    def toggle_batch_mode(self):
        """Toggle batch conversion mode."""
        if self.converter_tab.batch_convert_var.get():
            self.converter_tab.batch_dir_entry.config(state='normal')
            self.converter_tab.file_pattern_entry.config(state='normal')
            self.converter_tab.batch_browse_btn.config(state='normal')
        else:
            self.converter_tab.batch_dir_entry.config(state='disabled')
            self.converter_tab.file_pattern_entry.config(state='disabled')
            self.converter_tab.batch_browse_btn.config(state='disabled')
    
    def start_conversion(self):
        """Start conversion process."""
        if self.converter_tab.batch_convert_var.get():
            if not self.converter_tab.batch_dir_var.get():
                messagebox.showwarning("Warning", "Please select batch directory")
                return
        else:
            if not hasattr(self.converter_tab, 'input_files') or not self.converter_tab.input_files:
                messagebox.showwarning("Warning", "Please select input files")
                return
                
        if not self.converter_tab.output_format_var.get():
            messagebox.showwarning("Warning", "Please select output format")
            return
            
        # Clear previous results
        self.converter_tab.clear_results()
        
        # Start conversion in thread
        self.converter_tab.stop_event.clear()
        import threading
        self.converter_tab.conversion_thread = threading.Thread(target=self._conversion_worker)
        self.converter_tab.conversion_thread.daemon = True
        self.converter_tab.conversion_thread.start()
        
        # Update UI
        self.converter_tab.convert_btn.config(state='disabled')
        self.converter_tab.stop_btn.config(state='normal')
        self.converter_tab.status_label.config(text="Conversion in progress...")
    
    def _conversion_worker(self):
        """Worker thread for conversion process."""
        try:
            if self.converter_tab.batch_convert_var.get():
                self.converter_tab.logic_helper._batch_conversion_worker()
            else:
                self.converter_tab.logic_helper._single_conversion_worker()
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Conversion error: {error_msg}")
            self.converter_tab.main_window.run_in_main_thread(
                lambda: self.converter_tab.main_window.show_error_message("Error", f"Conversion failed: {error_msg}")
            )
        finally:
            self.converter_tab.main_window.run_in_main_thread(self._conversion_complete)
    
    def _conversion_complete(self):
        """Handle conversion completion."""
        self.converter_tab.convert_btn.config(state='normal')
        self.converter_tab.stop_btn.config(state='disabled')
        self.converter_tab.progress_var.set(100)
        
        if self.converter_tab.stop_event.is_set():
            self.converter_tab.status_label.config(text="Conversion stopped")
        else:
            self.converter_tab.status_label.config(text=f"Conversion complete: {len(self.converter_tab.converted_files)} files converted")
    
    def stop_conversion(self):
        """Stop conversion process."""
        self.converter_tab.stop_event.set()
        self.converter_tab.status_label.config(text="Stopping conversion...")
    
    def clear_results(self):
        """Clear conversion results."""
        for item in self.converter_tab.results_tree.get_children():
            self.converter_tab.results_tree.delete(item)
        self.converter_tab.converted_files.clear()
        self.converter_tab.progress_var.set(0)
    
    def load_to_data_tab(self):
        """Load selected converted file to data tab."""
        selected = self.converter_tab.results_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return
            
        item = self.converter_tab.results_tree.item(selected[0])
        output_file = item['values'][4]
        
        if output_file and item['values'][3] == "Success":
            output_path = os.path.join(self.converter_tab.output_dir_var.get(), output_file)
            if os.path.exists(output_path):
                # Switch to data tab and load file
                self.converter_tab.main_window.switch_to_tab("Data")
                self.converter_tab.main_window.data_tab.load_file(output_path)
            else:
                messagebox.showwarning("Warning", "Output file not found")
        else:
            messagebox.showwarning("Warning", "No successful conversion available")

