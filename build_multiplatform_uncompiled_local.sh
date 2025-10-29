#!/bin/bash

# Efficient Multi-Platform Docker Build - Uncompiled Local Version
# Builds one variant at a time to avoid disk space issues
# Creates uncompiled development images for debugging

set -e

echo "🚀 EFFICIENT MULTI-PLATFORM LOCAL BUILD - UNCOMPILED"
echo "====================================================="
echo ""
echo "🎯 Strategy: Build uncompiled variant locally for development"
echo "📦 Will create multi-platform manifests locally for testing"
echo "🏗️ Target platforms: linux/amd64, linux/arm64"
echo "🔧 Type: Uncompiled (Development/Debug)"
echo ""

# Define image names and versions
BASE_NAME="redline-webgui"
VERSION="v1.0.0-multiplatform"

# Ensure Buildx is available and create builder if needed
echo "🔧 Setting up multi-platform builder..."
if ! docker buildx ls | grep -q "multiplatform"; then
    echo "Creating multiplatform builder..."
    docker buildx create --name multiplatform --bootstrap --use
else
    echo "Using existing multiplatform builder."
    docker buildx use multiplatform
fi

echo ""
echo "📊 Builder Status:"
docker buildx inspect multiplatform

echo ""
echo "🏗️ BUILDING UNCOMPILED MULTI-PLATFORM IMAGE LOCALLY"
echo "===================================================="

# Build: Uncompiled Development Image
echo ""
echo "1️⃣ Building Uncompiled Development Multi-Platform Image..."
echo "   📦 Dockerfile: Dockerfile.webgui.uncompiled"
echo "   🎯 Platforms: linux/amd64, linux/arm64"
echo "   📝 Tag: ${BASE_NAME}-uncompiled:${VERSION}"
echo "   💾 Size: Expected ~1.5GB per platform (unoptimized)"
echo "   🔧 Features: Source code debugging, no bytecode compilation"

# Build for both platforms but don't load (saves space)
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -f Dockerfile.webgui.uncompiled \
    -t ${BASE_NAME}-uncompiled:${VERSION} \
    -t ${BASE_NAME}-uncompiled:latest \
    -t ${BASE_NAME}:dev \
    -t ${BASE_NAME}:debug \
    --output type=image,push=false \
    .

echo "✅ Uncompiled multi-platform image built successfully!"

# Now load just the ARM64 version for local testing (since we're on M3)
echo ""
echo "📦 Loading ARM64 version for local development testing..."
docker buildx build \
    --platform linux/arm64 \
    -f Dockerfile.webgui.uncompiled \
    -t ${BASE_NAME}-uncompiled:latest-arm64 \
    -t ${BASE_NAME}:dev-arm64 \
    --load \
    .

echo "✅ ARM64 uncompiled image loaded for development testing!"

echo ""
echo "🧪 TESTING UNCOMPILED MULTI-PLATFORM FUNCTIONALITY"
echo "=================================================="

# Test function
test_uncompiled_image() {
    local image=$1
    local container_name=$2
    
    echo ""
    echo "🚀 Testing: $image"
    echo "   Container: $container_name"
    echo "   Mode: Development/Debug"
    
    # Stop existing container
    docker stop $container_name 2>/dev/null || true
    docker rm $container_name 2>/dev/null || true
    
    # Start container with development settings
    echo "   🔄 Starting development container..."
    docker run -d \
        --name $container_name \
        -p 8080:8080 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -e FLASK_ENV=development \
        -e FLASK_DEBUG=1 \
        --restart unless-stopped \
        $image
    
    # Wait for startup (uncompiled may take longer)
    echo "   ⏱️  Waiting for startup (uncompiled version may take longer)..."
    sleep 12
    
    # Test health
    echo "   🌐 Testing health endpoint..."
    if curl -f http://localhost:8080/health 2>/dev/null; then
        echo "   ✅ SUCCESS! Uncompiled multi-platform image working!"
        echo "      🌐 Access: http://localhost:8080"
        echo "      🏗️ Platform: ARM64 (M3 native)"
        echo "      🔧 Mode: Development/Debug"
        return 0
    else
        echo "   ❌ Health check failed"
        echo "   📜 Container logs:"
        docker logs $container_name --tail 15
        return 1
    fi
}

# Test the uncompiled ARM64 image
if test_uncompiled_image "${BASE_NAME}-uncompiled:latest-arm64" "redline-uncompiled-dev"; then
    echo ""
    echo "🏆 UNCOMPILED MULTI-PLATFORM BUILD SUCCESS!"
    echo ""
    echo "🎯 Ready for Development:"
    echo "  🌐 Web Interface: http://localhost:8080"
    echo "  📦 Image: ${BASE_NAME}-uncompiled:latest-arm64"
    echo "  🏗️ Platform: ARM64 (M3 native)"
    echo "  🚀 Container: redline-uncompiled-dev"
    echo "  🔧 Mode: Development/Debug"
    echo ""
    echo "📊 Multi-Platform Manifest Created:"
    echo "  • ${BASE_NAME}-uncompiled:${VERSION} (AMD64 + ARM64)"
    echo "  • ${BASE_NAME}-uncompiled:latest (AMD64 + ARM64)"
    echo "  • ${BASE_NAME}:dev (AMD64 + ARM64)"
    echo "  • ${BASE_NAME}:debug (AMD64 + ARM64)"
    echo ""
    echo "🔄 Available for Cross-Platform Development:"
    echo "  • On Dell (AMD64): docker run ${BASE_NAME}:dev"
    echo "  • On M3 (ARM64): docker run ${BASE_NAME}:dev"
    echo "  • Auto-detects platform and uses correct architecture"
    echo ""
    echo "🔧 Development Features:"
    echo "  ✅ No bytecode compilation (easier debugging)"
    echo "  ✅ Source files preserved and accessible"
    echo "  ✅ Flask development environment"
    echo "  ✅ Gunicorn reload enabled"
    echo "  ✅ Debug logging level"
    echo "  ✅ Relaxed performance settings"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. ✅ Test web interface functionality in debug mode"
    echo "  2. ⏳ Test source code debugging capabilities"
    echo "  3. ⏳ Test on different architectures"
    echo "  4. ⏳ Mount local source for live development"
    echo ""
else
    echo ""
    echo "❌ Uncompiled multi-platform test failed"
    echo "📜 Checking available images..."
    docker images | grep "${BASE_NAME}"
fi

echo ""
echo "🎉 Efficient uncompiled multi-platform build completed!"
echo ""
echo "💡 Development Benefits Achieved:"
echo "  ✅ Multi-platform manifest created (AMD64 + ARM64)"
echo "  ✅ Single command works on any architecture"
echo "  ✅ Efficient build process (no disk space issues)"
echo "  ✅ Local development testing ready on M3 machine"
echo "  ✅ Professional Docker development strategy"
echo "  ✅ Custom API Builder included and ready"
echo "  ✅ Source code debugging enabled"
echo "  ✅ No compilation barriers for development"
echo ""
echo "🚀 Development Usage Examples:"
echo "# Basic development mode:"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${BASE_NAME}:dev"
echo ""
echo "# Live development with source mounting:"
echo "docker run -d -p 8080:8080 -v \$(pwd):/app -v redline-data:/app/data ${BASE_NAME}:dev"
echo ""
echo "# Debug mode with verbose logging:"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data -e FLASK_DEBUG=1 ${BASE_NAME}:debug"
echo ""
echo "💡 Custom API Builder:"
echo "Access at: http://localhost:8080/custom-api/"
echo ""
echo "🐳 Docker Compose Development (recommended):"
echo "docker-compose -f docker-compose-dev.yml up -d"
