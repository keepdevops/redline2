#!/bin/bash
# copy-redline-from-usb.sh
# Copy REDLINE automation from USB to local directory
# Based on actual USB structure

echo "🔧 Copying REDLINE Automation from USB"
echo "======================================"
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
LOCAL_DIR="/tmp/redline-automation"
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

# Copy ubuntu package files
print_info "Copying ubuntu package files..."
if cp -r "$USB_MOUNT/ubuntu-package" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "Ubuntu package files copied"
else
    print_warning "Could not copy ubuntu package files"
fi

# Copy executables
print_info "Copying executables..."
if cp -r "$USB_MOUNT/executables" "$LOCAL_DIR/" 2>/dev/null; then
    print_status "Executables copied"
else
    print_warning "Could not copy executables"
fi

# Make scripts executable
print_info "Making build scripts executable..."
chmod +x "$LOCAL_DIR/build/scripts"/*.sh 2>/dev/null && print_status "Build scripts made executable"

print_info "Making ubuntu package scripts executable..."
chmod +x "$LOCAL_DIR/ubuntu-package/Scripts"/*.sh 2>/dev/null && print_status "Ubuntu package scripts made executable"

# Create project structure for build scripts
print_info "Creating project structure..."
mkdir -p "$LOCAL_DIR/dist/executables"
mkdir -p "$LOCAL_DIR/dist/deb-package"
mkdir -p "$LOCAL_DIR/dist/flatpak-package"
mkdir -p "$LOCAL_DIR/dist/windows-package"

# Create main.py
print_info "Creating main.py..."
cat > "$LOCAL_DIR/main.py" << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Financial Platform - Main GUI Application
"""

import sys
import os

def main():
    print("REDLINE Financial Platform - GUI Application")
    print("Version: 1.0.0")
    print("Platform: Linux")
    print("GUI application started successfully!")

if __name__ == "__main__":
    main()
EOF
chmod +x "$LOCAL_DIR/main.py"

# Create web_app.py
print_info "Creating web_app.py..."
cat > "$LOCAL_DIR/web_app.py" << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Financial Platform - Web Application
"""

import sys
import os

def main():
    print("REDLINE Financial Platform - Web Application")
    print("Version: 1.0.0")
    print("Platform: Linux")
    print("Web application started successfully!")

if __name__ == "__main__":
    main()
EOF
chmod +x "$LOCAL_DIR/web_app.py"

# Create requirements.txt
print_info "Creating requirements.txt..."
cat > "$LOCAL_DIR/requirements.txt" << 'EOF'
pyinstaller>=5.0.0
flask>=2.0.0
pandas>=1.3.0
numpy>=1.21.0
EOF

# Create version file
print_info "Creating version file..."
mkdir -p "$LOCAL_DIR/redline"
cat > "$LOCAL_DIR/redline/__version__.py" << 'EOF'
__version__ = "1.0.0"
EOF

print_status "Project structure created"

# Verify files
print_info "Verifying copied files..."
echo "Build scripts:"
ls -la "$LOCAL_DIR/build/scripts/" 2>/dev/null || echo "No build scripts found"
echo ""
echo "Ubuntu package scripts:"
ls -la "$LOCAL_DIR/ubuntu-package/Scripts/" 2>/dev/null || echo "No ubuntu package scripts found"

echo ""
print_status "Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. cd $LOCAL_DIR"
echo "2. ./build/scripts/build_deb_package.sh"
echo "3. ./build/scripts/build_flatpak_package.sh"
echo "4. ./build/scripts/build_windows_package.sh"
echo ""
echo "📋 Or use ubuntu package scripts:"
echo "1. cd $LOCAL_DIR/ubuntu-package"
echo "2. ./Scripts/install-deb.sh"
echo "3. ./Scripts/install-flatpak.sh"
echo "4. ./Scripts/install.sh"
echo ""
echo "📋 Prerequisites (if not installed):"
echo "sudo apt install python3 python3-pip dpkg-dev flatpak flatpak-builder"
echo "pip3 install pyinstaller"
echo ""
print_status "Ready to run automation!"
