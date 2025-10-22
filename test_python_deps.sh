#!/bin/bash

# Test script to verify Python dependencies work

echo "🧪 TESTING PYTHON DEPENDENCIES"
echo "=============================="
echo ""

# Check Python version
echo "Python version:"
python3 --version

# Check pip version
echo ""
echo "pip version:"
pip3 --version

# Test installing compatible packages
echo ""
echo "Testing package installation..."

# Try Docker-compatible requirements first
if [ -f "requirements.docker.txt" ]; then
    echo "✅ Found requirements.docker.txt"
    echo "Testing Docker-compatible requirements..."
    pip3 install -r requirements.docker.txt --dry-run || {
        echo "❌ Docker requirements failed"
        echo "Trying individual packages..."
        pip3 install pandas numpy matplotlib seaborn plotly flask requests duckdb pyarrow fastparquet --dry-run || echo "❌ Individual packages failed"
    }
else
    echo "❌ requirements.docker.txt not found"
fi

# Try main requirements
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Testing main requirements..."
    pip3 install -r requirements.txt --dry-run || {
        echo "❌ Main requirements failed (likely version incompatibility)"
        echo "This is expected if Python version is too old"
    }
else
    echo "❌ requirements.txt not found"
fi

echo ""
echo "✅ Python dependency test completed"
