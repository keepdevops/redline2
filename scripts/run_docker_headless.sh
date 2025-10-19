#!/bin/bash

# REDLINE Docker Headless Script
# Run REDLINE in headless mode (CLI only or with virtual display)

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

# Run REDLINE in headless mode
run_redline() {
    local image_name="redline:latest"
    local container_name="redline-headless"
    local task="${1:-cli}"
    
    # Stop and remove existing container if running
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    log "Starting REDLINE in headless mode..."
    log "Task: $task"
    
    if [ "$task" = "gui" ]; then
        log "Note: GUI will run with virtual display (Xvfb)"
        log "Use VNC mode for remote GUI access"
    fi
    
    docker run -it --rm \
        --name "$container_name" \
        --volume "$PWD/data:/app/data" \
        --volume "$PWD/logs:/app/logs" \
        --mode=headless \
        "$image_name" \
        --task="$task"
}

# Show usage information
show_usage() {
    echo "REDLINE Headless Docker Launcher"
    echo "================================="
    echo ""
    echo "Usage: $0 [task] [options]"
    echo ""
    echo "Tasks:"
    echo "  cli         Run REDLINE CLI (default)"
    echo "  gui         Run REDLINE GUI with virtual display"
    echo "  download    Download financial data"
    echo "  convert     Convert data formats"
    echo "  analyze     Perform data analysis"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --build        Force rebuild Docker image"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run CLI"
    echo "  $0 gui               # Run GUI with virtual display"
    echo "  $0 download AAPL     # Download Apple stock data"
    echo "  $0 convert           # Convert data formats"
    echo ""
    echo "Note: GUI mode uses virtual display (Xvfb)."
    echo "For remote GUI access, use VNC mode instead."
}

# Main execution
main() {
    local task="${1:-cli}"
    
    case "$task" in
        --help|-h)
            show_usage
            exit 0
            ;;
        --build)
            docker rmi redline:latest 2>/dev/null || true
            build_image
            exit 0
            ;;
    esac
    
    log "REDLINE Headless Docker Launcher"
    log "================================"
    
    check_docker
    build_image
    run_redline "$task"
    
    log_success "REDLINE headless session completed"
}

# Run main function with all arguments
main "$@"
