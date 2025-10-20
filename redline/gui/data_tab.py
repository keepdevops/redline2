#!/usr/bin/env python3
"""
REDLINE Data Tab
GUI tab for data loading, viewing, and management operations.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from typing import Optional, List, Dict, Any

from ..core.data_loader import DataLoader
from ..core.schema import EXT_TO_FORMAT, FORMAT_DIALOG_INFO
from ..database.connector import DatabaseConnector
from ..database.operations import DatabaseOperations
from .widgets.virtual_treeview import VirtualScrollingTreeview
from .widgets.data_source import DataSource
from .widgets.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)

class DataTab:
    """Data tab for loading, viewing, and managing data."""
    
    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        """Initialize data tab."""
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Data state
        self.current_data = None
        self.current_data_source = None
        self.current_format = None
        self.unsaved_changes = False
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Create widgets
        self.create_widgets()
        
        # Setup event handlers
        self.setup_event_handlers()
    
    def create_widgets(self):
        """Create the data tab widgets."""
        # Top frame for controls
        self.control_frame = ttk.Frame(self.frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File operations frame
        self.file_frame = ttk.LabelFrame(self.control_frame, text="File Operations")
        self.file_frame.pack(fill=tk.X, pady=(0, 5))
        
        # File buttons
        self.open_button = ttk.Button(self.file_frame, text="Open File", command=self.open_file_dialog)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_converted_button = ttk.Button(self.file_frame, text="Load Converted Files", command=self.load_converted_files)
        self.load_converted_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_button = ttk.Button(self.file_frame, text="Save", command=self.save_current_data)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.refresh_button = ttk.Button(self.file_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Data operations frame
        self.operations_frame = ttk.LabelFrame(self.control_frame, text="Data Operations")
        self.operations_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search and filter
        self.search_button = ttk.Button(self.operations_frame, text="Search", command=self.open_search_dialog)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.filter_button = ttk.Button(self.operations_frame, text="Filter", command=self.open_filter_dialog)
        self.filter_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_button = ttk.Button(self.operations_frame, text="Clear", command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status frame
        self.status_frame = ttk.Frame(self.frame)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="No data loaded")
        self.status_label.pack(side=tk.LEFT)
        
        # Progress tracker
        self.progress_tracker = ProgressTracker(self.status_frame, "Loading...")
        self.progress_tracker.pack(side=tk.RIGHT)
        
        # Main data display frame
        self.data_frame = ttk.Frame(self.frame)
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights
        self.data_frame.grid_rowconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview with virtual scrolling
        self.treeview = VirtualScrollingTreeview(
            self.data_frame,
            columns=['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol']
        )
        self.treeview.grid(row=0, column=0, sticky='nsew')
        
        # Configure treeview columns
        self.treeview.tree.configure(columns=['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol'])
        self.treeview.tree.heading('#0', text='Row')
        self.treeview.tree.heading('ticker', text='Ticker')
        self.treeview.tree.heading('timestamp', text='Timestamp')
        self.treeview.tree.heading('open', text='Open')
        self.treeview.tree.heading('high', text='High')
        self.treeview.tree.heading('low', text='Low')
        self.treeview.tree.heading('close', text='Close')
        self.treeview.tree.heading('vol', text='Volume')
        
        # Configure column widths
        self.treeview.tree.column('#0', width=50)
        self.treeview.tree.column('ticker', width=80)
        self.treeview.tree.column('timestamp', width=120)
        self.treeview.tree.column('open', width=80)
        self.treeview.tree.column('high', width=80)
        self.treeview.tree.column('low', width=80)
        self.treeview.tree.column('close', width=80)
        self.treeview.tree.column('vol', width=100)
        
        # Add scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.VERTICAL, command=self.treeview.tree.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.treeview.tree.configure(yscrollcommand=self.v_scrollbar.set)
        
        self.h_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.HORIZONTAL, command=self.treeview.tree.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.treeview.tree.configure(xscrollcommand=self.h_scrollbar.set)
    
    def setup_event_handlers(self):
        """Setup event handlers."""
        # Bind treeview events
        self.treeview.bind_event('<<TreeviewSelect>>', self.on_data_selection)
        self.treeview.bind_event('<Double-1>', self.on_data_double_click)
        
        # Setup progress tracker callbacks
        self.progress_tracker.set_completion_callback(self.on_loading_complete)
        self.progress_tracker.set_cancel_callback(self.on_loading_cancelled)
    
    def open_file_dialog(self):
        """Open file dialog to select data files."""
        try:
            # Create file dialog
            file_paths = filedialog.askopenfilenames(
                title="Select Data Files",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("Parquet files", "*.parquet"),
                    ("Feather files", "*.feather"),
                    ("DuckDB files", "*.duckdb"),
                    ("All files", "*.*")
                ]
            )
            
            if file_paths:
                self.load_files(file_paths)
                
        except Exception as e:
            self.logger.error(f"Error opening file dialog: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to open file dialog: {str(e)}")
    
    def load_converted_files(self):
        """Load converted files from the converter output directory."""
        try:
            import glob
            
            # Get the converter output directory
            converted_dir = "data/converted"
            
            if not os.path.exists(converted_dir):
                self.main_window.show_warning_message("No Converted Files", 
                    "No converted files directory found. Please run conversions first.")
                return
            
            # Find all converted files in subdirectories
            converted_files = []
            for root, dirs, files in os.walk(converted_dir):
                for file in files:
                    if file.endswith(('.csv', '.feather', '.parquet', '.json')):
                        converted_files.append(os.path.join(root, file))
            
            if not converted_files:
                self.main_window.show_warning_message("No Converted Files", 
                    "No converted files found in the converted directory.")
                return
            
            # Ask user which files to load
            if len(converted_files) == 1:
                # Only one file, load it directly
                self.load_files([converted_files[0]])
            else:
                # Multiple files, show selection dialog
                self.show_converted_files_dialog(converted_files)
                
        except Exception as e:
            self.logger.error(f"Error loading converted files: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to load converted files: {str(e)}")
    
    def show_converted_files_dialog(self, files: List[str]):
        """Show dialog to select which converted files to load."""
        try:
            # Create a simple selection dialog
            dialog = tk.Toplevel(self.frame)
            dialog.title("Select Converted Files to Load")
            dialog.geometry("600x400")
            dialog.transient(self.frame)
            dialog.grab_set()
            
            # Create frame for listbox and scrollbar
            list_frame = ttk.Frame(dialog)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Label
            ttk.Label(list_frame, text="Select files to load:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Listbox with scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Add files to listbox
            for file_path in files:
                # Show relative path for better readability
                rel_path = os.path.relpath(file_path, "data/converted")
                listbox.insert(tk.END, rel_path)
            
            # Buttons frame
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # Load selected button
            def load_selected():
                selected_indices = listbox.curselection()
                if selected_indices:
                    selected_files = [files[i] for i in selected_indices]
                    dialog.destroy()
                    self.load_files(selected_files)
                else:
                    messagebox.showwarning("No Selection", "Please select at least one file to load.")
            
            # Load all button
            def load_all():
                dialog.destroy()
                self.load_files(files)
            
            # Cancel button
            def cancel():
                dialog.destroy()
            
            ttk.Button(button_frame, text="Load Selected", command=load_selected).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Load All", command=load_all).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
            
            # Instructions
            ttk.Label(button_frame, text="Hold Ctrl/Cmd to select multiple files", 
                     font=("Arial", 9), foreground="gray").pack(side=tk.RIGHT, padx=(0, 10))
            
        except Exception as e:
            self.logger.error(f"Error showing converted files dialog: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to show file selection dialog: {str(e)}")
    
    def load_files(self, file_paths: List[str]):
        """Load multiple files."""
        try:
            # Start progress tracking
            self.progress_tracker.start_operation(len(file_paths), "Loading files...")
            
            # Load files in background thread
            self.loading_thread = threading.Thread(target=self._load_files_thread, args=(file_paths,))
            self.loading_thread.daemon = True
            self.loading_thread.start()
            
            # Set up timeout to prevent infinite loading
            def check_timeout():
                if hasattr(self, 'loading_thread') and self.loading_thread.is_alive():
                    self.main_window.show_warning_message(
                        "Loading Timeout", 
                        "File loading is taking longer than expected. This may indicate a problem with the file format or size."
                    )
                    # Stop the progress tracker
                    self.progress_tracker.cancel_operation()
            
            # Set timeout after 30 seconds
            self.frame.after(30000, check_timeout)
            
        except Exception as e:
            self.logger.error(f"Error starting file loading: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to start file loading: {str(e)}")
    
    def _load_files_thread(self, file_paths: List[str]):
        """Load files in background thread."""
        try:
            loaded_data = []
            skipped_files = []
            large_files = []
            
            # Check file sizes first
            for file_path in file_paths:
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        large_files.append((file_path, file_size))
                except:
                    pass
            
            # Warn about large files
            if large_files:
                large_file_names = [os.path.basename(f[0]) for f in large_files]
                large_files_text = "\n".join(large_file_names)
                self.main_window.run_in_main_thread(
                    lambda: self.main_window.show_warning_message(
                        "Large Files Detected",
                        f"Large files detected: {large_files_text}\n\n"
                        "Loading may be slow. Consider using chunked loading for better performance."
                    )
                )
            
            # Use parallel processing for file loading
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all file loading tasks
                future_to_file = {
                    executor.submit(self._load_single_file_parallel, file_path): file_path
                    for file_path in file_paths
                }
                
                # Process completed loads
                completed = 0
                for future in as_completed(future_to_file):
                    if not self.progress_tracker.is_operation_running():
                        break
                        
                    file_path = future_to_file[future]
                    completed += 1
                    
                    # Update progress
                    self.progress_tracker.update_progress(
                        operation=f"Loading {os.path.basename(file_path)}... ({completed}/{len(file_paths)})"
                    )
                    
                    try:
                        data = future.result()
                        if data is not None and not data.empty:
                            loaded_data.append(data)
                            self.logger.info(f"Successfully loaded {file_path}: {len(data)} rows")
                        else:
                            skipped_files.append(file_path)
                            self.logger.warning(f"Skipped empty file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error loading {file_path}: {str(e)}")
                        skipped_files.append(file_path)
                    
                    # Increment progress
                    self.progress_tracker.update_progress(increment=True)
            
            # Combine loaded data with memory optimization
            if loaded_data:
                try:
                    # Combine data with memory management
                    if len(loaded_data) == 1:
                        combined_data = loaded_data[0]
                    else:
                        combined_data = pd.concat(loaded_data, ignore_index=True)
                    
                    # Clear the list to free memory
                    loaded_data.clear()
                    
                    # Display the combined data
                    self._display_data(combined_data)
                    
                    # Clear the combined data after display setup
                    del combined_data
                    
                except MemoryError as mem_error:
                    self.logger.error(f"Memory error combining data: {str(mem_error)}")
                    self.main_window.run_in_main_thread(
                        lambda: self.main_window.show_error_message(
                            "Memory Error", 
                            "File too large to load. Try loading smaller files or use chunked processing."
                        )
                    )
                except Exception as e:
                    self.logger.error(f"Error combining data: {str(e)}")
                    raise
                
                # Update status
                self.main_window.run_in_main_thread(
                    lambda: self.status_label.config(
                        text=f"Loaded {len(loaded_data)} files, {len(skipped_files)} skipped"
                    )
                )
            else:
                self.main_window.run_in_main_thread(
                    lambda: self.status_label.config(text="No data loaded")
                )
            
            # Show skipped files if any
            if skipped_files:
                self.main_window.show_warning_message(
                    "Skipped Files",
                    f"The following files could not be loaded:\n" + "\n".join(skipped_files)
                )
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in load files thread: {error_msg}")
            self.main_window.run_in_main_thread(
                lambda: self.main_window.show_error_message("Error", f"Failed to load files: {error_msg}")
            )
    
    def _load_single_file_parallel(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load a single file - designed for parallel processing."""
        try:
            # Check if this is a large file
            file_size = os.path.getsize(file_path)
            is_large_file = file_size > 50 * 1024 * 1024  # 50MB
            
            # Detect format from extension
            format_type = self._detect_format_from_path(file_path)
            
            # Load data with chunked approach for large files
            if is_large_file and format_type in ['csv', 'txt']:
                data = self._load_large_file_chunked(file_path, format_type)
            else:
                data = self.loader.load_file_by_type(file_path, format_type)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    def _detect_format_from_path(self, file_path: str) -> str:
        """Detect format from file path."""
        ext = os.path.splitext(file_path)[1].lower()
        return EXT_TO_FORMAT.get(ext, 'csv')
    
    def _load_large_file_chunked(self, file_path: str, format_type: str, chunk_size: int = 10000) -> pd.DataFrame:
        """Load large files in chunks to prevent memory issues."""
        try:
            self.logger.info(f"Loading large file {file_path} in chunks of {chunk_size} rows")
            
            if format_type == 'csv':
                # Load CSV in chunks
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    chunks.append(chunk)
                    if len(chunks) >= 10:  # Limit memory usage
                        combined = pd.concat(chunks, ignore_index=True)
                        chunks = [combined]
                
                if chunks:
                    return pd.concat(chunks, ignore_index=True)
                else:
                    return pd.DataFrame()
            
            elif format_type == 'txt':
                # For text files, try to detect if it's Stooq format
                try:
                    # Read first few lines to detect format
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                        
                    if '<TICKER>' in first_line:
                        # Stooq format - load in chunks
                        chunks = []
                        for chunk in pd.read_csv(file_path, chunksize=chunk_size, sep=','):
                            chunks.append(chunk)
                            if len(chunks) >= 10:
                                combined = pd.concat(chunks, ignore_index=True)
                                chunks = [combined]
                        
                        if chunks:
                            return pd.concat(chunks, ignore_index=True)
                    
                except Exception as e:
                    self.logger.warning(f"Error in chunked text loading: {str(e)}")
                
                # Fallback to regular loading
                return self.loader.load_file_by_type(file_path, format_type)
            
            else:
                # For other formats, use regular loading
                return self.loader.load_file_by_type(file_path, format_type)
                
        except Exception as e:
            self.logger.error(f"Error in chunked loading: {str(e)}")
            return pd.DataFrame()
    
    def _display_data(self, data):
        """Display data in the treeview."""
        try:
            # Create data source
            if self.current_data_source:
                self.current_data_source.close()
            
            # Check if data is empty
            if data is None or data.empty:
                self.logger.warning("No data to display - empty DataFrame")
                self.main_window.show_warning_message("No Data", "The loaded file contains no data.")
                return
            
            # Try to use database if available, otherwise use direct pandas display
            try:
                # Try database approach first
                # Use the same database file as the connector
                db_path = self.connector.db_path
                self.connector.write_shared_data("temp_display_data", data, "display")
                self.current_data_source = DataSource(db_path, "duckdb", "temp_display_data")
                self.treeview.set_data_source(self.current_data_source)
            except (ImportError, ValueError) as db_error:
                # Fallback to direct pandas display if database not available or data invalid
                self.logger.warning(f"Database not available or data invalid, using direct display: {db_error}")
                self.current_data_source = DataSource(None, "pandas")
                self.current_data_source.data = data
                self.current_data_source.total_rows = len(data)
                self.treeview.set_data_source(self.current_data_source)
            
            # Store current data
            self.current_data = data
            self.current_format = "display"
            self.unsaved_changes = False
            
            # Update main window
            self.main_window.set_current_file_path("Multiple files")
            
        except Exception as e:
            self.logger.error(f"Error displaying data: {str(e)}")
            raise
    
    def save_current_data(self):
        """Save current data to file."""
        if self.current_data is None or self.current_data.empty:
            self.main_window.show_warning_message("Warning", "No data to save")
            return
        
        try:
            # Open save dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Data As",
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("JSON files", "*.json"),
                    ("Parquet files", "*.parquet"),
                    ("Feather files", "*.feather"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Detect format from extension
                format_type = self._detect_format_from_path(file_path)
                
                # Save data
                DataLoader.save_file_by_type(self.current_data, file_path, format_type)
                
                self.unsaved_changes = False
                self.main_window.show_info_message("Success", f"Data saved to {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to save data: {str(e)}")
    
    def refresh_data(self):
        """Refresh the current data display."""
        if self.current_data is not None:
            self.treeview.refresh()
            self.status_label.config(text="Data refreshed")
    
    def clear_data(self):
        """Clear the current data."""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before clearing?"
            )
            
            if result is True:
                self.save_current_data()
            elif result is None:  # Cancel
                return
        
        # Clear data
        self.treeview.clear()
        self.current_data = None
        self.current_format = None
        self.unsaved_changes = False
        
        if self.current_data_source:
            self.current_data_source.close()
            self.current_data_source = None
        
        self.status_label.config(text="No data loaded")
        self.main_window.set_current_file_path(None)
    
    def open_search_dialog(self):
        """Open search dialog."""
        # Create search dialog
        search_window = tk.Toplevel(self.frame)
        search_window.title("Search Data")
        search_window.geometry("400x200")
        search_window.resizable(False, False)
        
        # Center the window
        search_window.transient(self.frame)
        search_window.grab_set()
        
        # Search entry
        ttk.Label(search_window, text="Search term:").pack(pady=5)
        search_entry = ttk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        # Column selection
        ttk.Label(search_window, text="Search in column (optional):").pack(pady=5)
        column_var = tk.StringVar()
        column_combo = ttk.Combobox(search_window, textvariable=column_var, width=37)
        if self.current_data is not None:
            column_combo['values'] = list(self.current_data.columns)
        column_combo.pack(pady=5)
        
        # Search button
        def perform_search():
            search_term = search_entry.get().strip()
            column = column_var.get().strip() or None
            
            if search_term:
                matching_indices = self.treeview.search_and_highlight(search_term, column)
                search_window.destroy()
                
                if matching_indices:
                    self.status_label.config(text=f"Found {len(matching_indices)} matches")
                else:
                    self.status_label.config(text="No matches found")
        
        ttk.Button(search_window, text="Search", command=perform_search).pack(pady=10)
        
        # Bind Enter key
        search_entry.bind('<Return>', lambda e: perform_search())
    
    def open_filter_dialog(self):
        """Open filter dialog."""
        if self.current_data is None or self.current_data.empty:
            self.main_window.show_warning_message("Warning", "No data to filter")
            return
        
        try:
            from .widgets.filter_dialog import FilterDialog
            
            def apply_filter(filtered_data):
                """Apply filtered data to display."""
                try:
                    self.logger.info(f"Applying filter: received {len(filtered_data)} rows")
                    self.logger.info(f"Filtered data columns: {list(filtered_data.columns)}")
                    self.logger.info(f"Filtered data shape: {filtered_data.shape}")
                    
                    self.current_data = filtered_data
                    self._display_data(filtered_data)
                    self.unsaved_changes = True
                    self.main_window.show_info_message("Success", f"Filter applied: {len(filtered_data)} rows remaining")
                    self.logger.info(f"Filter applied successfully: {len(filtered_data)} rows displayed")
                except Exception as e:
                    self.logger.error(f"Error applying filter: {str(e)}")
                    self.main_window.show_error_message("Error", f"Failed to apply filter: {str(e)}")
            
            # Create and show filter dialog
            filter_dialog = FilterDialog(self.frame, self.current_data, apply_filter)
            # Pass main window reference for thread-safe updates
            filter_dialog.main_window = self.main_window
            
        except Exception as e:
            self.logger.error(f"Error opening filter dialog: {str(e)}")
            self.main_window.show_error_message("Error", f"Failed to open filter dialog: {str(e)}")
    
    def on_data_selection(self, event):
        """Handle data selection events."""
        selected_items = self.treeview.get_selected_items()
        if selected_items:
            self.status_label.config(text=f"{len(selected_items)} items selected")
    
    def on_data_double_click(self, event):
        """Handle data double-click events."""
        # Could open detailed view or edit dialog
        pass
    
    def on_loading_complete(self):
        """Handle loading completion."""
        self.status_label.config(text="Loading complete")
    
    def on_loading_cancelled(self):
        """Handle loading cancellation."""
        self.status_label.config(text="Loading cancelled")
    
    def on_tab_activated(self):
        """Handle tab activation."""
        # Refresh data when tab becomes active
        if self.current_data is not None:
            self.refresh_data()
    
    def on_window_resize(self):
        """Handle window resize events."""
        try:
            # Update treeview layout if needed
            if hasattr(self, 'treeview') and self.treeview:
                self.treeview.refresh()
            
            # Update status if needed
            if hasattr(self, 'status_label') and self.status_label:
                # Could update status with window size info
                pass
                
        except Exception as e:
            self.logger.error(f"Error handling window resize in DataTab: {str(e)}")
    
    def save_unsaved_changes(self):
        """Save any unsaved changes."""
        if self.unsaved_changes:
            try:
                self.save_current_data()
            except Exception as e:
                self.logger.error(f"Error saving unsaved changes: {str(e)}")
    
    def cleanup_resources(self):
        """Clean up resources."""
        try:
            if self.current_data_source:
                self.current_data_source.close()
                self.current_data_source = None
        except Exception as e:
            self.logger.error(f"Error cleaning up data tab resources: {str(e)}")
