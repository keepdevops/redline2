#!/bin/bash
# Quick one-liner style copy - copies all CSV/TXT/ZIP files immediately
# Usage: ./quick_copy.sh [pattern]
# Examples:
#   ./quick_copy.sh           # Copy all CSV/TXT/ZIP files
#   ./quick_copy.sh aapl      # Copy only AAPL files
#   ./quick_copy.sh stooq     # Copy only Stooq files

CONTAINER_NAME="redline-development"
DEST_DIR="/app/data/stooq"
DOWNLOADS_DIR="$HOME/Downloads"
PATTERN="${1:-}"

# Check container
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container not running"
    exit 1
fi

# Build find command
if [ -z "$PATTERN" ]; then
    # Copy all CSV/TXT/ZIP
    find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.txt" -o -name "*.zip" \)
elif [ "$PATTERN" = "stooq" ]; then
    # Stooq files only
    find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "d_*" -o -name "m_*" -o -name "h_*" -o -name "w_*" -o -name "data_*" -o -name "*stooq*" \)
else
    # Pattern match
    find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.txt" -o -name "*.zip" \) -iname "*$PATTERN*"
fi | while read file; do
    filename=$(basename "$file")
    echo -n "📤 $filename... "
    if docker cp "$file" "$CONTAINER_NAME:$DEST_DIR/" 2>/dev/null; then
        echo "✅"
    else
        echo "❌"
    fi
done

echo "✅ Done!"

