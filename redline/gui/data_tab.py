#!/usr/bin/env python3
"""
REDLINE Data Tab
GUI tab for data loading, viewing, and management operations.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector
from .widgets.virtual_treeview import VirtualScrollingTreeview
from .utils.file_operations import FileOperationsHelper
from .utils.data_display import DataDisplayHelper
from .utils.data_management import DataManagementHelper

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
        
        # Initialize helper modules
        self.file_ops = FileOperationsHelper(self)
        self.display = DataDisplayHelper(self)
        self.ops = DataManagementHelper(self)
        
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
        
        # No progress tracker - removed for cleaner interface
        
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
        
        # No progress tracker callbacks - removed for cleaner interface
    
    def open_file_dialog(self):
        """Open file dialog to select data files."""
        return self.file_ops.open_file_dialog()
    
    def load_converted_files(self):
        """Load converted files from the converter output directory."""
        return self.file_ops.load_converted_files()
    
    def load_file(self, file_path: str):
        """Load a single file."""
        self.file_ops.load_files([file_path])
    
    def load_files(self, file_paths):
        """Load multiple files."""
        return self.file_ops.load_files(file_paths)
    
    def _display_data(self, data):
        """Display data in the treeview."""
        return self.display.display_data(data)
    
    def save_current_data(self):
        """Save current data to file."""
        return self.ops.save_current_data()
    
    def refresh_data(self):
        """Refresh the current data display."""
        return self.display.refresh_data()
    
    def clear_data(self):
        """Clear the current data."""
        return self.ops.clear_data()
    
    def open_search_dialog(self):
        """Open search dialog."""
        return self.ops.open_search_dialog()
    
    def open_filter_dialog(self):
        """Open filter dialog."""
        return self.ops.open_filter_dialog()
    
    def on_data_selection(self, event):
        """Handle data selection events."""
        return self.display.on_data_selection(event)
    
    def on_data_double_click(self, event):
        """Handle data double-click events."""
        return self.display.on_data_double_click(event)
    
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
        return self.ops.save_unsaved_changes()
    
    def cleanup_resources(self):
        """Clean up resources."""
        try:
            if self.current_data_source:
                self.current_data_source.close()
                self.current_data_source = None
        except Exception as e:
            self.logger.error(f"Error cleaning up data tab resources: {str(e)}")
