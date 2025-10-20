#!/bin/bash
set -e

# REDLINE Multi-Platform Docker Build Script
# Builds Docker images for all supported platforms

echo "🚀 REDLINE Multi-Platform Docker Build Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        exit 1
    fi
    
    print_success "Docker is running"
}

# Function to check if Docker Buildx is available
check_buildx() {
    print_status "Checking Docker Buildx..."
    if ! docker buildx version &> /dev/null; then
        print_warning "Docker Buildx not available, will use regular docker build"
        return 1
    fi
    
    print_success "Docker Buildx is available"
    return 0
}

# Function to build Docker image for specific platform
build_platform() {
    local platform=$1
    local dockerfile=$2
    local tag="redline:$platform"
    local registry_tag=""
    
    # If registry is specified, use it
    if [ ! -z "$REGISTRY" ]; then
        registry_tag="$REGISTRY/redline:$platform"
    fi
    
    print_status "Building for platform: $platform"
    print_status "Using Dockerfile: $dockerfile"
    print_status "Tag: $tag"
    
    if [ ! -z "$registry_tag" ]; then
        print_status "Registry tag: $registry_tag"
    fi
    
    # Build the image
    if docker build --platform="$platform" -f "$dockerfile" -t "$tag" .; then
        print_success "Build successful for $platform"
        
        # Tag for registry if specified
        if [ ! -z "$registry_tag" ]; then
            docker tag "$tag" "$registry_tag"
            print_success "Tagged for registry: $registry_tag"
        fi
        
        # Show image info
        print_status "Image info:"
        docker images "$tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        
    else
        print_error "Build failed for $platform"
        return 1
    fi
}

# Function to build multi-platform image with buildx
build_multi_platform() {
    local dockerfile=$1
    local tag="redline:latest"
    local registry_tag=""
    
    # If registry is specified, use it
    if [ ! -z "$REGISTRY" ]; then
        registry_tag="$REGISTRY/redline:latest"
    fi
    
    print_status "Building multi-platform image"
    print_status "Using Dockerfile: $dockerfile"
    print_status "Tag: $tag"
    
    if [ ! -z "$registry_tag" ]; then
        print_status "Registry tag: $registry_tag"
    fi
    
    # Create a new builder instance
    docker buildx create --name redline-builder --use --bootstrap > /dev/null 2>&1 || true
    
    # Build arguments
    local build_args="--platform linux/amd64,linux/arm64 -f $dockerfile -t $tag"
    
    # Add registry tag if specified
    if [ ! -z "$registry_tag" ]; then
        build_args="$build_args -t $registry_tag"
    fi
    
    # Add push flag if registry is specified
    if [ ! -z "$REGISTRY" ] && [ "$PUSH" = "true" ]; then
        build_args="$build_args --push"
        print_status "Will push to registry: $REGISTRY"
    else
        build_args="$build_args --load"
    fi
    
    # Build the multi-platform image
    if docker buildx build $build_args .; then
        print_success "Multi-platform build successful"
        
        if [ -z "$REGISTRY" ] || [ "$PUSH" != "true" ]; then
            # Show image info
            print_status "Image info:"
            docker images "$tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        fi
        
    else
        print_error "Multi-platform build failed"
        return 1
    fi
}

# Function to build web-only image
build_web() {
    local platform=$1
    local tag="redline-web:$platform"
    local registry_tag=""
    
    # If registry is specified, use it
    if [ ! -z "$REGISTRY" ]; then
        registry_tag="$REGISTRY/redline-web:$platform"
    fi
    
    print_status "Building web-only image for platform: $platform"
    print_status "Tag: $tag"
    
    if [ ! -z "$registry_tag" ]; then
        print_status "Registry tag: $registry_tag"
    fi
    
    # Build the image
    if docker build --platform="$platform" -f Dockerfile.web -t "$tag" .; then
        print_success "Web build successful for $platform"
        
        # Tag for registry if specified
        if [ ! -z "$registry_tag" ]; then
            docker tag "$tag" "$registry_tag"
            print_success "Tagged for registry: $registry_tag"
        fi
        
        # Show image info
        print_status "Image info:"
        docker images "$tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        
    else
        print_error "Web build failed for $platform"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --platform PLATFORM    Build for specific platform (amd64, arm64, all)"
    echo "  -w, --web-only             Build web-only images"
    echo "  -m, --multi-platform       Build multi-platform images (requires buildx)"
    echo "  -r, --registry REGISTRY    Registry to tag images for"
    echo "  --push                     Push images to registry (requires -r)"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                         # Build all images for current platform"
    echo "  $0 -p amd64                # Build for x86_64 only"
    echo "  $0 -p arm64                # Build for ARM64 only"
    echo "  $0 -w                      # Build web-only images"
    echo "  $0 -m                      # Build multi-platform images"
    echo "  $0 -r myregistry.com --push # Build and push to registry"
}

# Parse command line arguments
PLATFORM=""
WEB_ONLY=false
MULTI_PLATFORM=false
REGISTRY=""
PUSH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -w|--web-only)
            WEB_ONLY=true
            shift
            ;;
        -m|--multi-platform)
            MULTI_PLATFORM=true
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main build execution
main() {
    print_status "Starting REDLINE Docker builds"
    
    # Check prerequisites
    check_docker
    BUILDX_AVAILABLE=false
    check_buildx && BUILDX_AVAILABLE=true
    
    # Build based on options
    if [ "$WEB_ONLY" = true ]; then
        print_status "Building web-only images..."
        
        if [ -z "$PLATFORM" ] || [ "$PLATFORM" = "all" ]; then
            build_web "linux/amd64"
            if [ "$BUILDX_AVAILABLE" = true ]; then
                build_web "linux/arm64"
            fi
        elif [ "$PLATFORM" = "amd64" ]; then
            build_web "linux/amd64"
        elif [ "$PLATFORM" = "arm64" ]; then
            if [ "$BUILDX_AVAILABLE" = true ]; then
                build_web "linux/arm64"
            else
                print_error "ARM64 build requires Docker Buildx"
                exit 1
            fi
        else
            print_error "Invalid platform: $PLATFORM"
            exit 1
        fi
        
    elif [ "$MULTI_PLATFORM" = true ]; then
        if [ "$BUILDX_AVAILABLE" = true ]; then
            print_status "Building multi-platform images..."
            build_multi_platform "Dockerfile"
        else
            print_error "Multi-platform builds require Docker Buildx"
            exit 1
        fi
        
    else
        print_status "Building platform-specific images..."
        
        if [ -z "$PLATFORM" ] || [ "$PLATFORM" = "all" ]; then
            build_platform "linux/amd64" "Dockerfile.x86"
            if [ "$BUILDX_AVAILABLE" = true ]; then
                build_platform "linux/arm64" "Dockerfile.arm"
            fi
        elif [ "$PLATFORM" = "amd64" ]; then
            build_platform "linux/amd64" "Dockerfile.x86"
        elif [ "$PLATFORM" = "arm64" ]; then
            if [ "$BUILDX_AVAILABLE" = true ]; then
                build_platform "linux/arm64" "Dockerfile.arm"
            else
                print_error "ARM64 build requires Docker Buildx"
                exit 1
            fi
        else
            print_error "Invalid platform: $PLATFORM"
            exit 1
        fi
    fi
    
    print_success "All Docker builds completed!"
    print_status "Built images:"
    docker images "redline*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Run main function
main "$@"
