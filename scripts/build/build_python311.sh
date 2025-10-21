#!/bin/bash

# REDLINE Web GUI - Python 3.11.14 Build Script
# Builds with Python 3.11.14 as requested

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
TAG="python311"

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
    
    log_success "BuildKit disabled"
}

# Check for Python 3.11.14 files
check_python311_files() {
    log "Checking for Python 3.11.14 files..."
    
    # Get the project root directory
    PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
    
    if [ ! -f "$PROJECT_ROOT/dockerfiles/Dockerfile.python311" ]; then
        log_error "dockerfiles/Dockerfile.python311 not found at $PROJECT_ROOT/dockerfiles/Dockerfile.python311"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_ROOT/requirements-python311.txt" ]; then
        log_error "requirements-python311.txt not found at $PROJECT_ROOT/requirements-python311.txt"
        exit 1
    fi
    
    log_success "Python 3.11.14 files found"
}

# Build with Python 3.11.14
build_python311() {
    log "Building with Python 3.11.14..."
    
    # Get the project root directory
    PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
    
    # Change to project root directory for build context
    cd "$PROJECT_ROOT"
    
    # Use the Python 3.11.14 Dockerfile
    docker build \
        --file dockerfiles/Dockerfile.python311 \
        --tag "$IMAGE_NAME:$TAG" \
        --tag "$IMAGE_NAME:python311" \
        --tag "$IMAGE_NAME:latest" \
        --tag "$IMAGE_NAME:$(date +%Y%m%d)" \
        .
    
    log_success "Python 3.11.14 build completed"
}

# Test the image
test_image() {
    log "Testing the built image..."
    
    # Test if image exists
    if ! docker image inspect "$IMAGE_NAME:$TAG" >/dev/null 2>&1; then
        log_error "Image $IMAGE_NAME:$TAG not found"
        return 1
    fi
    
    # Test if image can start and show Python version
    log "Testing Python 3.11.14..."
    local test_container="redline-test-$(date +%s)"
    
    if docker run --rm --name "$test_container" "$IMAGE_NAME:$TAG" python3.11 --version >/dev/null 2>&1; then
        log_success "Python 3.11.14 test passed"
    else
        log_warning "Python 3.11.14 test failed, but image was built"
    fi
}

# Show build information
show_build_info() {
    log_success "Python 3.11.14 build completed successfully!"
    echo ""
    echo "Build Information:"
    echo "=================="
    echo "Image Name: $IMAGE_NAME"
    echo "Tags: $IMAGE_NAME:$TAG, $IMAGE_NAME:python311, $IMAGE_NAME:latest, $IMAGE_NAME:$(date +%Y%m%d)"
    echo "Python Version: 3.11.14"
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
    echo ""
    echo "To verify Python version:"
    echo "  docker run --rm $IMAGE_NAME:$TAG python3.11 --version"
}

# Main build function
main() {
    log "REDLINE Web GUI - Python 3.11.14 Builder"
    log "=========================================="
    
    disable_buildkit
    check_python311_files
    build_python311
    test_image
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
            echo "  --tag TAG          Image tag (default: python311)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "This script builds REDLINE with Python 3.11.14 as requested."
            echo "It completely avoids BuildKit and uses legacy Docker build."
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
