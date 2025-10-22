#!/bin/bash

# REDLINE Tkinter GUI Docker Run Script
# Runs Docker containers with proper X11 forwarding and volume mounting

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
IMAGE_NAME="redline-gui"
VERSION="latest"
CONTAINER_NAME="redline-gui-container"
DATA_DIR="./data"
LOGS_DIR="./logs"
CONFIG_DIR="./config"

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
    echo -e "${PURPLE}[RUN]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if image exists
check_image() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    if ! docker images "$tag" --format "{{.Repository}}:{{.Tag}}" | grep -q "$tag"; then
        print_error "Image not found: $tag"
        print_error "Please build the image first using: ./build_docker_gui.sh build-$platform"
        exit 1
    fi
    print_success "Image found: $tag"
}

# Function to detect current platform
detect_platform() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "linux/amd64"
            ;;
        aarch64|arm64)
            echo "linux/arm64"
            ;;
        *)
            print_error "Unsupported architecture: $arch"
            exit 1
            ;;
    esac
}

# Function to setup X11 forwarding
setup_x11() {
    print_header "Setting up X11 forwarding"
    
    # Check if DISPLAY is set
    if [ -z "$DISPLAY" ]; then
        print_warning "DISPLAY not set. Setting to :0"
        export DISPLAY=:0
    fi
    
    print_status "Display: $DISPLAY"
    
    # Check X11 socket
    if [ ! -S "/tmp/.X11-unix/X0" ]; then
        print_warning "X11 socket not found at /tmp/.X11-unix/X0"
        print_warning "Make sure X11 server is running"
    else
        print_success "X11 socket found"
    fi
    
    # Check XAUTHORITY
    if [ -z "$XAUTHORITY" ]; then
        export XAUTHORITY="$HOME/.Xauthority"
        print_status "Set XAUTHORITY to: $XAUTHORITY"
    fi
    
    # Allow X11 connections (Linux)
    if command -v xhost > /dev/null 2>&1; then
        xhost +local:docker 2>/dev/null || true
        print_success "X11 connections allowed for Docker"
    fi
}

# Function to create directories
create_directories() {
    print_header "Creating directories"
    
    local dirs=("$DATA_DIR" "$LOGS_DIR" "$CONFIG_DIR")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory exists: $dir"
        fi
    done
}

# Function to stop existing container
stop_existing_container() {
    if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
        print_success "Existing container removed"
    fi
}

# Function to run GUI container
run_gui() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    local interactive=${2:-true}
    
    print_header "Starting REDLINE GUI"
    print_status "Platform: $platform"
    print_status "Image: $tag"
    print_status "Container: $CONTAINER_NAME"
    
    # Stop existing container
    stop_existing_container
    
    # Prepare Docker run command
    local docker_cmd="docker run"
    
    if [ "$interactive" = "true" ]; then
        docker_cmd="$docker_cmd -it"
    else
        docker_cmd="$docker_cmd -d"
    fi
    
    docker_cmd="$docker_cmd --rm"
    docker_cmd="$docker_cmd --name $CONTAINER_NAME"
    docker_cmd="$docker_cmd --platform $platform"
    docker_cmd="$docker_cmd --network host"
    
    # Environment variables
    docker_cmd="$docker_cmd -e DISPLAY=$DISPLAY"
    docker_cmd="$docker_cmd -e XAUTHORITY=$XAUTHORITY"
    docker_cmd="$docker_cmd -e PYTHONPATH=/app"
    docker_cmd="$docker_cmd -e PYTHONUNBUFFERED=1"
    
    # Volume mounts
    docker_cmd="$docker_cmd -v $(pwd)/$DATA_DIR:/app/data"
    docker_cmd="$docker_cmd -v $(pwd)/$LOGS_DIR:/app/logs"
    docker_cmd="$docker_cmd -v $(pwd)/$CONFIG_DIR:/app/config"
    docker_cmd="$docker_cmd -v /tmp/.X11-unix:/tmp/.X11-unix:rw"
    
    if [ -f "$XAUTHORITY" ]; then
        docker_cmd="$docker_cmd -v $XAUTHORITY:/tmp/.X11-unix/X0:rw"
    fi
    
    # Security options
    docker_cmd="$docker_cmd --security-opt no-new-privileges:true"
    
    # Resource limits
    docker_cmd="$docker_cmd --memory=2g"
    docker_cmd="$docker_cmd --cpus=2.0"
    
    # Image and command
    docker_cmd="$docker_cmd $tag"
    
    print_status "Running command: $docker_cmd"
    
    # Execute the command
    eval "$docker_cmd"
}

# Function to run GUI in background
run_gui_background() {
    local platform=$1
    
    print_header "Starting REDLINE GUI in background"
    run_gui "$platform" "false"
    
    print_success "GUI started in background"
    print_status "Container: $CONTAINER_NAME"
    print_status "View logs: docker logs $CONTAINER_NAME"
    print_status "Stop container: ./stop_docker_gui.sh"
}

# Function to show container status
show_status() {
    print_header "Container Status"
    
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        print_success "Container is running: $CONTAINER_NAME"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_warning "Container is not running: $CONTAINER_NAME"
    fi
}

# Function to show logs
show_logs() {
    print_header "Container Logs"
    
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker logs --tail 50 -f "$CONTAINER_NAME"
    else
        print_error "Container is not running: $CONTAINER_NAME"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "REDLINE Tkinter GUI Docker Run Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  run-amd64       Run GUI for AMD64 architecture"
    echo "  run-arm64       Run GUI for ARM64 architecture"
    echo "  run-auto        Run GUI for current platform"
    echo "  background      Run GUI in background"
    echo "  status          Show container status"
    echo "  logs            Show container logs"
    echo "  help            Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-x11        Skip X11 setup"
    echo "  --no-dirs       Skip directory creation"
    echo "  --verbose       Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 run-amd64"
    echo "  $0 run-auto"
    echo "  $0 background"
    echo "  $0 logs"
    echo ""
}

# Main script logic
main() {
    # Parse arguments
    local skip_x11=""
    local skip_dirs=""
    local verbose=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-x11)
                skip_x11="true"
                shift
                ;;
            --no-dirs)
                skip_dirs="true"
                shift
                ;;
            --verbose)
                verbose="true"
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    case "${1:-help}" in
        run-amd64)
            check_docker
            check_image "linux/amd64"
            [ "$skip_x11" != "true" ] && setup_x11
            [ "$skip_dirs" != "true" ] && create_directories
            run_gui "linux/amd64"
            ;;
        run-arm64)
            check_docker
            check_image "linux/arm64"
            [ "$skip_x11" != "true" ] && setup_x11
            [ "$skip_dirs" != "true" ] && create_directories
            run_gui "linux/arm64"
            ;;
        run-auto)
            local platform=$(detect_platform)
            check_docker
            check_image "$platform"
            [ "$skip_x11" != "true" ] && setup_x11
            [ "$skip_dirs" != "true" ] && create_directories
            run_gui "$platform"
            ;;
        background)
            local platform=$(detect_platform)
            check_docker
            check_image "$platform"
            [ "$skip_x11" != "true" ] && setup_x11
            [ "$skip_dirs" != "true" ] && create_directories
            run_gui_background "$platform"
            ;;
        status)
            check_docker
            show_status
            ;;
        logs)
            check_docker
            show_logs
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
