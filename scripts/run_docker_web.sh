#!/bin/bash

# REDLINE Docker Web Mode Script
# Run REDLINE with web interface

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
    local image_name="redline:latest"
    local container_name="redline-web"
    
    # Stop and remove existing container if running
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    log "Starting REDLINE Web Interface..."
    log "Web Port: $WEB_PORT"
    
    docker run -it --rm \
        --name "$container_name" \
        --env WEB_PORT="$WEB_PORT" \
        --env MODE=web \
        --volume "$PWD/data:/app/data" \
        --volume "$PWD/logs:/app/logs" \
        --publish "$WEB_PORT:$WEB_PORT" \
        "$image_name" \
        --mode=web
}

# Show web interface info
show_web_info() {
    log_success "REDLINE Web Interface is starting!"
    echo ""
    echo "Web Interface Information:"
    echo "========================="
    echo "URL: http://localhost:$WEB_PORT"
    echo "Port: $WEB_PORT"
    echo ""
    echo "Features:"
    echo "  - Modern web-based GUI"
    echo "  - Data downloading and viewing"
    echo "  - Analysis and visualization"
    echo "  - Format conversion"
    echo "  - Real-time updates"
    echo ""
    echo "To access from another machine:"
    echo "  Replace 'localhost' with the Docker host IP address"
    echo ""
    echo "Press Ctrl+C to stop the container"
}

# Main execution
main() {
    log "REDLINE Web Docker Launcher"
    log "==========================="
    
    check_docker
    check_port
    build_image
    
    # Show web info in background
    show_web_info &
    INFO_PID=$!
    
    # Run REDLINE
    run_redline
    
    # Clean up info process
    kill $INFO_PID 2>/dev/null || true
    
    log_success "REDLINE Web session completed"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --build        Force rebuild Docker image"
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
    --build)
        docker rmi redline:latest 2>/dev/null || true
        build_image
        ;;
    --port)
        WEB_PORT="$2"
        shift 2
        ;;
esac

# Run main function
main "$@"
