#!/usr/bin/env python3
"""
REDLINE GUI Smoke Test
Quick smoke test to verify GUI basic functionality.
"""

import sys
import os
import tkinter as tk
import time

# Add the redline package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def smoke_test():
    """Run a quick smoke test of the GUI."""
    print("Running REDLINE GUI Smoke Test...")
    print("=" * 40)
    
    try:
        # Test 1: Import modules
        print("1. Testing imports...")
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        print("   ✅ All imports successful")
        
        # Test 2: Create GUI
        print("2. Testing GUI creation...")
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        loader = DataLoader()
        connector = DatabaseConnector()
        gui = StockAnalyzerGUI(root, loader, connector)
        print("   ✅ GUI created successfully")
        
        # Test 3: Check basic components
        print("3. Testing basic components...")
        assert gui.root.title() == "REDLINE Data Analyzer"
        assert gui.notebook is not None
        assert gui.help_btn is not None
        assert gui.data_tab is not None
        assert gui.analysis_tab is not None
        assert gui.download_tab is not None
        assert gui.converter_tab is not None
        assert gui.settings_tab is not None
        print("   ✅ All basic components present")
        
        # Test 4: Test window properties
        print("4. Testing window properties...")
        assert gui.root.resizable() == (True, True)
        assert gui.root.minsize() == (800, 600)
        assert gui.root.maxsize() == (2400, 1600)
        print("   ✅ Window properties correct")
        
        # Test 5: Test tab switching
        print("5. Testing tab switching...")
        tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
        for tab_name in tabs:
            tab_index = None
            for i in range(gui.notebook.index("end")):
                if gui.notebook.tab(i, "text") == tab_name:
                    tab_index = i
                    break
            assert tab_index is not None, f"Tab {tab_name} not found"
            gui.notebook.select(tab_index)
        print("   ✅ Tab switching works")
        
        # Test 6: Test help system
        print("6. Testing help system...")
        assert hasattr(gui, 'show_help')
        assert hasattr(gui, 'create_tooltip')
        print("   ✅ Help system components exist")
        
        # Test 7: Test window resizing
        print("7. Testing window resizing...")
        gui.root.geometry("800x600")
        gui.root.geometry("1200x800")
        gui.root.geometry("1600x1000")
        print("   ✅ Window resizing works")
        
        # Test 8: Test tooltip creation
        print("8. Testing tooltip creation...")
        test_widget = tk.Label(root, text="Test")
        gui.create_tooltip(test_widget, "Test tooltip")
        print("   ✅ Tooltip creation works")
        
        # Clean up
        root.destroy()
        
        print("\n✅ All smoke tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    success = smoke_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
