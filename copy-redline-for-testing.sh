#!/bin/bash
# copy-redline-for-testing.sh
# Copy REDLINE automation AND source files from USB to local directory
# This ensures all required files are in the correct structure

echo "🔧 Copying REDLINE for Testing"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Find USB drive
USB_MOUNT=""
if [ -d "/media/$USER/REDLINE" ]; then
    USB_MOUNT="/media/$USER/REDLINE"
elif [ -d "/mnt/REDLINE" ]; then
    USB_MOUNT="/mnt/REDLINE"
elif [ -d "/run/media/$USER/REDLINE" ]; then
    USB_MOUNT="/run/media/$USER/REDLINE"
else
    echo "❌ USB drive not found. Please check:"
    echo "   ls /media/"
    echo "   ls /mnt/"
    echo "   ls /run/media/"
    exit 1
fi

print_info "Found USB drive at: $USB_MOUNT"

# Create local directory
LOCAL_DIR="/tmp/redline-build"
print_info "Creating local directory: $LOCAL_DIR"
rm -rf "$LOCAL_DIR"
mkdir -p "$LOCAL_DIR"

# Copy build automation files
print_info "Copying build automation files..."
if cp -r "$USB_MOUNT/build" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "Build automation files copied"
else
    print_warning "Could not copy build automation files"
fi

# Copy SOURCE FILES to LOCAL_DIR (critical!)
print_info "Copying source files..."
if cp "$USB_MOUNT/main.py" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "main.py copied"
else
    print_warning "Could not copy main.py"
fi

if cp "$USB_MOUNT/web_app.py" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "web_app.py copied"
else
    print_warning "Could not copy web_app.py"
fi

if cp "$USB_MOUNT/requirements.txt" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "requirements.txt copied"
else
    print_warning "Could not copy requirements.txt"
fi

if cp -r "$USB_MOUNT/redline" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "redline directory copied"
else
    print_warning "Could not copy redline directory"
fi

# Make scripts executable
print_info "Making scripts executable..."
chmod +x "$LOCAL_DIR/build/scripts"/*.sh 2>/dev/null && print_status "Scripts made executable"

# Verify files
print_info "Verifying copied files..."
echo "File structure:"
ls -la "$LOCAL_DIR/" | grep -E "(main.py|web_app.py|requirements.txt|redline|build)"
echo ""
echo "Scripts:"
ls -la "$LOCAL_DIR/build/scripts/" 2>/dev/null || echo "No scripts found"

echo ""
print_status "Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. cd $LOCAL_DIR"
echo "2. ./build/scripts/build_deb_package.sh"
echo ""
echo "📋 Prerequisites (if not installed):"
echo "sudo apt install python3 python3-pip dpkg-dev flatpak flatpak-builder"
echo "pip3 install pyinstaller"
echo ""
print_status "Ready to run automation!"
