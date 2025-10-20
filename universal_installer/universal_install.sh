#!/bin/bash
set -e

# REDLINE Universal Installation Script
# Complete installation without GitHub verification
# Supports Docker and bare metal installations

echo "🚀 REDLINE Universal Installer"
echo "============================="
echo "Complete installation with all dependencies"
echo "Supports Docker and bare metal installations"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Configuration
CURRENT_USER="$USER"
REDLINE_HOME="$HOME"
REDLINE_DIR="$REDLINE_HOME/redline"
SOURCE_DIR="$(pwd)"
INSTALL_MODE="auto"
PYTHON_VERSION="3.11"
SKIP_DOCKER=false
SKIP_GUI=false
WEB_ONLY=false

# Complete dependency list based on codebase analysis
REQUIRED_PACKAGES=(
    "pandas>=2.0.0"
    "numpy>=1.24.0"
    "configparser>=5.3.0"
    "pyarrow>=10.0.0"
    "polars>=0.20.0"
    "duckdb>=0.8.0"
    "yfinance>=0.2.0"
    "flask>=2.3.0"
    "flask-socketio>=5.3.0"
    "flask-compress>=1.13"
    "requests>=2.31.0"
    "urllib3>=2.0.0"
    "python-dateutil>=2.8.0"
    "pytz>=2023.3"
)

# Optional dependencies for enhanced features
OPTIONAL_PACKAGES=(
    "matplotlib>=3.7.0"
    "seaborn>=0.12.0"
    "scipy>=1.9.0"
    "scikit-learn>=1.3.0"
    "openpyxl>=3.1.0"
    "xlsxwriter>=3.1.0"
    "psutil>=5.9.0"
    "gunicorn>=21.0.0"
    "celery>=5.3.0"
    "redis>=4.5.0"
)

# System packages for different OS
UBUNTU_PACKAGES=(
    "curl"
    "wget"
    "git"
    "python3"
    "python3-pip"
    "python3-venv"
    "python3-dev"
    "python3-tk"
    "python3-tkinter"
    "build-essential"
    "libpq-dev"
    "libx11-dev"
    "libxext-dev"
    "libxrender-dev"
    "libxtst-dev"
    "libxi-dev"
)

MACOS_PACKAGES=(
    "python3"
    "git"
    "curl"
    "wget"
)

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --mode MODE          Installation mode: auto, minimal, full, docker, bare-metal"
    echo "  --user USER          Install for specific user (default: current user)"
    echo "  --dir DIRECTORY      Installation directory (default: ~/redline)"
    echo "  --skip-docker        Skip Docker installation"
    echo "  --skip-gui           Skip GUI components"
    echo "  --web-only           Install only web interface"
    echo "  --docker-only        Install only Docker components"
    echo "  --bare-metal         Install only bare metal components"
    echo "  --help               Show this help message"
    echo ""
    echo "Installation Modes:"
    echo "  auto       - Automatically detect and install appropriate components"
    echo "  minimal    - Install only essential components (Python + web)"
    echo "  full       - Install everything (Python + Docker + GUI + web)"
    echo "  docker     - Install Docker environment with REDLINE"
    echo "  bare-metal - Install directly on system without Docker"
    echo ""
    echo "Examples:"
    echo "  $0                           # Auto-detect and install"
    echo "  $0 --mode bare-metal         # Bare metal installation"
    echo "  $0 --mode docker             # Docker installation"
    echo "  $0 --mode minimal            # Minimal installation"
    echo "  $0 --skip-docker             # Skip Docker installation"
}

# Function to detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v lsb_release &> /dev/null; then
            local distro=$(lsb_release -si)
            local version=$(lsb_release -sr)
            echo "$distro $version"
        else
            echo "Linux (unknown distribution)"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        local version=$(sw_vers -productVersion)
        echo "macOS $version"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "Windows"
    else
        echo "Unknown"
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

# Function to detect environment capabilities
detect_environment() {
    local capabilities=()
    
    # Check if we have sudo access
    if sudo -n true 2>/dev/null; then
        capabilities+=("sudo")
    fi
    
    # Check if we're in a REDLINE directory
    if [[ -f "main.py" ]] && [[ -d "redline" ]]; then
        capabilities+=("local_files")
    fi
    
    # Check if we have internet access
    if curl -s --max-time 5 https://github.com &>/dev/null; then
        capabilities+=("internet")
    fi
    
    # Check if we have Docker
    if command -v docker &> /dev/null; then
        capabilities+=("docker")
    fi
    
    # Check if we have Python
    if command -v python3 &> /dev/null; then
        capabilities+=("python3")
    fi
    
    # Check if we have a display (for GUI)
    if [[ -n "$DISPLAY" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        capabilities+=("gui")
    fi
    
    echo "${capabilities[*]}"
}

# Function to determine optimal installation mode
determine_mode() {
    local capabilities=($(detect_environment))
    local os=$(detect_os)
    local arch=$(detect_arch)
    
    print_status "Detected environment:"
    print_status "  OS: $os"
    print_status "  Architecture: $arch"
    print_status "  Capabilities: ${capabilities[*]}"
    
    # Check for specific mode requests
    if [[ "$INSTALL_MODE" != "auto" ]]; then
        echo "$INSTALL_MODE"
        return
    fi
    
    # Auto-detect optimal mode
    if [[ " ${capabilities[*]} " =~ " docker " ]] && [[ " ${capabilities[*]} " =~ " sudo " ]]; then
        echo "full"
    elif [[ " ${capabilities[*]} " =~ " python3 " ]] && [[ " ${capabilities[*]} " =~ " local_files " ]]; then
        echo "minimal"
    elif [[ " ${capabilities[*]} " =~ " internet " ]] && [[ " ${capabilities[*]} " =~ " sudo " ]]; then
        echo "full"
    else
        echo "minimal"
    fi
}

# Function to install system packages (Ubuntu/Debian)
install_system_packages_ubuntu() {
    print_step "Installing system packages for Ubuntu/Debian..."
    
    # Update package lists
    sudo apt-get update
    
    # Install essential packages
    sudo apt-get install -y "${UBUNTU_PACKAGES[@]}"
    
    # Try to install Tkinter packages (Ubuntu 24.04 fix)
    sudo apt-get install -y python3-tk python3-tkinter 2>/dev/null || {
        print_warning "Tkinter packages not available, will install via pip"
    }
    
    print_success "System packages installed for Ubuntu/Debian"
}

# Function to install system packages (CentOS/RHEL/Fedora)
install_system_packages_centos() {
    print_step "Installing system packages for CentOS/RHEL/Fedora..."
    
    # Try dnf first (Fedora), then yum (CentOS/RHEL)
    if command -v dnf &> /dev/null; then
        sudo dnf update -y
        sudo dnf install -y \
            curl \
            wget \
            git \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            tkinter
    else
        sudo yum update -y
        sudo yum install -y \
            curl \
            wget \
            git \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            tkinter
    fi
    
    print_success "System packages installed for CentOS/RHEL/Fedora"
}

# Function to install system packages (macOS)
install_system_packages_macos() {
    print_step "Installing system packages for macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install packages via Homebrew
    brew install "${MACOS_PACKAGES[@]}"
    
    print_success "System packages installed for macOS"
}

# Function to install system packages
install_system_packages() {
    local os_info=$(detect_os)
    
    print_header "Installing System Packages"
    print_status "Detected OS: $os_info"
    
    if [[ "$os_info" == *"Ubuntu"* ]] || [[ "$os_info" == *"Debian"* ]]; then
        install_system_packages_ubuntu
    elif [[ "$os_info" == *"CentOS"* ]] || [[ "$os_info" == *"Red Hat"* ]] || [[ "$os_info" == *"Fedora"* ]]; then
        install_system_packages_centos
    elif [[ "$os_info" == *"macOS"* ]]; then
        install_system_packages_macos
    else
        print_warning "Unknown Linux distribution, attempting basic installation..."
        # Try generic package manager
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip curl wget git
        elif command -v yum &> /dev/null; then
            sudo yum update -y && sudo yum install -y python3 python3-pip curl wget git
        elif command -v dnf &> /dev/null; then
            sudo dnf update -y && sudo dnf install -y python3 python3-pip curl wget git
        else
            print_error "No supported package manager found"
            return 1
        fi
    fi
}

# Function to install Docker
install_docker() {
    local os_info=$(detect_os)
    
    print_header "Installing Docker"
    print_status "Installing Docker for $os_info..."
    
    if [[ "$os_info" == *"Ubuntu"* ]] || [[ "$os_info" == *"Debian"* ]]; then
        # Remove old Docker versions
        sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Set up the stable repository
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Update package index and install Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Add current user to docker group
        sudo usermod -aG docker $CURRENT_USER
        
        # Enable Docker to start on boot
        sudo systemctl enable docker
        sudo systemctl start docker
        
    elif [[ "$os_info" == *"macOS"* ]]; then
        print_status "For macOS, please install Docker Desktop manually:"
        print_status "https://docs.docker.com/desktop/mac/install/"
        print_warning "Skipping Docker installation on macOS"
        return 0
        
    else
        print_warning "Docker installation not supported on this platform"
        return 0
    fi
    
    print_success "Docker installed successfully"
}

# Function to setup Python environment
setup_python_environment() {
    print_header "Setting up Python Environment"
    
    # Create installation directory
    mkdir -p "$REDLINE_DIR"
    
    # Copy or clone REDLINE files
    if [[ -f "main.py" ]] && [[ -d "redline" ]]; then
        print_status "Copying local REDLINE files..."
        cp -r "$SOURCE_DIR"/* "$REDLINE_DIR/" 2>/dev/null || true
    else
        print_warning "REDLINE files not found locally"
        print_status "Creating basic directory structure..."
        mkdir -p "$REDLINE_DIR/redline"
        
        # Create basic main.py if it doesn't exist
        if [[ ! -f "$REDLINE_DIR/main.py" ]]; then
            cat > "$REDLINE_DIR/main.py" << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Main Application Entry Point
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        # Try to import and run REDLINE
        from redline.gui.main_window import StockAnalyzerGUI
        import tkinter as tk
        
        logger.info("Starting REDLINE GUI...")
        root = tk.Tk()
        app = StockAnalyzerGUI(root)
        root.mainloop()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Starting web interface instead...")
        
        # Fallback to web interface
        from web_app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=8080, debug=False)
        
    except Exception as e:
        logger.error(f"Error starting REDLINE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
        fi
    fi
    
    cd "$REDLINE_DIR"
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment and install packages
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install Tkinter via pip if needed
    print_status "Installing Tkinter..."
    pip install tk || print_warning "Tkinter installation failed, GUI may not work"
    
    # Install required packages
    print_status "Installing required dependencies..."
    for package in "${REQUIRED_PACKAGES[@]}"; do
        print_status "Installing $package..."
        pip install "$package" || {
            print_error "Failed to install $package"
            return 1
        }
    done
    
    # Install optional packages
    print_status "Installing optional dependencies..."
    for package in "${OPTIONAL_PACKAGES[@]}"; do
        print_status "Installing $package..."
        pip install "$package" || print_warning "Failed to install $package (optional)"
    done
    
    # Try to install additional packages if requirements.txt exists
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
    fi
    
    print_success "Python environment setup complete"
}

# Function to create startup scripts
create_startup_scripts() {
    print_header "Creating Startup Scripts"
    
    # Web app startup script
    tee "$REDLINE_DIR/start_web.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Web Interface..."

# Start the web app
source venv/bin/activate
export WEB_PORT=${WEB_PORT:-8080}
export FLASK_APP=web_app.py
export FLASK_ENV=production
python3 web_app.py
EOF

    # GUI startup script
    tee "$REDLINE_DIR/start_gui.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE GUI..."

# Check if GUI is supported
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Tkinter not available, cannot start GUI"
    echo "💡 Use start_web.sh for web interface instead"
    exit 1
fi

# Start the GUI
source venv/bin/activate
python3 main.py
EOF

    # Docker startup script
    tee "$REDLINE_DIR/start_docker.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Docker Services..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not available, cannot start Docker services"
    echo "💡 Use start_web.sh for web interface instead"
    exit 1
fi

# Check if docker-compose.yml exists
if [[ -f "docker-compose.yml" ]]; then
    docker-compose up -d
    echo "✅ REDLINE Docker services started"
    echo "🌐 Web interface: http://localhost:8080"
else
    echo "❌ docker-compose.yml not found"
    echo "💡 Use start_web.sh for web interface instead"
fi
EOF

    # Make scripts executable
    chmod +x "$REDLINE_DIR"/*.sh
    
    print_success "Startup scripts created"
}

# Function to create configuration files
create_config_files() {
    print_header "Creating Configuration Files"
    
    # Basic configuration
    tee "$REDLINE_DIR/redline.conf" > /dev/null <<EOF
# REDLINE Configuration
[DEFAULT]
data_dir = ./data
logs_dir = ./logs
web_port = 8080

[WEB]
host = 0.0.0.0
port = 8080
debug = false

[GUI]
display = :0
theme = default

[DATABASE]
db_path = ./data/redline_data.duckdb
backup_enabled = true
EOF

    # Docker configuration
    tee "$REDLINE_DIR/docker-compose.yml" > /dev/null <<EOF
version: '3.8'

services:
  redline-web:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - WEB_PORT=8080
      - FLASK_ENV=production
    restart: unless-stopped
    
  redline-gui:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DISPLAY=\${DISPLAY:-:0}
    restart: unless-stopped
EOF

    # Dockerfile
    tee "$REDLINE_DIR/Dockerfile" > /dev/null <<EOF
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    build-essential \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data logs

# Expose port
EXPOSE 8080

# Default command
CMD ["python3", "web_app.py"]
EOF

    print_success "Configuration files created"
}

# Function to create data directories
create_data_directories() {
    print_header "Creating Data Directories"
    
    mkdir -p "$REDLINE_DIR/data"
    mkdir -p "$REDLINE_DIR/logs"
    mkdir -p "$REDLINE_DIR/data/downloaded"
    mkdir -p "$REDLINE_DIR/data/converted"
    
    print_success "Data directories created"
}

# Function to run installation tests
run_tests() {
    print_header "Running Installation Tests"
    
    cd "$REDLINE_DIR"
    
    # Test Python environment
    if source venv/bin/activate && python3 --version &>/dev/null; then
        print_success "Python environment test passed"
    else
        print_error "Python environment test failed"
        return 1
    fi
    
    # Test required packages
    print_status "Testing required packages..."
    for package in "${REQUIRED_PACKAGES[@]}"; do
        package_name=$(echo "$package" | cut -d'>' -f1)
        if source venv/bin/activate && python3 -c "import $package_name" &>/dev/null; then
            print_success "$package_name test passed"
        else
            print_error "$package_name test failed"
            return 1
        fi
    done
    
    # Test REDLINE modules (if they exist)
    print_status "Testing REDLINE modules..."
    if source venv/bin/activate && python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    # Test basic imports
    import pandas
    import numpy
    import flask
    import duckdb
    import pyarrow
    import polars
    import yfinance
    print('✅ All core packages imported successfully')
    
    # Test REDLINE modules if they exist
    try:
        import redline
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        print('✅ All REDLINE modules imported successfully')
    except ImportError:
        print('⚠️  REDLINE modules not found, but core packages work')
        
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
" &>/dev/null; then
        print_success "Package import tests passed"
    else
        print_error "Package import tests failed"
        return 1
    fi
    
    print_success "All installation tests passed"
}

# Function to show installation summary
show_summary() {
    local mode=$1
    local os=$(detect_os)
    local arch=$(detect_arch)
    
    print_success "REDLINE installation completed successfully!"
    echo ""
    echo "📋 Installation Summary:"
    echo "========================"
    echo "• Mode: $mode"
    echo "• OS: $os"
    echo "• Architecture: $arch"
    echo "• User: $CURRENT_USER"
    echo "• Installation directory: $REDLINE_DIR"
    echo "• Python: $(python3 --version)"
    if command -v docker &> /dev/null; then
        echo "• Docker: $(docker --version)"
    else
        echo "• Docker: Not installed"
    fi
    echo ""
    echo "🚀 How to start REDLINE:"
    echo "========================"
    echo ""
    echo "1. Web Interface:"
    echo "   cd $REDLINE_DIR && ./start_web.sh"
    echo "   # Then open: http://localhost:8080"
    echo ""
    if [[ -f "$REDLINE_DIR/start_gui.sh" ]]; then
        echo "2. GUI Interface:"
        echo "   cd $REDLINE_DIR && ./start_gui.sh"
        echo ""
    fi
    if [[ -f "$REDLINE_DIR/start_docker.sh" ]] && command -v docker &> /dev/null; then
        echo "3. Docker Services:"
        echo "   cd $REDLINE_DIR && ./start_docker.sh"
        echo ""
    fi
    echo "📊 Access Information:"
    echo "====================="
    echo "• Web Interface: http://localhost:8080"
    echo "• Installation: $REDLINE_DIR"
    echo "• Logs: $REDLINE_DIR/logs/"
    echo "• Data: $REDLINE_DIR/data/"
    echo ""
    echo "⚠️  Important Notes:"
    echo "==================="
    echo "• You may need to log out and log back in for Docker group changes to take effect"
    echo "• Check firewall settings if you can't access the web interface"
    echo "• All files are installed in: $REDLINE_DIR"
    echo ""
    echo "🛠️  Troubleshooting:"
    echo "==================="
    echo "• If GUI doesn't work: Use web interface instead"
    echo "• If Docker doesn't work: Use bare metal installation"
    echo "• For import errors: Check Python virtual environment"
    echo "• For web access issues: Check firewall and port 8080"
}

# Main installation function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode)
                INSTALL_MODE="$2"
                shift 2
                ;;
            --user)
                CURRENT_USER="$2"
                REDLINE_DIR="/home/$CURRENT_USER/redline"
                shift 2
                ;;
            --dir)
                REDLINE_DIR="$2"
                shift 2
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-gui)
                SKIP_GUI=true
                shift
                ;;
            --web-only)
                WEB_ONLY=true
                INSTALL_MODE="web-only"
                shift
                ;;
            --docker-only)
                INSTALL_MODE="docker"
                shift
                ;;
            --bare-metal)
                INSTALL_MODE="bare-metal"
                shift
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
    
    # Determine installation mode
    local mode=$(determine_mode)
    print_header "REDLINE Universal Installation"
    print_status "Installation mode: $mode"
    
    # Pre-installation checks
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Detect OS and install system packages
    local os=$(detect_os)
    if [[ "$mode" != "docker" ]]; then
        install_system_packages
    fi
    
    # Install Docker if requested and supported
    if [[ "$SKIP_DOCKER" != "true" ]] && [[ "$mode" != "web-only" ]] && [[ "$mode" != "bare-metal" ]]; then
        install_docker
    fi
    
    # Setup Python environment
    setup_python_environment
    
    # Create data directories
    create_data_directories
    
    # Create startup scripts
    create_startup_scripts
    
    # Create configuration files
    create_config_files
    
    # Run tests
    run_tests
    
    # Show summary
    show_summary "$mode"
    
    print_success "Installation completed successfully!"
}

# Run main function
main "$@"
