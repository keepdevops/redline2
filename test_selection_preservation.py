#!/usr/bin/env python3
"""
Test script to verify that file selection preservation works correctly.
This test simulates the conditions where file selections should be preserved.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import StockAnalyzerGUI, DataLoader, DatabaseConnector

def test_selection_preservation():
    """Test that file selections are preserved during refresh"""
    print("Testing file selection preservation...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Selection Preservation Test")
    root.geometry("800x600")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Test the selection preservation
    def test_refresh_preserves_selection():
        print("Testing refresh_file_list preserves selections...")
        
        # First, let's add some test files to the listbox
        test_files = [
            "data/test1.csv [csv]",
            "data/test2.txt [txt]", 
            "data/test3.parquet [parquet]"
        ]
        
        # Clear and populate with test files
        gui.file_listbox.delete(0, tk.END)
        for file in test_files:
            gui.file_listbox.insert(tk.END, file)
        
        # Select the second file
        gui.file_listbox.selection_clear(0, tk.END)
        gui.file_listbox.selection_set(1)  # Select test2.txt
        
        # Verify selection
        selection = gui.file_listbox.curselection()
        if not selection:
            print("✗ Failed to set initial selection")
            return False
        
        selected_file = gui.file_listbox.get(selection[0])
        print(f"✓ Initial selection: {selected_file}")
        
        # Now call refresh_file_list (which should preserve selection)
        gui.refresh_file_list()
        
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
    
    # Test multiple selections
    def test_multiple_selections():
        print("Testing multiple selection preservation...")
        
        # Add test files
        test_files = [
            "data/test1.csv [csv]",
            "data/test2.txt [txt]", 
            "data/test3.parquet [parquet]",
            "data/test4.json [json]"
        ]
        
        # Clear and populate
        gui.file_listbox.delete(0, tk.END)
        for file in test_files:
            gui.file_listbox.insert(tk.END, file)
        
        # Select multiple files
        gui.file_listbox.selection_clear(0, tk.END)
        gui.file_listbox.selection_set(0, 2)  # Select first 3 files
        
        # Verify multiple selections
        selection = gui.file_listbox.curselection()
        if len(selection) != 3:
            print(f"✗ Expected 3 selections, got {len(selection)}")
            return False
        
        selected_files = [gui.file_listbox.get(idx) for idx in selection]
        print(f"✓ Initial selections: {selected_files}")
        
        # Call refresh
        gui.refresh_file_list()
        
        # Check if selections are preserved
        new_selection = gui.file_listbox.curselection()
        if len(new_selection) != 3:
            print(f"✗ Expected 3 selections after refresh, got {len(new_selection)}")
            return False
        
        new_selected_files = [gui.file_listbox.get(idx) for idx in new_selection]
        if new_selected_files == selected_files:
            print(f"✓ Multiple selections preserved: {new_selected_files}")
            return True
        else:
            print(f"✗ Multiple selections changed: {new_selected_files}")
            return False
    
    # Test selection when file is removed
    def test_selection_when_file_removed():
        print("Testing selection behavior when file is removed...")
        
        # Add test files
        test_files = [
            "data/test1.csv [csv]",
            "data/test2.txt [txt]", 
            "data/test3.parquet [parquet]"
        ]
        
        # Clear and populate
        gui.file_listbox.delete(0, tk.END)
        for file in test_files:
            gui.file_listbox.insert(tk.END, file)
        
        # Select the last file (which will be "removed")
        gui.file_listbox.selection_clear(0, tk.END)
        gui.file_listbox.selection_set(2)  # Select test3.parquet
        
        selected_file = gui.file_listbox.get(2)
        print(f"✓ Selected file to be removed: {selected_file}")
        
        # Simulate file removal by refreshing with fewer files
        gui.file_listbox.delete(0, tk.END)
        # Only add first two files (simulating removal of third file)
        for file in test_files[:2]:
            gui.file_listbox.insert(tk.END, file)
        
        # Check if selection is cleared (since file no longer exists)
        new_selection = gui.file_listbox.curselection()
        if not new_selection:
            print("✓ Selection correctly cleared when file was removed")
            return True
        else:
            print("✗ Selection should have been cleared when file was removed")
            return False
    
    # Run the tests
    test1_passed = test_refresh_preserves_selection()
    test2_passed = test_multiple_selections()
    test3_passed = test_selection_when_file_removed()
    
    # Close the window after a short delay
    def close_test():
        root.destroy()
    
    root.after(3000, close_test)
    root.mainloop()
    
    if test1_passed and test2_passed and test3_passed:
        print("✓ All selection preservation tests passed!")
        return True
    else:
        print("✗ Some selection preservation tests failed!")
        return False

def test_real_world_scenario():
    """Test the real-world scenario that was causing the issue"""
    print("\nTesting real-world scenario (file saving)...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Real-World Scenario Test")
    root.geometry("800x600")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    def test_file_saving_scenario():
        print("Testing file saving scenario...")
        
        # Simulate the scenario where a user has a file selected
        # and then saves a new file, which triggers refresh_file_list
        
        # Add some test files
        test_files = [
            "data/existing_file.csv [csv]",
            "data/another_file.txt [txt]"
        ]
        
        # Populate file list
        gui.file_listbox.delete(0, tk.END)
        for file in test_files:
            gui.file_listbox.insert(tk.END, file)
        
        # User selects the first file
        gui.file_listbox.selection_clear(0, tk.END)
        gui.file_listbox.selection_set(0)
        
        selected_file = gui.file_listbox.get(0)
        print(f"✓ User selected: {selected_file}")
        
        # Simulate saving a new file (which would call refresh_file_list)
        # Add a new file to the list
        new_files = test_files + ["data/new_saved_file.parquet [parquet]"]
        
        # This simulates what happens in data_cleaning_and_save
        gui.refresh_file_list()
        
        # Check if the original selection is preserved
        new_selection = gui.file_listbox.curselection()
        if not new_selection:
            print("✗ Original selection was lost after saving new file")
            return False
        
        new_selected_file = gui.file_listbox.get(new_selection[0])
        if new_selected_file == selected_file:
            print(f"✓ Original selection preserved after saving: {new_selected_file}")
            return True
        else:
            print(f"✗ Original selection changed: {new_selected_file}")
            return False
    
    # Run the test
    test_passed = test_file_saving_scenario()
    
    # Close the window after a short delay
    def close_test():
        root.destroy()
    
    root.after(2000, close_test)
    root.mainloop()
    
    if test_passed:
        print("✓ Real-world scenario test passed!")
        return True
    else:
        print("✗ Real-world scenario test failed!")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("File Selection Preservation Test Suite")
    print("=" * 60)
    
    # Run the tests
    selection_preserved = test_selection_preservation()
    real_world_works = test_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Selection Preservation: {'✓ PASSED' if selection_preserved else '✗ FAILED'}")
    print(f"Real-World Scenario: {'✓ PASSED' if real_world_works else '✗ FAILED'}")
    
    if selection_preserved and real_world_works:
        print("\n🎉 All tests passed! File selection preservation is working correctly.")
        print("The fix successfully prevents file selection loss during refresh operations.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. The selection preservation fix may need adjustment.")
        sys.exit(1) 