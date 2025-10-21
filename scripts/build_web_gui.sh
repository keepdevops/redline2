#!/bin/bash

# REDLINE Web GUI Docker Build Script
# Simple build without BuildKit for HP AMD64 Ubuntu compatibility

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
PLATFORM="linux/amd64"
BUILD_CONTEXT="."

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
}

# Clean up old images
cleanup_images() {
    log "Cleaning up old images..."
    
    # Remove old containers
    docker ps -aq --filter "name=redline-web" | xargs -r docker rm -f 2>/dev/null || true
    
    # Remove old images (optional)
    if [ "$CLEAN_BUILD" = "true" ]; then
        docker images -q "$IMAGE_NAME" | xargs -r docker rmi -f 2>/dev/null || true
        log_success "Old images cleaned up"
    fi
}

# Build the Docker image
build_image() {
    log "Building REDLINE Web GUI Docker image..."
    log "Image: $IMAGE_NAME:$TAG"
    log "Platform: $PLATFORM"
    
    # Disable BuildKit to avoid buildx issues
    export DOCKER_BUILDKIT=0
    export COMPOSE_DOCKER_CLI_BUILD=0
    
    # Build command
    docker build \
        --platform "$PLATFORM" \
        --tag "$IMAGE_NAME:$TAG" \
        --tag "$IMAGE_NAME:latest" \
        --tag "$IMAGE_NAME:$(date +%Y%m%d)" \
        --file Dockerfile \
        "$BUILD_CONTEXT"
    
    log_success "Docker image built successfully"
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

# Show build information
show_build_info() {
    log_success "Build completed successfully!"
    echo ""
    echo "Build Information:"
    echo "=================="
    echo "Image Name: $IMAGE_NAME"
    echo "Tags: $IMAGE_NAME:$TAG, $IMAGE_NAME:latest, $IMAGE_NAME:$(date +%Y%m%d)"
    echo "Platform: $PLATFORM"
    echo "Build Context: $BUILD_CONTEXT"
    echo ""
    echo "Available Images:"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo "To run the web interface:"
    echo "  docker run -d --name redline-web -p 8080:8080 $IMAGE_NAME:$TAG"
    echo ""
    echo "To access the web interface:"
    echo "  http://localhost:8080"
}

# Main build function
main() {
    log "REDLINE Web GUI Docker Builder"
    log "=============================="
    
    check_docker
    cleanup_images
    build_image
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
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --clean)
            CLEAN_BUILD="true"
            shift
            ;;
        --context)
            BUILD_CONTEXT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --name NAME        Image name (default: redline-web-gui)"
            echo "  --tag TAG          Image tag (default: latest)"
            echo "  --platform PLATFORM Platform to build for (default: linux/amd64)"
            echo "  --clean            Clean old images before building"
            echo "  --context PATH     Build context path (default: .)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Build with defaults"
            echo "  $0 --clean                           # Clean build"
            echo "  $0 --tag v1.0 --platform linux/arm64 # Custom tag and platform"
            echo "  $0 --name my-redline --tag dev       # Custom name and tag"
            echo ""
            echo "Environment Variables:"
            echo "  DOCKER_BUILDKIT=0  Disable BuildKit (set automatically)"
            echo "  COMPOSE_DOCKER_CLI_BUILD=0  Disable Compose BuildKit (set automatically)"
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
