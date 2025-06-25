#!/usr/bin/env python3
"""
Simple test script to verify the file selection preservation fix.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import StockAnalyzerGUI, DataLoader, DatabaseConnector

def test_selection_preservation():
    """Test that file selections are preserved during refresh"""
    print("Testing file selection preservation fix...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Selection Fix Test")
    root.geometry("600x400")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Test the selection preservation
    def run_test():
        print("1. Adding test files to listbox...")
        
        # Add some test files to the listbox
        test_files = [
            "data/test1.csv [csv]",
            "data/test2.txt [txt]", 
            "data/test3.parquet [parquet]"
        ]
        
        # Clear and populate with test files
        gui.file_listbox.delete(0, tk.END)
        for file in test_files:
            gui.file_listbox.insert(tk.END, file)
        
        print("2. Setting initial selection...")
        
        # Select the second file
        gui.file_listbox.selection_clear(0, tk.END)
        gui.file_listbox.selection_set(1)  # Select test2.txt
        
        # Verify initial selection
        selection = gui.file_listbox.curselection()
        if not selection:
            print("✗ Failed to set initial selection")
            return False
        
        selected_file = gui.file_listbox.get(selection[0])
        print(f"✓ Initial selection: {selected_file}")
        
        print("3. Calling refresh_file_list...")
        
        # Now call refresh_file_list (which should preserve selection)
        gui.refresh_file_list()
        
        print("4. Checking if selection is preserved...")
        
        # Check if selection is preserved
        new_selection = gui.file_listbox.curselection()
        if not new_selection:
            print("✗ Selection was lost after refresh")
            return False
        
        new_selected_file = gui.file_listbox.get(new_selection[0])
        if new_selected_file == selected_file:
            print(f"✓ Selection preserved: {new_selected_file}")
            return True
        else:
            print(f"✗ Selection changed: {new_selected_file} (expected: {selected_file})")
            return False
    
    # Run the test
    test_passed = run_test()
    
    # Close the window after a short delay
    def close_test():
        root.destroy()
    
    root.after(2000, close_test)
    root.mainloop()
    
    if test_passed:
        print("🎉 Selection preservation fix is working correctly!")
        return True
    else:
        print("❌ Selection preservation fix failed!")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("File Selection Preservation Fix Test")
    print("=" * 50)
    
    success = test_selection_preservation()
    
    print("\n" + "=" * 50)
    print("Test Result:")
    print(f"{'✓ PASSED' if success else '✗ FAILED'}")
    print("=" * 50)
    
    if success:
        print("\nThe high priority fix is working! File selections will now be preserved")
        print("when the file list is refreshed (e.g., after saving new files).")
        sys.exit(0)
    else:
        print("\nThe fix needs adjustment. Please check the implementation.")
        sys.exit(1) 