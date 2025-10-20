#!/bin/bash
set -e

# REDLINE Installation Wrapper Script
# Automatically detects platform and runs appropriate installation

echo "🚀 REDLINE Installation Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v lsb_release &> /dev/null; then
            local distro=$(lsb_release -si)
            if [[ "$distro" == "Ubuntu" ]]; then
                echo "ubuntu"
                return
            fi
        fi
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to detect architecture
detect_arch() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "amd64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        armv7l)
            echo "arm32"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --platform PLATFORM    Force platform (ubuntu, macos, windows)"
    echo "  --arch ARCHITECTURE    Force architecture (amd64, arm64)"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Auto-detect platform and run installation"
    echo "  $0 --platform ubuntu   # Force Ubuntu installation"
    echo "  $0 --arch arm64        # Force ARM64 installation"
    echo ""
    echo "Supported Platforms:"
    echo "  - Ubuntu (Intel/AMD x86_64)"
    echo "  - Ubuntu (ARM64/Apple Silicon)"
    echo "  - macOS (Intel/Apple Silicon)"
    echo "  - Windows (WSL2)"
}

# Main installation function
main() {
    local platform=""
    local arch=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --platform)
                platform="$2"
                shift 2
                ;;
            --arch)
                arch="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Auto-detect if not specified
    if [[ -z "$platform" ]]; then
        platform=$(detect_os)
    fi
    
    if [[ -z "$arch" ]]; then
        arch=$(detect_arch)
    fi
    
    print_status "Detected platform: $platform"
    print_status "Detected architecture: $arch"
    
    # Check if we have the appropriate installation script
    local install_script=""
    
    case "$platform" in
        ubuntu)
            case "$arch" in
                amd64)
                    install_script="install_ubuntu_intel.sh"
                    ;;
                arm64)
                    install_script="install_ubuntu_arm.sh"
                    ;;
                *)
                    print_error "Unsupported architecture for Ubuntu: $arch"
                    exit 1
                    ;;
            esac
            ;;
        macos)
            case "$arch" in
                amd64|arm64)
                    install_script="install_macos.sh"
                    ;;
                *)
                    print_error "Unsupported architecture for macOS: $arch"
                    exit 1
                    ;;
            esac
            ;;
        windows)
            install_script="install_windows.sh"
            ;;
        *)
            print_error "Unsupported platform: $platform"
            print_status "Supported platforms: ubuntu, macos, windows"
            exit 1
            ;;
    esac
    
    # Get the directory where this script is located
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Check if installation script exists
    if [[ ! -f "$script_dir/$install_script" ]]; then
        print_error "Installation script not found: $script_dir/$install_script"
        print_status "Available installation scripts:"
        ls -la "$script_dir"/install_*.sh 2>/dev/null || print_warning "No installation scripts found"
        exit 1
    fi
    
    # Check if installation script is executable
    if [[ ! -x "$script_dir/$install_script" ]]; then
        print_status "Making installation script executable..."
        chmod +x "$script_dir/$install_script"
    fi
    
    print_status "Running installation script: $script_dir/$install_script"
    echo ""
    
    # Add Ubuntu 24.04 specific warning for Tkinter
    if [[ "$platform" == "ubuntu" && "$arch" == "amd64" ]]; then
        print_warning "Ubuntu 24.04 LTS uses different Tkinter package names"
        print_status "If you encounter 'package tkinter not found', run:"
        print_status "  ./install/fix_tkinter_ubuntu24.sh"
        echo ""
    fi
    
    # Run the appropriate installation script
    exec "$script_dir/$install_script"
}

# Run main function
main "$@"
