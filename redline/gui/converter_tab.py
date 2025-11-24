#!/usr/bin/env python3
"""
REDLINE Converter Tab
GUI tab for data format conversion utilities.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
import pandas as pd

from redline.core.data_loader import DataLoader
from redline.core.format_converter import FormatConverter
from redline.database.connector import DatabaseConnector
from redline.gui.widgets.progress_tracker import ProgressTracker
from redline.core.schema import EXT_TO_FORMAT, FORMAT_DIALOG_INFO
from redline.gui.utils.conversion_ui import ConversionUIHelper
from redline.gui.utils.conversion_logic import ConversionLogicHelper
from redline.gui.utils.file_browser import FileBrowserHelper
from redline.gui.utils.converter_events import ConverterEventsHelper

logger = logging.getLogger(__name__)

class ConverterTab:
    """Converter tab for data format conversion."""

    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

        self.frame = ttk.Frame(parent)
        self.converter = FormatConverter()
        
        # Initialize helper modules
        self.ui_helper = ConversionUIHelper(self)
        self.logic_helper = ConversionLogicHelper(self)
        self.browser_helper = FileBrowserHelper(self)
        self.events_helper = ConverterEventsHelper(self)
        
        # Conversion state
        self.conversion_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.converted_files: List[str] = []
        
        self.create_widgets()
        self.events_helper.setup_event_handlers()
        
        # Validate that only supported formats are available
        self._validate_supported_formats()
        
    def _validate_supported_formats(self):
        """Validate that only supported formats are available in the GUI."""
        try:
            supported_formats = self.converter.get_supported_formats()
            schema_formats = list(FORMAT_DIALOG_INFO.keys())
            
            # Check for formats in schema that are not supported
            unsupported_in_schema = [f for f in schema_formats if f not in supported_formats]
            if unsupported_in_schema:
                self.logger.warning(f"Found unsupported formats in schema: {unsupported_in_schema}")
                self.logger.warning("These formats will be removed from GUI dropdowns")
            
            # Check for supported formats not in schema
            missing_in_schema = [f for f in supported_formats if f not in schema_formats]
            if missing_in_schema:
                self.logger.warning(f"Supported formats missing from schema: {missing_in_schema}")
                
            self.logger.info(f"Format validation complete. Supported: {supported_formats}")
            
        except Exception as e:
            self.logger.error(f"Error validating supported formats: {str(e)}")
        
    def create_widgets(self):
        """Create converter tab widgets."""
        # Main container with scrollbar
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Data Format Converter", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Input section
        self.ui_helper.create_input_section(scrollable_frame)
        
        # Output section
        self.ui_helper.create_output_section(scrollable_frame)
        
        # Conversion options
        self.ui_helper.create_conversion_options(scrollable_frame)
        
        # Batch conversion
        self.ui_helper.create_batch_section(scrollable_frame)
        
        # Progress section
        self.ui_helper.create_progress_section(scrollable_frame)
        
        # Results section
        self.ui_helper.create_results_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    # All UI creation methods are delegated to ui_helper
    # All event handlers are delegated to events_helper
    # All file browsing is delegated to browser_helper
    # All conversion logic is delegated to logic_helper
    
    def add_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0",
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
            
    def on_tab_activated(self):
        """Handle tab activation."""
        # Refresh any necessary data when tab becomes active
        pass
    
    def on_window_resize(self):
        """Handle window resize events."""
        try:
            # Update results tree layout if needed
            if hasattr(self, 'results_tree') and self.results_tree:
                # Could update tree column widths or refresh display
                pass
                
        except Exception as e:
            self.logger.error(f"Error handling window resize in ConverterTab: {str(e)}")
