#!/usr/bin/env python3
"""
Legacy GUI virtual scrolling utilities extracted from StockAnalyzerGUI class.
Handles virtual scrolling for large datasets.
"""

import logging
from tkinter import ttk

logger = logging.getLogger(__name__)


class VirtualScrollingManager:
    """Virtual scrolling manager for legacy GUI."""
    
    @staticmethod
    def enable_virtual_scrolling(data_tree, data_source):
        """Enable virtual scrolling for better performance with large datasets."""
        try:
            from redline.gui.widgets.virtual_treeview_shared import VirtualScrollingTreeview
            
            # Get treeview parent and columns
            parent = data_tree.master
            columns = data_tree['columns'] if data_tree['columns'] else []
            
            # Create virtual scrolling treeview
            virtual_tree = VirtualScrollingTreeview(parent, columns)
            virtual_tree.set_data_source(data_source)
            
            logger.info("Virtual scrolling enabled")
            return virtual_tree
            
        except Exception as e:
            logger.error(f"Failed to enable virtual scrolling: {str(e)}")
            return None

    @staticmethod
    def load_data_with_virtual_scrolling(file_path, format_type, data_tree):
        """Load data using virtual scrolling for large files."""
        try:
            from redline.gui.widgets.data_source_shared import DataSource
            from redline.gui.widgets.virtual_treeview_shared import VirtualScrollingTreeview
            
            # Create data source
            data_source = DataSource(file_path, format_type)
            
            # Get treeview parent and columns
            parent = data_tree.master
            columns = data_tree['columns'] if data_tree['columns'] else []
            
            # Create virtual scrolling treeview
            virtual_tree = VirtualScrollingTreeview(parent, columns)
            virtual_tree.set_data_source(data_source)
            
            logger.info(f"Loaded {data_source.get_total_rows()} rows with virtual scrolling")
            return virtual_tree, data_source
            
        except Exception as e:
            logger.error(f"Failed to load data with virtual scrolling: {str(e)}")
            return None, None

