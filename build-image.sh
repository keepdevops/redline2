#!/bin/bash
set -e

# Build script for REDLINE Docker images
# Usage: ./build-image.sh [OPTIONS]
#
# Examples:
#   ./build-image.sh                     # Build web image with defaults
#   ./build-image.sh --all               # Build all images
#   ./build-image.sh --type license      # Build license server image
#   ./build-image.sh --type celery       # Build celery worker image
#   ./build-image.sh -t v1.0.0 --all     # Build all with version tag

# Default values
IMAGE_PREFIX="redline"
IMAGE_TAG="latest"
BUILD_TYPE="web"
PLATFORM=""
PUSH=false
NO_CACHE=false
BUILD_ALL=false

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    echo "REDLINE Docker Image Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --type TYPE           Image type to build: web, license, celery, simple (default: web)"
    echo "  --all                 Build all images (web, license, celery)"
    echo "  -t, --tag TAG         Image tag (default: latest)"
    echo "  -p, --platform PLAT   Target platform (e.g., linux/amd64, linux/arm64)"
    echo "  --push                Push images to registry after build"
    echo "  --no-cache            Build without using cache"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Image Types:"
    echo "  web       Main Flask web application (dockerfiles/Dockerfile.web)"
    echo "  license   License server (dockerfiles/Dockerfile.license-server)"
    echo "  celery    Celery worker (dockerfiles/Dockerfile.celery)"
    echo "  simple    Simple Python image (dockerfiles/Dockerfile.ultra-simple)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build web image"
    echo "  $0 --all                              # Build all images"
    echo "  $0 --type license -t v1.0.0           # Build license server with version"
    echo "  $0 --all -t v1.0.0 --push             # Build all and push to registry"
    echo "  $0 -p linux/arm64                     # Build for ARM64 (Apple Silicon)"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        --all)
            BUILD_ALL=true
            shift
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$(dirname "$0")"

# Get build date for labels
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build a single image
build_image() {
    local type=$1
    local dockerfile=""
    local image_name=""

    case $type in
        web)
            dockerfile="dockerfiles/Dockerfile.web"
            image_name="${IMAGE_PREFIX}-web"
            ;;
        license)
            dockerfile="dockerfiles/Dockerfile.license-server"
            image_name="${IMAGE_PREFIX}-license-server"
            ;;
        celery)
            dockerfile="dockerfiles/Dockerfile.celery"
            image_name="${IMAGE_PREFIX}-celery"
            ;;
        simple)
            dockerfile="dockerfiles/Dockerfile.ultra-simple"
            image_name="${IMAGE_PREFIX}"
            ;;
        *)
            log_error "Unknown image type: $type"
            echo "Valid types: web, license, celery, simple"
            exit 1
            ;;
    esac

    if [[ ! -f "$dockerfile" ]]; then
        log_error "Dockerfile not found: $dockerfile"
        exit 1
    fi

    log_info "Building ${image_name}:${IMAGE_TAG}"
    log_info "  Dockerfile: ${dockerfile}"
    [[ -n "$PLATFORM" ]] && log_info "  Platform:   ${PLATFORM}"

    # Build arguments
    BUILD_ARGS=(
        "-t" "${image_name}:${IMAGE_TAG}"
        "-f" "${dockerfile}"
        "--build-arg" "BUILD_DATE=${BUILD_DATE}"
        "--build-arg" "VERSION=${IMAGE_TAG}"
    )

    [[ -n "$PLATFORM" ]] && BUILD_ARGS+=("--platform" "$PLATFORM")
    [[ "$NO_CACHE" == true ]] && BUILD_ARGS+=("--no-cache")

    # Execute build
    docker build "${BUILD_ARGS[@]}" .

    log_success "Built ${image_name}:${IMAGE_TAG}"

    # Push if requested
    if [[ "$PUSH" == true ]]; then
        log_info "Pushing ${image_name}:${IMAGE_TAG}..."
        docker push "${image_name}:${IMAGE_TAG}"
        log_success "Pushed ${image_name}:${IMAGE_TAG}"
    fi
}

# Main execution
echo ""
echo "=========================================="
echo "  REDLINE Docker Build"
echo "=========================================="
echo ""

if [[ "$BUILD_ALL" == true ]]; then
    log_info "Building all images..."
    echo ""

    for type in web license celery; do
        build_image "$type"
        echo ""
    done

    log_success "All images built successfully!"
else
    build_image "$BUILD_TYPE"
fi

echo ""
echo "=========================================="
echo "  Build Complete"
echo "=========================================="
echo ""

if [[ "$BUILD_ALL" == true ]]; then
    echo "Built images:"
    echo "  - ${IMAGE_PREFIX}-web:${IMAGE_TAG}"
    echo "  - ${IMAGE_PREFIX}-license-server:${IMAGE_TAG}"
    echo "  - ${IMAGE_PREFIX}-celery:${IMAGE_TAG}"
    echo ""
    echo "To start all services:"
    echo "  docker-compose -f dockerfiles/docker-compose.full.yml up -d"
else
    case $BUILD_TYPE in
        web)
            echo "To run the web application:"
            echo "  docker run -p 8080:8080 ${IMAGE_PREFIX}-web:${IMAGE_TAG}"
            ;;
        license)
            echo "To run the license server:"
            echo "  docker run -p 5001:5001 ${IMAGE_PREFIX}-license-server:${IMAGE_TAG}"
            ;;
        celery)
            echo "To run celery worker (requires Redis):"
            echo "  docker run --network redline-network ${IMAGE_PREFIX}-celery:${IMAGE_TAG}"
            ;;
        simple)
            echo "To run the container:"
            echo "  docker run -p 8080:8080 ${IMAGE_PREFIX}:${IMAGE_TAG}"
            ;;
    esac
fi
echo ""
