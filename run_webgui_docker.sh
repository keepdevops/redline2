#!/bin/bash

# REDLINE Web-Based GUI Docker Script
# Builds and runs GUI through web browser (no X11 required)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="redline-webgui"
VERSION="latest"
CONTAINER_NAME="redline-webgui"
DOCKERFILE="Dockerfile.webgui"
COMPOSE_FILE="docker-compose.webgui.yml"
WEB_PORT="6080"
VNC_PORT="5901"

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
    echo -e "${PURPLE}[WEBGUI]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build web-based GUI image
build_webgui() {
    print_header "Building Web-Based GUI Image"
    print_status "Image: $IMAGE_NAME:$VERSION"
    print_status "Dockerfile: $DOCKERFILE"
    
    docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:$VERSION" .
    
    print_success "Web-based GUI image built successfully"
    
    # Show image info
    print_status "Image information:"
    docker images "$IMAGE_NAME:$VERSION" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Function to run web-based GUI
run_webgui() {
    print_header "Starting Web-Based GUI"
    print_status "Container: $CONTAINER_NAME"
    print_status "Web interface: http://localhost:$WEB_PORT"
    print_status "VNC server: localhost:$VNC_PORT"
    
    # Stop existing container
    if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    
    # Run container
    docker run -d \
        --name "$CONTAINER_NAME" \
        --network host \
        -p "$WEB_PORT:$WEB_PORT" \
        -p "$VNC_PORT:$VNC_PORT" \
        -e DISPLAY=:1 \
        -e VNC_PORT="$VNC_PORT" \
        -e NO_VNC_PORT="$WEB_PORT" \
        -e VNC_RESOLUTION=1920x1080 \
        -e VNC_COL_DEPTH=24 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        --restart unless-stopped \
        "$IMAGE_NAME:$VERSION"
    
    print_success "Web-based GUI started successfully"
    print_status "Access GUI at: http://localhost:$WEB_PORT"
    print_status "VNC password: redline123"
}

# Function to run with Docker Compose
run_compose() {
    print_header "Starting Web-Based GUI with Docker Compose"
    print_status "Compose file: $COMPOSE_FILE"
    
    # Stop existing services
    docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Web-based GUI started with Docker Compose"
    print_status "Access GUI at: http://localhost:$WEB_PORT"
    print_status "VNC password: redline123"
}

# Function to show status
show_status() {
    print_header "Web-Based GUI Status"
    
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        print_success "Container is running: $CONTAINER_NAME"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        print_status "Access URLs:"
        echo "  • Web GUI: http://localhost:$WEB_PORT"
        echo "  • VNC: localhost:$VNC_PORT"
        echo "  • VNC Password: redline123"
    else
        print_warning "Container is not running: $CONTAINER_NAME"
    fi
}

# Function to show logs
show_logs() {
    print_header "Web-Based GUI Logs"
    
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker logs --tail 50 -f "$CONTAINER_NAME"
    else
        print_error "Container is not running: $CONTAINER_NAME"
        exit 1
    fi
}

# Function to stop web-based GUI
stop_webgui() {
    print_header "Stopping Web-Based GUI"
    
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        print_success "Web-based GUI stopped and removed"
    else
        print_warning "Container is not running: $CONTAINER_NAME"
    fi
}

# Function to stop with Docker Compose
stop_compose() {
    print_header "Stopping Web-Based GUI with Docker Compose"
    
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Web-based GUI stopped with Docker Compose"
}

# Function to test web interface
test_webgui() {
    print_header "Testing Web-Based GUI"
    
    # Wait for container to start
    print_status "Waiting for container to start..."
    sleep 10
    
    # Test web interface
    if curl -f http://localhost:$WEB_PORT/ > /dev/null 2>&1; then
        print_success "Web interface is accessible"
        print_status "Open http://localhost:$WEB_PORT in your browser"
    else
        print_error "Web interface is not accessible"
        print_status "Check container logs: docker logs $CONTAINER_NAME"
    fi
}

# Function to show help
show_help() {
    echo "REDLINE Web-Based GUI Docker Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build            Build web-based GUI image"
    echo "  run              Run web-based GUI container"
    echo "  compose          Run with Docker Compose"
    echo "  stop             Stop web-based GUI container"
    echo "  stop-compose     Stop with Docker Compose"
    echo "  status           Show container status"
    echo "  logs             Show container logs"
    echo "  test             Test web interface"
    echo "  help             Show this help message"
    echo ""
    echo "Options:"
    echo "  --verbose        Verbose output"
    echo "  --no-cache       Build without cache"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 compose"
    echo "  $0 test"
    echo ""
    echo "Access:"
    echo "  • Web GUI: http://localhost:$WEB_PORT"
    echo "  • VNC: localhost:$VNC_PORT"
    echo "  • VNC Password: redline123"
    echo ""
}

# Main script logic
main() {
    # Parse arguments
    local verbose=""
    local no_cache=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                verbose="true"
                shift
                ;;
            --no-cache)
                no_cache="--no-cache"
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    case "${1:-help}" in
        build)
            check_docker
            build_webgui
            ;;
        run)
            check_docker
            run_webgui
            ;;
        compose)
            check_docker
            run_compose
            ;;
        stop)
            check_docker
            stop_webgui
            ;;
        stop-compose)
            check_docker
            stop_compose
            ;;
        status)
            check_docker
            show_status
            ;;
        logs)
            check_docker
            show_logs
            ;;
        test)
            check_docker
            test_webgui
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
}

# Run main function
main "$@"
