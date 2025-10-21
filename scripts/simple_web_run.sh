#!/bin/bash

# Simple REDLINE Web GUI Runner for HP AMD64 Ubuntu
# This avoids BuildKit issues

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
WEB_PORT=${WEB_PORT:-8080}
IMAGE_NAME="redline-web-simple"

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_warning "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Build simple Docker image without BuildKit
build_simple_image() {
    log "Building simple REDLINE Docker image..."
    
    # Disable BuildKit for this build
    export DOCKER_BUILDKIT=0
    export COMPOSE_DOCKER_CLI_BUILD=0
    
    docker build -t "$IMAGE_NAME" .
    log_success "Simple Docker image built successfully"
}

# Check if web port is available
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$WEB_PORT "; then
        log_warning "Port $WEB_PORT is already in use."
        log "Please stop the service using this port or change WEB_PORT environment variable."
        exit 1
    fi
}

# Run REDLINE with web interface
run_redline() {
    local container_name="redline-web-simple"
    
    # Stop and remove existing container if running
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    log "Starting REDLINE Web Interface..."
    log "Web Port: $WEB_PORT"
    
    docker run -d \
        --name "$container_name" \
        --env WEB_PORT="$WEB_PORT" \
        --env MODE=web \
        --volume "$PWD/data:/opt/redline/data" \
        --volume "$PWD/logs:/var/log/redline" \
        --publish "$WEB_PORT:8080" \
        "$IMAGE_NAME"
    
    log_success "REDLINE Web Interface started!"
    log "Container name: $container_name"
    log "Access URL: http://localhost:$WEB_PORT"
}

# Show web interface info
show_web_info() {
    log_success "REDLINE Web Interface is running!"
    echo ""
    echo "Web Interface Information:"
    echo "========================="
    echo "URL: http://localhost:$WEB_PORT"
    echo "Port: $WEB_PORT"
    echo "Container: redline-web-simple"
    echo ""
    echo "To access from another machine:"
    echo "  Replace 'localhost' with the HP machine's IP address"
    echo ""
    echo "To stop the container:"
    echo "  docker stop redline-web-simple"
    echo ""
    echo "To view logs:"
    echo "  docker logs redline-web-simple"
}

# Main execution
main() {
    log "REDLINE Simple Web Launcher for HP AMD64"
    log "========================================"
    
    check_docker
    check_port
    build_simple_image
    run_redline
    show_web_info
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --rebuild      Force rebuild Docker image"
        echo "  --port PORT    Set web port (default: 8080)"
        echo ""
        echo "Environment Variables:"
        echo "  WEB_PORT       Web server port (default: 8080)"
        echo ""
        echo "Example:"
        echo "  $0 --port 8081"
        echo "  WEB_PORT=8081 $0"
        exit 0
        ;;
    --rebuild)
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
        build_simple_image
        ;;
    --port)
        WEB_PORT="$2"
        shift 2
        ;;
esac

# Run main function
main "$@"
