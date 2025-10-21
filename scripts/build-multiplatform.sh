#!/bin/bash
# REDLINE Web GUI Multi-Platform Docker Build Script
# Supports multiple architectures and Python versions

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="redline-web-gui"
IMAGE_TAG="latest"
CONTAINER_NAME="redline-web-container"
HOST_PORT="8080"
CONTAINER_PORT="8080"
NGINX_PORT="80"

# Multi-platform configuration
PLATFORMS="linux/amd64,linux/arm64"
PYTHON_VERSIONS="3.11,3.12"
BUILDX_ENABLED=false
DOCKERFILE="Dockerfile"
BUILD_CONTEXT="."

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  REDLINE Multi-Platform Build${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -p, --platforms PLAT    Comma-separated platforms (default: linux/amd64,linux/arm64)"
    echo "  -t, --tag TAG           Image tag (default: latest)"
    echo "  -n, --name NAME         Image name (default: redline-web-gui)"
    echo "  --no-multiarch          Build for current platform only"
    echo "  --push                  Push to registry after build"
    echo "  --no-cache              Build without cache"
    echo "  --test                  Test image after build"
    echo ""
    echo "Platforms:"
    echo "  linux/amd64            Intel/AMD 64-bit"
    echo "  linux/arm64             ARM 64-bit"
    echo "  linux/arm/v7            ARM 32-bit"
    echo ""
    echo "Examples:"
    echo "  $0                      # Build for all platforms"
    echo "  $0 -p linux/amd64       # Build for AMD64 only"
    echo "  $0 --no-multiarch       # Build for current platform"
    echo "  $0 --push               # Build and push to registry"
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check Docker Buildx for multi-platform builds
    if [[ "$BUILDX_ENABLED" == true ]]; then
        if ! docker buildx version >/dev/null 2>&1; then
            print_warning "Docker Buildx not available. Multi-platform builds disabled."
            BUILDX_ENABLED=false
        else
            print_success "Docker Buildx available for multi-platform builds"
        fi
    fi
    
    # Check required files
    local required_files=("$DOCKERFILE" "requirements.txt" "web_app.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "Prerequisites check passed"
}

# Function to setup buildx
setup_buildx() {
    if [[ "$BUILDX_ENABLED" == true ]]; then
        print_step "Setting up Docker Buildx..."
        
        # Create buildx builder if it doesn't exist
        if ! docker buildx ls | grep -q "redline-builder"; then
            docker buildx create --name redline-builder --use
            print_status "Created new buildx builder: redline-builder"
        else
            docker buildx use redline-builder
            print_status "Using existing buildx builder: redline-builder"
        fi
        
        # Inspect builder
        docker buildx inspect --bootstrap
        print_success "Buildx setup completed"
    fi
}

# Function to build image
build_image() {
    print_step "Building Docker image..."
    
    # Set build arguments
    local build_args=(
        "--tag" "${IMAGE_NAME}:${IMAGE_TAG}"
        "--tag" "${IMAGE_NAME}:ubuntu-24.04-multiarch"
        "--tag" "${IMAGE_NAME}:$(date +%Y%m%d)"
        "--build-arg" "BUILDKIT_INLINE_CACHE=1"
        "--progress=plain"
    )
    
    # Add no-cache flag if requested
    if [[ "${NO_CACHE:-false}" == true ]]; then
        build_args+=("--no-cache")
    fi
    
    # Multi-platform build
    if [[ "$BUILDX_ENABLED" == true && "${NO_MULTIARCH:-false}" == false ]]; then
        print_status "Building for platforms: $PLATFORMS"
        build_args+=("--platform" "$PLATFORMS")
        
        # Add push flag if requested
        if [[ "${PUSH:-false}" == true ]]; then
            build_args+=("--push")
        fi
        
        docker buildx build "${build_args[@]}" "$BUILD_CONTEXT"
    else
        # Single platform build
        print_status "Building for current platform"
        docker build "${build_args[@]}" "$BUILD_CONTEXT"
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to test image
test_image() {
    if [[ "${TEST:-false}" == true ]]; then
        print_step "Testing Docker image..."
        
        # Test with current platform
        local test_platform="linux/amd64"
        if [[ "$(uname -m)" == "arm64" ]]; then
            test_platform="linux/arm64"
        fi
        
        print_status "Testing on platform: $test_platform"
        
        # Run a quick test
        docker run --rm \
            --name "redline-test-$(date +%s)" \
            "${IMAGE_NAME}:${IMAGE_TAG}" \
            python3 -c "
import sys
print('Python version:', sys.version)
print('Platform:', sys.platform)

# Test key libraries
libraries = ['flask', 'pandas', 'numpy', 'duckdb']
for lib in libraries:
    try:
        __import__(lib)
        print(f'✓ {lib}: Available')
    except Exception as e:
        print(f'✗ {lib}: {e}')
"
        
        if [[ $? -eq 0 ]]; then
            print_success "Image test passed"
        else
            print_error "Image test failed"
            exit 1
        fi
    fi
}

# Function to show build information
show_build_info() {
    print_step "Build Information"
    
    echo -e "${CYAN}Image Details:${NC}"
    echo "  • Name: ${IMAGE_NAME}"
    echo "  • Tag: ${IMAGE_TAG}"
    echo "  • Platforms: ${PLATFORMS}"
    echo "  • Python Versions: ${PYTHON_VERSIONS}"
    
    echo -e "\n${CYAN}Available Images:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo -e "\n${CYAN}Next Steps:${NC}"
    echo "  • Run container: ./scripts/start.sh"
    echo "  • View logs: docker logs ${CONTAINER_NAME}"
    echo "  • Stop container: ./scripts/shutdown.sh"
    
    if [[ "${PUSH:-false}" == true ]]; then
        echo -e "\n${CYAN}Registry:${NC}"
        echo "  • Images pushed to registry"
        echo "  • Pull with: docker pull ${IMAGE_NAME}:${IMAGE_TAG}"
    fi
    
    print_success "Build completed successfully!"
}

# Function to cleanup
cleanup() {
    print_step "Cleaning up..."
    
    # Remove test containers
    docker ps -a --filter "name=redline-test-" --format "{{.Names}}" | xargs -r docker rm -f
    
    # Clean up dangling images
    docker image prune -f
    
    print_success "Cleanup completed"
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -p|--platforms)
                PLATFORMS="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -n|--name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            --no-multiarch)
                NO_MULTIARCH=true
                BUILDX_ENABLED=false
                shift
                ;;
            --push)
                PUSH=true
                BUILDX_ENABLED=true
                shift
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --test)
                TEST=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Pre-build checks
    check_prerequisites
    
    # Setup buildx if needed
    if [[ "$BUILDX_ENABLED" == true ]]; then
        setup_buildx
    fi
    
    # Build image
    build_image
    
    # Test image
    test_image
    
    # Show build information
    show_build_info
    
    # Cleanup
    cleanup
    
    print_success "Multi-platform build process completed!"
}

# Run main function
main "$@"
