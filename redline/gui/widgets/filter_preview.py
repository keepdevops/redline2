#!/usr/bin/env python3
"""
Filter Preview Helper for FilterDialog
Handles preview section creation and updates.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class FilterPreviewHelper:
    """Helper class for preview functionality in FilterDialog."""
    
    def __init__(self, filter_dialog):
        """Initialize with reference to FilterDialog."""
        self.filter_dialog = filter_dialog
        self.logger = logging.getLogger(__name__)
    
    def create_preview_section(self, parent):
        """Create preview section."""
        preview_frame = ttk.LabelFrame(parent, text="Filter Preview", padding=10)
        preview_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Preview info
        self.filter_dialog.preview_label = ttk.Label(preview_frame, text=f"Original data: {len(self.filter_dialog.data)} rows, {len(self.filter_dialog.data.columns)} columns")
        self.filter_dialog.preview_label.pack(anchor=tk.W)
        
        # Update preview button
        ttk.Button(preview_frame, text="Update Preview", 
                  command=self.filter_dialog.update_preview).pack(anchor=tk.W, pady=(5, 0))
        
        # Preview results
        self.filter_dialog.preview_text = tk.Text(preview_frame, height=4, width=70)
        self.filter_dialog.preview_text.pack(fill=tk.X, pady=(5, 0))
        
        # Scrollbar for preview
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.filter_dialog.preview_text.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.filter_dialog.preview_text.configure(yscrollcommand=preview_scrollbar.set)
    
    def update_preview(self):
        """Update filter preview."""
        try:
            filtered_data = self.filter_dialog.logic_helper.apply_filters_to_data(self.filter_dialog.data, preview=True)
            
            if filtered_data is not None:
                self.filter_dialog.preview_label.config(text=f"Original: {len(self.filter_dialog.data)} rows → Filtered: {len(filtered_data)} rows")
                
                # Show preview of filtered data
                preview_text = "Preview of filtered data:\n"
                if len(filtered_data) > 0:
                    preview_text += str(filtered_data.head(3).to_string())
                    if len(filtered_data) > 3:
                        preview_text += f"\n... and {len(filtered_data) - 3} more rows"
                else:
                    preview_text += "No data matches the current filters"
                    
                self.filter_dialog.preview_text.delete(1.0, tk.END)
                self.filter_dialog.preview_text.insert(1.0, preview_text)
            else:
                self.filter_dialog.preview_label.config(text=f"Original data: {len(self.filter_dialog.data)} rows (invalid filter)")
                self.filter_dialog.preview_text.delete(1.0, tk.END)
                self.filter_dialog.preview_text.insert(1.0, "Invalid filter expression")
                
        except Exception as e:
            self.filter_dialog.preview_label.config(text=f"Original data: {len(self.filter_dialog.data)} rows (filter error)")
            self.filter_dialog.preview_text.delete(1.0, tk.END)
            self.filter_dialog.preview_text.insert(1.0, f"Filter error: {str(e)}")
    
    def schedule_preview_update(self):
        """Schedule preview update to avoid too frequent updates."""
        if hasattr(self.filter_dialog, '_preview_timer'):
            self.filter_dialog.dialog.after_cancel(self.filter_dialog._preview_timer)
        self.filter_dialog._preview_timer = self.filter_dialog.dialog.after(500, self.update_preview)

