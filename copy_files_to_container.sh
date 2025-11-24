#!/bin/bash
# Script to copy files from Mac Downloads folder to Docker container
# This bypasses M3 Apple Silicon security restrictions on file uploads
# Enhanced version with batch selection and filtering

CONTAINER_NAME="redline-development"
DEST_DIR="/app/data/stooq"

echo "======================================================================"
echo "COPY FILES TO CONTAINER - BATCH MODE"
echo "======================================================================"
echo ""

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Start it with: docker-compose -f docker-compose-dev.yml up -d"
    exit 1
fi

# Get Downloads folder path
DOWNLOADS_DIR="$HOME/Downloads"

if [ ! -d "$DOWNLOADS_DIR" ]; then
    echo "❌ Error: Downloads folder not found: $DOWNLOADS_DIR"
    exit 1
fi

echo "📁 Source: $DOWNLOADS_DIR"
echo "📦 Destination: $CONTAINER_NAME:$DEST_DIR"
echo ""

# Find all CSV/TXT/ZIP files
echo "🔍 Scanning for data files..."
mapfile -t files < <(find "$DOWNLOADS_DIR" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.txt" -o -name "*.zip" \) | sort)

if [ ${#files[@]} -eq 0 ]; then
    echo "❌ No CSV, TXT, or ZIP files found in Downloads folder"
    exit 1
fi

echo "✅ Found ${#files[@]} file(s)"
echo ""

# Display files with numbers
echo "📋 Available files:"
echo "----------------------------------------------------------------------"
for i in "${!files[@]}"; do
    filename=$(basename "${files[$i]}")
    size=$(ls -lh "${files[$i]}" | awk '{print $5}')
    date=$(ls -l "${files[$i]}" | awk '{print $6, $7, $8}')
    printf "%3d. %-50s %8s  %s\n" $((i+1)) "$filename" "$size" "$date"
done
echo "----------------------------------------------------------------------"
echo ""

# Selection menu
echo "Selection Options:"
echo "  • Enter numbers (e.g., 1,3,5 or 1-5 or 1,3-7,9)"
echo "  • Enter 'all' to copy all files"
echo "  • Enter pattern (e.g., 'aapl' or 'googl') to filter by ticker"
echo "  • Enter 'stooq' to copy only Stooq-formatted files"
echo "  • Enter 'q' to quit"
echo ""

read -p "👉 Your selection: " selection

# Handle quit
if [ "$selection" = "q" ] || [ "$selection" = "Q" ]; then
    echo "Cancelled."
    exit 0
fi

# Array to store selected files
selected_files=()

# Process selection
if [ "$selection" = "all" ] || [ "$selection" = "ALL" ]; then
    # Copy all files
    selected_files=("${files[@]}")
    echo "📦 Selected: ALL files (${#selected_files[@]} files)"
elif [[ "$selection" =~ ^[0-9,\-]+$ ]]; then
    # Parse number ranges (e.g., 1,3-5,7)
    IFS=',' read -ra parts <<< "$selection"
    for part in "${parts[@]}"; do
        if [[ "$part" =~ ^[0-9]+$ ]]; then
            # Single number
            idx=$((part - 1))
            if [ $idx -ge 0 ] && [ $idx -lt ${#files[@]} ]; then
                selected_files+=("${files[$idx]}")
            fi
        elif [[ "$part" =~ ^([0-9]+)-([0-9]+)$ ]]; then
            # Range (e.g., 1-5)
            start=$((BASH_REMATCH[1] - 1))
            end=$((BASH_REMATCH[2] - 1))
            for ((i=start; i<=end && i<${#files[@]}; i++)); do
                if [ $i -ge 0 ]; then
                    selected_files+=("${files[$i]}")
                fi
            done
        fi
    done
    echo "📦 Selected: ${#selected_files[@]} file(s)"
elif [ "$selection" = "stooq" ] || [ "$selection" = "STOOQ" ]; then
    # Filter Stooq files (common patterns: d_, m_, h_, w_, data_)
    for file in "${files[@]}"; do
        filename=$(basename "$file")
        if [[ "$filename" =~ ^(d_|m_|h_|w_|data_) ]] || [[ "$filename" =~ stooq ]]; then
            selected_files+=("$file")
        fi
    done
    echo "📦 Selected: ${#selected_files[@]} Stooq file(s)"
elif [ -n "$selection" ]; then
    # Pattern matching (e.g., "aapl", "googl")
    pattern=$(echo "$selection" | tr '[:upper:]' '[:lower:]')
    for file in "${files[@]}"; do
        filename=$(basename "$file" | tr '[:upper:]' '[:lower:]')
        if [[ "$filename" =~ $pattern ]]; then
            selected_files+=("$file")
        fi
    done
    echo "📦 Selected: ${#selected_files[@]} file(s) matching '$selection'"
else
    echo "❌ Invalid selection"
    exit 1
fi

if [ ${#selected_files[@]} -eq 0 ]; then
    echo "❌ No files selected"
    exit 1
fi

# Show selected files
echo ""
echo "📋 Files to copy:"
for i in "${!selected_files[@]}"; do
    filename=$(basename "${selected_files[$i]}")
    printf "  %d. %s\n" $((i+1)) "$filename"
done
echo ""

# Confirm
read -p "✅ Copy these files? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Copy files
echo ""
echo "📤 Copying files..."
copied=0
failed=0

for file in "${selected_files[@]}"; do
    filename=$(basename "$file")
    echo -n "  Copying $filename... "
    
    if docker cp "$file" "$CONTAINER_NAME:$DEST_DIR/" 2>/dev/null; then
        echo "✅"
        ((copied++))
    else
        echo "❌"
        ((failed++))
    fi
done

echo ""
echo "======================================================================"
echo "COPY COMPLETE"
echo "======================================================================"
echo "✅ Successfully copied: $copied file(s)"
if [ $failed -gt 0 ]; then
    echo "❌ Failed: $failed file(s)"
fi
echo ""
echo "📁 Files are now in: $DEST_DIR"
echo "🔄 Refresh Data View in browser to see the files"
echo ""
