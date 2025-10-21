#!/bin/bash

# REDLINE Docker Files Verification Script
# Run this on your HP machine to check if files are present

echo "=== REDLINE Docker Files Verification ==="
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check if dockerfiles directory exists
if [ -d "dockerfiles" ]; then
    echo "✅ dockerfiles/ directory exists"
    echo "Contents:"
    ls -la dockerfiles/
    echo ""
else
    echo "❌ dockerfiles/ directory NOT found"
    echo ""
fi

# Check Git status
echo "Git status:"
git status
echo ""

# Check Git branch
echo "Current branch:"
git branch
echo ""

# Check if files are tracked by Git
echo "Files tracked by Git in dockerfiles/:"
git ls-files dockerfiles/
echo ""

# Check remote repository
echo "Remote repository status:"
git remote -v
echo ""

# Check if we're up to date with remote
echo "Checking if local is up to date with remote:"
git fetch origin
git status -uno
echo ""

# Show recent commits
echo "Recent commits:"
git log --oneline -5
echo ""

echo "=== Verification Complete ==="
echo ""
echo "If Dockerfile.simple is missing, try:"
echo "  git pull origin main"
echo "  git reset --hard origin/main"
echo ""
echo "If still missing, try fresh clone:"
echo "  cd .."
echo "  git clone https://github.com/keepdevops/redline2.git redline-fresh"
echo "  cd redline-fresh"
echo "  ls -la dockerfiles/"
