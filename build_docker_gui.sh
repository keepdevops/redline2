#!/bin/bash

# REDLINE Tkinter GUI Docker Build Script
# Builds Docker images for AMD64 and ARM64 architectures

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
DOCKERFILE="Dockerfile.gui"
BUILD_CONTEXT="."

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
    echo -e "${PURPLE}[BUILD]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Dockerfile exists
check_dockerfile() {
    if [ ! -f "$DOCKERFILE" ]; then
        print_error "Dockerfile not found: $DOCKERFILE"
        print_error "Please ensure the Dockerfile exists in the current directory."
        exit 1
    fi
    print_success "Dockerfile found: $DOCKERFILE"
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

# Function to build for specific platform
build_platform() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    print_header "Building for platform: $platform"
    print_status "Tag: $tag"
    print_status "Dockerfile: $DOCKERFILE"
    print_status "Context: $BUILD_CONTEXT"
    
    # Build the image
    docker build \
        --platform "$platform" \
        --file "$DOCKERFILE" \
        --tag "$tag" \
        --build-arg TARGETPLATFORM="$platform" \
        --build-arg BUILDPLATFORM="$(detect_platform)" \
        --progress=plain \
        "$BUILD_CONTEXT"
    
    print_success "Built successfully: $tag"
    
    # Show image info
    print_status "Image information:"
    docker images "$tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Function to build multi-platform image
build_multi_platform() {
    local platforms="linux/amd64,linux/arm64"
    local tag="${IMAGE_NAME}:${VERSION}"
    
    print_header "Building multi-platform image"
    print_status "Platforms: $platforms"
    print_status "Tag: $tag"
    
    # Check if buildx is available
    if ! docker buildx version > /dev/null 2>&1; then
        print_error "Docker Buildx is not available. Please install Docker Buildx."
        exit 1
    fi
    
    # Create and use buildx builder
    print_status "Setting up buildx builder..."
    docker buildx create --name redline-builder --use 2>/dev/null || true
    docker buildx inspect --bootstrap
    
    # Build multi-platform image
    print_status "Building multi-platform image..."
    docker buildx build \
        --platform "$platforms" \
        --file "$DOCKERFILE" \
        --tag "$tag" \
        --build-arg TARGETPLATFORM="linux/amd64" \
        --build-arg BUILDPLATFORM="$(detect_platform)" \
        --progress=plain \
        --load \
        "$BUILD_CONTEXT"
    
    print_success "Multi-platform image built successfully: $tag"
    
    # Show image info
    print_status "Image information:"
    docker images "$tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Function to test built image
test_image() {
    local platform=$1
    local tag="${IMAGE_NAME}:${VERSION}-${platform##*/}"
    
    print_header "Testing image: $tag"
    
    # Test GUI components
    docker run --rm \
        --platform "$platform" \
        "$tag" \
        /app/test_gui.sh
    
    print_success "Image test passed: $tag"
}

# Function to show build summary
show_summary() {
    print_header "Build Summary"
    print_status "Available images:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    print_status "Next steps:"
    echo "  • Run GUI: ./run_docker_gui.sh"
    echo "  • Stop containers: ./stop_docker_gui.sh"
    echo "  • Test GUI: docker run --rm -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw ${IMAGE_NAME}:${VERSION}"
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
    echo "  build-all        Build both AMD64 and ARM64"
    echo "  test-amd64       Test AMD64 image"
    echo "  test-arm64       Test ARM64 image"
    echo "  test-all         Test all built images"
    echo "  clean            Remove all built images"
    echo "  help             Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-cache       Build without using cache"
    echo "  --push           Push to registry (multi-platform only)"
    echo "  --verbose        Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 build-amd64"
    echo "  $0 build-multi --no-cache"
    echo "  $0 test-all"
    echo ""
}

# Function to clean up images
clean_images() {
    print_header "Cleaning up images"
    
    # Remove all redline-gui images
    local images=$(docker images "${IMAGE_NAME}" --format "{{.Repository}}:{{.Tag}}")
    
    if [ -z "$images" ]; then
        print_warning "No ${IMAGE_NAME} images found to clean"
        return
    fi
    
    print_status "Removing images:"
    echo "$images"
    
    echo "$images" | xargs docker rmi -f
    print_success "Images cleaned up"
}

# Main script logic
main() {
    # Parse arguments
    local no_cache=""
    local push=""
    local verbose=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cache)
                no_cache="--no-cache"
                shift
                ;;
            --push)
                push="--push"
                shift
                ;;
            --verbose)
                verbose="--progress=plain"
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    case "${1:-help}" in
        build-amd64)
            check_docker
            check_dockerfile
            build_platform "linux/amd64"
            show_summary
            ;;
        build-arm64)
            check_docker
            check_dockerfile
            build_platform "linux/arm64"
            show_summary
            ;;
        build-multi)
            check_docker
            check_dockerfile
            build_multi_platform
            show_summary
            ;;
        build-all)
            check_docker
            check_dockerfile
            build_platform "linux/amd64"
            build_platform "linux/arm64"
            show_summary
            ;;
        test-amd64)
            check_docker
            test_image "linux/amd64"
            ;;
        test-arm64)
            check_docker
            test_image "linux/arm64"
            ;;
        test-all)
            check_docker
            test_image "linux/amd64"
            test_image "linux/arm64"
            ;;
        clean)
            check_docker
            clean_images
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
