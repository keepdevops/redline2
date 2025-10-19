#!/bin/bash

# REDLINE Docker VNC Script
# Run REDLINE GUI with VNC server for remote access

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

# Default values
VNC_PORT=${VNC_PORT:-5900}
VNC_PASSWORD=${VNC_PASSWORD:-redline123}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_warning "Docker is not running. Please start Docker first."
        exit 1
    fi
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

# Check if VNC port is available
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$VNC_PORT "; then
        log_warning "Port $VNC_PORT is already in use."
        log "Please stop the service using this port or change VNC_PORT environment variable."
        exit 1
    fi
}

# Run REDLINE with VNC server
run_redline() {
    local image_name="redline:latest"
    local container_name="redline-vnc"
    
    # Stop and remove existing container if running
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    log "Starting REDLINE GUI with VNC server..."
    log "VNC Port: $VNC_PORT"
    log "VNC Password: $VNC_PASSWORD"
    
    docker run -it --rm \
        --name "$container_name" \
        --env VNC_PORT="$VNC_PORT" \
        --env VNC_PASSWORD="$VNC_PASSWORD" \
        --volume "$PWD/data:/app/data" \
        --volume "$PWD/logs:/app/logs" \
        --publish "$VNC_PORT:$VNC_PORT" \
        --mode=vnc \
        "$image_name" \
        --task=gui
}

# Show VNC connection info
show_connection_info() {
    log_success "REDLINE VNC server is running!"
    echo ""
    echo "Connection Information:"
    echo "======================="
    echo "VNC Server: localhost:$VNC_PORT"
    echo "Password: $VNC_PASSWORD"
    echo ""
    echo "VNC Client Options:"
    echo "  - TigerVNC: vncviewer localhost:$VNC_PORT"
    echo "  - RealVNC: vncviewer localhost:$VNC_PORT"
    echo "  - Web Browser: http://localhost:$VNC_PORT (if web VNC client available)"
    echo ""
    echo "To connect from another machine:"
    echo "  Replace 'localhost' with the Docker host IP address"
    echo ""
    echo "Press Ctrl+C to stop the container"
}

# Main execution
main() {
    log "REDLINE VNC Docker Launcher"
    log "==========================="
    
    check_docker
    check_port
    build_image
    
    # Show connection info in background
    show_connection_info &
    INFO_PID=$!
    
    # Run REDLINE
    run_redline
    
    # Clean up info process
    kill $INFO_PID 2>/dev/null || true
    
    log_success "REDLINE VNC session completed"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --build        Force rebuild Docker image"
        echo "  --port PORT    Set VNC port (default: 5900)"
        echo "  --password PASS Set VNC password (default: redline123)"
        echo ""
        echo "Environment Variables:"
        echo "  VNC_PORT       VNC server port (default: 5900)"
        echo "  VNC_PASSWORD   VNC server password (default: redline123)"
        echo ""
        echo "Example:"
        echo "  $0 --port 5901 --password mypassword"
        echo "  VNC_PORT=5901 VNC_PASSWORD=mypass $0"
        exit 0
        ;;
    --build)
        docker rmi redline:latest 2>/dev/null || true
        build_image
        ;;
    --port)
        VNC_PORT="$2"
        shift 2
        ;;
    --password)
        VNC_PASSWORD="$2"
        shift 2
        ;;
esac

# Run main function
main "$@"
