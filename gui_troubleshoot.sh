#!/bin/bash
echo "============================================================"
echo "GUI TROUBLESHOOTING SCRIPT"
echo "============================================================"

echo ""
echo "1. Checking Python version..."
python3 --version

echo ""
echo "2. Checking tkinter..."
python3 -c "import tkinter; print('✅ tkinter available')" 2>&1

echo ""
echo "3. Checking for running GUI processes..."
ps aux | grep -i "python.*main.py\|python.*gui" | grep -v grep || echo "   No GUI processes running"

echo ""
echo "4. Testing basic tkinter window..."
python3 << 'PYTHON'
import tkinter as tk
import sys

try:
    root = tk.Tk()
    root.title("Test")
    root.geometry("200x100")
    label = tk.Label(root, text="Test Window")
    label.pack()
    print("   ✅ Basic tkinter window created")
    root.after(100, root.destroy)
    root.mainloop()
    print("   ✅ tkinter test passed")
except Exception as e:
    print(f"   ❌ tkinter test failed: {e}")
    sys.exit(1)
PYTHON

echo ""
echo "5. Testing GUI imports..."
python3 << 'PYTHON'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    from redline.gui.main_window import StockAnalyzerGUI
    print("   ✅ StockAnalyzerGUI imported")
    from redline.core.data_loader import DataLoader
    print("   ✅ DataLoader imported")
    from redline.database.connector import DatabaseConnector
    print("   ✅ DatabaseConnector imported")
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON

echo ""
echo "============================================================"
echo "If all tests passed, try running: python3 main.py"
echo "If GUI still doesn't work, use web interface: python3 web_app.py"
echo "============================================================"
