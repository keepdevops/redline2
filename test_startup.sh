#!/bin/bash

# Test script to verify startup scripts work correctly

echo "🧪 Testing REDLINE Flask Web Application Startup Scripts"
echo "=================================================="

# Test 1: Check if scripts exist and are executable
echo "📋 Test 1: Checking script files..."
scripts=("quick_start_web.sh" "start_web_app.sh" "install_and_start_web.sh" "start_web_app.bat")

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "✅ $script exists and is executable"
        else
            echo "⚠️  $script exists but is not executable"
            chmod +x "$script"
            echo "✅ Made $script executable"
        fi
    else
        echo "❌ $script not found"
    fi
done

echo ""

# Test 2: Check help functionality
echo "📋 Test 2: Testing help functionality..."
echo "Testing quick_start_web.sh --help:"
./quick_start_web.sh --help
echo ""

# Test 3: Check if web_app.py exists
echo "📋 Test 3: Checking web_app.py..."
if [ -f "web_app.py" ]; then
    echo "✅ web_app.py exists"
else
    echo "❌ web_app.py not found"
fi

# Test 4: Check Python dependencies
echo "📋 Test 4: Checking Python dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "✅ Flask is installed"
else
    echo "⚠️  Flask is not installed"
fi

if python3 -c "import pandas" 2>/dev/null; then
    echo "✅ Pandas is installed"
else
    echo "⚠️  Pandas is not installed"
fi

# Test 5: Check if directories exist
echo "📋 Test 5: Checking directories..."
directories=("data" "redline/web/static" "redline/web/templates")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "⚠️  $dir does not exist"
    fi
done

echo ""
echo "🎉 Startup script testing completed!"
echo ""
echo "To start the Flask web application, use one of these commands:"
echo "  ./quick_start_web.sh           # Quick start on port 8082"
echo "  ./quick_start_web.sh 8080      # Quick start on port 8080"
echo "  ./start_web_app.sh             # Full-featured startup"
echo "  ./install_and_start_web.sh     # Complete installation and startup"
