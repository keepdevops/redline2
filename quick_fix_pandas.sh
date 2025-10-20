#!/bin/bash
# Quick fix for pandas import issue
# Run this from the REDLINE directory

echo "🔧 Quick Pandas Fix"
echo "=================="

# Check if we're in the right directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Please run this from the REDLINE directory"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Please run the installer first."
    exit 1
fi

# Activate virtual environment and install pandas
echo "📦 Installing pandas and dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install pandas numpy matplotlib seaborn scipy scikit-learn flask requests

# Test pandas import
echo "🧪 Testing pandas import..."
python3 -c "import pandas as pd; print('✅ Pandas version:', pd.__version__)"

echo "🎉 Pandas fix completed!"
echo ""
echo "Now try running:"
echo "  python3 main.py --task=gui"
