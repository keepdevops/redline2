#!/usr/bin/env python3
"""
Legacy GUI performance monitoring utilities extracted from StockAnalyzerGUI class.
Handles performance monitoring, memory optimization, and virtual scrolling.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring utilities for legacy GUI."""
    
    @staticmethod
    def setup_performance_monitoring(root):
        """Setup performance monitoring frame.
        
        Returns:
            dict: Dictionary with performance widgets and update function
        """
        perf_frame = ttk.LabelFrame(root, text="Performance Monitor")
        perf_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        memory_label = ttk.Label(perf_frame, text="Memory: 0 MB")
        memory_label.pack(side='left', padx=5)
        
        return {
            'frame': perf_frame,
            'memory_label': memory_label
        }
    
    @staticmethod
    def update_performance_monitor(root, memory_label):
        """Update performance monitoring display."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_label:
                memory_label.config(text=f"Memory: {memory_mb:.1f} MB")
            
            # Schedule next update
            root.after(5000, lambda: PerformanceMonitor.update_performance_monitor(root, memory_label))
            
        except ImportError:
            logger.warning("psutil not available for performance monitoring")
            if memory_label:
                memory_label.config(text="Memory: N/A (psutil not installed)")
        except Exception as e:
            logger.error(f"Failed to update performance monitor: {str(e)}")

    @staticmethod
    def optimize_memory_usage(data_tree, original_data):
        """Optimize memory usage by clearing cached data."""
        try:
            # Clear treeview items that are not visible
            all_items = data_tree.get_children()
            if len(all_items) > 1000:
                # Keep only first and last 500 items visible
                items_to_remove = all_items[500:-500]
                for item in items_to_remove:
                    data_tree.detach(item)
            
            # Clear original_data if it's too large
            if original_data is not None and len(original_data) > 10000:
                logger.info("Large dataset detected, consider using virtual scrolling")
            
            logger.info("Memory optimization completed")
        except Exception as e:
            logger.error(f"Failed to optimize memory: {str(e)}")

