#!/usr/bin/env python3
"""
REDLINE Virtual Scrolling TreeView
A virtual scrolling TreeView that only loads visible items into memory.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from .data_source import DataSource

logger = logging.getLogger(__name__)

class VirtualScrollingTreeview:
    """A virtual scrolling TreeView that only loads visible items into memory."""
    
    def __init__(self, parent, columns: List[str], **kwargs):
        """Initialize virtual scrolling treeview."""
        self.parent = parent
        self.columns = columns
        self.tree = ttk.Treeview(parent, columns=columns, **kwargs)
        self.logger = logging.getLogger(__name__)
        
        # Virtual scrolling state
        self.total_rows = 0
        self.visible_start = 0
        self.visible_end = 0
        self.row_height = 20  # Approximate row height
        self.visible_count = 0
        self.data_source: Optional[DataSource] = None
        self.cached_data: Dict[int, List] = {}
        self.cache_size = 1000  # Number of rows to cache
        
        # Bind scroll events
        self.tree.bind('<Configure>', self._on_configure)
        self.tree.bind('<MouseWheel>', self._on_scroll)
        self.tree.bind('<Button-4>', self._on_scroll)  # Linux scroll up
        self.tree.bind('<Button-5>', self._on_scroll)  # Linux scroll down
        
        # Bind selection events
        self.tree.bind('<<TreeviewSelect>>', self._on_selection)
        
        # Current selection
        self.selected_items = []
        
    def _on_configure(self, event):
        """Handle window resize to recalculate visible items."""
        self._update_visible_range()
    
    def _on_scroll(self, event):
        """Handle scroll events to update visible items."""
        self._update_visible_range()
    
    def _on_selection(self, event):
        """Handle selection changes."""
        self.selected_items = self.tree.selection()
    
    def _update_visible_range(self):
        """Calculate which rows should be visible."""
        if not self.data_source:
            return
        
        # Calculate visible range based on scroll position
        scroll_pos = self.tree.yview()
        visible_start = int(scroll_pos[0] * self.total_rows)
        visible_end = int(scroll_pos[1] * self.total_rows)
        
        if visible_start != self.visible_start or visible_end != self.visible_end:
            self.visible_start = visible_start
            self.visible_end = visible_end
            self._load_visible_items()
    
    def _load_visible_items(self):
        """Load only the visible items into the tree."""
        if not self.data_source:
            return
        
        # Clear current items
        self.tree.delete(*self.tree.get_children())
        
        # Load visible items
        for i in range(self.visible_start, min(self.visible_end + 1, self.total_rows)):
            if i in self.cached_data:
                row_data = self.cached_data[i]
            else:
                row_data = self.data_source.get_row(i)
                if len(self.cached_data) < self.cache_size:
                    self.cached_data[i] = row_data
            
            # Insert item with row index as identifier
            item_id = self.tree.insert('', 'end', text=str(i), values=row_data)
    
    def set_data_source(self, data_source: DataSource):
        """Set the data source for virtual scrolling."""
        self.data_source = data_source
        self.total_rows = data_source.get_total_rows()
        self.cached_data.clear()
        self._update_visible_range()
    
    def refresh(self):
        """Refresh the display."""
        self._update_visible_range()
    
    def clear(self):
        """Clear all items from the tree."""
        self.tree.delete(*self.tree.get_children())
        self.cached_data.clear()
        self.total_rows = 0
        self.data_source = None
    
    def get_selected_items(self) -> List[str]:
        """Get list of selected item IDs."""
        return self.tree.selection()
    
    def get_selected_data(self) -> List[List]:
        """Get data for selected items."""
        selected_data = []
        for item_id in self.tree.selection():
            values = self.tree.item(item_id, 'values')
            selected_data.append(list(values))
        return selected_data
    
    def search_and_highlight(self, search_term: str, column: str = None) -> List[int]:
        """
        Search for items and highlight matches.
        
        Args:
            search_term: Term to search for
            column: Specific column to search (None for all columns)
            
        Returns:
            List of matching row indices
        """
        if not self.data_source:
            return []
        
        matching_indices = self.data_source.search_rows(search_term, column)
        
        # Clear previous selection
        self.tree.selection_remove(self.tree.selection())
        
        # Highlight matching items that are currently visible
        for i, item in enumerate(self.tree.get_children()):
            row_index = self.visible_start + i
            if row_index in matching_indices:
                self.tree.selection_add(item)
        
        return matching_indices
    
    def filter_and_display(self, conditions: Dict[str, Any]) -> List[int]:
        """
        Filter data and display matching items.
        
        Args:
            conditions: Dictionary of column -> value conditions
            
        Returns:
            List of matching row indices
        """
        if not self.data_source:
            return []
        
        matching_indices = self.data_source.filter_rows(conditions)
        
        # Clear current display
        self.tree.delete(*self.tree.get_children())
        
        # Display only matching items
        for i, index in enumerate(matching_indices):
            if index in self.cached_data:
                row_data = self.cached_data[index]
            else:
                row_data = self.data_source.get_row(index)
                if len(self.cached_data) < self.cache_size:
                    self.cached_data[index] = row_data
            
            self.tree.insert('', 'end', values=row_data)
        
        return matching_indices
    
    def get_visible_range(self) -> tuple:
        """Get the current visible row range."""
        return (self.visible_start, self.visible_end)
    
    def scroll_to_row(self, row_index: int):
        """Scroll to a specific row."""
        if not self.data_source or row_index < 0 or row_index >= self.total_rows:
            return
        
        # Calculate scroll position
        scroll_position = row_index / self.total_rows
        
        # Set scroll position
        self.tree.yview_moveto(scroll_position)
        self._update_visible_range()
    
    def get_row_count(self) -> int:
        """Get total number of rows."""
        return self.total_rows
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache."""
        return {
            'cache_size': len(self.cached_data),
            'max_cache_size': self.cache_size,
            'cache_hit_ratio': len(self.cached_data) / max(self.total_rows, 1)
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self.cached_data.clear()
        self._load_visible_items()
    
    def configure_column(self, column: str, **kwargs):
        """Configure a column."""
        self.tree.column(column, **kwargs)
    
    def configure_heading(self, column: str, **kwargs):
        """Configure a column heading."""
        self.tree.heading(column, **kwargs)
    
    def bind_event(self, event: str, handler):
        """Bind an event handler."""
        self.tree.bind(event, handler)
    
    def pack(self, **kwargs):
        """Pack the treeview widget."""
        self.tree.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the treeview widget."""
        self.tree.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place the treeview widget."""
        self.tree.place(**kwargs)
    
    def destroy(self):
        """Destroy the treeview widget."""
        if self.data_source:
            self.data_source.close()
        self.tree.destroy()
    
    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying treeview."""
        return getattr(self.tree, name)
