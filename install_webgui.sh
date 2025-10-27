#!/bin/bash

# REDLINE Web-Based GUI Installer
# Standalone installer for web-based GUI option
# Runs entirely in Docker - does not modify your system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect platform
detect_platform() {
    local os=$(uname -s)
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

# Function to show banner
show_banner() {
    echo -e "${PURPLE}"
    echo "=========================================="
    echo "    REDLINE Web-Based GUI Installer"
    echo "    Version $VERSION"
    echo "=========================================="
    echo -e "${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed"
        print_status "Please install Docker from: https://www.docker.com/get-started"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_status "Please start Docker and run this script again"
        exit 1
    fi
    print_success "Docker daemon is running"
    
    # Check for required files (in priority order)
    local dockerfiles=(
        "Dockerfile.webgui"
        "Dockerfile.webgui.universal"
        "Dockerfile.webgui.buildx"
        "Dockerfile.webgui.simple"
        "Dockerfile.webgui.fixed"
    )
    
    local found_dockerfile=""
    for dockerfile in "${dockerfiles[@]}"; do
        if [ -f "$dockerfile" ]; then
            found_dockerfile="$dockerfile"
            break
        fi
    done
    
    if [ -z "$found_dockerfile" ]; then
        print_error "No Dockerfile found for web-based GUI"
        exit 1
    fi
    
    print_success "Dockerfile found: $found_dockerfile"
    
    # Setup directories
    print_status "Setting up directories"
    mkdir -p data logs config data/uploads data/user_files
    print_success "Directories ready"
    
    return 0
}

# Function to install web-based GUI
install_webgui() {
    print_header "Installing Web-Based GUI"
    
    # Check if prune flag was passed (check all arguments)
    local prune_flag=""
    if [[ " $@ " =~ " --prune " ]]; then
        prune_flag="--prune"
    fi
    
    # Determine which Dockerfile to use
    # Try Dockerfile.webgui.simple first (no VNC - just Flask web app)
    local dockerfile="Dockerfile.webgui.simple"
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.universal"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.buildx"
    fi
    if [ ! -f "$dockerfile" ]; then
        dockerfile="Dockerfile.webgui.fixed"
    fi
    
    print_status "Using Dockerfile: $dockerfile"
    
    # Clean up old REDLINE container if it exists
    if docker ps -a --filter "name=redline-webgui" --format "{{.Names}}" | grep -q "^redline-webgui$"; then
        print_status "Removing old REDLINE container..."
        docker stop redline-webgui 2>/dev/null || true
        docker rm redline-webgui 2>/dev/null || true
    fi
    
    # Prune build cache (keeps images but removes unused build cache)
    print_status "Cleaning up Docker build cache..."
    docker builder prune -f || true
    
    # Optionally prune unused images if --prune flag is used
    if [[ "$prune_flag" == "--prune" ]]; then
        print_status "Cleaning up unused Docker images (this may free up disk space)..."
        docker image prune -f || true
        print_success "Docker cleanup complete"
    fi
    
    # Build web-based GUI image with version detection
    print_status "Building web-based GUI Docker image..."
    
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
        
        # Build with Buildx
        print_status "Building image (this may take a few minutes)..."
        docker buildx build \
            --file "$dockerfile" \
            --tag redline-webgui:latest \
            --load \
            . || {
            print_warning "Buildx failed, falling back to regular docker build"
            print_status "Building image (this may take a few minutes)..."
            docker build -f "$dockerfile" -t redline-webgui:latest .
        }
    else
        print_status "Using regular docker build (older Docker detected)"
        print_status "Building image (this may take a few minutes)..."
        docker build -f "$dockerfile" -t redline-webgui:latest .
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Web-based GUI image built successfully"
        
        # Create startup script
        print_status "Creating startup script..."
        cat > start_webgui.sh << 'EOF'
#!/bin/bash

# REDLINE Web-Based GUI Startup Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_header "STARTING REDLINE WEB-BASED GUI"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running!"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if image exists
if ! docker images redline-webgui:latest --format "{{.Repository}}:{{.Tag}}" | grep -q "redline-webgui:latest"; then
    echo "❌ REDLINE image not found!"
    echo "Please run: ./install_webgui.sh"
    exit 1
fi

# Stop existing container if running
if docker ps -a --format "{{.Names}}" | grep -q "^redline-webgui$"; then
    print_status "Stopping existing container..."
    docker stop redline-webgui >/dev/null 2>&1 || true
    docker rm redline-webgui >/dev/null 2>&1 || true
fi

print_status "Starting REDLINE Web-Based GUI..."
docker run -d \
    --name redline-webgui \
    --network host \
    -p 8080:8080 \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/config:/app/config" \
    --restart unless-stopped \
    redline-webgui:latest

if [ $? -eq 0 ]; then
    echo ""
    print_success "REDLINE Web-Based GUI started!"
    echo ""
    print_header "Access Information"
    echo "  🌐 Web Interface: http://localhost:8080"
    echo ""
    print_status "To view logs: docker logs -f redline-webgui"
    print_status "To stop:      docker stop redline-webgui"
    print_status "To restart:   docker restart redline-webgui"
    echo ""
else
    echo "❌ Failed to start REDLINE Web-Based GUI"
    echo "Check the logs: docker logs redline-webgui"
    exit 1
fi
EOF
        chmod +x start_webgui.sh
        
        print_success "Startup script created: ./start_webgui.sh"
        
        echo ""
        print_header "Installation Complete!"
        echo ""
        print_status "To start REDLINE Web-Based GUI:"
        echo "  ./start_webgui.sh"
        echo ""
        print_status "Then access it at:"
        echo "  http://localhost:8080"
        echo ""
    else
        print_error "Failed to build web-based GUI image"
        return 1
    fi
}

# Function to show status
show_status() {
    print_header "REDLINE Status"
    
    echo ""
    echo "Platform: $(detect_platform)"
    echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "Docker: $(docker --version 2>/dev/null || echo 'Not found')"
    
    echo ""
    echo "Installed Components:"
    
    # Check web-based GUI
    if docker images redline-webgui:latest --format "{{.Repository}}:{{.Tag}}" | grep -q "redline-webgui:latest"; then
        echo "  ✅ Web-based GUI image installed"
    else
        echo "  ❌ Web-based GUI image not installed"
    fi
    
    # Check if container is running
    if docker ps --format "{{.Names}}" | grep -q "^redline-webgui$"; then
        echo "  ✅ Container is running"
    else
        echo "  ⏸️  Container is not running"
    fi
    
    echo ""
}

# Function to show help
show_help() {
    cat << EOF
REDLINE Web-Based GUI Installer

This installer sets up REDLINE to run in your web browser using Docker.
It does not modify your operating system - everything runs in containers.

Installation:
    ./install_webgui.sh
    ./install_webgui.sh --prune   # Install with full Docker cleanup

Start REDLINE:
    ./start_webgui.sh

Access REDLINE:
    Open your browser to: http://localhost:6080

Manage REDLINE:
    View logs:   docker logs -f redline-webgui
    Stop:        docker stop redline-webgui
    Start:       docker start redline-webgui
    Restart:     docker restart redline-webgui
    Remove:      docker rm -f redline-webgui

Status:
    ./install_webgui.sh status

Prerequisites:
    - Docker must be installed and running
    - No other system requirements

Features:
    ✅ Runs in web browser
    ✅ No X11 required
    ✅ Does not modify your system
    ✅ Easy to remove (just delete container)
    ✅ Automatic restart on reboot

Troubleshooting:
    If Docker is not running:
        Start Docker and run this script again
    
    If image build fails:
        Check Docker logs: docker system events
    
    If port 6080 is in use:
        Stop other services on that port
        Or modify the startup script to use a different port

EOF
}

# Main function
main() {
    show_banner
    
    case "${1:-install}" in
        install|--prune)
            check_prerequisites
            install_webgui "$@"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
