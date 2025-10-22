#!/bin/bash

# Git Merge Conflict Resolution Script

echo "🔧 RESOLVING GIT MERGE CONFLICT"
echo "==============================="
echo ""

# Check current status
echo "📋 Current git status:"
git status --porcelain | grep start_compose.sh || echo "No start_compose.sh in status"

echo ""

# Option 1: Backup and remove local file
echo "🔄 OPTION 1: Backup local file and pull"
echo "This will backup your local start_compose.sh and use the repository version"
echo ""
read -p "Do you want to backup and remove the local file? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Backing up local start_compose.sh..."
    cp start_compose.sh start_compose.sh.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
    
    echo "🗑️ Removing local file..."
    rm start_compose.sh
    echo "✅ Local file removed"
    
    echo "⬇️ Pulling from repository..."
    git pull origin main
    echo "✅ Pull completed"
    
    echo ""
    echo "📋 Files after pull:"
    ls -la start_compose.sh*
    
    echo ""
    echo "💡 If you need your local changes, check the backup file"
fi

echo ""

# Option 2: Add and commit local file first
echo "🔄 OPTION 2: Add local file to git first"
echo "This will add your local start_compose.sh to git before pulling"
echo ""
read -p "Do you want to add the local file to git? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Adding local file to git..."
    git add start_compose.sh
    echo "✅ File added to git"
    
    echo "💾 Committing local changes..."
    git commit -m "Add local start_compose.sh before merge"
    echo "✅ Local changes committed"
    
    echo "⬇️ Pulling from repository..."
    git pull origin main
    echo "✅ Pull completed"
    
    echo ""
    echo "⚠️ You may need to resolve merge conflicts if there are differences"
fi

echo ""

# Option 3: Force pull (overwrite local)
echo "🔄 OPTION 3: Force pull (overwrite local)"
echo "This will overwrite your local file with the repository version"
echo ""
read -p "Do you want to force pull and overwrite local file? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing local file..."
    rm start_compose.sh
    echo "✅ Local file removed"
    
    echo "⬇️ Pulling from repository..."
    git pull origin main
    echo "✅ Pull completed"
fi

echo ""
echo "🎉 Git merge conflict resolution completed!"
echo "Run: git status to check the current state"
