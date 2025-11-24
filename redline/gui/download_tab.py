#!/usr/bin/env python3
"""
REDLINE Download Tab
GUI tab for downloading financial data from various sources.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector
from ..downloaders.yahoo_downloader import YahooDownloader
from ..downloaders.stooq_downloader import StooqDownloader
from ..downloaders.multi_source import MultiSourceDownloader
from ..downloaders.bulk_downloader import BulkDownloader
from .utils.download_ui import DownloadUIHelper
from .utils.download_logic import DownloadLogicHelper
from .utils.download_utils import DownloadUtilsHelper
from .utils.download_file_ops import DownloadFileOpsHelper
from .utils.download_events import DownloadEventsHelper

logger = logging.getLogger(__name__)

class DownloadTab:
    """Download tab for acquiring financial data from various sources."""
    
    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        """Initialize download tab."""
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Downloaders
        self.yahoo_downloader = YahooDownloader()
        self.stooq_downloader = StooqDownloader()
        self.multi_downloader = MultiSourceDownloader()
        self.bulk_downloader = BulkDownloader(max_workers=4)  # Use 4 workers for faster downloads
        
        # Variables
        self.ticker_input = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value='data/downloads')
        self.api_key_var = tk.StringVar()
        self.bulk_mode_var = tk.BooleanVar()
        
        # Initialize helper classes
        self.ui_helper = DownloadUIHelper(self)
        self.logic_helper = DownloadLogicHelper(self)
        self.utils_helper = DownloadUtilsHelper(self)
        self.file_ops_helper = DownloadFileOpsHelper(self)
        self.events_helper = DownloadEventsHelper(self)
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Create widgets
        self.ui_helper.create_widgets()
        
        # Setup event handlers
        self.events_helper.setup_event_handlers()
        
        # Set default date range
        self.utils_helper.set_date_range(365)  # Default to 1 year
    
    def on_tab_activated(self):
        """Handle tab activation."""
        self.events_helper.on_tab_activated()
    
    def on_window_resize(self):
        """Handle window resize events."""
        self.events_helper.on_window_resize()
    
    def _on_left_frame_configure(self, event):
        """Handle scrollable frame configuration."""
        self.events_helper._on_left_frame_configure(event)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.events_helper._on_mousewheel(event)
