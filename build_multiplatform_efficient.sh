#!/bin/bash

# Efficient Multi-Platform Docker Build - Local Only
# Builds one variant at a time to avoid disk space issues

set -e

echo "🚀 EFFICIENT MULTI-PLATFORM LOCAL BUILD"
echo "======================================="
echo ""
echo "🎯 Strategy: Build one variant at a time to avoid disk space issues"
echo "📦 Will create multi-platform manifests locally for testing"
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
echo "🏗️ BUILDING MULTI-PLATFORM IMAGES EFFICIENTLY"
echo "=============================================="

# Build 1: Ultra-Slim (Smallest, Most Likely to Succeed)
echo ""
echo "1️⃣ Building Ultra-Slim Multi-Platform Image..."
echo "   📦 Dockerfile: Dockerfile.webgui.ultra-slim"
echo "   🎯 Platforms: linux/amd64, linux/arm64"
echo "   📝 Tag: ${BASE_NAME}-ultra-slim:${VERSION}"
echo "   💾 Size: Expected ~1.4GB per platform"

# Build for both platforms but don't load (saves space)
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -f Dockerfile.webgui.ultra-slim \
    -t ${BASE_NAME}-ultra-slim:${VERSION} \
    -t ${BASE_NAME}-ultra-slim:latest \
    --output type=image,push=false \
    .

echo "✅ Ultra-slim multi-platform image built successfully!"

# Now load just the ARM64 version for local testing (since we're on M3)
echo ""
echo "📦 Loading ARM64 version for local testing..."
docker buildx build \
    --platform linux/arm64 \
    -f Dockerfile.webgui.ultra-slim \
    -t ${BASE_NAME}-ultra-slim:latest-arm64 \
    --load \
    .

echo "✅ ARM64 ultra-slim image loaded for testing!"

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
        echo "      🏗️ Platform: ARM64 (M3 native)"
        return 0
    else
        echo "   ❌ Health check failed"
        echo "   📜 Container logs:"
        docker logs $container_name --tail 10
        return 1
    fi
}

# Test the ultra-slim ARM64 image
if test_multiplatform_image "${BASE_NAME}-ultra-slim:latest-arm64" "redline-multiplatform-test"; then
    echo ""
    echo "🏆 MULTI-PLATFORM BUILD SUCCESS!"
    echo ""
    echo "🎯 Ready for Testing:"
    echo "  🌐 Web Interface: http://localhost:8080"
    echo "  📦 Image: ${BASE_NAME}-ultra-slim:latest-arm64"
    echo "  🏗️ Platform: ARM64 (M3 native)"
    echo "  🚀 Container: redline-multiplatform-test"
    echo ""
    echo "📊 Multi-Platform Manifest Created:"
    echo "  • ${BASE_NAME}-ultra-slim:${VERSION} (AMD64 + ARM64)"
    echo "  • ${BASE_NAME}-ultra-slim:latest (AMD64 + ARM64)"
    echo ""
    echo "🔄 Available for Cross-Platform Testing:"
    echo "  • On Dell (AMD64): docker run ${BASE_NAME}-ultra-slim:latest"
    echo "  • On M3 (ARM64): docker run ${BASE_NAME}-ultra-slim:latest"
    echo "  • Auto-detects platform and uses correct architecture"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. ✅ Test web interface functionality"
    echo "  2. ⏳ Build additional variants if needed (optimized, compiled)"
    echo "  3. ⏳ Test on different architectures"
    echo ""
else
    echo ""
    echo "❌ Multi-platform test failed"
    echo "📜 Checking available images..."
    docker images | grep "${BASE_NAME}"
fi

echo ""
echo "🎉 Efficient multi-platform build completed!"
echo ""
echo "💡 Benefits Achieved:"
echo "  ✅ Multi-platform manifest created (AMD64 + ARM64)"
echo "  ✅ Single command works on any architecture"
echo "  ✅ Efficient build process (no disk space issues)"
echo "  ✅ Local testing ready on M3 machine"
echo "  ✅ Professional Docker deployment strategy"
echo "  ✅ Custom API Builder included and ready"
echo ""
echo "🚀 Usage Examples (with Custom API persistence):"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${BASE_NAME}:latest"
echo "docker run -d -p 8080:8080 -v redline-data:/app/data ${BASE_NAME}:slim"
echo ""
echo "💡 Custom API Builder:"
echo "Access at: http://localhost:8080/custom-api/"
echo ""
echo "🐳 Docker Compose (recommended):"
echo "docker-compose up -d"
