#!/bin/bash

# Multi-Platform Docker Build - Local Only (No Push)
# Creates unified manifests locally on M3 machine for testing

set -e

echo "🚀 MULTI-PLATFORM LOCAL BUILD"
echo "============================="
echo ""
echo "🎯 Building locally on M3 machine (no Docker Hub push)"
echo "📦 Will create multi-platform manifests for testing"
echo "🏗️ Target platforms: linux/amd64, linux/arm64"
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
echo "🏗️ BUILDING MULTI-PLATFORM IMAGES LOCALLY"
echo "=========================================="

# Build 1: Optimized (Production Ready)
echo ""
echo "1️⃣ Building Optimized Multi-Platform Image..."
echo "   📦 Dockerfile: Dockerfile.webgui.simple"
echo "   🎯 Platforms: linux/amd64, linux/arm64"
echo "   📝 Tag: ${BASE_NAME}-optimized:${VERSION}"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -f Dockerfile.webgui.simple \
    -t ${BASE_NAME}-optimized:${VERSION} \
    -t ${BASE_NAME}-optimized:latest \
    --load \
    .

echo "✅ Optimized multi-platform image built successfully!"

# Build 2: Ultra-Slim (Minimal Dependencies)
echo ""
echo "2️⃣ Building Ultra-Slim Multi-Platform Image..."
echo "   📦 Dockerfile: Dockerfile.webgui.ultra-slim"
echo "   🎯 Platforms: linux/amd64, linux/arm64"
echo "   📝 Tag: ${BASE_NAME}-ultra-slim:${VERSION}"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -f Dockerfile.webgui.ultra-slim \
    -t ${BASE_NAME}-ultra-slim:${VERSION} \
    -t ${BASE_NAME}-ultra-slim:latest \
    --load \
    .

echo "✅ Ultra-slim multi-platform image built successfully!"

# Build 3: Compiled (20% Faster Startup)
echo ""
echo "3️⃣ Building Compiled Multi-Platform Image..."
echo "   📦 Dockerfile: Dockerfile.webgui.compiled"
echo "   🎯 Platforms: linux/amd64, linux/arm64"
echo "   📝 Tag: ${BASE_NAME}-compiled:${VERSION}"

if [ -f "Dockerfile.webgui.compiled" ]; then
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f Dockerfile.webgui.compiled \
        -t ${BASE_NAME}-compiled:${VERSION} \
        -t ${BASE_NAME}-compiled:latest \
        --load \
        .
    echo "✅ Compiled multi-platform image built successfully!"
else
    echo "⚠️  Dockerfile.webgui.compiled not found, skipping compiled build"
fi

echo ""
echo "🎉 LOCAL MULTI-PLATFORM BUILD COMPLETE!"
echo "======================================="

echo ""
echo "📊 Available Multi-Platform Images:"
docker images | grep "${BASE_NAME}" | grep -E "(${VERSION}|latest)"

echo ""
echo "🧪 TESTING MULTI-PLATFORM FUNCTIONALITY"
echo "======================================="

# Test function
test_multiplatform_image() {
    local image=$1
    local container_name=$2
    
    echo ""
    echo "🚀 Testing: $image"
    echo "   Container: $container_name"
    
    # Stop existing container
    docker stop $container_name 2>/dev/null || true
    docker rm $container_name 2>/dev/null || true
    
    # Start container
    echo "   🔄 Starting container..."
    docker run -d \
        --name $container_name \
        -p 8080:8080 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        --restart unless-stopped \
        $image
    
    # Wait for startup
    echo "   ⏱️  Waiting for startup..."
    sleep 8
    
    # Test health
    echo "   🌐 Testing health endpoint..."
    if curl -f http://localhost:8080/health 2>/dev/null; then
        echo "   ✅ SUCCESS! Multi-platform image working!"
        echo "      🌐 Access: http://localhost:8080"
        echo "      🏗️ Platform: $(docker inspect $container_name --format '{{.Platform}}')"
        return 0
    else
        echo "   ❌ Health check failed"
        echo "   📜 Container logs:"
        docker logs $container_name --tail 10
        return 1
    fi
}

# Test the optimized image first
if test_multiplatform_image "${BASE_NAME}-optimized:latest" "redline-multiplatform-test"; then
    echo ""
    echo "🏆 MULTI-PLATFORM BUILD SUCCESS!"
    echo ""
    echo "🎯 Ready for Testing:"
    echo "  🌐 Web Interface: http://localhost:8080"
    echo "  📦 Image: ${BASE_NAME}-optimized:latest"
    echo "  🏗️ Platform: Auto-detected (M3 ARM64)"
    echo "  🚀 Container: redline-multiplatform-test"
    echo ""
    echo "🔄 Other Available Images:"
    echo "  • ${BASE_NAME}-ultra-slim:latest (minimal size)"
    echo "  • ${BASE_NAME}-compiled:latest (20% faster startup)"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Test web interface functionality"
    echo "  2. Verify all features work correctly"
    echo "  3. Test on different architectures if needed"
    echo ""
else
    echo ""
    echo "❌ Multi-platform test failed, trying ultra-slim..."
    if test_multiplatform_image "${BASE_NAME}-ultra-slim:latest" "redline-multiplatform-test-slim"; then
        echo "✅ Ultra-slim multi-platform image working!"
    else
        echo "❌ All multi-platform tests failed"
        echo "📜 Checking available images..."
        docker images | grep "${BASE_NAME}"
    fi
fi

echo ""
echo "🎉 Multi-platform build completed locally on M3 machine!"
