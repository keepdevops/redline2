#!/bin/bash
set -e

# REDLINE Universal Installation Script
# Automatically detects platform, environment, and installs REDLINE accordingly

echo "🚀 REDLINE Universal Installation Script"
echo "========================================"

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
SOURCE_DIR="$(pwd)"
INSTALL_MODE="auto"  # auto, minimal, full, docker-only, web-only
PYTHON_VERSION="3.11"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --mode MODE          Installation mode: auto, minimal, full, docker-only, web-only"
    echo "  --user USER          Install for specific user (default: current user)"
    echo "  --dir DIRECTORY      Installation directory (default: ~/redline)"
    echo "  --skip-docker        Skip Docker installation"
    echo "  --skip-gui           Skip GUI components (Tkinter)"
    echo "  --web-only           Install only web interface"
    echo "  --help               Show this help message"
    echo ""
    echo "Installation Modes:"
    echo "  auto       - Automatically detect and install appropriate components"
    echo "  minimal    - Install only essential components (Python + web)"
    echo "  full       - Install everything (Python + Docker + GUI + web)"
    echo "  docker-only - Install only Docker components"
    echo "  web-only   - Install only web interface"
    echo ""
    echo "Examples:"
    echo "  $0                           # Auto-detect and install"
    echo "  $0 --mode minimal            # Minimal installation"
    echo "  $0 --mode web-only           # Web interface only"
    echo "  $0 --skip-docker             # Skip Docker installation"
    echo "  $0 --user myuser             # Install for specific user"
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

# Function to install system packages (Linux)
install_system_packages_linux() {
    local os_info=$(detect_os)
    
    print_status "Installing system packages for $os_info..."
    
    if [[ "$os_info" == *"Ubuntu"* ]] || [[ "$os_info" == *"Debian"* ]]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            curl \
            wget \
            git \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            build-essential
        
        # Try to install Tkinter packages
        sudo apt-get install -y python3-tk python3-tkinter 2>/dev/null || {
            print_warning "Tkinter packages not available, will install via pip"
        }
        
    elif [[ "$os_info" == *"CentOS"* ]] || [[ "$os_info" == *"Red Hat"* ]] || [[ "$os_info" == *"Fedora"* ]]; then
        # CentOS/RHEL/Fedora
        sudo yum update -y || sudo dnf update -y
        sudo yum install -y \
            curl \
            wget \
            git \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            tkinter || sudo dnf install -y \
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
    
    print_success "System packages installed"
}

# Function to install system packages (macOS)
install_system_packages_macos() {
    print_status "Installing system packages for macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install packages via Homebrew
    brew install python3 git curl wget
    
    print_success "System packages installed"
}

# Function to install Docker
install_docker() {
    local os_info=$(detect_os)
    
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
    print_status "Setting up Python environment..."
    
    # Create installation directory
    mkdir -p "$REDLINE_DIR"
    
    # Copy or clone REDLINE files
    if [[ -f "main.py" ]] && [[ -d "redline" ]]; then
        print_status "Copying local REDLINE files..."
        cp -r "$SOURCE_DIR"/* "$REDLINE_DIR/" 2>/dev/null || true
    else
        print_status "REDLINE files not found locally, you may need to provide them manually"
        print_warning "Creating basic directory structure..."
        mkdir -p "$REDLINE_DIR/redline"
    fi
    
    cd "$REDLINE_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install packages
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install Tkinter via pip if needed
    pip install tk || print_warning "Tkinter installation failed, GUI may not work"
    
    # Install basic requirements
    pip install flask pandas numpy matplotlib seaborn scipy scikit-learn requests
    
    # Try to install additional packages if requirements.txt exists
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi
    
    print_success "Python environment setup complete"
}

# Function to create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
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
python3 main.py --task=gui
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
    print_status "Creating configuration files..."
    
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
EOF

    print_success "Configuration files created"
}

# Function to create data directories
create_data_directories() {
    print_status "Creating data directories..."
    
    mkdir -p "$REDLINE_DIR/data"
    mkdir -p "$REDLINE_DIR/logs"
    
    print_success "Data directories created"
}

# Function to run tests
run_tests() {
    print_status "Running installation tests..."
    
    cd "$REDLINE_DIR"
    
    # Test Python environment
    if source venv/bin/activate && python3 --version &>/dev/null; then
        print_success "Python environment test passed"
    else
        print_error "Python environment test failed"
        return 1
    fi
    
    # Test Flask
    if source venv/bin/activate && python3 -c 'import flask' &>/dev/null; then
        print_success "Flask test passed"
    else
        print_warning "Flask test failed"
    fi
    
    # Test Tkinter (optional)
    if source venv/bin/activate && python3 -c 'import tkinter' &>/dev/null; then
        print_success "Tkinter test passed"
    else
        print_warning "Tkinter test failed - GUI may not work"
    fi
    
    # Test Docker (optional)
    if command -v docker &> /dev/null && docker --version &>/dev/null; then
        print_success "Docker test passed"
    else
        print_warning "Docker not available"
    fi
    
    print_success "Installation tests completed"
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
                INSTALL_MODE="web-only"
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
    print_status "Installation mode: $mode"
    
    # Pre-installation checks
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Detect OS and install system packages
    local os=$(detect_os)
    if [[ "$os" == *"Linux"* ]]; then
        install_system_packages_linux
    elif [[ "$os" == *"macOS"* ]]; then
        install_system_packages_macos
    else
        print_warning "Unsupported operating system: $os"
        print_status "Proceeding with basic installation..."
    fi
    
    # Install Docker if requested and supported
    if [[ "$SKIP_DOCKER" != "true" ]] && [[ "$mode" != "web-only" ]]; then
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
