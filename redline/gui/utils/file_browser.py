#!/usr/bin/env python3
"""
File Browser Helper for ConverterTab
Handles file browsing, directory selection, and file operations.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# Check for optional dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileBrowserHelper:
    """Helper class for file browsing operations in ConverterTab."""
    
    def __init__(self, converter_tab):
        """Initialize with reference to ConverterTab."""
        self.converter_tab = converter_tab
        self.logger = logging.getLogger(__name__)
    
    def browse_input_files(self):
        """Browse for input files."""
        # File types for file dialog
        # Note: On macOS, tkinter may not show all extensions in "All supported files"
        # So we list each format explicitly to ensure visibility
        # Order: Most common first, then less common formats
        filetypes = [
            ("CSV files", "*.csv"),           # Most common
            ("TXT files", "*.txt"),           # Common (Stooq format)
            ("JSON files", "*.json"),         # Common
            ("Parquet files", "*.parquet"),    # Common (efficient)
            ("Feather files", "*.feather"),   # Less common but supported
            ("DuckDB files", "*.duckdb"),      # Less common but supported
        ]
        
        # Add ML formats if TensorFlow is available
        if TENSORFLOW_AVAILABLE:
            filetypes.extend([
                ("Keras Model files", "*.h5"),      # Keras models
                ("TensorFlow NPZ files", "*.npz"),  # TensorFlow/NumPy format
            ])
        
        # Add "All supported files" - on macOS, use tuple format for better compatibility
        # Note: Some macOS versions may not show all extensions in a single pattern
        # So we also keep individual format filters above
        all_extensions_list = ["*.csv", "*.txt", "*.json", "*.parquet", "*.feather", "*.duckdb"]
        if TENSORFLOW_AVAILABLE:
            all_extensions_list.extend(["*.h5", "*.npz"])
        # Try tuple format first (better macOS support)
        try:
            filetypes.append(("All supported files", tuple(all_extensions_list)))
        except:
            # Fallback to space-separated string if tuple doesn't work
            all_extensions = " ".join(all_extensions_list)
            filetypes.append(("All supported files", all_extensions))
        
        # Always add "All files" as last option (this always works)
        filetypes.append(("All files", "*.*"))
        
        try:
            # On macOS, set initial directory to Downloads for better UX
            # Also ensure the file dialog can navigate to common locations
            initialdir = None
            if os.path.exists(os.path.expanduser("~/Downloads")):
                initialdir = os.path.expanduser("~/Downloads")
            elif os.path.exists("/app/data/stooq"):
                initialdir = "/app/data/stooq"
            elif os.path.exists("data/stooq"):
                initialdir = "data/stooq"
            
            files = filedialog.askopenfilenames(
                title="Select Input Files",
                filetypes=filetypes,
                initialdir=initialdir
            )
        except Exception as e:
            self.logger.error(f"Error opening file dialog: {str(e)}")
            self.converter_tab.main_window.show_error_message("Error", f"Failed to open file dialog: {str(e)}")
            return
        
        if files:
            self.converter_tab.input_files_var.set(f"{len(files)} file(s) selected")
            self.converter_tab.input_files = list(files)
            
            # Auto-detect format from first file
            if len(files) == 1:
                self.auto_detect_format()
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.converter_tab.output_dir_var.set(directory)
    
    def browse_batch_directory(self):
        """Browse for batch directory."""
        directory = filedialog.askdirectory(title="Select Batch Directory")
        if directory:
            self.converter_tab.batch_dir_var.set(directory)
    
    def auto_detect_format(self):
        """Auto-detect input format from file extension."""
        from ...core.schema import EXT_TO_FORMAT
        
        if hasattr(self.converter_tab, 'input_files') and self.converter_tab.input_files:
            first_file = self.converter_tab.input_files[0]
            ext = os.path.splitext(first_file)[1].lower()
            format_type = EXT_TO_FORMAT.get(ext, 'csv')
            self.converter_tab.input_format_var.set(format_type)
    
    def preview_input_file(self):
        """Preview input file contents."""
        if not hasattr(self.converter_tab, 'input_files') or not self.converter_tab.input_files:
            messagebox.showwarning("Warning", "No input files selected")
            return
            
        try:
            # Load first file for preview
            file_path = self.converter_tab.input_files[0]
            input_format = self.converter_tab.input_format_var.get()
            
            if not input_format:
                messagebox.showwarning("Warning", "Please select input format")
                return
                
            # Load data
            data = self.converter_tab.loader.load_file_by_type(file_path, input_format)
            
            # Show preview dialog
            self.show_preview_dialog(file_path, data)
            
        except Exception as e:
            self.logger.error(f"Error previewing file: {str(e)}")
            messagebox.showerror("Error", f"Failed to preview file: {str(e)}")
    
    def show_preview_dialog(self, file_path: str, data):
        """Show data preview dialog."""
        # Mask API keys in preview
        from ...web.utils.security_helpers import should_mask_file, mask_dataframe_columns
        preview_data = data.copy()
        if should_mask_file(file_path):
            preview_data = mask_dataframe_columns(preview_data)
            self.logger.info(f"Masked API keys in preview for file: {file_path}")
        else:
            # Still check for API key columns
            preview_data = mask_dataframe_columns(preview_data)
        
        preview_window = tk.Toplevel(self.converter_tab.frame)
        preview_window.title(f"Preview: {os.path.basename(file_path)}")
        preview_window.geometry("800x600")
        
        # Info frame
        info_frame = ttk.Frame(preview_window)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"File: {os.path.basename(file_path)}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Shape: {preview_data.shape[0]} rows × {preview_data.shape[1]} columns").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Columns: {list(preview_data.columns)}").pack(anchor=tk.W)
        
        # Data preview
        preview_frame = ttk.Frame(preview_window)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for preview
        preview_tree = ttk.Treeview(preview_frame, columns=list(preview_data.columns), show='headings')
        
        # Configure columns
        for col in preview_data.columns:
            preview_tree.heading(col, text=str(col))
            preview_tree.column(col, width=100)
            
        # Add data (first 100 rows) - using masked data
        preview_data_display = preview_data.head(100)
        for idx, row in preview_data_display.iterrows():
            preview_tree.insert('', 'end', values=list(row))
            
        # Scrollbars
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_tree.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=preview_tree.xview)
        
        preview_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
    
    def open_output_file(self):
        """Open selected output file."""
        selected = self.converter_tab.results_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return
            
        item = self.converter_tab.results_tree.item(selected[0])
        output_file = item['values'][4]
        
        if output_file:
            import subprocess
            import platform
            
            output_path = os.path.join(self.converter_tab.output_dir_var.get(), output_file)
            if os.path.exists(output_path):
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_path])
                    elif platform.system() == 'Windows':
                        os.startfile(output_path)
                    else:  # Linux/Container
                        # Try xdg-open first, fallback to showing file path
                        try:
                            subprocess.run(['xdg-open', output_path], check=True)
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            # xdg-open not available (common in Docker containers)
                            messagebox.showinfo(
                                "Output File", 
                                f"File location:\n{output_path}\n\n"
                                "Note: File opener not available in this environment.\n"
                                "You can access the file through the file system."
                            )
                except Exception as e:
                    self.logger.error(f"Error opening file: {str(e)}")
                    # Show file path instead of error
                    messagebox.showinfo(
                        "Output File", 
                        f"File location:\n{output_path}\n\n"
                        "File opener not available in this environment."
                    )
            else:
                messagebox.showwarning("Warning", "Output file not found")
        else:
            messagebox.showwarning("Warning", "No output file available")
    
    def open_output_directory(self):
        """Open output directory."""
        output_dir = self.converter_tab.output_dir_var.get()
        if os.path.exists(output_dir):
            import subprocess
            import platform
            
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', output_dir])
                elif platform.system() == 'Windows':
                    os.startfile(output_dir)
                else:  # Linux/Container
                    # Try xdg-open first, fallback to showing path in message
                    try:
                        subprocess.run(['xdg-open', output_dir], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # xdg-open not available (common in Docker containers)
                        messagebox.showinfo(
                            "Output Directory", 
                            f"Output directory location:\n{output_dir}\n\n"
                            "Note: File explorer not available in this environment.\n"
                            "You can access the files through the file system."
                        )
            except Exception as e:
                self.logger.error(f"Error opening directory: {str(e)}")
                # Show directory path instead of error
                messagebox.showinfo(
                    "Output Directory", 
                    f"Output directory location:\n{output_dir}\n\n"
                    "File explorer not available in this environment."
                )
        else:
            messagebox.showwarning("Warning", "Output directory does not exist")

