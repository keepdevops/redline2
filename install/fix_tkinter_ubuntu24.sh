#!/bin/bash
set -e

# Fix Tkinter installation for Ubuntu 24.04 LTS
# This script addresses the "package tkinter not found" issue

echo "🔧 Fixing Tkinter Installation for Ubuntu 24.04 LTS"
echo "==================================================="

# Check if running on Ubuntu 24.04
if ! command -v lsb_release &> /dev/null; then
    echo "❌ lsb_release not found. Please install lsb-release first."
    exit 1
fi

ubuntu_version=$(lsb_release -sr)
echo "📋 Detected Ubuntu version: $ubuntu_version"

if [[ "$ubuntu_version" != "24.04" ]]; then
    echo "⚠️  This script is specifically for Ubuntu 24.04 LTS"
    echo "   Current version: $ubuntu_version"
    echo "   Proceeding anyway..."
fi

echo ""
echo "🔍 Current Tkinter Status:"
echo "=========================="

# Check current Tkinter status
if python3 -c "import tkinter; print('✅ Tkinter is working (version:', tkinter.TkVersion, ')')" 2>/dev/null; then
    echo "✅ Tkinter is already working correctly!"
    exit 0
else
    echo "❌ Tkinter is not working"
fi

echo ""
echo "🛠️  Installing Tkinter for Ubuntu 24.04:"
echo "========================================"

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Try different package combinations
echo "🔧 Attempting to install Tkinter packages..."

# Method 1: Standard packages
echo "Method 1: Installing python3-tk..."
if sudo apt-get install -y python3-tk; then
    echo "✅ python3-tk installed successfully"
else
    echo "❌ Failed to install python3-tk"
fi

# Method 2: Alternative package name
echo "Method 2: Installing python3-tkinter..."
if sudo apt-get install -y python3-tkinter; then
    echo "✅ python3-tkinter installed successfully"
else
    echo "❌ Failed to install python3-tkinter"
fi

# Method 3: Install via pip as fallback
echo "Method 3: Installing tk via pip..."
if pip3 install tk; then
    echo "✅ tk installed via pip"
else
    echo "❌ Failed to install tk via pip"
fi

echo ""
echo "🧪 Testing Tkinter Installation:"
echo "================================"

# Test Tkinter again
if python3 -c "import tkinter; print('✅ SUCCESS: Tkinter is now working (version:', tkinter.TkVersion, ')')" 2>/dev/null; then
    echo ""
    echo "🎉 Tkinter installation fixed successfully!"
    echo ""
    echo "📋 Installation Summary:"
    echo "• Tkinter version: $(python3 -c 'import tkinter; print(tkinter.TkVersion)')"
    echo "• Python version: $(python3 --version)"
    echo ""
    echo "✅ You can now run REDLINE with GUI support!"
else
    echo ""
    echo "❌ Tkinter installation still not working"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "1. Check if you're on a headless server (no display)"
    echo "2. Try installing additional X11 packages:"
    echo "   sudo apt-get install xvfb"
    echo "3. For headless servers, use the web interface instead"
    echo "4. Check system logs: journalctl -f"
fi

echo ""
echo "📚 Additional Information:"
echo "========================="
echo "• Ubuntu 24.04 LTS uses different package names for Tkinter"
echo "• The main packages are: python3-tk and python3-tkinter"
echo "• For headless servers, Tkinter GUI won't work (use web interface)"
echo "• Web interface works without Tkinter: http://localhost:8080"
