#!/bin/bash
# Script to remove large .tar files from Git history
# WARNING: This rewrites Git history. Use with caution!

set -e

echo "🔍 Checking for large files in Git history..."

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo is not installed"
    echo ""
    echo "Install it with:"
    echo "  pip install git-filter-repo"
    echo ""
    echo "Or use BFG Repo-Cleaner alternative"
    exit 1
fi

echo "✅ git-filter-repo found"
echo ""
echo "⚠️  WARNING: This will rewrite Git history!"
echo "⚠️  Make sure you have a backup of your repository"
echo "⚠️  Coordinate with team if working collaboratively"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🗑️  Removing large files from Git history..."

# Remove specific large tar files
git filter-repo --path redline-webgui.tar --invert-paths --force
git filter-repo --path redline-webgui-amd64.tar --invert-paths --force

# Remove all .tar.gz files matching pattern
git filter-repo --path-glob 'redline-*-v*.tar.gz' --invert-paths --force
git filter-repo --path-glob 'redline-compiled-*.tar.gz' --invert-paths --force
git filter-repo --path-glob 'redline-gui-executable-*.tar.gz' --invert-paths --force
git filter-repo --path-glob 'redline-portable-*.tar.gz' --invert-paths --force
git filter-repo --path-glob 'redline-source-*.tar.gz' --invert-paths --force

echo ""
echo "✅ Large files removed from history"
echo ""
echo "📋 Next steps:"
echo "1. Verify the changes: git log --stat"
echo "2. Force push: git push --force origin main"
echo "   (⚠️  Only if you're sure about rewriting history)"

