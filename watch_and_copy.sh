#!/bin/bash
# File watcher that automatically copies files from Downloads to container
# Runs continuously and copies files as they're added

CONTAINER_NAME="redline-development"
DEST_DIR="/app/data/stooq"
DOWNLOADS_DIR="$HOME/Downloads"

echo "======================================================================"
echo "FILE WATCHER - AUTO-COPY TO CONTAINER"
echo "======================================================================"
echo ""
echo "📁 Watching: $DOWNLOADS_DIR"
echo "📦 Copying to: $CONTAINER_NAME:$DEST_DIR"
echo "🔍 Monitoring for: *.csv, *.txt, *.zip"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Start it with: docker-compose -f docker-compose-dev.yml up -d"
    exit 1
fi

# Track copied files to avoid duplicates
COPIED_LOG="/tmp/copied_files.log"
touch "$COPIED_LOG"

# Function to copy file
copy_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Check if already copied (avoid duplicates)
    if grep -q "^$filename$" "$COPIED_LOG" 2>/dev/null; then
        return 0
    fi
    
    # Check if file is still being written (wait if size changes)
    local size1=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    sleep 2
    local size2=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    
    if [ "$size1" != "$size2" ]; then
        echo "⏳ File still downloading: $filename (waiting...)"
        sleep 3
        size2=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    fi
    
    # Copy file
    echo -n "📤 Copying $filename... "
    if docker cp "$file" "$CONTAINER_NAME:$DEST_DIR/" 2>/dev/null; then
        echo "$filename" >> "$COPIED_LOG"
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

# Watch for new files
if command -v fswatch >/dev/null 2>&1; then
    # Use fswatch if available (install with: brew install fswatch)
    echo "✅ Using fswatch (real-time monitoring)"
    fswatch -o "$DOWNLOADS_DIR" | while read f; do
        # Check for new CSV/TXT/ZIP files
        find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.txt" -o -name "*.zip" \) -newer "$COPIED_LOG" 2>/dev/null | while read file; do
            copy_file "$file"
        done
    done
elif command -v inotifywait >/dev/null 2>&1; then
    # Use inotifywait (Linux)
    echo "✅ Using inotifywait (real-time monitoring)"
    inotifywait -m -e close_write --format '%w%f' "$DOWNLOADS_DIR" | while read file; do
        if [[ "$file" =~ \.(csv|txt|zip)$ ]]; then
            copy_file "$file"
        fi
    done
else
    # Fallback: Polling mode (checks every 5 seconds)
    echo "⚠️  Using polling mode (checking every 5 seconds)"
    echo "   Install fswatch for real-time: brew install fswatch"
    echo ""
    
    while true; do
        # Find new files
        find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.txt" -o -name "*.zip" \) | while read file; do
            copy_file "$file"
        done
        sleep 5
    fi
fi

