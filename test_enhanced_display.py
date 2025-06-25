#!/usr/bin/env python3
"""
Test script to verify enhanced data display and search functionality.
This test simulates the conditions to test smart column handling and search features.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import pandas as pd
import numpy as np

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import StockAnalyzerGUI, DataLoader, DatabaseConnector

def test_enhanced_display():
    """Test enhanced data display and search functionality"""
    print("Testing enhanced data display and search functionality...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Enhanced Display Test")
    root.geometry("1000x700")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Create test data with different column types
    test_data = pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'],
        'timestamp': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        'open': [150.0, 2800.0, 300.0, 120.0, 3300.0],
        'high': [155.0, 2850.0, 305.0, 125.0, 3350.0],
        'low': [148.0, 2750.0, 295.0, 115.0, 3250.0],
        'close': [152.0, 2820.0, 302.0, 122.0, 3320.0],
        'volume': [1000000, 500000, 800000, 2000000, 750000],
        'description': ['Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.', 'Tesla Inc.', 'Amazon.com Inc.']
    })
    
    # Save test data to a CSV file
    test_file = 'data/test_enhanced_display.csv'
    os.makedirs('data', exist_ok=True)
    test_data.to_csv(test_file, index=False)
    
    def test_smart_columns():
        """Test smart column handling"""
        print("  Testing smart column handling...")
        
        # Simulate loading the test file
        gui.current_file_path = test_file
        gui.current_page = 1
        gui.rows_per_page = 100
        
        # Test the smart column setup
        gui.setup_smart_columns(test_data)
        
        # Verify columns are set up correctly
        columns = gui.data_tree['columns']
        assert len(columns) == len(test_data.columns), "Column count mismatch"
        
        print(f"    ✓ Smart columns set up for {len(columns)} columns")
        
        # Test column configurations
        for col in columns:
            col_config = gui.data_tree.column(col)
            heading = gui.data_tree.heading(col)
            
            # Verify column has proper configuration
            assert col_config['width'] > 0, f"Column {col} has invalid width"
            assert heading['text'] == col, f"Column {col} heading mismatch"
            
        print("    ✓ All columns have proper configuration")
    
    def test_search_functionality():
        """Test search functionality"""
        print("  Testing search functionality...")
        
        # Populate treeview with test data
        gui.setup_smart_columns(test_data)
        gui.store_original_data(test_data)
        
        # Clear and populate treeview
        gui.data_tree.delete(*gui.data_tree.get_children())
        for _, row in test_data.iterrows():
            gui.data_tree.insert('', 'end', values=tuple(row))
        
        # Test search for "AAPL"
        gui.search_var.set("AAPL")
        gui.on_search_change()
        
        # Verify search results
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) == 1, f"Expected 1 result for 'AAPL', got {len(visible_items)}"
        
        # Check the result contains AAPL
        item_values = gui.data_tree.item(visible_items[0])['values']
        assert 'AAPL' in str(item_values), "Search result doesn't contain 'AAPL'"
        
        print("    ✓ Search for 'AAPL' found correct result")
        
        # Test case insensitive search
        gui.search_var.set("apple")
        gui.search_case_sensitive.set(False)
        gui.on_search_change()
        
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) == 1, f"Expected 1 result for 'apple' (case insensitive), got {len(visible_items)}"
        
        print("    ✓ Case insensitive search works")
        
        # Test clear search
        gui.clear_search()
        visible_items = gui.data_tree.get_children()
        assert len(visible_items) == len(test_data), f"Expected {len(test_data)} items after clear, got {len(visible_items)}"
        
        print("    ✓ Clear search restores all items")
    
    def run_tests():
        """Run all tests"""
        try:
            test_smart_columns()
            test_search_functionality()
            
            print("\n🎉 All enhanced display and search tests passed!")
            
            # Show success message
            messagebox.showinfo("Test Results", "All enhanced display and search tests passed!\n\n✅ Smart column handling works\n✅ Search functionality works\n✅ Case sensitivity works\n✅ Clear search works")
            
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
    test_enhanced_display() 