#!/bin/bash
# REDLINE Web GUI Multi-Distribution Docker Build Script
# Supports multiple Linux distributions and architectures

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
BUILD_CONTEXT="."

# Multi-distribution configuration
DISTRIBUTIONS=(
    "ubuntu:24.04"
    "alpine:3.19"
    "centos:stream9"
    "rockylinux:9"
    "debian:12-slim"
    "archlinux:latest"
    "fedora:40"
    "opensuse/tumbleweed"
)

# Multi-platform configuration
PLATFORMS="linux/amd64,linux/arm64"
BUILDX_ENABLED=false
PUSH_TO_REGISTRY=false

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  REDLINE Multi-Distribution Build${NC}"
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
    echo "  -d, --distro DISTRO     Specific distribution (ubuntu, alpine, centos, rocky, debian, arch, fedora, opensuse)"
    echo "  -p, --platforms PLAT    Comma-separated platforms (default: linux/amd64,linux/arm64)"
    echo "  -t, --tag TAG           Image tag (default: latest)"
    echo "  -n, --name NAME         Image name (default: redline-web-gui)"
    echo "  --all-distros           Build for all distributions"
    echo "  --no-multiarch          Build for current platform only"
    echo "  --push                  Push to registry after build"
    echo "  --no-cache              Build without cache"
    echo "  --test                  Test image after build"
    echo ""
    echo "Distributions:"
    echo "  ubuntu                  Ubuntu 24.04 LTS"
    echo "  alpine                  Alpine Linux 3.19"
    echo "  centos                  CentOS Stream 9"
    echo "  rocky                   Rocky Linux 9"
    echo "  debian                  Debian 12 Slim"
    echo "  arch                    Arch Linux Latest"
    echo "  fedora                  Fedora 40"
    echo "  opensuse                OpenSUSE Tumbleweed"
    echo ""
    echo "Platforms:"
    echo "  linux/amd64            Intel/AMD 64-bit"
    echo "  linux/arm64             ARM 64-bit"
    echo "  linux/arm/v7            ARM 32-bit"
    echo ""
    echo "Examples:"
    echo "  $0 -d alpine            # Build Alpine Linux image"
    echo "  $0 --all-distros        # Build all distributions"
    echo "  $0 -d ubuntu -p linux/amd64  # Build Ubuntu for AMD64 only"
    echo "  $0 --all-distros --push # Build and push all distributions"
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
    local required_files=("requirements.txt" "web_app.py")
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
        if ! docker buildx ls | grep -q "redline-multidist-builder"; then
            docker buildx create --name redline-multidist-builder --use
            print_status "Created new buildx builder: redline-multidist-builder"
        else
            docker buildx use redline-multidist-builder
            print_status "Using existing buildx builder: redline-multidist-builder"
        fi
        
        # Inspect builder
        docker buildx inspect --bootstrap
        print_success "Buildx setup completed"
    fi
}

# Function to get Dockerfile path for distribution
get_dockerfile_path() {
    local distro="$1"
    case "$distro" in
        "ubuntu")
            echo "Dockerfile"
            ;;
        "alpine")
            echo "dockerfiles/Dockerfile.alpine"
            ;;
        "centos")
            echo "dockerfiles/Dockerfile.centos"
            ;;
        "rocky")
            echo "dockerfiles/Dockerfile.rocky"
            ;;
        "debian")
            echo "dockerfiles/Dockerfile.debian"
            ;;
        "arch")
            echo "dockerfiles/Dockerfile.arch"
            ;;
        "fedora")
            echo "dockerfiles/Dockerfile.fedora"
            ;;
        "opensuse")
            echo "dockerfiles/Dockerfile.opensuse"
            ;;
        *)
            print_error "Unknown distribution: $distro"
            exit 1
            ;;
    esac
}

# Function to build image for specific distribution
build_distribution() {
    local distro="$1"
    local dockerfile_path=$(get_dockerfile_path "$distro")
    
    print_step "Building $distro image..."
    
    # Check if Dockerfile exists
    if [[ ! -f "$dockerfile_path" ]]; then
        print_error "Dockerfile not found: $dockerfile_path"
        return 1
    fi
    
    # Set build arguments
    local build_args=(
        "--file" "$dockerfile_path"
        "--tag" "${IMAGE_NAME}:${IMAGE_TAG}-${distro}"
        "--tag" "${IMAGE_NAME}:${distro}-latest"
        "--tag" "${IMAGE_NAME}:${distro}-$(date +%Y%m%d)"
        "--build-arg" "BUILDKIT_INLINE_CACHE=1"
        "--progress=plain"
    )
    
    # Add no-cache flag if requested
    if [[ "${NO_CACHE:-false}" == true ]]; then
        build_args+=("--no-cache")
    fi
    
    # Multi-platform build
    if [[ "$BUILDX_ENABLED" == true && "${NO_MULTIARCH:-false}" == false ]]; then
        print_status "Building $distro for platforms: $PLATFORMS"
        build_args+=("--platform" "$PLATFORMS")
        
        # Add push flag if requested
        if [[ "${PUSH_TO_REGISTRY}" == true ]]; then
            build_args+=("--push")
        fi
        
        docker buildx build "${build_args[@]}" "$BUILD_CONTEXT"
    else
        # Single platform build
        print_status "Building $distro for current platform"
        docker build "${build_args[@]}" "$BUILD_CONTEXT"
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "$distro image built successfully"
    else
        print_error "Failed to build $distro image"
        return 1
    fi
}

# Function to test image
test_image() {
    local distro="$1"
    
    if [[ "${TEST:-false}" == true ]]; then
        print_step "Testing $distro image..."
        
        # Test with current platform
        local test_platform="linux/amd64"
        if [[ "$(uname -m)" == "arm64" ]]; then
            test_platform="linux/arm64"
        fi
        
        print_status "Testing $distro on platform: $test_platform"
        
        # Run a quick test
        docker run --rm \
            --name "redline-test-${distro}-$(date +%s)" \
            "${IMAGE_NAME}:${IMAGE_TAG}-${distro}" \
            python3 -c "
import sys
print('Python version:', sys.version)
print('Platform:', sys.platform)
print('Distribution:', '${distro}')

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
            print_success "$distro image test passed"
        else
            print_error "$distro image test failed"
            return 1
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
    echo "  • Distributions: ${DISTRIBUTIONS[*]}"
    
    echo -e "\n${CYAN}Available Images:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo -e "\n${CYAN}Distribution-Specific Images:${NC}"
    for distro in "${DISTRIBUTIONS[@]}"; do
        local distro_name=$(echo "$distro" | cut -d: -f1 | sed 's/.*\///')
        echo "  • ${IMAGE_NAME}:${IMAGE_TAG}-${distro_name}"
    done
    
    echo -e "\n${CYAN}Next Steps:${NC}"
    echo "  • Run specific distro: docker run -p 8080:8080 ${IMAGE_NAME}:${IMAGE_TAG}-alpine"
    echo "  • Compare sizes: docker images ${IMAGE_NAME}"
    echo "  • Test performance: docker run --rm ${IMAGE_NAME}:${IMAGE_TAG}-ubuntu python3 -c 'import time; print(time.time())'"
    
    if [[ "${PUSH_TO_REGISTRY}" == true ]]; then
        echo -e "\n${CYAN}Registry:${NC}"
        echo "  • Images pushed to registry"
        echo "  • Pull with: docker pull ${IMAGE_NAME}:${IMAGE_TAG}-ubuntu"
    fi
    
    print_success "Multi-distribution build completed successfully!"
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
    local specific_distro=""
    local build_all_distros=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -d|--distro)
                specific_distro="$2"
                shift 2
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
            --all-distros)
                build_all_distros=true
                shift
                ;;
            --no-multiarch)
                NO_MULTIARCH=true
                BUILDX_ENABLED=false
                shift
                ;;
            --push)
                PUSH_TO_REGISTRY=true
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
    
    # Build images
    if [[ "$build_all_distros" == true ]]; then
        print_step "Building all distributions..."
        for distro in "${DISTRIBUTIONS[@]}"; do
            local distro_name=$(echo "$distro" | cut -d: -f1 | sed 's/.*\///')
            build_distribution "$distro_name"
            test_image "$distro_name"
        done
    elif [[ -n "$specific_distro" ]]; then
        print_step "Building specific distribution: $specific_distro"
        build_distribution "$specific_distro"
        test_image "$specific_distro"
    else
        print_error "Please specify --all-distros or --distro DISTRO"
        show_usage
        exit 1
    fi
    
    # Show build information
    show_build_info
    
    # Cleanup
    cleanup
    
    print_success "Multi-distribution build process completed!"
}

# Run main function
main "$@"
