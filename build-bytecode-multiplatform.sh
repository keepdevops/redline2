#!/bin/bash

# VarioSync Multi-Platform Docker Build Script - Bytecode Optimized Version
# Builds and pushes bytecode-compiled images for AMD64 and ARM64 simultaneously
# Creates multi-platform manifests for production deployment with optimized performance

set -e

# Configuration
IMAGE_NAME="keepdevops/variosync1"
VERSION="v2.1.0-bytecode-multiplatform"
PLATFORMS="linux/amd64,linux/arm64"

echo "🚀 VARIOSYNC MULTI-PLATFORM BUILD - BYTECODE OPTIMIZED VERSION"
echo "==========================================================="
echo ""
echo "📦 Building for platforms: ${PLATFORMS}"
echo "🏷️ Image: ${IMAGE_NAME}:${VERSION}"
echo "🏗️ Builder: multiplatform"
echo "🔧 Type: Bytecode Optimized (Production)"
echo ""

# Ensure multiplatform builder is active
echo "🔧 Setting up multi-platform builder..."
docker buildx use multiplatform 2>/dev/null || {
    echo "Creating multiplatform builder..."
    docker buildx create --name multiplatform --bootstrap --use
}
docker buildx inspect --bootstrap

echo ""
echo "🏗️ BUILDING BYTECODE OPTIMIZED MULTI-PLATFORM IMAGE"
echo "==================================================="
echo ""

# Build and push bytecode-optimized multi-platform image
echo "📦 Building bytecode-optimized variant (for production)..."
docker buildx build \
    --platform ${PLATFORMS} \
    -f Dockerfile.webgui.bytecode \
    -t ${IMAGE_NAME}:${VERSION} \
    -t ${IMAGE_NAME}:bytecode \
    -t ${IMAGE_NAME}:bytecode-latest \
    --push \
    .

echo ""
echo "✅ BYTECODE OPTIMIZED MULTI-PLATFORM BUILD COMPLETE!"
echo "===================================================="
echo ""
echo "🎯 Available Images:"
echo "  • ${IMAGE_NAME}:bytecode (multi-platform, bytecode optimized)"
echo "  • ${IMAGE_NAME}:bytecode-latest (latest bytecode variant)"
echo "  • ${IMAGE_NAME}:${VERSION} (versioned)"
echo ""
echo "🚀 Usage Examples:"
echo ""
echo "# Production deployment with persistent data (recommended):"
echo "docker run -d -p 8080:8080 -v variosync-data:/app/data ${IMAGE_NAME}:bytecode"
echo ""
echo "# Production with custom environment variables:"
echo "docker run -d -p 8080:8080 -v variosync-data:/app/data \\"
echo "  -e FLASK_ENV=production \\"
echo "  -e GUNICORN_WORKERS=2 \\"
echo "  ${IMAGE_NAME}:bytecode"
echo ""
echo "📊 Platform Support:"
echo "  ✅ AMD64 (Intel/Dell machines)"
echo "  ✅ ARM64 (Apple Silicon M1/M2/M3)"
echo "  🔄 Automatic detection and deployment"
echo ""
echo "🔧 Production Features:"
echo "  ✅ Pre-compiled Python bytecode (20% faster startup)"
echo "  ✅ Minified JavaScript and CSS assets"
echo "  ✅ Optimized Gunicorn settings"
echo "  ✅ All dependencies from requirements.txt:"
echo "     • TensorFlow (Keras/TensorFlow formats)"
echo "     • Polars (high-performance DataFrames)"
echo "     • PyArrow (Feather format)"
echo "     • Scikit-learn (ML features)"
echo "     • Matplotlib/Seaborn (visualizations)"
echo "     • All other core dependencies"
echo ""
echo "📦 Dependencies Included:"
echo "  • Core: Flask, Pandas, NumPy, DuckDB"
echo "  • ML Formats: TensorFlow, Keras, PyArrow, Polars"
echo "  • ML Features: Scikit-learn, Matplotlib, Seaborn"
echo "  • Data Sources: yfinance, Alpha Vantage, Finnhub, Massive.com"
echo "  • Web: Flask-SocketIO, Gunicorn, Redis, Celery"
echo ""
echo "⚠️  Production Notice:"
echo "  • This image is optimized for production use"
echo "  • Source code is compiled to bytecode"
echo "  • JavaScript/CSS are minified"
echo "  • For development, use :uncompiled or :dev variants"
echo ""
echo "🎉 Bytecode optimized multi-platform deployment ready!"



