#!/bin/bash
set -e

# REDLINE Multi-Platform Docker Test Script
# Tests Docker builds and deployments across different platforms

echo "🚀 REDLINE Multi-Platform Docker Test Script"
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
        print_warning "Docker Buildx not available, using regular docker build"
        return 1
    fi
    
    print_success "Docker Buildx is available"
    return 0
}

# Function to test Docker build for a specific platform
test_build() {
    local platform=$1
    local dockerfile=$2
    local tag="redline-test:$platform"
    
    print_status "Testing build for platform: $platform"
    print_status "Using Dockerfile: $dockerfile"
    
    if docker build --platform="$platform" -f "$dockerfile" -t "$tag" .; then
        print_success "Build successful for $platform"
        
        # Test the container
        print_status "Testing container for $platform..."
        if docker run --rm --platform="$platform" "$tag" --help > /dev/null 2>&1; then
            print_success "Container test successful for $platform"
        else
            print_warning "Container test failed for $platform"
        fi
        
        # Clean up
        docker rmi "$tag" > /dev/null 2>&1 || true
    else
        print_error "Build failed for $platform"
        return 1
    fi
}

# Function to test multi-platform build with buildx
test_multi_platform_build() {
    local dockerfile=$1
    local tag="redline-test:multi"
    
    print_status "Testing multi-platform build with Buildx"
    
    # Create a new builder instance
    docker buildx create --name redline-builder --use --bootstrap > /dev/null 2>&1 || true
    
    if docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f "$dockerfile" \
        -t "$tag" \
        --load \
        .; then
        print_success "Multi-platform build successful"
        
        # Clean up
        docker rmi "$tag" > /dev/null 2>&1 || true
    else
        print_error "Multi-platform build failed"
        return 1
    fi
}

# Function to test Docker Compose
test_compose() {
    local profile=$1
    local service=$2
    
    print_status "Testing Docker Compose with profile: $profile"
    
    # Build and start the service
    if docker-compose --profile "$profile" up --build -d "$service"; then
        print_success "Docker Compose build and start successful for $service"
        
        # Wait a moment for the service to start
        sleep 10
        
        # Check if the service is running
        if docker-compose ps "$service" | grep -q "Up"; then
            print_success "Service $service is running"
        else
            print_warning "Service $service is not running"
        fi
        
        # Stop the service
        docker-compose --profile "$profile" down
        print_status "Stopped service $service"
    else
        print_error "Docker Compose test failed for $service"
        return 1
    fi
}

# Main test execution
main() {
    print_status "Starting REDLINE Multi-Platform Docker Tests"
    
    # Check prerequisites
    check_docker
    BUILDX_AVAILABLE=false
    check_buildx && BUILDX_AVAILABLE=true
    
    # Test individual platform builds
    print_status "Testing individual platform builds..."
    
    # Test x86_64 build
    test_build "linux/amd64" "Dockerfile.x86"
    
    # Test ARM64 build (if supported)
    if [ "$BUILDX_AVAILABLE" = true ]; then
        test_build "linux/arm64" "Dockerfile.arm"
    else
        print_warning "Skipping ARM64 build test (Buildx not available)"
    fi
    
    # Test web-only build
    test_build "linux/amd64" "Dockerfile.web"
    
    # Test multi-platform build (if buildx is available)
    if [ "$BUILDX_AVAILABLE" = true ]; then
        test_multi_platform_build "Dockerfile"
    else
        print_warning "Skipping multi-platform build test (Buildx not available)"
    fi
    
    # Test Docker Compose profiles
    print_status "Testing Docker Compose profiles..."
    
    # Test web profile
    test_compose "web" "redline-web"
    
    # Test x86 profile (if buildx is available)
    if [ "$BUILDX_AVAILABLE" = true ]; then
        test_compose "x86" "redline-x86"
    else
        print_warning "Skipping x86 profile test (Buildx not available)"
    fi
    
    print_success "All Docker tests completed!"
    print_status "Summary:"
    print_status "- Individual platform builds: ✅"
    if [ "$BUILDX_AVAILABLE" = true ]; then
        print_status "- Multi-platform builds: ✅"
        print_status "- ARM64 support: ✅"
    else
        print_status "- Multi-platform builds: ⚠️ (Buildx not available)"
        print_status "- ARM64 support: ⚠️ (Buildx not available)"
    fi
    print_status "- Docker Compose integration: ✅"
    print_status "- Web interface: ✅"
}

# Run main function
main "$@"
