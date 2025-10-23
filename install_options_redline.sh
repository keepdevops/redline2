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
                    sudo apt-get update || true
                    sudo apt-get install -y python3 python3-pip python3-dev \
                        libgl1-mesa-glx libglib2.0-0 libxext6 libxrender1 libxtst6 libxi6 || true
                    # Try different Tkinter package names
                    sudo apt-get install -y python3-tk || \
                    sudo apt-get install -y python-tk || \
                    sudo apt-get install -y tkinter || \
                    print_warning "Tkinter package not found via apt, will try pip"
                    ;;
                centos|rhel|fedora)
                    print_status "Installing dependencies for CentOS/RHEL/Fedora"
                    sudo yum install -y python3 python3-pip python3-devel \
                        mesa-libGL glib2 libXext libXrender libXtst libXi || true
                    # Try different Tkinter package names
                    sudo yum install -y tkinter || \
                    sudo yum install -y python3-tk || \
                    sudo yum install -y python-tk || \
                    print_warning "Tkinter package not found via yum, will try pip"
                    ;;
                arch|manjaro)
                    print_status "Installing dependencies for Arch/Manjaro"
                    sudo pacman -S --noconfirm python python-pip \
                        mesa-libgl glib2 libxext libxrender libxtst libxi || true
                    # Try different Tkinter package names
                    sudo pacman -S --noconfirm python-tkinter || \
                    sudo pacman -S --noconfirm python-tk || \
                    sudo pacman -S --noconfirm tkinter || \
                    print_warning "Tkinter package not found via pacman, will try pip"
                    ;;
                *)
                    print_warning "Unknown Linux distribution: $distro"
                    print_status "Attempting to install common packages"
                    # Try apt first
                    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-tk python3-dev || true
                    # Try yum if apt fails
                    sudo yum install -y python3 python3-pip tkinter python3-devel || true
                    # Try pacman if yum fails
                    sudo pacman -S --noconfirm python python-pip python-tkinter || true
                    print_warning "Some packages may not have installed correctly"
                    ;;
            esac
            ;;
        macOS)
            print_status "Installing dependencies for macOS"
            if command_exists brew; then
                brew install python3 || true
                # Tkinter is included with Python on macOS
            else
                print_warning "Homebrew not found. Please install Python3 manually."
            fi
            ;;
        Windows)
            print_warning "Windows detected. Please install Python3 manually."
            ;;
    esac
    
    # Always try to install Tkinter via pip as fallback
    print_status "Installing Tkinter via pip as fallback"
    pip3 install tk || print_warning "Could not install Tkinter via pip"
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
    
    if [ -f "requirements.docker.txt" ]; then
        print_status "Installing from Docker-compatible requirements"
        pip3 install -r requirements.docker.txt || {
            print_warning "Docker requirements failed, trying main requirements"
            pip3 install -r requirements.txt || {
                print_warning "Main requirements failed, installing basic dependencies"
                pip3 install pandas numpy matplotlib seaborn plotly flask requests duckdb pyarrow fastparquet
            }
        }
        print_success "Python dependencies installed"
    elif [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt"
        pip3 install -r requirements.txt || {
            print_warning "Requirements.txt failed, installing basic dependencies"
            pip3 install pandas numpy matplotlib seaborn plotly flask requests duckdb pyarrow fastparquet
        }
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
    
    # Use the universal Dockerfile (compatible with all Docker versions)
    local dockerfile="Dockerfile.webgui.universal"
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.buildx"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.simple"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.fixed"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui"
    fi
    
    # Build web-based GUI image with version detection
    print_status "Building web-based GUI Docker image"
    
    # Check Docker version and capabilities
    local docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    local docker_major=$(echo $docker_version | cut -d. -f1)
    local docker_minor=$(echo $docker_version | cut -d. -f2)
    
    print_status "Docker version: $docker_version"
    
    # Try Buildx if Docker version supports it (20.10+)
    if [ "$docker_major" -gt 20 ] || ([ "$docker_major" -eq 20 ] && [ "$docker_minor" -ge 10 ]); then
        print_status "Using Docker Buildx (modern Docker detected)"
        
        # Enable Buildx if not already enabled
        docker buildx create --name redline-builder --use 2>/dev/null || docker buildx use redline-builder 2>/dev/null || true
        
        # Build with Buildx (without --platform for compatibility)
        docker buildx build \
            --file "$dockerfile" \
            --tag redline-webgui:latest \
            --load \
            . || {
            print_warning "Buildx failed, falling back to regular docker build"
            docker build -f "$dockerfile" -t redline-webgui:latest .
        }
    else
        print_status "Using regular docker build (older Docker detected)"
        docker build -f "$dockerfile" -t redline-webgui:latest .
    fi
    
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
# Function to install Docker Compose setup (Hybrid approach)
install_docker_compose() {
    print_header "Installing Docker Compose Setup (Hybrid Approach)"
    
    # Install Python dependencies first (from working approach)
    print_status "Installing Python dependencies..."
    local platform=$(detect_platform)
    case $platform in
        Linux)
            local distro=$(detect_linux_distro)
            case $distro in
                ubuntu|debian)
                    print_status "Installing Python dependencies for Ubuntu/Debian"
                    sudo apt update
                    sudo apt install -y python3-distutils python3-setuptools python3-pip || true
                    pip3 install setuptools || true
                    ;;
                centos|rhel|fedora)
                    print_status "Installing Python dependencies for CentOS/RHEL/Fedora"
                    sudo yum install -y python3-distutils python3-setuptools python3-pip || true
                    pip3 install setuptools || true
                    ;;
                *)
                    print_status "Installing Python dependencies via pip"
                    pip3 install setuptools || true
                    ;;
            esac
            ;;
        macOS)
            print_status "Installing Python dependencies for macOS"
            pip3 install setuptools || true
            ;;
    esac
    
    # Install Docker Compose using pip (most reliable method)
    print_status "Installing Docker Compose via pip..."
    pip3 install docker-compose || {
        print_warning "Pip installation failed, trying system package manager..."
        case $platform in
            Linux)
                case $distro in
                    ubuntu|debian)
                        sudo apt install -y docker-compose || true
                        ;;
                    centos|rhel|fedora)
                        sudo yum install -y docker-compose || true
                        ;;
                esac
                ;;
        esac
    }
    
    # Verify Docker Compose installation
    if command_exists docker-compose; then
        print_success "Docker Compose installed: $(docker-compose --version)"
    else
        print_error "Docker Compose installation failed"
        return 1
    fi
    
    # Use the working webgui installation approach (from Option 1)
    print_status "Installing web-based GUI (using working Option 1 approach)..."
    install_webgui
    
    # Create Docker Compose files using the working approach
    print_status "Creating Docker Compose configuration..."
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
# REDLINE Docker Compose Configuration (Hybrid Approach)
# Combines working webgui with Docker Compose orchestration

version: '3.8'

services:
  # REDLINE Web App + Web GUI (using working Option 1 approach)
  redline-webgui:
    build:
      context: .
      dockerfile: Dockerfile.webgui.universal
    image: redline-webgui:latest
    container_name: redline-web-app
    restart: unless-stopped
    
    # Ports
    ports:
      - "8080:8080"    # Flask web app
      - "6080:6080"    # noVNC web GUI
    
    # Environment variables
    environment:
      - FLASK_APP=web_app.py
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=8080
      - VNC_PASSWORD=redline123
      - DISPLAY=:1
      - VNC_PORT=5901
      - NO_VNC_PORT=6080
    
    # Volumes
    volumes:
      - ./data:/opt/redline/data
      - ./logs:/var/log/redline
      - ./config:/opt/redline/config
    
    # Working directory
    working_dir: /opt/redline
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.25'

# Networks
networks:
  default:
    driver: bridge
EOF
    fi
    
    # Create startup script using the working approach
    cat > start_compose.sh << 'EOF'
#!/bin/bash

# REDLINE Docker Compose Startup Script (Hybrid Approach)
# Combines working webgui with Docker Compose orchestration

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_header "STARTING REDLINE WITH DOCKER COMPOSE (HYBRID)"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose not found!"
    print_status "Please run: ./install_options_redline.sh and choose option 4"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon not running!"
    print_status "Please start Docker: sudo systemctl start docker"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found!"
    print_status "Please run: ./install_options_redline.sh and choose option 4"
    exit 1
fi

print_status "Starting REDLINE services (using working webgui approach)..."

# Start services
docker-compose up -d

# Check if services started successfully
if [ $? -eq 0 ]; then
    print_success "Services started successfully!"
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Web App:     http://localhost:8080"
    echo "  🖥️  Web GUI:     http://localhost:6080"
    echo "  🔑 VNC Password: redline123"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop:      docker-compose down"
    echo ""
    
    # Wait a moment and check service status
    sleep 5
    print_status "Checking service status..."
    docker-compose ps
else
    print_error "Failed to start services!"
    print_status "Check logs: docker-compose logs"
    exit 1
fi
EOF
    chmod +x start_compose.sh
    
    print_success "Docker Compose setup complete (Hybrid approach)"
    print_status "Run: ./start_compose.sh"
}

# Function to install working Docker Compose setup
install_working_docker_compose() {
    print_header "Installing Working Docker Compose Setup (Recommended)"
    
    # Check if Docker Compose is available
    if ! command_exists docker-compose; then
        print_error "Docker Compose is required for this option"
        print_status "Please install Docker Compose and run again"
        return 1
    fi
    
    # Check if working Docker Compose file exists
    if [ ! -f "docker-compose-working.yml" ]; then
        print_error "Working Docker Compose file not found: docker-compose-working.yml"
        print_status "Please ensure docker-compose-working.yml exists"
        return 1
    fi
    
    # Build using working Docker Compose
    print_status "Building REDLINE using working Docker Compose configuration"
    docker-compose -f docker-compose-working.yml build --no-cache --progress=plain
    
    if [ $? -eq 0 ]; then
        print_success "REDLINE built successfully using working configuration"
        
        # Create startup script for working Docker Compose
        cat > start_working_compose.sh << 'EOF'
#!/bin/bash

# REDLINE Working Docker Compose Startup Script
# Uses proven working configuration

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_header "STARTING REDLINE WITH WORKING DOCKER COMPOSE"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose not found!"
    print_status "Please run: ./install_options_redline.sh and choose option 5"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon not running!"
    print_status "Please start Docker: sudo systemctl start docker"
    exit 1
fi

# Check if docker-compose-working.yml exists
if [ ! -f "docker-compose-working.yml" ]; then
    print_error "docker-compose-working.yml not found!"
    print_status "Please run: ./install_options_redline.sh and choose option 5"
    exit 1
fi

print_status "Starting REDLINE services (using working configuration)..."

# Start services using working Docker Compose
docker-compose -f docker-compose-working.yml up -d

# Check if services started successfully
if [ $? -eq 0 ]; then
    print_success "Services started successfully!"
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Complete REDLINE: http://localhost:8080"
    echo "  📊 All features available"
    echo ""
    print_status "To view logs: docker-compose -f docker-compose-working.yml logs -f"
    print_status "To stop:      docker-compose -f docker-compose-working.yml down"
    echo ""
    
    # Wait a moment and check service status
    sleep 5
    print_status "Checking service status..."
    docker-compose -f docker-compose-working.yml ps
else
    print_error "Failed to start services!"
    print_status "Check logs: docker-compose -f docker-compose-working.yml logs"
    exit 1
fi
EOF
        chmod +x start_working_compose.sh
        
        print_success "Working Docker Compose setup complete"
        print_status "Run: ./start_working_compose.sh"
        print_status "Access: http://localhost:8080"
    else
        print_error "Failed to build REDLINE using working configuration"
        return 1
    fi
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
    echo "5) Working Docker Compose (Recommended)"
    echo "   • Uses proven working configuration"
    echo "   • Complete REDLINE web app"
    echo "   • Most reliable method"
    echo ""
    echo "6) Native Installation"
    echo "   • Web application only"
    echo "   • No Docker required"
    echo "   • Simple setup"
    echo ""
    echo "7) Check Dependencies"
    echo "8) Show Status"
    echo "9) Help"
    echo "0) Exit"
    echo ""
    read -p "Enter your choice [0-9]: " choice
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
            print_header "Installing Working Docker Compose (Recommended)"
            if install_working_docker_compose; then
                print_success "Installation complete!"
                print_status "Run: ./start_working_compose.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        6)
            print_header "Installing Native Setup"
            if install_native; then
                print_success "Installation complete!"
                print_status "Run: ./start_native.sh"
            else
                print_error "Installation failed"
            fi
            ;;
        7)
            check_dependencies
            ;;
        8)
            show_status
            ;;
        9)
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
