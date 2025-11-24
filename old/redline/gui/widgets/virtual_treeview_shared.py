#!/usr/bin/env python3
"""
VirtualScrollingTreeview class extracted from data_module_shared.py (shared module)
A virtual scrolling TreeView that only loads visible items into memory.
"""

import logging
from tkinter import ttk

logger = logging.getLogger(__name__)


class VirtualScrollingTreeview:
    """A virtual scrolling TreeView that only loads visible items into memory."""
    
    def __init__(self, parent, columns, **kwargs):
        """Initialize virtual scrolling treeview."""
        self.parent = parent
        self.columns = columns
        self.tree = ttk.Treeview(parent, columns=columns, **kwargs)
        
        # Virtual scrolling state
        self.total_rows = 0
        self.visible_start = 0
        self.visible_end = 0
        self.row_height = 20  # Approximate row height
        self.visible_count = 0
        self.data_source = None
        self.cached_data = {}
        self.cache_size = 1000  # Number of rows to cache
        
        # Bind scroll events
        self.tree.bind('<Configure>', self._on_configure)
        self.tree.bind('<MouseWheel>', self._on_scroll)
        
    def _on_configure(self, event):
        """Handle window resize to recalculate visible items."""
        self._update_visible_range()
        
    def _on_scroll(self, event):
        """Handle scroll events to update visible items."""
        self._update_visible_range()
        
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
                    
            self.tree.insert('', 'end', values=row_data)
    
    def set_data_source(self, data_source):
        """Set the data source for virtual scrolling."""
        self.data_source = data_source
        self.total_rows = data_source.get_total_rows()
        self._update_visible_range()
        
    def refresh(self):
        """Refresh the display."""
        self._update_visible_range()

