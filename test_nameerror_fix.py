#!/usr/bin/env python3
"""
Test script to verify the NameError fix for the threading issue.
This test simulates the conditions that caused the NameError.
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

def test_nameerror_fix():
    """Test that the NameError in threading is fixed"""
    print("Testing NameError fix...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("NameError Fix Test")
    root.geometry("400x300")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Test the remove_selected_file method (which had the NameError)
    def test_remove_file():
        print("Testing remove_selected_file method...")
        try:
            # This should not raise a NameError anymore
            gui.remove_selected_file()
            print("✓ remove_selected_file method works without NameError")
        except NameError as e:
            print(f"✗ NameError still exists: {e}")
            return False
        except Exception as e:
            print(f"✗ Other error occurred: {e}")
            return False
        return True
    
    # Test the load_and_convert method (which also had the NameError)
    def test_load_convert():
        print("Testing load_and_convert method...")
        try:
            # This should not raise a NameError anymore
            gui.load_and_convert()
            print("✓ load_and_convert method works without NameError")
        except NameError as e:
            print(f"✗ NameError still exists: {e}")
            return False
        except Exception as e:
            print(f"✗ Other error occurred: {e}")
            return False
        return True
    
    # Run the tests
    test1_passed = test_remove_file()
    test2_passed = test_load_convert()
    
    # Close the window after a short delay
    def close_test():
        root.destroy()
    
    root.after(2000, close_test)
    root.mainloop()
    
    if test1_passed and test2_passed:
        print("✓ All NameError tests passed!")
        return True
    else:
        print("✗ Some NameError tests failed!")
        return False

def test_threading_safety():
    """Test that threading operations are safe"""
    print("\nTesting threading safety...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Threading Safety Test")
    root.geometry("400x300")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Test that run_in_main_thread works correctly
    def test_run_in_main_thread():
        print("Testing run_in_main_thread method...")
        try:
            # Test basic functionality
            gui.run_in_main_thread(lambda: print("✓ run_in_main_thread works"))
            
            # Test with arguments
            gui.run_in_main_thread(lambda x, y: print(f"✓ run_in_main_thread with args: {x}, {y}"), "test", 123)
            
            print("✓ run_in_main_thread method works correctly")
            return True
        except Exception as e:
            print(f"✗ run_in_main_thread error: {e}")
            return False
    
    # Test that safe update methods work
    def test_safe_updates():
        print("Testing safe update methods...")
        try:
            # Test safe_update_widget
            gui.safe_update_widget("test_widget", lambda: print("✓ safe_update_widget works"))
            
            # Test safe_update_treeview
            gui.safe_update_treeview(lambda: print("✓ safe_update_treeview works"))
            
            # Test safe_update_listbox
            gui.safe_update_listbox("test_listbox", lambda: print("✓ safe_update_listbox works"))
            
            print("✓ Safe update methods work correctly")
            return True
        except Exception as e:
            print(f"✗ Safe update error: {e}")
            return False
    
    # Run the tests
    test1_passed = test_run_in_main_thread()
    test2_passed = test_safe_updates()
    
    # Close the window after a short delay
    def close_test():
        root.destroy()
    
    root.after(2000, close_test)
    root.mainloop()
    
    if test1_passed and test2_passed:
        print("✓ All threading safety tests passed!")
        return True
    else:
        print("✗ Some threading safety tests failed!")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("NameError Fix Test Suite")
    print("=" * 50)
    
    # Run the tests
    nameerror_fixed = test_nameerror_fix()
    threading_safe = test_threading_safety()
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"NameError Fix: {'✓ PASSED' if nameerror_fixed else '✗ FAILED'}")
    print(f"Threading Safety: {'✓ PASSED' if threading_safe else '✗ FAILED'}")
    
    if nameerror_fixed and threading_safe:
        print("\n🎉 All tests passed! The NameError fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 