#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE GUI..."

# Check if GUI is supported
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Tkinter not available, cannot start GUI"
    echo "💡 Use start_web.sh for web interface instead"
    exit 1
fi

# Start the GUI
source venv/bin/activate
python3 main.py
