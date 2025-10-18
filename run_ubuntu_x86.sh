#!/bin/bash

# REDLINE Ubuntu x86 Launch Script
# For Dell x86 systems running Ubuntu
# This script handles environment setup and launches REDLINE GUI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/redline_ubuntu.log"
PYTHON_MIN_VERSION="3.8"

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

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Found Python $PYTHON_VERSION"
        
        # Check if version is sufficient
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python3 not found"
        return 1
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt-get update -y
    
    # Install essential packages
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-tk \
        python3-venv \
        python3-dev \
        build-essential \
        curl \
        wget \
        git \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        libxft-dev \
        libxext-dev \
        libxrender-dev \
        tk-dev \
        tcl-dev \
        libx11-dev \
        libxss1 \
        libgconf-2-4
    
    print_success "System dependencies installed"
}

# Function to install conda if not present
install_conda() {
    if command_exists conda; then
        print_status "Conda already installed"
        return 0
    fi
    
    print_status "Installing Miniconda..."
    
    # Download Miniconda installer
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    
    # Install Miniconda
    bash miniconda.sh -b -p "$HOME/miniconda3"
    
    # Add conda to PATH
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/miniconda3/bin:$PATH"
    
    # Initialize conda
    "$HOME/miniconda3/bin/conda" init bash
    
    # Clean up
    rm miniconda.sh
    
    print_success "Miniconda installed"
}

# Function to create conda environment
setup_conda_environment() {
    print_status "Setting up conda environment..."
    
    # Add conda to PATH if not already there
    if [ -d "$HOME/miniconda3/bin" ]; then
        export PATH="$HOME/miniconda3/bin:$PATH"
    fi
    
    # Check if stock environment exists
    if conda env list | grep -q "stock"; then
        print_status "Found existing 'stock' environment"
        conda activate stock
    else
        print_status "Creating 'stock' environment..."
        
        # Create environment with Python 3.11
        conda create -n stock python=3.11 -y
        
        # Activate environment
        conda activate stock
        
        # Install core dependencies
        conda install -y \
            pandas \
            numpy \
            matplotlib \
            seaborn \
            scipy \
            scikit-learn \
            pyarrow \
            duckdb \
            polars \
            requests \
            beautifulsoup4 \
            lxml \
            openpyxl \
            xlrd \
            tk \
            pip
        
        # Install additional packages via pip if conda fails
        pip install \
            pandas \
            numpy \
            matplotlib \
            seaborn \
            scipy \
            scikit-learn \
            pyarrow \
            duckdb \
            polars \
            requests \
            beautifulsoup4 \
            lxml \
            openpyxl \
            xlrd
        
        print_success "Stock environment created and configured"
    fi
    
    # Verify environment
    print_status "Verifying environment..."
    python -c "import pandas, numpy, pyarrow, duckdb, polars; print('All dependencies available')"
    
    print_success "Environment setup complete"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install from requirements files if they exist
    if [ -f "$SCRIPT_DIR/requirements_ubuntu.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements_ubuntu.txt"
    elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements.txt"
    else
        # Install core dependencies manually with error handling
        pip install --upgrade pip
        
        # Install packages one by one to handle failures gracefully
        packages=(
            "pandas"
            "numpy" 
            "matplotlib"
            "seaborn"
            "scipy"
            "scikit-learn"
            "pyarrow"
            "duckdb"
            "polars"
            "requests"
            "beautifulsoup4"
            "lxml"
            "openpyxl"
            "xlrd"
        )
        
        for package in "${packages[@]}"; do
            print_status "Installing $package..."
            if pip install "$package"; then
                print_success "$package installed"
            else
                print_warning "Failed to install $package, trying with --user flag..."
                pip install --user "$package" || print_warning "Failed to install $package"
            fi
        done
    fi
    
    print_success "Python dependencies installation completed"
}

# Function to check X11 display
check_x11_display() {
    if [ -z "$DISPLAY" ]; then
        print_warning "DISPLAY variable not set"
        export DISPLAY=:0
        print_status "Set DISPLAY to :0"
    else
        print_status "DISPLAY is set to $DISPLAY"
    fi
    
    # Test X11 connection
    if command_exists xdpyinfo; then
        if xdpyinfo >/dev/null 2>&1; then
            print_success "X11 display is working"
            return 0
        else
            print_error "X11 display connection failed"
            return 1
        fi
    else
        print_warning "xdpyinfo not found, skipping X11 test"
        return 0
    fi
}

# Function to check GUI dependencies
check_gui_dependencies() {
    print_status "Checking GUI dependencies..."
    
    # Check if running in desktop environment
    if [ -n "$XDG_CURRENT_DESKTOP" ] || [ -n "$DESKTOP_SESSION" ]; then
        print_success "Desktop environment detected: $XDG_CURRENT_DESKTOP"
    else
        print_warning "No desktop environment detected"
        print_warning "GUI may not work properly without X11 forwarding"
    fi
    
    # Check tkinter
    python3 -c "import tkinter; print('tkinter available')" 2>/dev/null || {
        print_error "tkinter not available"
        return 1
    }
    
    print_success "GUI dependencies check complete"
}

# Function to fix common Ubuntu issues
fix_ubuntu_issues() {
    print_status "Applying Ubuntu-specific fixes..."
    
    # Fix potential locale issues
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    
    # Fix potential display issues
    export QT_X11_NO_MITSHM=1
    
    # Fix potential threading issues
    export OMP_NUM_THREADS=1
    
    print_success "Ubuntu-specific fixes applied"
}

# Function to run REDLINE
run_redline() {
    print_status "Starting REDLINE..."
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Try to activate conda environment if available
    if command_exists conda && conda env list | grep -q "stock"; then
        print_status "Activating conda environment 'stock'..."
        source ~/miniconda3/bin/activate stock
    fi
    
    # Set environment variables for Ubuntu
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    export MPLBACKEND=TkAgg
    
    # Run REDLINE with GUI
    print_status "Launching REDLINE GUI..."
    python3 main.py --task=gui
    
    print_success "REDLINE session ended"
}

# Function to run diagnostics
run_diagnostics() {
    print_status "Running system diagnostics..."
    
    echo "=== System Information ==="
    uname -a
    echo
    
    echo "=== Python Information ==="
    python3 --version
    python3 -c "import sys; print(f'Python path: {sys.executable}')"
    echo
    
    echo "=== Available Python Packages ==="
    python3 -c "
import sys
packages = ['pandas', 'numpy', 'matplotlib', 'tkinter', 'pyarrow', 'duckdb', 'polars']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
"
    echo
    
    echo "=== Display Information ==="
    echo "DISPLAY: $DISPLAY"
    echo "XDG_CURRENT_DESKTOP: $XDG_CURRENT_DESKTOP"
    echo "DESKTOP_SESSION: $DESKTOP_SESSION"
    echo
    
    echo "=== Conda Information ==="
    if command_exists conda; then
        conda info
        conda env list
    else
        echo "Conda not installed"
    fi
    echo
    
    echo "=== Disk Space ==="
    df -h
    echo
    
    print_success "Diagnostics complete"
}

# Function to show help
show_help() {
    echo "REDLINE Ubuntu x86 Launch Script"
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  --install     Install all dependencies and setup environment"
    echo "  --run         Run REDLINE (default)"
    echo "  --diagnose    Run system diagnostics"
    echo "  --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0                    # Run REDLINE"
    echo "  $0 --install          # Install dependencies"
    echo "  $0 --diagnose         # Run diagnostics"
    echo
}

# Main function
main() {
    # Initialize log file
    echo "REDLINE Ubuntu Launch Script - $(date)" > "$LOG_FILE"
    
    print_status "REDLINE Ubuntu x86 Launch Script"
    print_status "Starting at $(date)"
    
    # Parse command line arguments
    case "${1:-}" in
        --install)
            print_status "Installation mode"
            check_python_version || install_system_dependencies
            install_conda
            setup_conda_environment
            install_python_dependencies
            check_gui_dependencies
            fix_ubuntu_issues
            print_success "Installation complete!"
            ;;
        --diagnose)
            run_diagnostics
            ;;
        --help)
            show_help
            ;;
        --run|"")
            print_status "Launch mode"
            check_python_version || {
                print_error "Python check failed. Run with --install to fix dependencies."
                exit 1
            }
            check_x11_display || {
                print_warning "X11 display issues detected. GUI may not work properly."
            }
            check_gui_dependencies || {
                print_error "GUI dependencies missing. Run with --install to fix."
                exit 1
            }
            fix_ubuntu_issues
            run_redline
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    
    print_success "Script completed successfully"
}

# Trap errors and cleanup
trap 'print_error "Script failed at line $LINENO"; exit 1' ERR

# Run main function with all arguments
main "$@"
