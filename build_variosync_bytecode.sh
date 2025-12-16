#!/bin/bash

# VarioSync Docker Build Script - Bytecode + Minification
# Builds optimized production image with bytecode compilation and asset minification

set -e

# Configuration
IMAGE_NAME="keepdevops/variosync"
VERSION="v2.1.0-bytecode"
TAG_BYTECODE="${IMAGE_NAME}:bytecode"
TAG_LATEST="${IMAGE_NAME}:latest"
TAG_VERSION="${IMAGE_NAME}:${VERSION}"

echo "🚀 VARIOSYNC DOCKER BUILD - BYTECODE + MINIFICATION"
echo "===================================================="
echo ""
echo "📦 Image: ${IMAGE_NAME}"
echo "🏷️  Tags: ${TAG_BYTECODE}, ${TAG_LATEST}, ${TAG_VERSION}"
echo "🔧 Dockerfile: Dockerfile.webgui.bytecode"
echo "⚡ Optimizations: Bytecode compilation + JS/CSS minification"
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile.webgui.bytecode" ]; then
    echo "❌ Error: Dockerfile.webgui.bytecode not found!"
    exit 1
fi

# Build the image
echo "🏗️  Building VarioSync bytecode-optimized image..."
echo ""

docker build \
    -f Dockerfile.webgui.bytecode \
    -t ${TAG_BYTECODE} \
    -t ${TAG_LATEST} \
    -t ${TAG_VERSION} \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD SUCCESSFUL!"
    echo "==================="
    echo ""
    echo "📦 Built Images:"
    echo "  • ${TAG_BYTECODE}"
    echo "  • ${TAG_LATEST}"
    echo "  • ${TAG_VERSION}"
    echo ""
    
    # Show image size
    echo "📊 Image Size:"
    docker images ${IMAGE_NAME} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -4
    echo ""
    
    echo "🚀 Usage Examples:"
    echo ""
    echo "# Run locally:"
    echo "docker run -d -p 8080:8080 --name variosync-web ${TAG_BYTECODE}"
    echo ""
    echo "# Run with persistent data:"
    echo "docker run -d -p 8080:8080 \\"
    echo "  -v variosync-data:/app/data \\"
    echo "  -v variosync-logs:/app/logs \\"
    echo "  --name variosync-web ${TAG_BYTECODE}"
    echo ""
    echo "# Run with environment variables:"
    echo "docker run -d -p 8080:8080 \\"
    echo "  -e FLASK_ENV=production \\"
    echo "  -e GUNICORN_WORKERS=2 \\"
    echo "  -e STRIPE_SECRET_KEY=your_key \\"
    echo "  --name variosync-web ${TAG_BYTECODE}"
    echo ""
    echo "# Push to Docker Hub (if configured):"
    echo "docker push ${TAG_BYTECODE}"
    echo "docker push ${TAG_LATEST}"
    echo ""
    echo "✨ Features:"
    echo "  ✅ Python bytecode compiled (faster startup)"
    echo "  ✅ JavaScript minified (smaller bundle)"
    echo "  ✅ CSS minified (smaller bundle)"
    echo "  ✅ Production-optimized Gunicorn settings"
    echo "  ✅ Multi-platform support (AMD64/ARM64)"
    echo ""
    echo "🎉 VarioSync bytecode build complete!"
else
    echo ""
    echo "❌ BUILD FAILED!"
    echo "Check the error messages above for details."
    exit 1
fi
