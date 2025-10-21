#!/bin/bash

# REDLINE Web GUI Docker Run Script
# Runs the redline-web-gui container

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Default values
IMAGE_NAME="redline-web-gui"
TAG="latest"
CONTAINER_NAME="redline-web-gui"
WEB_PORT="8080"
MODE="detached"

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
}

# Check if image exists
check_image() {
    if ! docker image inspect "$IMAGE_NAME:$TAG" >/dev/null 2>&1; then
        log_error "Image $IMAGE_NAME:$TAG not found"
        log "Please build the image first with: ./scripts/build_web_gui.sh"
        exit 1
    fi
    log_success "Image $IMAGE_NAME:$TAG found"
}

# Check if port is available
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$WEB_PORT "; then
        log_warning "Port $WEB_PORT is already in use"
        log "Please stop the service using this port or use --port to specify a different port"
        exit 1
    fi
    log_success "Port $WEB_PORT is available"
}

# Stop existing container
stop_existing() {
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        log "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        log_success "Existing container stopped and removed"
    fi
}

# Run the container
run_container() {
    log "Starting REDLINE Web GUI container..."
    log "Container: $CONTAINER_NAME"
    log "Image: $IMAGE_NAME:$TAG"
    log "Port: $WEB_PORT"
    log "Mode: $MODE"
    
    if [ "$MODE" = "detached" ]; then
        # Run in background
        docker run -d \
            --name "$CONTAINER_NAME" \
            --env WEB_PORT="$WEB_PORT" \
            --env MODE=web \
            --volume "$PWD/data:/opt/redline/data" \
            --volume "$PWD/logs:/var/log/redline" \
            --publish "$WEB_PORT:8080" \
            --restart unless-stopped \
            "$IMAGE_NAME:$TAG"
        
        log_success "Container started in background"
    else
        # Run in foreground
        docker run -it --rm \
            --name "$CONTAINER_NAME" \
            --env WEB_PORT="$WEB_PORT" \
            --env MODE=web \
            --volume "$PWD/data:/opt/redline/data" \
            --volume "$PWD/logs:/var/log/redline" \
            --publish "$WEB_PORT:8080" \
            "$IMAGE_NAME:$TAG"
    fi
}

# Show container information
show_info() {
    log_success "REDLINE Web GUI is running!"
    echo ""
    echo "Container Information:"
    echo "====================="
    echo "Container Name: $CONTAINER_NAME"
    echo "Image: $IMAGE_NAME:$TAG"
    echo "Port: $WEB_PORT"
    echo "Mode: $MODE"
    echo ""
    echo "Web Interface:"
    echo "============="
    echo "URL: http://localhost:$WEB_PORT"
    echo ""
    echo "Management Commands:"
    echo "==================="
    echo "View logs:    docker logs $CONTAINER_NAME"
    echo "Stop:         docker stop $CONTAINER_NAME"
    echo "Remove:       docker rm $CONTAINER_NAME"
    echo "Restart:      docker restart $CONTAINER_NAME"
    echo "Shell access: docker exec -it $CONTAINER_NAME /bin/bash"
    echo ""
    echo "To access from another machine:"
    echo "  Replace 'localhost' with this machine's IP address"
}

# Main function
main() {
    log "REDLINE Web GUI Runner"
    log "====================="
    
    check_docker
    check_image
    check_port
    stop_existing
    run_container
    
    if [ "$MODE" = "detached" ]; then
        show_info
    fi
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --port)
            WEB_PORT="$2"
            shift 2
            ;;
        --foreground|-f)
            MODE="foreground"
            shift
            ;;
        --detached|-d)
            MODE="detached"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --image NAME       Image name (default: redline-web-gui)"
            echo "  --tag TAG          Image tag (default: latest)"
            echo "  --name NAME        Container name (default: redline-web-gui)"
            echo "  --port PORT        Web port (default: 8080)"
            echo "  --foreground, -f   Run in foreground (default: detached)"
            echo "  --detached, -d     Run in background (default)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run with defaults"
            echo "  $0 --port 8081                       # Use port 8081"
            echo "  $0 --foreground                       # Run in foreground"
            echo "  $0 --image my-redline --tag v1.0     # Custom image"
            echo ""
            echo "Prerequisites:"
            echo "  - Docker must be running"
            echo "  - Image must be built with: ./scripts/build_web_gui.sh"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
