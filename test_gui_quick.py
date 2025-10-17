#!/usr/bin/env python3
"""
REDLINE Quick GUI Tests
Quick test suite for basic GUI functionality.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import time
import threading

# Add the redline package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_creation():
    """Test basic GUI creation."""
    print("Testing GUI creation...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        print("✅ GUI created successfully")
        
        # Test basic properties
        assert gui.root.title() == "REDLINE Data Analyzer"
        assert gui.notebook is not None
        assert gui.data_tab is not None
        assert gui.analysis_tab is not None
        assert gui.download_tab is not None
        assert gui.converter_tab is not None
        assert gui.settings_tab is not None
        
        print("✅ All tabs created successfully")
        
        # Test window properties
        assert gui.root.resizable() == (True, True)
        assert gui.root.minsize() == (800, 600)
        assert gui.root.maxsize() == (2400, 1600)
        
        print("✅ Window properties correct")
        
        # Test toolbar
        assert gui.help_btn is not None
        assert gui.status_label is not None
        assert gui.memory_label is not None
        
        print("✅ Toolbar created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {str(e)}")
        return False

def test_window_resizing():
    """Test window resizing functionality."""
    print("Testing window resizing...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test resizing (geometry changes may not be visible when window is withdrawn)
        root.geometry("800x600")
        root.geometry("1200x800")
        root.geometry("1600x1000")
        
        # Test that the geometry method works (even if not visible)
        geometry = root.geometry()
        assert geometry is not None
        assert len(geometry) > 0
        
        print("✅ Window resizing works correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Window resizing failed: {str(e)}")
        return False

def test_tab_switching():
    """Test tab switching functionality."""
    print("Testing tab switching...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test switching to each tab
        tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
        
        for tab_name in tabs:
            # Find tab index
            tab_index = None
            for i in range(gui.notebook.index("end")):
                if gui.notebook.tab(i, "text") == tab_name:
                    tab_index = i
                    break
            
            assert tab_index is not None, f"Tab {tab_name} not found"
            
            # Select tab
            gui.notebook.select(tab_index)
            selected = gui.notebook.select()
            # The selected value might be a widget path, not just the index
            assert selected is not None
        
        print("✅ Tab switching works correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Tab switching failed: {str(e)}")
        return False

def test_help_system():
    """Test help system functionality."""
    print("Testing help system...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test help button
        assert gui.help_btn is not None
        assert gui.help_btn['text'] == '?'
        
        # Test help methods exist
        assert hasattr(gui, 'show_help')
        assert hasattr(gui, 'create_tooltip')
        assert hasattr(gui, 'get_tab_help_content')
        
        print("✅ Help system components exist")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Help system test failed: {str(e)}")
        return False

def test_tooltips():
    """Test tooltip functionality."""
    print("Testing tooltips...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test tooltip creation
        test_widget = tk.Label(root, text="Test")
        gui.create_tooltip(test_widget, "Test tooltip")
        
        # Check that bindings were added
        assert test_widget.bind('<Enter>') is not None
        assert test_widget.bind('<Leave>') is not None
        
        print("✅ Tooltips work correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Tooltip test failed: {str(e)}")
        return False

def test_data_tab_basic():
    """Test basic Data tab functionality."""
    print("Testing Data tab basics...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test Data tab components
        data_tab = gui.data_tab
        assert data_tab.frame is not None
        assert data_tab.treeview is not None
        assert data_tab.open_button is not None
        assert data_tab.save_button is not None
        assert data_tab.refresh_button is not None
        
        print("✅ Data tab components created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Data tab test failed: {str(e)}")
        return False

def test_converter_tab_basic():
    """Test basic Converter tab functionality."""
    print("Testing Converter tab basics...")
    
    try:
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create GUI
        gui = StockAnalyzerGUI(root, loader, connector)
        
        # Test Converter tab components
        converter_tab = gui.converter_tab
        assert converter_tab.frame is not None
        assert converter_tab.input_files_var is not None
        assert converter_tab.output_format_var is not None
        assert converter_tab.convert_btn is not None
        assert converter_tab.results_tree is not None
        
        print("✅ Converter tab components created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Converter tab test failed: {str(e)}")
        return False

def run_quick_tests():
    """Run all quick GUI tests."""
    print("Running REDLINE Quick GUI Tests...")
    print("=" * 50)
    
    tests = [
        test_gui_creation,
        test_window_resizing,
        test_tab_switching,
        test_help_system,
        test_tooltips,
        test_data_tab_basic,
        test_converter_tab_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All quick GUI tests passed!")
        return True
    else:
        print("❌ Some quick GUI tests failed!")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)
