#!/bin/bash

# Quick Docker Build Script for REDLINE Web Application
# Simplified version for fast builds

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
IMAGE_NAME=${1:-"redline-web"}
TAG=${2:-"latest"}
PLATFORM=${3:-"linux/amd64"}
DOCKERFILE="Dockerfile.web"

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [IMAGE_NAME] [TAG] [PLATFORM]"
    echo ""
    echo "Arguments:"
    echo "  IMAGE_NAME    Docker image name (default: redline-web)"
    echo "  TAG           Docker image tag (default: latest)"
    echo "  PLATFORM      Target platform (default: linux/amd64)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with defaults"
    echo "  $0 my-redline v1.0.0                 # Custom name and tag"
    echo "  $0 redline-web latest linux/arm64    # Build for ARM64"
    echo ""
    echo "Platform Options:"
    echo "  linux/amd64    Intel/AMD 64-bit Linux"
    echo "  linux/arm64    ARM 64-bit Linux"
    echo "  linux/arm/v7   ARM v7 Linux"
    exit 0
fi

print_status "🚀 Building REDLINE Web Application Docker Image"
print_status "Image: $IMAGE_NAME:$TAG"
print_status "Platform: $PLATFORM"
print_status "Dockerfile: $DOCKERFILE"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    print_error "Dockerfile not found: $DOCKERFILE"
    exit 1
fi

# Setup buildx if not already available
if ! docker buildx ls | grep -q "redline-builder"; then
    print_status "Setting up buildx builder..."
    docker buildx create --name redline-builder --use >/dev/null 2>&1
fi

docker buildx use redline-builder >/dev/null 2>&1

# Build the image
print_status "Building Docker image..."
docker buildx build \
    --platform "$PLATFORM" \
    --tag "$IMAGE_NAME:$TAG" \
    --file "$DOCKERFILE" \
    --load \
    .

if [ $? -eq 0 ]; then
    print_status "✅ Docker image built successfully!"
    print_status "Image: $IMAGE_NAME:$TAG"
    echo ""
    print_status "To run the container:"
    print_status "  docker run -p 8080:8080 $IMAGE_NAME:$TAG"
    echo ""
    print_status "To test the image:"
    print_status "  docker run -d -p 8080:8080 --name redline-test $IMAGE_NAME:$TAG"
    print_status "  curl http://localhost:8080/health"
    print_status "  docker stop redline-test && docker rm redline-test"
else
    print_error "❌ Docker image build failed"
    exit 1
fi
