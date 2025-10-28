#!/bin/bash

# REDLINE Web-Based GUI Startup Script
# Starts the REDLINE web interface in a Docker container

set -e

# Colors
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is not installed"
    echo ""
    echo "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running"
    echo ""
    
    # Try to detect OS and suggest how to start Docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "To start Docker on macOS:"
        echo "  1. Open Docker Desktop"
        echo "  2. Or run: open -a Docker"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "To start Docker on Linux:"
        echo "  sudo systemctl start docker"
    else
        print_status "Please start Docker Desktop"
    fi
    
    exit 1
fi

print_success "Docker is running"

# Check if REDLINE image exists
if ! docker images redline-webgui:latest --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep -q "redline-webgui:latest"; then
    print_warning "REDLINE Docker image not found"
    echo ""
    print_status "To install REDLINE, run:"
    echo "  ./install_webgui.sh"
    echo ""
    print_status "Or run the full installer:"
    echo "  ./install_options_redline.sh"
    exit 1
fi

print_success "REDLINE Docker image found"

# Stop existing container if running
if docker ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^redline-webgui$"; then
    if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^redline-webgui$"; then
        print_status "Container already running, restarting..."
        docker stop redline-webgui >/dev/null 2>&1 || true
    fi
    docker rm redline-webgui >/dev/null 2>&1 || true
fi

# Setup directories
mkdir -p data logs config data/uploads data/user_files 2>/dev/null || true

# Generate VNC password if not set
if [ -z "$VNC_PASSWORD" ]; then
    VNC_PASSWORD=$(openssl rand -base64 12 2>/dev/null || echo "redline123")
fi

print_header "Starting REDLINE Web-Based GUI"

# Start the container
docker run -d \
    --name redline-webgui \
    -p 8080:8080 \
    -e VNC_PASSWORD="$VNC_PASSWORD" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/config:/app/config" \
    --restart unless-stopped \
    redline-webgui:latest

if [ $? -eq 0 ]; then
    echo ""
    print_header "REDLINE Started Successfully!"
    echo ""
    echo "  🌐 Web Interface: http://localhost:8080"
    echo ""
    print_status "Quick Commands:"
    echo "  View logs:   docker logs -f redline-webgui"
    echo "  Stop:        docker stop redline-webgui"
    echo "  Restart:     docker restart redline-webgui"
    echo "  Remove:      docker rm -f redline-webgui"
    echo ""
    
    # Show container status
    sleep 2
    print_status "Container status:"
    docker ps --filter name=redline-webgui --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    print_error "Failed to start REDLINE"
    echo ""
    print_status "Check the logs:"
    echo "  docker logs redline-webgui"
    exit 1
fi
