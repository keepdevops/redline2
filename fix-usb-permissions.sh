#!/bin/bash
# fix-usb-permissions.sh
# Complete USB permission fix script for Linux test computer

echo "🔧 Fixing USB Drive Permissions on Linux"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_important() {
    echo -e "${PURPLE}🔑 $1${NC}"
}

# Function to find USB drive
find_usb_drive() {
    print_info "Searching for USB drive..."
    
    # Common mount points
    MOUNT_POINTS=(
        "/media/$USER/REDLINE"
        "/mnt/REDLINE"
        "/run/media/$USER/REDLINE"
        "/media/REDLINE"
        "/mnt/usb"
        "/run/media/REDLINE"
    )
    
    for mount_point in "${MOUNT_POINTS[@]}"; do
        if [ -d "$mount_point" ]; then
            print_status "Found USB drive at: $mount_point"
            echo "$mount_point"
            return 0
        fi
    done
    
    print_error "USB drive not found in common mount points"
    print_info "Please check:"
    print_info "  ls /media/"
    print_info "  ls /mnt/"
    print_info "  ls /run/media/"
    print_info "  mount | grep REDLINE"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check for required commands
    local missing_commands=()
    
    if ! command -v python3 &> /dev/null; then
        missing_commands+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null; then
        missing_commands+=("pip3")
    fi
    
    if ! command -v dpkg-deb &> /dev/null; then
        missing_commands+=("dpkg-dev")
    fi
    
    if ! command -v flatpak &> /dev/null; then
        missing_commands+=("flatpak")
    fi
    
    if ! command -v flatpak-builder &> /dev/null; then
        missing_commands+=("flatpak-builder")
    fi
    
    if [ ${#missing_commands[@]} -gt 0 ]; then
        print_warning "Missing prerequisites: ${missing_commands[*]}"
        print_info "Installing missing packages..."
        
        # Install missing packages
        sudo apt update
        sudo apt install -y python3 python3-pip dpkg-dev flatpak flatpak-builder
        
        # Install PyInstaller
        pip3 install pyinstaller
        
        print_status "Prerequisites installed"
    else
        print_status "All prerequisites found"
    fi
}

# Function to setup Flatpak runtime
setup_flatpak_runtime() {
    print_info "Setting up Flatpak runtime..."
    
    # Add Flathub remote
    if ! flatpak remote-list | grep -q "flathub"; then
        print_info "Adding Flathub remote..."
        flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    fi
    
    # Install runtime and SDK
    print_info "Installing runtime and SDK..."
    flatpak install --assumeyes flathub org.freedesktop.Platform//23.08
    flatpak install --assumeyes flathub org.freedesktop.Sdk//23.08
    
    print_status "Flatpak runtime setup complete"
}

# Function to fix USB permissions
fix_usb_permissions() {
    local usb_mount="$1"
    
    print_info "Attempting to fix USB permissions..."
    
    # Try to make scripts executable
    if chmod +x "$usb_mount/build/scripts/*.sh" 2>/dev/null; then
        print_status "USB scripts made executable"
        
        # Verify permissions
        print_info "Verifying script permissions..."
        ls -la "$usb_mount/build/scripts/*.sh"
        
        print_status "USB drive permissions fixed!"
        print_info "You can now run the automation scripts from:"
        print_info "  cd $usb_mount"
        print_info "  ./build/scripts/build_deb_package.sh"
        print_info "  ./build/scripts/build_flatpak_package.sh"
        print_info "  ./build/scripts/build_windows_package.sh"
        
        return 0
    else
        print_warning "Cannot modify USB permissions - USB may be read-only"
        return 1
    fi
}

# Function to copy to local directory
copy_to_local() {
    local usb_mount="$1"
    
    print_info "Copying scripts to local directory..."
    
    # Create local directory
    LOCAL_DIR="/tmp/redline-build"
    rm -rf "$LOCAL_DIR"
    mkdir -p "$LOCAL_DIR"
    
    # Copy automation files
    if cp -r "$usb_mount/build/automation" "$LOCAL_DIR/" 2>/dev/null; then
        print_status "Automation files copied"
    else
        print_warning "Could not copy automation files"
    fi
    
    # Copy scripts
    if cp -r "$usb_mount/build/scripts" "$LOCAL_DIR/" 2>/dev/null; then
        print_status "Scripts copied"
    else
        print_error "Failed to copy scripts"
        return 1
    fi
    
    # Make scripts executable
    if chmod +x "$LOCAL_DIR/scripts/*.sh" 2>/dev/null; then
        print_status "Scripts made executable"
    else
        print_error "Failed to make scripts executable"
        return 1
    fi
    
    # Verify copy
    print_info "Verifying copied files..."
    ls -la "$LOCAL_DIR/scripts/"
    
    print_status "Scripts successfully copied to: $LOCAL_DIR"
    print_info "You can now run:"
    print_info "  cd $LOCAL_DIR"
    print_info "  ./scripts/build_deb_package.sh"
    print_info "  ./scripts/build_flatpak_package.sh"
    print_info "  ./scripts/build_windows_package.sh"
    
    return 0
}

# Function to create project structure
create_project_structure() {
    local local_dir="$1"
    
    print_info "Creating project structure..."
    
    # Create necessary directories
    mkdir -p "$local_dir/dist/executables"
    mkdir -p "$local_dir/dist/deb-package"
    mkdir -p "$local_dir/dist/flatpak-package"
    mkdir -p "$local_dir/dist/windows-package"
    
    # Create main.py and web_app.py if they don't exist
    if [ ! -f "$local_dir/main.py" ]; then
        print_info "Creating placeholder main.py..."
        cat > "$local_dir/main.py" << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Financial Platform - Main GUI Application
Placeholder for testing package automation
"""

import sys
import os

def main():
    print("REDLINE Financial Platform - GUI Application")
    print("This is a placeholder for testing package automation")
    print("Version: 1.0.0")
    print("Platform: Linux")
    
    # Simulate GUI application
    print("\nStarting GUI application...")
    print("GUI would normally start here")
    print("Application started successfully!")

if __name__ == "__main__":
    main()
EOF
    fi
    
    if [ ! -f "$local_dir/web_app.py" ]; then
        print_info "Creating placeholder web_app.py..."
        cat > "$local_dir/web_app.py" << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Financial Platform - Web Application
Placeholder for testing package automation
"""

import sys
import os

def main():
    print("REDLINE Financial Platform - Web Application")
    print("This is a placeholder for testing package automation")
    print("Version: 1.0.0")
    print("Platform: Linux")
    
    # Simulate web application
    print("\nStarting web application...")
    print("Web server would normally start on http://localhost:8080")
    print("Web application started successfully!")

if __name__ == "__main__":
    main()
EOF
    fi
    
    # Create requirements.txt
    if [ ! -f "$local_dir/requirements.txt" ]; then
        print_info "Creating requirements.txt..."
        cat > "$local_dir/requirements.txt" << 'EOF'
# REDLINE Financial Platform Requirements
# Placeholder for testing package automation

pyinstaller>=5.0.0
flask>=2.0.0
flask-socketio>=5.0.0
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
requests>=2.25.0
EOF
    fi
    
    # Create version file
    if [ ! -f "$local_dir/redline/__version__.py" ]; then
        print_info "Creating version file..."
        mkdir -p "$local_dir/redline"
        cat > "$local_dir/redline/__version__.py" << 'EOF'
"""
REDLINE Financial Platform Version
"""

__version__ = "1.0.0"
EOF
    fi
    
    print_status "Project structure created"
}

# Main execution
main() {
    echo "Starting USB permission fix process..."
    echo ""
    
    # Find USB drive
    USB_MOUNT=$(find_usb_drive)
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Setup Flatpak runtime
    setup_flatpak_runtime
    
    # Try to fix USB permissions
    if fix_usb_permissions "$USB_MOUNT"; then
        print_status "USB permissions fixed successfully!"
        print_info "You can now run the automation scripts directly from the USB drive"
        exit 0
    fi
    
    # If USB fix failed, copy to local directory
    print_warning "USB permissions could not be fixed, copying to local directory..."
    
    if copy_to_local "$USB_MOUNT"; then
        # Create project structure
        create_project_structure "/tmp/redline-build"
        
        print_status "Setup complete!"
        print_important "Next steps:"
        print_info "1. cd /tmp/redline-build"
        print_info "2. ./scripts/build_deb_package.sh"
        print_info "3. ./scripts/build_flatpak_package.sh"
        print_info "4. ./scripts/build_windows_package.sh"
        
        echo ""
        print_important "All automation scripts are ready to use!"
    else
        print_error "Failed to copy scripts to local directory"
        exit 1
    fi
}

# Run main function
main "$@"