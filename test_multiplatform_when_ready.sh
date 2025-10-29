#!/bin/bash

# Test Multi-Platform Images When Ready
# Monitors Docker Hub and tests the new unified manifests

set -e

echo "🔍 MONITORING MULTI-PLATFORM BUILD COMPLETION"
echo "============================================="
echo ""

# Function to check if image exists on Docker Hub
check_image_exists() {
    local image=$1
    echo "🔍 Checking if $image is available..."
    if docker manifest inspect $image >/dev/null 2>&1; then
        echo "✅ $image is available!"
        return 0
    else
        echo "⏳ $image not yet available..."
        return 1
    fi
}

# Function to test multi-platform image
test_multiplatform_image() {
    local image=$1
    local container_name=$2
    
    echo ""
    echo "🚀 TESTING MULTI-PLATFORM IMAGE: $image"
    echo "========================================"
    echo ""
    
    # Stop any existing container
    echo "🛑 Stopping existing containers..."
    docker stop $container_name 2>/dev/null || true
    docker rm $container_name 2>/dev/null || true
    
    # Pull and inspect the multi-platform manifest
    echo "📦 Pulling multi-platform image..."
    docker pull $image
    
    echo ""
    echo "🔍 Inspecting multi-platform manifest..."
    docker manifest inspect $image | jq -r '.manifests[] | "Platform: \(.platform.architecture)/\(.platform.os) - Size: \(.size)"' 2>/dev/null || docker manifest inspect $image
    
    # Start container with multi-platform image
    echo ""
    echo "🚀 Starting container with multi-platform image..."
    docker run -d \
        --name $container_name \
        -p 8080:8080 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        --restart unless-stopped \
        $image
    
    # Wait for startup
    echo "⏱️ Waiting for application startup..."
    sleep 10
    
    # Check container status
    echo ""
    echo "📊 Container Status:"
    docker ps | grep $container_name || echo "❌ Container not running"
    
    # Test health endpoint
    echo ""
    echo "🌐 Testing health endpoint..."
    if curl -f http://localhost:8080/health 2>/dev/null; then
        echo ""
        echo "✅ MULTI-PLATFORM IMAGE WORKING!"
        echo ""
        echo "🎉 SUCCESS! Multi-platform deployment complete!"
        echo "   🌐 Access: http://localhost:8080"
        echo "   📦 Image: $image"
        echo "   🏗️ Platform: Automatically detected"
        echo ""
        return 0
    else
        echo "❌ Health check failed"
        echo ""
        echo "📜 Container logs:"
        docker logs $container_name --tail 20
        return 1
    fi
}

# Main monitoring loop
echo "⏳ Waiting for multi-platform images to be available..."
echo "   This will check every 30 seconds until ready"
echo ""

# Images to test (in order of priority)
IMAGES=(
    "keepdevops/redline:latest"
    "keepdevops/redline:optimized"
    "keepdevops/redline:ultra-slim"
)

# Monitor until at least one image is available
while true; do
    for image in "${IMAGES[@]}"; do
        if check_image_exists "$image"; then
            echo ""
            echo "🎯 Found available image: $image"
            echo ""
            
            # Test the first available image
            if test_multiplatform_image "$image" "redline-multiplatform"; then
                echo "🏆 MULTI-PLATFORM TEST SUCCESSFUL!"
                echo ""
                echo "📋 Next Steps:"
                echo "  • Test on different architectures"
                echo "  • Update documentation"
                echo "  • Announce multi-platform support"
                echo ""
                exit 0
            else
                echo "❌ Test failed, will retry..."
            fi
        fi
    done
    
    echo "⏳ Images not ready yet, waiting 30 seconds..."
    sleep 30
done
