#!/usr/bin/env python3
"""
Test script to verify export improvements and data statistics functionality.
This test simulates the conditions to test enhanced export and statistics features.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import pandas as pd
import numpy as np
import tempfile

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import StockAnalyzerGUI, DataLoader, DatabaseConnector

def test_export_and_stats():
    """Test export improvements and data statistics functionality"""
    print("Testing export improvements and data statistics...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Export & Stats Test")
    root.geometry("1200x800")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Create test data with different column types
    test_data = pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX'],
        'timestamp': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', 
                     '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08'],
        'open': [150.0, 2800.0, 300.0, 120.0, 3300.0, 180.0, 400.0, 250.0],
        'high': [155.0, 2850.0, 305.0, 125.0, 3350.0, 185.0, 410.0, 255.0],
        'low': [148.0, 2750.0, 295.0, 115.0, 3250.0, 175.0, 390.0, 245.0],
        'close': [152.0, 2820.0, 302.0, 122.0, 3320.0, 182.0, 405.0, 252.0],
        'volume': [1000000, 500000, 800000, 2000000, 750000, 1200000, 900000, 600000],
        'description': ['Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.', 'Tesla Inc.', 
                       'Amazon.com Inc.', 'Meta Platforms', 'NVIDIA Corp.', 'Netflix Inc.']
    })
    
    # Save test data to a CSV file
    test_file = 'data/test_export_stats.csv'
    os.makedirs('data', exist_ok=True)
    test_data.to_csv(test_file, index=False)
    
    def test_get_visible_data():
        """Test get_visible_data functionality"""
        print("  Testing get_visible_data functionality...")
        
        # Populate treeview with test data
        gui.setup_smart_columns(test_data)
        gui.store_original_data(test_data)
        
        # Clear and populate treeview
        gui.data_tree.delete(*gui.data_tree.get_children())
        for _, row in test_data.iterrows():
            gui.data_tree.insert('', 'end', values=tuple(row))
        
        # Test getting all visible data
        df = gui.get_visible_data()
        assert len(df) == len(test_data), f"Expected {len(test_data)} rows, got {len(df)}"
        assert list(df.columns) == list(test_data.columns), "Column mismatch"
        print("    ✓ get_visible_data works for all data")
        
        # Test getting filtered data
        gui.search_var.set("AAPL")
        gui.on_search_change()
        
        df_filtered = gui.get_visible_data()
        assert len(df_filtered) == 1, f"Expected 1 row for AAPL, got {len(df_filtered)}"
        assert df_filtered.iloc[0]['ticker'] == 'AAPL', "Filtered data doesn't contain AAPL"
        print("    ✓ get_visible_data works for filtered data")
    
    def test_statistics_functionality():
        """Test statistics functionality"""
        print("  Testing statistics functionality...")
        
        # Clear search to show all data
        gui.clear_search()
        
        # Test statistics for all data
        print("    Testing statistics for all data...")
        try:
            # Get visible data and calculate expected stats
            df = gui.get_visible_data()
            assert len(df) == len(test_data), f"Expected {len(test_data)} rows, got {len(df)}"
            
            # Test that statistics can be calculated
            stats = df.describe(include='all').T
            assert not stats.empty, "Statistics should not be empty"
            
            print("    ✓ Statistics for all data works")
            
        except Exception as e:
            print(f"    ❌ Statistics test failed: {str(e)}")
            raise
    
    def test_statistics_filtered_data():
        """Test statistics for filtered/searched data"""
        print("  Testing statistics for filtered data...")
        
        # Apply search filter to show only rows with 'Inc.' in the description
        gui.search_var.set("Inc.")
        gui.on_search_change()
        
        # Verify filtered data
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) > 0, "Should have some filtered results"
        
        try:
            # Get visible data and calculate stats
            df = gui.get_visible_data()
            assert len(df) < len(test_data), "Filtered data should be smaller than full dataset"
            
            # Test that statistics reflect only filtered data
            stats = df.describe(include='all').T
            assert not stats.empty, "Filtered statistics should not be empty"
            
            print("    ✓ Statistics for filtered data works")
            
        except Exception as e:
            print(f"    ❌ Filtered statistics test failed: {str(e)}")
            raise
    
    def test_export_data_structure():
        """Test that export_data method has the correct structure"""
        print("  Testing export_data method structure...")
        
        # Test that the method exists and has the right signature
        assert hasattr(gui, 'export_data'), "export_data method should exist"
        assert callable(gui.export_data), "export_data should be callable"
        
        # Test that get_visible_data returns the right structure
        df = gui.get_visible_data()
        assert isinstance(df, pd.DataFrame), "get_visible_data should return a DataFrame"
        
        print("    ✓ Export data structure is correct")
    
    def test_search_and_clear():
        """Test search and clear functionality"""
        print("  Testing search and clear functionality...")
        
        # Test search
        gui.search_var.set("AAPL")
        gui.on_search_change()
        
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) == 1, f"Expected 1 result for 'AAPL', got {len(visible_items)}"
        
        # Test clear
        gui.clear_search()
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) == len(test_data), f"Expected {len(test_data)} items after clear, got {len(visible_items)}"
        
        print("    ✓ Search and clear functionality works")
    
    def run_tests():
        """Run all tests"""
        try:
            test_get_visible_data()
            test_statistics_functionality()
            test_statistics_filtered_data()
            test_export_data_structure()
            test_search_and_clear()
            
            print("\n🎉 All export and statistics tests passed!")
            
            # Show success message
            messagebox.showinfo("Test Results", 
                "All export and statistics tests passed!\n\n"
                "✅ get_visible_data works for all data\n"
                "✅ get_visible_data works for filtered data\n"
                "✅ Statistics for all data works\n"
                "✅ Statistics for filtered data works\n"
                "✅ Export data structure is correct\n"
                "✅ Search and clear functionality works")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            messagebox.showerror("Test Failed", f"Test failed: {str(e)}")
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
            root.after(2000, root.destroy)
    
    # Run tests after a short delay to let GUI initialize
    root.after(1000, run_tests)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_export_and_stats() 