#!/bin/bash

# REDLINE Web Application Docker Build Script
# Uses Docker buildx for multi-platform builds and optimized Linux containers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_IMAGE_NAME="redline-web"
DEFAULT_TAG="latest"
DEFAULT_PLATFORM="linux/amd64"
DEFAULT_DOCKERFILE="Dockerfile.web"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE}  REDLINE Web Application Docker Build${NC}"
    echo -e "${BLUE}==============================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and buildx availability
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed or not in PATH"
        print_error "Please install Docker and try again"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_error "Please start Docker and try again"
        exit 1
    fi
    
    print_status "Docker is available and running"
    
    # Check if buildx is available
    if ! docker buildx version >/dev/null 2>&1; then
        print_error "Docker buildx is not available"
        print_error "Please update Docker to a version that supports buildx"
        exit 1
    fi
    
    print_status "Docker buildx is available"
}

# Function to setup buildx builder
setup_buildx() {
    print_status "Setting up Docker buildx builder..."
    
    # Create a new builder instance if it doesn't exist
    if ! docker buildx ls | grep -q "redline-builder"; then
        print_status "Creating new buildx builder instance..."
        docker buildx create --name redline-builder --use
    else
        print_status "Using existing buildx builder instance..."
        docker buildx use redline-builder
    fi
    
    # Bootstrap the builder
    docker buildx inspect --bootstrap
}

# Function to validate files
validate_files() {
    print_status "Validating required files..."
    
    local dockerfile=${1:-$DEFAULT_DOCKERFILE}
    
    # Check if Dockerfile exists
    if [ ! -f "$dockerfile" ]; then
        print_error "Dockerfile not found: $dockerfile"
        exit 1
    fi
    
    # Check if requirements file exists
    if [ ! -f "requirements_docker.txt" ]; then
        print_error "requirements_docker.txt not found"
        exit 1
    fi
    
    # Check if web_app.py exists
    if [ ! -f "web_app.py" ]; then
        print_error "web_app.py not found"
        exit 1
    fi
    
    # Check if redline directory exists
    if [ ! -d "redline" ]; then
        print_error "redline directory not found"
        exit 1
    fi
    
    print_status "All required files validated"
}

# Function to build Docker image
build_image() {
    local image_name=$1
    local tag=$2
    local platform=$3
    local dockerfile=$4
    local push=$5
    local no_cache=$6
    
    print_status "Building Docker image..."
    print_status "Image: $image_name:$tag"
    print_status "Platform: $platform"
    print_status "Dockerfile: $dockerfile"
    
    # Build command arguments
    local build_args=""
    if [ "$no_cache" = true ]; then
        build_args="$build_args --no-cache"
    fi
    
    if [ "$push" = true ]; then
        build_args="$build_args --push"
        print_status "Will push to registry after build"
    else
        build_args="$build_args --load"
    fi
    
    # Build the image
    docker buildx build \
        --platform "$platform" \
        --tag "$image_name:$tag" \
        --file "$dockerfile" \
        $build_args \
        .
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully!"
        
        if [ "$push" = false ]; then
            print_status "Image loaded locally: $image_name:$tag"
        fi
    else
        print_error "Docker image build failed"
        exit 1
    fi
}

# Function to test the built image
test_image() {
    local image_name=$1
    local tag=$2
    local port=$3
    
    print_status "Testing built image..."
    
    # Start container in background
    local container_id=$(docker run -d -p "$port:$port" --name "redline-test-$$" "$image_name:$tag")
    
    if [ -z "$container_id" ]; then
        print_error "Failed to start test container"
        return 1
    fi
    
    print_status "Test container started: $container_id"
    
    # Wait for container to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$container_id" curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
            print_status "Image test successful! Container is healthy."
            break
        fi
        
        print_status "Waiting for container to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Image test failed - container not responding"
        docker logs "$container_id"
        docker stop "$container_id" >/dev/null 2>&1
        docker rm "$container_id" >/dev/null 2>&1
        return 1
    fi
    
    # Clean up test container
    docker stop "$container_id" >/dev/null 2>&1
    docker rm "$container_id" >/dev/null 2>&1
    
    print_status "Test container cleaned up"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --image NAME       Docker image name (default: $DEFAULT_IMAGE_NAME)"
    echo "  -t, --tag TAG          Docker image tag (default: $DEFAULT_TAG)"
    echo "  -p, --platform PLATFORM   Target platform (default: $DEFAULT_PLATFORM)"
    echo "  -f, --file DOCKERFILE  Dockerfile path (default: $DEFAULT_DOCKERFILE)"
    echo "  --push                 Push image to registry after build"
    echo "  --no-cache             Build without using cache"
    echo "  --test                 Test the built image"
    echo "  --test-port PORT       Port for testing (default: 8080)"
    echo "  --setup-only           Only setup buildx builder"
    echo "  --clean                Clean up buildx builder"
    echo "  --help                 Show this help message"
    echo ""
    echo "Platform Options:"
    echo "  linux/amd64            Intel/AMD 64-bit Linux"
    echo "  linux/arm64            ARM 64-bit Linux"
    echo "  linux/arm/v7           ARM v7 Linux"
    echo "  linux/amd64,linux/arm64   Multi-platform build"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with defaults"
    echo "  $0 -i redline-web -t v1.0.0         # Custom name and tag"
    echo "  $0 -p linux/arm64                    # Build for ARM64"
    echo "  $0 --push --test                     # Build, push, and test"
    echo "  $0 -p linux/amd64,linux/arm64 --push # Multi-platform build and push"
}

# Function to clean up buildx builder
cleanup_buildx() {
    print_status "Cleaning up buildx builder..."
    
    if docker buildx ls | grep -q "redline-builder"; then
        docker buildx rm redline-builder
        print_status "Buildx builder removed"
    else
        print_status "No buildx builder to clean up"
    fi
}

# Main function
main() {
    local image_name=$DEFAULT_IMAGE_NAME
    local tag=$DEFAULT_TAG
    local platform=$DEFAULT_PLATFORM
    local dockerfile=$DEFAULT_DOCKERFILE
    local push=false
    local no_cache=false
    local test=false
    local test_port=8080
    local setup_only=false
    local clean=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--image)
                image_name="$2"
                shift 2
                ;;
            -t|--tag)
                tag="$2"
                shift 2
                ;;
            -p|--platform)
                platform="$2"
                shift 2
                ;;
            -f|--file)
                dockerfile="$2"
                shift 2
                ;;
            --push)
                push=true
                shift
                ;;
            --no-cache)
                no_cache=true
                shift
                ;;
            --test)
                test=true
                shift
                ;;
            --test-port)
                test_port="$2"
                shift 2
                ;;
            --setup-only)
                setup_only=true
                shift
                ;;
            --clean)
                clean=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Clean up if requested
    if [ "$clean" = true ]; then
        cleanup_buildx
        exit 0
    fi
    
    # Check Docker
    check_docker
    
    # Setup buildx
    setup_buildx
    
    # Exit early if setup-only
    if [ "$setup_only" = true ]; then
        print_status "Buildx setup completed"
        exit 0
    fi
    
    # Validate files
    validate_files "$dockerfile"
    
    # Build the image
    build_image "$image_name" "$tag" "$platform" "$dockerfile" "$push" "$no_cache"
    
    # Test the image if requested and not pushing
    if [ "$test" = true ] && [ "$push" = false ]; then
        test_image "$image_name" "$tag" "$test_port"
    fi
    
    # Show final information
    echo ""
    print_status "🎉 Docker build completed successfully!"
    print_status "Image: $image_name:$tag"
    print_status "Platform: $platform"
    
    if [ "$push" = false ]; then
        echo ""
        print_status "To run the container:"
        print_status "  docker run -p $test_port:8080 $image_name:$tag"
        echo ""
        print_status "To push to registry:"
        print_status "  docker push $image_name:$tag"
    fi
    
    if [ "$test" = false ] && [ "$push" = false ]; then
        echo ""
        print_status "To test the image:"
        print_status "  $0 --test --test-port $test_port -i $image_name -t $tag"
    fi
}

# Trap Ctrl+C to clean up
trap 'echo ""; print_status "Build interrupted"; exit 1' INT

# Run main function with all arguments
main "$@"
