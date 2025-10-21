#!/bin/bash

# REDLINE File Diagnostic Script
# Run this on your HP machine to check what files are available

echo "=== REDLINE File Diagnostic ==="
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check if we're in the right place
if [ -f "web_app.py" ]; then
    echo "✅ Found web_app.py - we're in the right directory"
else
    echo "❌ web_app.py not found - wrong directory"
    echo "Please navigate to the REDLINE project directory"
    exit 1
fi
echo ""

# Check dockerfiles directory
echo "Checking dockerfiles/ directory:"
if [ -d "dockerfiles" ]; then
    echo "✅ dockerfiles/ directory exists"
    echo "Contents:"
    ls -la dockerfiles/
    echo ""
else
    echo "❌ dockerfiles/ directory not found"
    echo ""
fi

# Check requirements files
echo "Checking requirements files:"
if [ -f "requirements-simple.txt" ]; then
    echo "✅ requirements-simple.txt exists"
    echo "Size: $(wc -c < requirements-simple.txt) bytes"
else
    echo "❌ requirements-simple.txt not found"
fi

if [ -f "requirements-ultra-minimal.txt" ]; then
    echo "✅ requirements-ultra-minimal.txt exists"
    echo "Size: $(wc -c < requirements-ultra-minimal.txt) bytes"
else
    echo "❌ requirements-ultra-minimal.txt not found"
fi
echo ""

# Check Git status
echo "Git status:"
git status
echo ""

# Check if files are tracked
echo "Files tracked by Git:"
git ls-files | grep -E "(Dockerfile|requirements)" | head -10
echo ""

# Show recent commits
echo "Recent commits:"
git log --oneline -3
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "If files are missing, try:"
echo "  git pull origin main"
echo "  git reset --hard origin/main"
echo ""
echo "If still missing, try fresh clone:"
echo "  cd .."
echo "  git clone https://github.com/keepdevops/redline2.git redline-fresh"
echo "  cd redline-fresh"
