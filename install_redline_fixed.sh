#!/bin/bash

# REDLINE Universal Installer Script (Fixed)
# One-install script with all implementation options for web and Tkinter GUI
# Fixed package names for different Linux distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="REDLINE"
VERSION="1.0.1"

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

print_header() {
    echo -e "${PURPLE}[INSTALLER]${NC} $1"
}

print_title() {
    echo -e "${WHITE}$1${NC}"
}

# Function to detect platform
detect_platform() {
    local os=$(uname -s)
    local arch=$(uname -m)
    
    case $os in
        Darwin)
            echo "macOS"
            ;;
        Linux)
            echo "Linux"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "Windows"
            ;;
        *)
            echo "Unknown"
            ;;
    esac
}

# Function to detect Linux distribution
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to detect architecture
detect_architecture() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system dependencies
install_system_deps() {
    local platform=$(detect_platform)
    
    print_header "Installing System Dependencies"
    
    case $platform in
        Linux)
            local distro=$(detect_linux_distro)
            case $distro in
                ubuntu|debian)
                    print_status "Installing dependencies for Ubuntu/Debian"
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip python3-tk python3-dev \
                        libgl1-mesa-glx libglib2.0-0 libxext6 libxrender1 libxtst6 libxi6
                    ;;
                centos|rhel|fedora)
                    print_status "Installing dependencies for CentOS/RHEL/Fedora"
                    sudo yum install -y python3 python3-pip tkinter python3-devel \
                        mesa-libGL glib2 libXext libXrender libXtst libXi
                    ;;
                arch|manjaro)
                    print_status "Installing dependencies for Arch/Manjaro"
                    sudo pacman -S --noconfirm python python-pip python-tkinter \
                        mesa-libgl glib2 libxext libxrender libxtst libxi
                    ;;
                *)
                    print_warning "Unknown Linux distribution: $distro"
                    print_status "Attempting to install common packages"
                    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-tk python3-dev || \
                    sudo yum install -y python3 python3-pip tkinter python3-devel || \
                    sudo pacman -S --noconfirm python python-pip python-tkinter || \
                    print_error "Could not install system dependencies"
                    ;;
            esac
            ;;
        macOS)
            print_status "Installing dependencies for macOS"
            if command_exists brew; then
                brew install python3
                # Tkinter is included with Python on macOS
            else
                print_warning "Homebrew not found. Please install Python3 manually."
            fi
            ;;
        Windows)
            print_warning "Windows detected. Please install Python3 manually."
            ;;
    esac
}

# Function to check dependencies
check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing_deps=()
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    else
        print_success "Python3 found: $(python3 --version)"
    fi
    
    # Check pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    else
        print_success "pip3 found"
    fi
    
    # Check Tkinter
    if python3 -c "import tkinter" 2>/dev/null; then
        print_success "Tkinter found"
    else
        print_warning "Tkinter not found - will install system dependencies"
        install_system_deps
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        print_success "Docker found: $(docker --version)"
    else
        print_warning "Docker not found (optional for containerized deployment)"
    fi
    
    # Check Git
    if command_exists git; then
        print_success "Git found: $(git --version)"
    else
        print_warning "Git not found (optional)"
    fi
    
    # Report missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Installing missing dependencies..."
        install_system_deps
    fi
    
    print_success "All required dependencies found"
    return 0
}

# Function to install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt"
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, installing basic dependencies"
        pip3 install pandas numpy matplotlib seaborn plotly flask requests duckdb pyarrow fastparquet
        print_success "Basic Python dependencies installed"
    fi
}

# Function to setup directories
setup_directories() {
    print_header "Setting up Directories"
    
    local dirs=("data" "logs" "config" "data/uploads" "data/user_files")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory exists: $dir"
        fi
    done
}

# Function to install web-based GUI
install_webgui() {
    print_header "Installing Web-Based GUI"
    
    # Check if Docker is available
    if ! command_exists docker; then
        print_error "Docker is required for web-based GUI"
        print_status "Please install Docker and run again"
        return 1
    fi
    
    # Use the fixed Dockerfile
    local dockerfile="Dockerfile.webgui.fixed"
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui"
    fi
    
    # Build web-based GUI image
    print_status "Building web-based GUI Docker image"
    docker build -f "$dockerfile" -t redline-webgui:latest .
    
    if [ $? -eq 0 ]; then
        print_success "Web-based GUI image built successfully"
        
        # Create startup script
        cat > start_webgui.sh << 'EOF'
#!/bin/bash
echo "Starting REDLINE Web-Based GUI..."
docker run -d \
    --name redline-webgui \
    --network host \
    -p 6080:6080 \
    -p 5901:5901 \
    -e DISPLAY=:1 \
    -e VNC_PORT=5901 \
    -e NO_VNC_PORT=6080 \
    -e VNC_RESOLUTION=1920x1080 \
    -e VNC_COL_DEPTH=24 \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/config:/app/config" \
    --restart unless-stopped \
    redline-webgui:latest

echo "Web-based GUI started!"
echo "Access at: http://localhost:6080"
echo "VNC password: redline123"
EOF
        chmod +x start_webgui.sh
        
        print_success "Web-based GUI installation complete"
        print_status "Run: ./start_webgui.sh"
        print_status "Access: http://localhost:6080"
    else
        print_error "Failed to build web-based GUI image"
        return 1
    fi
}

# Function to install Tkinter GUI with X11
install_tkinter_x11() {
    print_header "Installing Tkinter GUI with X11"
    
    local platform=$(detect_platform)
    
    case $platform in
        macOS)
            print_status "Setting up X11 for macOS"
            
            # Check if XQuartz is installed
            if [ -d "/Applications/Utilities/XQuartz.app" ]; then
                print_success "XQuartz found"
            else
                print_warning "XQuartz not found"
                print_status "Installing XQuartz via Homebrew..."
                if command_exists brew; then
                    brew install --cask xquartz
                else
                    print_error "Homebrew not found. Please install XQuartz manually:"
                    print_status "https://www.xquartz.org/"
                    return 1
                fi
            fi
            
            # Create X11 setup script
            cat > setup_x11_macos.sh << 'EOF'
#!/bin/bash
echo "Setting up X11 for macOS..."

# Start XQuartz
open -a XQuartz

# Wait for XQuartz to start
sleep 5

# Allow connections
xhost +localhost

# Set display
export DISPLAY=localhost:0

echo "X11 setup complete!"
echo "Display: $DISPLAY"
EOF
            chmod +x setup_x11_macos.sh
            
            print_success "X11 setup script created: ./setup_x11_macos.sh"
            ;;
            
        Linux)
            print_status "Setting up X11 for Linux"
            
            # Check if X11 is running
            if [ -n "$DISPLAY" ]; then
                print_success "X11 display found: $DISPLAY"
            else
                print_warning "X11 display not set"
                export DISPLAY=:0
            fi
            
            # Allow Docker X11 connections
            xhost +local:docker 2>/dev/null || true
            
            print_success "X11 setup complete"
            ;;
            
        Windows)
            print_warning "X11 on Windows requires WSL2 + VcXsrv"
            print_status "Please set up WSL2 and VcXsrv manually"
            ;;
    esac
    
    # Create Tkinter startup script
    cat > start_tkinter.sh << 'EOF'
#!/bin/bash
echo "Starting REDLINE Tkinter GUI..."

# Set display for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    export DISPLAY=localhost:0
fi

# Start Tkinter GUI
python3 main.py
EOF
    chmod +x start_tkinter.sh
    
    print_success "Tkinter GUI installation complete"
    print_status "Run: ./start_tkinter.sh"
}

# Function to install Tkinter GUI with web fallback
install_tkinter_web_fallback() {
    print_header "Installing Tkinter GUI with Web Fallback"
    
    # Install both Tkinter and web-based GUI
    install_tkinter_x11
    install_webgui
    
    # Create hybrid startup script
    cat > start_hybrid.sh << 'EOF'
#!/bin/bash
echo "Starting REDLINE Hybrid GUI..."

# Try Tkinter first
if [[ "$OSTYPE" == "darwin"* ]]; then
    export DISPLAY=localhost:0
fi

# Check if X11 is available
if [ -n "$DISPLAY" ] && [ -S "/tmp/.X11-unix/X0" ]; then
    echo "Starting Tkinter GUI..."
    python3 main.py
else
    echo "X11 not available, starting web-based GUI..."
    ./start_webgui.sh
fi
EOF
    chmod +x start_hybrid.sh
    
    print_success "Hybrid GUI installation complete"
    print_status "Run: ./start_hybrid.sh"
}

# Function to install Docker Compose setup
install_docker_compose() {
    print_header "Installing Docker Compose Setup"
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose not found"
        print_status "Please install Docker Compose and run again"
        return 1
    fi
    
    # Create Docker Compose files if they don't exist
    if [ ! -f "docker-compose.yml" ]; then
        print_status "Creating docker-compose.yml"
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redline-web:
    build: .
    container_name: redline-web
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app

  redline-webgui:
    build:
      context: .
      dockerfile: Dockerfile.webgui.fixed
    container_name: redline-webgui
    ports:
      - "6080:6080"
      - "5901:5901"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    environment:
      - DISPLAY=:1
      - VNC_PORT=5901
      - NO_VNC_PORT=6080
      - VNC_RESOLUTION=1920x1080
      - VNC_COL_DEPTH=24
    networks:
      - redline-network

networks:
  redline-network:
    driver: bridge
EOF
    fi
    
    # Create startup script
    cat > start_compose.sh << 'EOF'
#!/bin/bash
echo "Starting REDLINE with Docker Compose..."

# Start services
docker-compose up -d

echo "Services started!"
echo "Web App: http://localhost:8080"
echo "Web GUI: http://localhost:6080"
echo "VNC password: redline123"
EOF
    chmod +x start_compose.sh
    
    print_success "Docker Compose setup complete"
    print_status "Run: ./start_compose.sh"
}

# Function to install native setup
install_native() {
    print_header "Installing Native Setup"
    
    # Install Python dependencies
    install_python_deps
    
    # Setup directories
    setup_directories
    
    # Create native startup script
    cat > start_native.sh << 'EOF'
#!/bin/bash
echo "Starting REDLINE Native..."

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Start web application
python3 web_app.py
EOF
    chmod +x start_native.sh
    
    print_success "Native setup complete"
    print_status "Run: ./start_native.sh"
    print_status "Access: http://localhost:8080"
}

# Function to show main menu
show_main_menu() {
    clear
    print_title "=========================================="
    print_title "    REDLINE Universal Installer v$VERSION"
    print_title "=========================================="
    echo ""
    print_status "Platform: $(detect_platform) ($(detect_architecture))"
    if [ "$(detect_platform)" = "Linux" ]; then
        print_status "Distribution: $(detect_linux_distro)"
    fi
    echo ""
    print_title "Installation Options:"
    echo ""
    echo "1) Web-Based GUI (Recommended)"
    echo "   • Runs in web browser"
    echo "   • No X11 required"
    echo "   • Universal access"
    echo ""
    echo "2) Tkinter GUI with X11"
    echo "   • Native desktop application"
    echo "   • Requires X11 setup"
    echo "   • Best performance"
    echo ""
    echo "3) Hybrid (Tkinter + Web Fallback)"
    echo "   • Tries Tkinter first"
    echo "   • Falls back to web GUI"
    echo "   • Best of both worlds"
    echo ""
    echo "4) Docker Compose Setup"
    echo "   • Multiple services"
    echo "   • Web app + Web GUI"
    echo "   • Production ready"
    echo ""
    echo "5) Native Installation"
    echo "   • Web application only"
    echo "   • No Docker required"
    echo "   • Simple setup"
    echo ""
    echo "6) Check Dependencies"
    echo "7) Show Status"
    echo "8) Help"
    echo "0) Exit"
    echo ""
    read -p "Enter your choice [0-8]: " choice
}

# Function to show status
show_status() {
    print_header "REDLINE Status"
    
    echo ""
    print_title "Platform Information:"
    echo "• OS: $(detect_platform)"
    echo "• Architecture: $(detect_architecture)"
    if [ "$(detect_platform)" = "Linux" ]; then
        echo "• Distribution: $(detect_linux_distro)"
    fi
    echo "• Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "• Docker: $(docker --version 2>/dev/null || echo 'Not found')"
    echo "• Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not found')"
    
    echo ""
    print_title "Installed Components:"
    
    # Check web-based GUI
    if docker images redline-webgui:latest --format "{{.Repository}}:{{.Tag}}" | grep -q "redline-webgui:latest"; then
        echo "• Web-based GUI: ✅ Installed"
    else
        echo "• Web-based GUI: ❌ Not installed"
    fi
    
    # Check Tkinter GUI
    if [ -f "main.py" ]; then
        echo "• Tkinter GUI: ✅ Available"
    else
        echo "• Tkinter GUI: ❌ Not available"
    fi
    
    # Check web application
    if [ -f "web_app.py" ]; then
        echo "• Web Application: ✅ Available"
    else
        echo "• Web Application: ❌ Not available"
    fi
    
    echo ""
    print_title "Running Services:"
    
    # Check Docker containers
    if command_exists docker; then
        local containers=$(docker ps --format "{{.Names}}" | grep -i redline || true)
        if [ -n "$containers" ]; then
            echo "• Docker containers:"
            echo "$containers" | sed 's/^/  - /'
        else
            echo "• Docker containers: None running"
        fi
    fi
    
    # Check Python processes
    local python_procs=$(ps aux | grep -E "(web_app\.py|main\.py)" | grep -v grep || true)
    if [ -n "$python_procs" ]; then
        echo "• Python processes:"
        echo "$python_procs" | sed 's/^/  - /'
    else
        echo "• Python processes: None running"
    fi
}

# Function to show help
show_help() {
    print_title "REDLINE Universal Installer Help"
    echo ""
    print_title "Installation Options:"
    echo ""
    echo "1. Web-Based GUI (Recommended)"
    echo "   • Best for: Universal access, easy setup"
    echo "   • Requirements: Docker"
    echo "   • Access: Web browser"
    echo ""
    echo "2. Tkinter GUI with X11"
    echo "   • Best for: Native performance, desktop use"
    echo "   • Requirements: X11 (XQuartz on macOS)"
    echo "   • Access: Desktop application"
    echo ""
    echo "3. Hybrid (Tkinter + Web Fallback)"
    echo "   • Best for: Flexibility, automatic fallback"
    echo "   • Requirements: X11 + Docker"
    echo "   • Access: Desktop or web browser"
    echo ""
    echo "4. Docker Compose Setup"
    echo "   • Best for: Production, multiple services"
    echo "   • Requirements: Docker Compose"
    echo "   • Access: Web browser"
    echo ""
    echo "5. Native Installation"
    echo "   • Best for: Simple setup, no Docker"
    echo "   • Requirements: Python only"
    echo "   • Access: Web browser"
    echo ""
    print_title "Quick Start:"
    echo "1. Run: ./install_redline.sh"
    echo "2. Choose option 1 (Web-Based GUI)"
    echo "3. Wait for installation"
    echo "4. Run: ./start_webgui.sh"
    echo "5. Open: http://localhost:6080"
    echo ""
    print_title "Troubleshooting:"
    echo "• If you get 'python3-tkinter' error, run option 6 (Check Dependencies)"
    echo "• The installer will automatically install system dependencies"
    echo "• For Linux, it detects your distribution and installs correct packages"
    echo ""
}

# Function to handle menu choice
handle_menu_choice() {
    case $1 in
        1)
            print_header "Installing Web-Based GUI"
            if install_webgui; then
                print_success "Installation complete!"
                print_status "Run: ./start_webgui.sh"
                print_status "Access: http://localhost:6080"
            else
                print_error "Installation failed"
            fi
            ;;
        2)
            print_header "Installing Tkinter GUI with X11"
            if install_tkinter_x11; then
                print_success "Installation complete!"
                print_status "Run: ./start_tkinter.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        3)
            print_header "Installing Hybrid GUI"
            if install_tkinter_web_fallback; then
                print_success "Installation complete!"
                print_status "Run: ./start_hybrid.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        4)
            print_header "Installing Docker Compose Setup"
            if install_docker_compose; then
                print_success "Installation complete!"
                print_status "Run: ./start_compose.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        5)
            print_header "Installing Native Setup"
            if install_native; then
                print_success "Installation complete!"
                print_status "Run: ./start_native.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        6)
            check_dependencies
            ;;
        7)
            show_status
            ;;
        8)
            show_help
            ;;
        0)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

# Function to create management script
create_management_script() {
    cat > manage_redline.sh << 'EOF'
#!/bin/bash

# REDLINE Management Script
# Unified management for all REDLINE installations

case "${1:-help}" in
    start-webgui)
        ./start_webgui.sh
        ;;
    start-tkinter)
        ./start_tkinter.sh
        ;;
    start-hybrid)
        ./start_hybrid.sh
        ;;
    start-compose)
        ./start_compose.sh
        ;;
    start-native)
        ./start_native.sh
        ;;
    stop)
        docker stop $(docker ps -q --filter "name=redline") 2>/dev/null || true
        pkill -f "web_app.py" 2>/dev/null || true
        pkill -f "main.py" 2>/dev/null || true
        echo "All REDLINE services stopped"
        ;;
    status)
        ./install_redline.sh 7
        ;;
    help)
        echo "REDLINE Management Script"
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start-webgui   Start web-based GUI"
        echo "  start-tkinter  Start Tkinter GUI"
        echo "  start-hybrid   Start hybrid GUI"
        echo "  start-compose  Start Docker Compose"
        echo "  start-native   Start native web app"
        echo "  stop           Stop all services"
        echo "  status         Show status"
        echo "  help           Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        ;;
esac
EOF
    chmod +x manage_redline.sh
}

# Main function
main() {
    # Check if running interactively
    if [ -t 0 ]; then
        # Interactive mode
        while true; do
            show_main_menu
            handle_menu_choice "$choice"
            echo ""
            read -p "Press Enter to continue..."
        done
    else
        # Non-interactive mode
        case "${1:-help}" in
            webgui)
                install_webgui
                ;;
            tkinter)
                install_tkinter_x11
                ;;
            hybrid)
                install_tkinter_web_fallback
                ;;
            compose)
                install_docker_compose
                ;;
            native)
                install_native
                ;;
            status)
                show_status
                ;;
            help|--help|-h)
                show_help
                ;;
            *)
                print_error "Unknown command: $1"
                show_help
                exit 1
                ;;
        esac
    fi
}

# Create management script
create_management_script

# Run main function
main "$@"
