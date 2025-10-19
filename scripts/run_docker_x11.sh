#!/bin/bash

# REDLINE Docker X11 Forwarding Script
# Run REDLINE GUI with X11 forwarding on Ubuntu

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_warning "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check X11 forwarding
check_x11() {
    if [ -z "$DISPLAY" ]; then
        log_warning "DISPLAY environment variable not set."
        log "Please run: export DISPLAY=:0"
        exit 1
    fi
    
    # Allow X11 connections from Docker
    log "Allowing X11 connections from Docker containers..."
    xhost +local:docker 2>/dev/null || {
        log_warning "xhost command not found. X11 forwarding may not work."
        log "Install xhost: sudo apt-get install x11-xserver-utils"
    }
}

# Build Docker image if needed
build_image() {
    local image_name="redline:latest"
    
    if ! docker image inspect "$image_name" >/dev/null 2>&1; then
        log "Building REDLINE Docker image..."
        docker build -t "$image_name" .
        log_success "Docker image built successfully"
    else
        log "Using existing Docker image: $image_name"
    fi
}

# Run REDLINE with X11 forwarding
run_redline() {
    local image_name="redline:latest"
    local container_name="redline-gui"
    
    # Stop and remove existing container if running
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    log "Starting REDLINE GUI with X11 forwarding..."
    
    docker run -it --rm \
        --name "$container_name" \
        --env DISPLAY="$DISPLAY" \
        --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
        --volume "$PWD/data:/app/data" \
        --volume "$PWD/logs:/app/logs" \
        --network host \
        --mode=x11 \
        "$image_name" \
        --task=gui
}

# Main execution
main() {
    log "REDLINE X11 Docker Launcher"
    log "=========================="
    
    check_docker
    check_x11
    build_image
    run_redline
    
    log_success "REDLINE GUI session completed"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --build        Force rebuild Docker image"
        echo ""
        echo "Prerequisites:"
        echo "  - Docker installed and running"
        echo "  - X11 server running (DISPLAY set)"
        echo "  - xhost allowing Docker connections"
        echo ""
        echo "Example:"
        echo "  export DISPLAY=:0"
        echo "  xhost +local:docker"
        echo "  $0"
        exit 0
        ;;
    --build)
        docker rmi redline:latest 2>/dev/null || true
        build_image
        ;;
esac

# Run main function
main "$@"
