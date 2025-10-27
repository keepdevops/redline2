#!/bin/bash
# update-usb-scripts.sh
# Updates all build scripts on USB drive

echo "📋 Updating USB Scripts..."

# Check if USB is mounted
if [ -d "/Volumes/REDLINE" ]; then
    USB_PATH="/Volumes/REDLINE"
elif [ -d "/media/$USER/REDLINE" ]; then
    USB_PATH="/media/$USER/REDLINE"
elif [ -d "/mnt/REDLINE" ]; then
    USB_PATH="/mnt/REDLINE"
elif [ -d "/run/media/$USER/REDLINE" ]; then
    USB_PATH="/run/media/$USER/REDLINE"
else
    echo "❌ USB drive not found"
    exit 1
fi

echo "✅ USB found at: $USB_PATH"

# Copy updated scripts
cp build/scripts/build_deb_package.sh "$USB_PATH/build/scripts/"
cp build/scripts/build_flatpak_package.sh "$USB_PATH/build/scripts/"
cp build/scripts/build_windows_package.sh "$USB_PATH/build/scripts/"

echo "✅ All scripts updated on USB!"
