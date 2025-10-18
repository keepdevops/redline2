#!/bin/bash

# REDLINE Ubuntu Setup Test Script
# Tests if REDLINE can run on Ubuntu x86 systems

set -e

echo "🧪 REDLINE Ubuntu Setup Test"
echo "============================"

# Test functions
test_python() {
    echo "🐍 Testing Python..."
    if python3 --version | grep -q "Python 3"; then
        echo "✅ Python found: $(python3 --version)"
    else
        echo "❌ Python not found or version too old"
        return 1
    fi
}

test_tkinter() {
    echo "🖼️ Testing tkinter..."
    if python3 -c "import tkinter; print('tkinter available')" 2>/dev/null; then
        echo "✅ tkinter available"
    else
        echo "❌ tkinter not available"
        return 1
    fi
}

test_dependencies() {
    echo "📦 Testing dependencies..."
    python3 -c "
import sys
packages = ['pandas', 'numpy', 'matplotlib', 'pyarrow', 'duckdb', 'polars']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
        missing.append(pkg)

if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
else:
    print('All dependencies available')
"
}

test_display() {
    echo "🖥️ Testing display..."
    if [ -n "$DISPLAY" ]; then
        echo "✅ DISPLAY set to: $DISPLAY"
    else
        echo "⚠️ DISPLAY not set"
        export DISPLAY=:0
        echo "Set DISPLAY to: $DISPLAY"
    fi
    
    if command -v xdpyinfo >/dev/null 2>&1; then
        if xdpyinfo >/dev/null 2>&1; then
            echo "✅ X11 display working"
        else
            echo "❌ X11 display not working"
            return 1
        fi
    else
        echo "⚠️ xdpyinfo not found, skipping X11 test"
    fi
}

test_redline_import() {
    echo "🚀 Testing REDLINE import..."
    if python3 -c "
import sys
sys.path.insert(0, '.')
from redline.core.data_loader import DataLoader
from redline.database.connector import DatabaseConnector
print('✅ REDLINE modules import successfully')
" 2>/dev/null; then
        echo "✅ REDLINE imports work"
    else
        echo "❌ REDLINE import failed"
        return 1
    fi
}

test_gui_creation() {
    echo "🖼️ Testing GUI creation..."
    if python3 -c "
import sys
import tkinter as tk
sys.path.insert(0, '.')
from redline.core.data_loader import DataLoader
from redline.database.connector import DatabaseConnector
from redline.gui.main_window import StockAnalyzerGUI

root = tk.Tk()
root.withdraw()
loader = DataLoader()
connector = DatabaseConnector()
gui = StockAnalyzerGUI(root, loader, connector)
root.destroy()
print('✅ GUI created successfully')
" 2>/dev/null; then
        echo "✅ GUI creation works"
    else
        echo "❌ GUI creation failed"
        return 1
    fi
}

# Run all tests
echo "Starting tests..."
echo ""

tests=(
    "test_python"
    "test_tkinter" 
    "test_dependencies"
    "test_display"
    "test_redline_import"
    "test_gui_creation"
)

passed=0
total=${#tests[@]}

for test in "${tests[@]}"; do
    echo "Running $test..."
    if $test; then
        passed=$((passed + 1))
        echo "✅ $test PASSED"
    else
        echo "❌ $test FAILED"
    fi
    echo ""
done

echo "============================"
echo "Test Results: $passed/$total passed"

if [ $passed -eq $total ]; then
    echo "🎉 All tests passed! REDLINE is ready to run."
    echo ""
    echo "To run REDLINE:"
    echo "  ./run_ubuntu_x86.sh"
    exit 0
else
    echo "❌ Some tests failed. Please check the setup."
    echo ""
    echo "To fix issues:"
    echo "  ./setup_ubuntu_x86.sh"
    exit 1
fi
