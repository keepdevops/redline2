#!/bin/bash

# REDLINE Multi-Platform Docker Build Script
# Builds and pushes optimized images for AMD64 and ARM64 simultaneously
# Creates multi-platform manifests for seamless deployment

set -e

# Configuration
IMAGE_NAME="keepdevops/redline"
VERSION="v1.0.0-multiplatform"
PLATFORMS="linux/amd64,linux/arm64"

echo "🚀 REDLINE MULTI-PLATFORM BUILD"
echo "==============================="
echo ""
echo "📦 Building for platforms: ${PLATFORMS}"
echo "🏷️ Image: ${IMAGE_NAME}:${VERSION}"
echo "🏗️ Builder: multiplatform"
echo ""

# Ensure multiplatform builder is active
echo "🔧 Setting up multi-platform builder..."
docker buildx use multiplatform
docker buildx inspect --bootstrap

echo ""
echo "🏗️ BUILDING OPTIMIZED MULTI-PLATFORM IMAGE"
echo "==========================================="
echo ""

# Build and push optimized multi-platform image
echo "📦 Building optimized variant (recommended for production)..."
docker buildx build \
    --platform ${PLATFORMS} \
    -f Dockerfile.webgui.simple \
    -t ${IMAGE_NAME}:${VERSION}-optimized \
    -t ${IMAGE_NAME}:optimized \
    -t ${IMAGE_NAME}:latest \
    --push \
    .

echo ""
echo "🏗️ BUILDING ULTRA-SLIM MULTI-PLATFORM IMAGE"
echo "============================================"
echo ""

# Build and push ultra-slim multi-platform image (experimental)
echo "📦 Building ultra-slim variant (all dependencies)..."
docker buildx build \
    --platform ${PLATFORMS} \
    -f Dockerfile.webgui.ultra-slim \
    -t ${IMAGE_NAME}:${VERSION}-ultra-slim \
    -t ${IMAGE_NAME}:ultra-slim \
    --push \
    .

echo ""
echo "🏗️ BUILDING COMPILED MULTI-PLATFORM IMAGE"
echo "=========================================="
echo ""

# Build and push compiled multi-platform image
echo "📦 Building compiled variant (20% faster startup)..."
docker buildx build \
    --platform ${PLATFORMS} \
    -f Dockerfile.webgui.compiled \
    -t ${IMAGE_NAME}:${VERSION}-compiled \
    -t ${IMAGE_NAME}:compiled \
    --push \
    .

echo ""
echo "✅ MULTI-PLATFORM BUILD COMPLETE!"
echo "================================="
echo ""
echo "🎯 Available Images:"
echo "  • ${IMAGE_NAME}:latest (optimized, multi-platform)"
echo "  • ${IMAGE_NAME}:optimized (production ready)"
echo "  • ${IMAGE_NAME}:ultra-slim (all dependencies)"
echo "  • ${IMAGE_NAME}:compiled (20% faster startup)"
echo ""
echo "🚀 Usage Examples:"
echo ""
echo "# Automatic platform detection with persistent data (recommended):"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:latest"
echo ""
echo "# Specific variants with data persistence:"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:optimized"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:ultra-slim"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:compiled"
echo ""
echo "📊 Platform Support:"
echo "  ✅ AMD64 (Intel/Dell machines)"
echo "  ✅ ARM64 (Apple Silicon M1/M2/M3)"
echo "  🔄 Automatic detection and deployment"
echo ""
echo "🎉 Multi-platform deployment ready!"
