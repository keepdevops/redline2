#!/bin/bash

# REDLINE Multi-Platform Docker Build Script - Uncompiled Version
# Builds and pushes uncompiled images for AMD64 and ARM64 simultaneously
# Creates multi-platform manifests for development and debugging

set -e

# Configuration
IMAGE_NAME="keepdevops/redline"
VERSION="v1.0.0-multiplatform"
PLATFORMS="linux/amd64,linux/arm64"

echo "🚀 REDLINE MULTI-PLATFORM BUILD - UNCOMPILED VERSION"
echo "===================================================="
echo ""
echo "📦 Building for platforms: ${PLATFORMS}"
echo "🏷️ Image: ${IMAGE_NAME}:${VERSION}"
echo "🏗️ Builder: multiplatform"
echo "🔧 Type: Uncompiled (Development/Debug)"
echo ""

# Ensure multiplatform builder is active
echo "🔧 Setting up multi-platform builder..."
docker buildx use multiplatform 2>/dev/null || {
    echo "Creating multiplatform builder..."
    docker buildx create --name multiplatform --bootstrap --use
}
docker buildx inspect --bootstrap

echo ""
echo "🏗️ BUILDING UNCOMPILED MULTI-PLATFORM IMAGE"
echo "==========================================="
echo ""

# Build and push uncompiled multi-platform image
echo "📦 Building uncompiled variant (for development and debugging)..."
docker buildx build \
    --platform ${PLATFORMS} \
    -f Dockerfile.webgui.uncompiled \
    -t ${IMAGE_NAME}:${VERSION}-uncompiled \
    -t ${IMAGE_NAME}:uncompiled \
    -t ${IMAGE_NAME}:dev \
    -t ${IMAGE_NAME}:debug \
    --push \
    .

echo ""
echo "✅ UNCOMPILED MULTI-PLATFORM BUILD COMPLETE!"
echo "============================================="
echo ""
echo "🎯 Available Images:"
echo "  • ${IMAGE_NAME}:uncompiled (multi-platform, unoptimized)"
echo "  • ${IMAGE_NAME}:dev (development alias)"
echo "  • ${IMAGE_NAME}:debug (debugging alias)"
echo "  • ${IMAGE_NAME}:${VERSION}-uncompiled (versioned)"
echo ""
echo "🚀 Usage Examples:"
echo ""
echo "# Development with source code access (recommended for debugging):"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:uncompiled"
echo ""
echo "# Development with local source mounting:"
echo "docker run -d -p 8080:8080 -v \$(pwd):/app -v redline-data:/app/data ${IMAGE_NAME}:dev"
echo ""
echo "# Debug mode with verbose logging:"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${IMAGE_NAME}:debug"
echo ""
echo "📊 Platform Support:"
echo "  ✅ AMD64 (Intel/Dell machines)"
echo "  ✅ ARM64 (Apple Silicon M1/M2/M3)"
echo "  🔄 Automatic detection and deployment"
echo ""
echo "🔧 Development Features:"
echo "  ✅ No bytecode compilation (easier debugging)"
echo "  ✅ Source files preserved"
echo "  ✅ Development environment settings"
echo "  ✅ Gunicorn reload enabled"
echo "  ✅ Debug logging level"
echo "  ✅ Relaxed worker settings"
echo ""
echo "⚠️  Development Notice:"
echo "  • This image is NOT optimized for production"
echo "  • Use for development and debugging only"
echo "  • For production, use :optimized or :compiled variants"
echo ""
echo "🎉 Uncompiled multi-platform deployment ready!"
