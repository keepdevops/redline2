#!/usr/bin/env python3
"""
REDLINE Virtual Scrolling TreeView
A virtual scrolling TreeView that only loads visible items into memory.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
import threading
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
        
        # Lock to prevent concurrent updates
        self._update_lock = threading.Lock()
        self._loading = False
        
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
        
        # Ensure at least one row is visible
        if visible_end <= visible_start:
            visible_end = min(visible_start + 10, self.total_rows)
        
        if visible_start != self.visible_start or visible_end != self.visible_end:
            self.logger.debug(f"Updating visible range: {self.visible_start}-{self.visible_end} -> {visible_start}-{visible_end}")
            self.visible_start = visible_start
            self.visible_end = visible_end
            self._load_visible_items()
        else:
            self.logger.debug(f"Visible range unchanged: {visible_start}-{visible_end}")
    
    def _load_visible_items(self):
        """Load only the visible items into the tree."""
        if not self.data_source:
            return
        
        # Prevent concurrent loading
        if self._loading:
            self.logger.debug("Already loading items, skipping duplicate call")
            return
        
        with self._update_lock:
            if self._loading:
                return
            self._loading = True
        
        try:
            # Clear current items first - get all children before deleting to avoid issues
            children = self.tree.get_children()
            if children:
                self.logger.debug(f"Clearing {len(children)} existing items before loading")
                self.tree.delete(*children)
            
            # Verify tree is empty
            remaining = self.tree.get_children()
            if remaining:
                self.logger.warning(f"Tree still has {len(remaining)} items after delete, forcing clear")
                # Force clear by deleting individually
                for item in list(remaining):
                    try:
                        self.tree.delete(item)
                    except:
                        pass
            
            # Load visible items
            items_to_load = list(range(self.visible_start, min(self.visible_end + 1, self.total_rows)))
            self.logger.debug(f"Loading {len(items_to_load)} items: rows {self.visible_start} to {min(self.visible_end, self.total_rows - 1)}")
            
            inserted_count = 0
            for i in items_to_load:
                # Check if item already exists (shouldn't happen after clear, but double-check)
                existing_iid = f"row_{i}"
                try:
                    self.tree.item(existing_iid)
                    self.logger.warning(f"Row {i} already exists, skipping duplicate")
                    continue
                except:
                    pass  # Item doesn't exist, which is correct
                
                if i in self.cached_data:
                    row_data = self.cached_data[i]
                else:
                    row_data = self.data_source.get_row(i)
                    if len(self.cached_data) < self.cache_size:
                        self.cached_data[i] = row_data
                
                # Insert item with row index as identifier
                # Use row index as iid to prevent duplicates
                try:
                    item_id = self.tree.insert('', 'end', iid=existing_iid, text=str(i), values=row_data)
                    inserted_count += 1
                except tk.TclError as e:
                    # TclError usually means iid already exists
                    if "already exists" in str(e).lower():
                        self.logger.warning(f"Row {i} iid already exists, skipping: {str(e)}")
                        continue
                    else:
                        self.logger.error(f"Error inserting row {i}: {str(e)}")
                        # Try without iid as fallback
                        try:
                            item_id = self.tree.insert('', 'end', text=str(i), values=row_data)
                            inserted_count += 1
                        except Exception as e2:
                            self.logger.error(f"Error inserting row {i} without iid: {str(e2)}")
                except Exception as e:
                    self.logger.error(f"Unexpected error inserting row {i}: {str(e)}")
            
            self.logger.debug(f"Successfully inserted {inserted_count} items")
            
        finally:
            self._loading = False
    
    def set_data_source(self, data_source: DataSource):
        """Set the data source for virtual scrolling."""
        self.logger.info(f"Setting data source: {data_source}")
        self.data_source = data_source
        self.total_rows = data_source.get_total_rows()
        self.logger.info(f"Data source set: {self.total_rows} total rows")
        self.cached_data.clear()
        self._update_visible_range()
        self.logger.info("Visible range updated")
    
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
