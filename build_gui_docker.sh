# REDLINE Tkinter GUI Multi-Platform Build Script
# Supports AMD64 and ARM64 architectures

#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="redline-gui"
VERSION="latest"
DOCKERFILE="Dockerfile.gui"

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to detect platform
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

# Function to build for specific platform
build_platform() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    print_status "Building for platform: $platform"
    print_status "Tag: $tag"
    
    docker build \
        --platform "$platform" \
        --file "$DOCKERFILE" \
        --tag "$tag" \
        --build-arg TARGETPLATFORM="$platform" \
        --build-arg BUILDPLATFORM="$(detect_platform)" \
        .
    
    print_success "Built successfully: $tag"
}

# Function to build multi-platform image
build_multi_platform() {
    local platforms="linux/amd64,linux/arm64"
    local tag="${IMAGE_NAME}:${VERSION}"
    
    print_status "Building multi-platform image"
    print_status "Platforms: $platforms"
    print_status "Tag: $tag"
    
    # Check if buildx is available
    if ! docker buildx version > /dev/null 2>&1; then
        print_error "Docker Buildx is not available. Please install Docker Buildx."
        exit 1
    fi
    
    # Create and use buildx builder
    docker buildx create --name redline-builder --use 2>/dev/null || true
    docker buildx inspect --bootstrap
    
    # Build multi-platform image
    docker buildx build \
        --platform "$platforms" \
        --file "$DOCKERFILE" \
        --tag "$tag" \
        --push \
        .
    
    print_success "Multi-platform image built successfully: $tag"
}

# Function to test GUI components
test_gui() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    print_status "Testing GUI components for platform: $platform"
    
    # Test GUI components
    docker run --rm \
        --platform "$platform" \
        -e DISPLAY=:0 \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        "$tag" \
        /app/test_gui.sh
    
    print_success "GUI components test passed for platform: $platform"
}

# Function to run GUI application
run_gui() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    print_status "Starting REDLINE GUI for platform: $platform"
    
    # Check if X11 is available
    if [ -z "$DISPLAY" ]; then
        print_warning "DISPLAY not set. Using virtual display."
        export DISPLAY=:0
    fi
    
    # Run GUI application
    docker run --rm \
        --platform "$platform" \
        -e DISPLAY="$DISPLAY" \
        -e XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}" \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v "${XAUTHORITY:-$HOME/.Xauthority}:/tmp/.X11-unix/X0:rw" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        --name "redline-gui-$(date +%s)" \
        "$tag"
}

# Function to show help
show_help() {
    echo "REDLINE Tkinter GUI Docker Build Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build-amd64      Build for AMD64 architecture"
    echo "  build-arm64      Build for ARM64 architecture"
    echo "  build-multi      Build multi-platform image"
    echo "  test-amd64       Test GUI components for AMD64"
    echo "  test-arm64       Test GUI components for ARM64"
    echo "  run-amd64        Run GUI application for AMD64"
    echo "  run-arm64        Run GUI application for ARM64"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build-amd64"
    echo "  $0 build-multi"
    echo "  $0 run-amd64"
    echo ""
}

# Main script logic
main() {
    case "${1:-help}" in
        build-amd64)
            check_docker
            build_platform "linux/amd64"
            ;;
        build-arm64)
            check_docker
            build_platform "linux/arm64"
            ;;
        build-multi)
            check_docker
            build_multi_platform
            ;;
        test-amd64)
            check_docker
            test_gui "linux/amd64"
            ;;
        test-arm64)
            check_docker
            test_gui "linux/arm64"
            ;;
        run-amd64)
            check_docker
            run_gui "linux/amd64"
            ;;
        run-arm64)
            check_docker
            run_gui "linux/arm64"
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
