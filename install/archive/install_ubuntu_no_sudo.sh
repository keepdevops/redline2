#!/bin/bash
set -e

# REDLINE Ubuntu Installation Script (No Sudo Required)
# Installs and configures REDLINE for the current user without sudo privileges

echo "🚀 REDLINE Ubuntu Installation Script (No Sudo)"
echo "=============================================="

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

# Configuration variables
CURRENT_USER="$USER"
REDLINE_HOME="$HOME"
REDLINE_DIR="$REDLINE_HOME/redline"
PYTHON_VERSION="3.11"

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user."
        exit 1
    fi
}

# Function to check if running on Ubuntu
check_ubuntu() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS. This script is designed for Ubuntu."
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        print_warning "This script is designed for Ubuntu, but you're running $ID"
        print_warning "Proceeding anyway..."
    fi
    
    print_status "Detected OS: $PRETTY_NAME"
}

# Function to check Python installation
check_python() {
    print_status "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version found"
}

# Function to check pip installation
check_pip() {
    print_status "Checking pip installation..."
    
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 not found, installing via get-pip.py..."
        curl -s https://bootstrap.pypa.io/get-pip.py | python3
    fi
    
    print_success "pip3 is available"
}

# Function to install Python packages via pip
install_python_packages() {
    print_status "Installing Python packages via pip..."
    
    # Upgrade pip first
    pip3 install --user --upgrade pip
    
    # Install tkinter via pip (fallback for system packages)
    print_status "Installing Tkinter via pip..."
    pip3 install --user tk || {
        print_warning "Failed to install tkinter via pip. GUI may not work."
    }
    
    print_success "Python packages installed"
}

# Function to setup REDLINE directory
setup_redline() {
    print_status "Setting up REDLINE directory..."
    
    if [ -d "$REDLINE_DIR" ]; then
        print_warning "REDLINE directory already exists."
        print_status "Using existing directory: $REDLINE_DIR"
    else
        print_status "Creating REDLINE directory: $REDLINE_DIR"
        mkdir -p "$REDLINE_DIR"
    fi
    
    # Copy files to REDLINE directory
    print_status "Copying REDLINE files..."
    cp -r . "$REDLINE_DIR/" 2>/dev/null || {
        print_warning "Some files may not have been copied. Continuing..."
    }
    
    print_success "REDLINE directory setup complete"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd "$REDLINE_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip in virtual environment
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Function to create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    cd "$REDLINE_DIR"
    
    # Create GUI startup script
    cat > start_gui.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py
EOF
    
    # Create web app startup script
    cat > start_web.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 web_app.py
EOF
    
    # Make scripts executable
    chmod +x start_gui.sh start_web.sh
    
    print_success "Startup scripts created"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    cd "$REDLINE_DIR"
    source venv/bin/activate
    
    # Test Python imports
    python3 -c "import sys; print('Python version:', sys.version)"
    
    # Test tkinter
    if python3 -c "import tkinter; print('Tkinter version:', tkinter.TkVersion)" 2>/dev/null; then
        print_success "Tkinter is working"
    else
        print_warning "Tkinter not available - GUI will not work"
    fi
    
    # Test core modules
    if python3 -c "from redline.core.data_loader import DataLoader; print('DataLoader imported successfully')" 2>/dev/null; then
        print_success "REDLINE core modules working"
    else
        print_warning "REDLINE core modules may have issues"
    fi
    
    print_success "Installation test complete"
}

# Function to print final instructions
print_final_instructions() {
    print_success "REDLINE installation complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Navigate to REDLINE directory: cd $REDLINE_DIR"
    echo "2. Start GUI application: ./start_gui.sh"
    echo "3. Start web application: ./start_web.sh"
    echo "4. Or run directly: source venv/bin/activate && python3 main.py"
    echo ""
    echo "🔧 If you encounter issues:"
    echo "- GUI not working: tkinter may not be available"
    echo "- Import errors: check virtual environment activation"
    echo "- Permission errors: ensure you own the REDLINE directory"
    echo ""
    echo "📁 REDLINE installed in: $REDLINE_DIR"
}

# Main installation function
main() {
    print_status "Starting REDLINE installation (No Sudo Mode)"
    echo ""
    
    check_root
    check_ubuntu
    check_python
    check_pip
    install_python_packages
    setup_redline
    setup_python_env
    create_startup_scripts
    test_installation
    print_final_instructions
}

# Run main function
main "$@"
