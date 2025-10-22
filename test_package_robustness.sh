#!/bin/bash

# Test script to verify package installation continues on failure

echo "🧪 TESTING PACKAGE INSTALLATION ROBUSTNESS"
echo "=========================================="
echo ""

# Test 1: Try installing non-existent package (should continue)
echo "Test 1: Installing non-existent package (should continue)"
sudo apt-get install -y python3-tkinter-nonexistent || echo "✅ Package not found, continuing..."

# Test 2: Try multiple package names
echo ""
echo "Test 2: Trying multiple Tkinter package names"
sudo apt-get install -y python3-tk || \
sudo apt-get install -y python-tk || \
sudo apt-get install -y tkinter || \
echo "✅ No Tkinter packages found, will try pip"

# Test 3: Try pip fallback
echo ""
echo "Test 3: Trying pip fallback"
pip3 install tk || echo "✅ Tkinter not available via pip"

echo ""
echo "✅ All tests completed - installation continues on package failures"
