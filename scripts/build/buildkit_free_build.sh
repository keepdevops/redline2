#!/bin/bash

# REDLINE Web GUI - BuildKit-Free Docker Build
# This script completely avoids BuildKit issues

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

# Completely disable BuildKit
disable_buildkit() {
    log "Disabling BuildKit completely..."
    
    # Unset all BuildKit environment variables
    unset DOCKER_BUILDKIT
    unset COMPOSE_DOCKER_CLI_BUILD
    unset BUILDKIT_PROGRESS
    
    # Set legacy build mode
    export DOCKER_BUILDKIT=0
    export COMPOSE_DOCKER_CLI_BUILD=0
    
    # Disable BuildKit in Docker daemon config if possible
    if [ -f ~/.docker/config.json ]; then
        log "Checking Docker config for BuildKit settings..."
        if grep -q "buildkit" ~/.docker/config.json; then
            log_warning "BuildKit found in Docker config. Consider removing it."
        fi
    fi
    
    log_success "BuildKit disabled"
}

# Use the pre-created simplified files
check_simple_files() {
    log "Checking for simplified Docker files..."
    
    if [ ! -f "dockerfiles/Dockerfile.simple" ]; then
        log_error "dockerfiles/Dockerfile.simple not found. Please ensure it exists."
        exit 1
    fi
    
    if [ ! -f "requirements-simple.txt" ]; then
        log_error "requirements-simple.txt not found. Please ensure it exists."
        exit 1
    fi
    
    log_success "Simplified files found"
}

# Build with legacy Docker
build_legacy() {
    log "Building with legacy Docker (no BuildKit)..."
    
    # Use the simple Dockerfile from dockerfiles directory
    docker build \
        --file dockerfiles/Dockerfile.simple \
        --tag "$IMAGE_NAME:$TAG" \
        --tag "$IMAGE_NAME:latest" \
        --tag "$IMAGE_NAME:$(date +%Y%m%d)" \
        .
    
    log_success "Legacy build completed"
}

# Test the image
test_image() {
    log "Testing the built image..."
    
    # Test if image exists
    if ! docker image inspect "$IMAGE_NAME:$TAG" >/dev/null 2>&1; then
        log_error "Image $IMAGE_NAME:$TAG not found"
        return 1
    fi
    
    # Test if image can start
    log "Testing image startup..."
    local test_container="redline-test-$(date +%s)"
    
    if docker run --rm --name "$test_container" "$IMAGE_NAME:$TAG" python3 --version >/dev/null 2>&1; then
        log_success "Image test passed"
    else
        log_warning "Image test failed, but image was built"
    fi
}

# Cleanup
cleanup() {
    log "Cleaning up temporary files..."
    # Keep Dockerfile.simple and requirements-simple.txt for future use
    log_success "Cleanup completed"
}

# Show build information
show_build_info() {
    log_success "Build completed successfully!"
    echo ""
    echo "Build Information:"
    echo "=================="
    echo "Image Name: $IMAGE_NAME"
    echo "Tags: $IMAGE_NAME:$TAG, $IMAGE_NAME:latest, $IMAGE_NAME:$(date +%Y%m%d)"
    echo "Build Method: Legacy Docker (No BuildKit)"
    echo ""
    echo "Available Images:"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo "To run the web interface:"
    echo "  docker run -d --name redline-web-gui -p 8080:8080 $IMAGE_NAME:$TAG"
    echo ""
    echo "To access the web interface:"
    echo "  http://localhost:8080"
}

# Main build function
main() {
    log "REDLINE Web GUI - BuildKit-Free Builder"
    log "======================================="
    
    disable_buildkit
    check_simple_files
    build_legacy
    test_image
    cleanup
    show_build_info
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --name NAME        Image name (default: redline-web-gui)"
            echo "  --tag TAG          Image tag (default: latest)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "This script completely avoids BuildKit by:"
            echo "  - Disabling all BuildKit environment variables"
            echo "  - Using a simple Dockerfile without BuildKit features"
            echo "  - Using legacy Docker build process"
            echo ""
            echo "Perfect for systems with BuildKit issues!"
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
