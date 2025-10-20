#!/bin/bash
set -e

# Test script to check Tkinter package availability on Ubuntu 24.04

echo "🧪 Testing Tkinter Package Availability on Ubuntu 24.04"
echo "====================================================="

# Check Ubuntu version
echo "📋 System Information:"
echo "• Ubuntu Version: $(lsb_release -d | cut -f2)"
echo "• Architecture: $(uname -m)"
echo "• Python Version: $(python3 --version)"
echo ""

echo "🔍 Testing Tkinter Package Names:"
echo "================================="

# Test different package names
packages_to_test=(
    "python3-tk"
    "python3-tkinter"
    "tkinter"
    "python-tk"
    "python-tkinter"
)

for package in "${packages_to_test[@]}"; do
    echo -n "Testing package: $package ... "
    if apt-cache show "$package" &>/dev/null; then
        echo "✅ Available"
        echo "  Description: $(apt-cache show "$package" | grep "Description:" | head -1 | cut -d: -f2- | xargs)"
        echo "  Version: $(apt-cache show "$package" | grep "Version:" | head -1 | cut -d: -f2- | xargs)"
    else
        echo "❌ Not available"
    fi
    echo ""
done

echo "🧪 Testing Tkinter Import:"
echo "========================="

# Test if Tkinter can be imported
echo -n "Testing Tkinter import ... "
if python3 -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)" 2>/dev/null; then
    echo "✅ Tkinter works"
else
    echo "❌ Tkinter import failed"
    echo ""
    echo "💡 Try installing one of these packages:"
    echo "   sudo apt-get install python3-tk"
    echo "   sudo apt-get install python3-tkinter"
    echo ""
    echo "   Or install via pip:"
    echo "   pip install tk"
fi

echo ""
echo "🎯 Recommended Installation Command:"
echo "==================================="
echo "sudo apt-get install python3-tk python3-tkinter"
