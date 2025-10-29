#!/usr/bin/env bash

# Test next batch of REDLINE Docker images

echo "🧪 Testing Next Batch of REDLINE Images"
echo "======================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Cleanup function
cleanup() {
    echo "Cleaning up test containers..."
    docker stop redline-batch-test 2>/dev/null || true
    docker rm redline-batch-test 2>/dev/null || true
}
trap cleanup EXIT

# Quick test function
quick_test() {
    local image=$1
    local port=$2
    local container_name="redline-batch-test"
    
    echo ""
    echo "Testing: $image"
    echo "=================="
    
    # Check if image exists
    if ! docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        log_error "Image not found"
        return 1
    fi
    
    # Get size
    local size=$(docker images "$image" --format "{{.Size}}")
    echo "Size: $size"
    
    # Start container
    if ! docker run -d --name "$container_name" -p "${port}:8080" "$image" >/dev/null 2>&1; then
        log_error "Failed to start"
        return 1
    fi
    
    # Quick health check
    local ready=false
    local attempts=0
    
    while [ $attempts -lt 10 ] && [ "$ready" != "true" ]; do
        if curl -sf "http://localhost:${port}/health" >/dev/null 2>&1; then
            ready=true
            log_success "Health check PASSED"
        elif curl -sf "http://localhost:${port}/" >/dev/null 2>&1; then
            ready=true
            log_success "Main page accessible"
        else
            sleep 2
            ((attempts++))
        fi
    done
    
    # Stop container
    docker stop "$container_name" >/dev/null 2>&1
    docker rm "$container_name" >/dev/null 2>&1
    
    if [ "$ready" = "true" ]; then
        log_success "✅ WORKING - $image ($size)"
        echo "$image|$size|WORKING" >> /tmp/working_images.txt
        return 0
    else
        log_error "❌ FAILED - $image"
        echo "$image|$size|FAILED" >> /tmp/failed_images.txt
        return 1
    fi
}

# Initialize result files
echo "" > /tmp/working_images.txt
echo "" > /tmp/failed_images.txt

# Next batch of images to test
images_to_test=(
    "keepdevops/redline:v1.0.0-amd64-ultra-slim"
    "keepdevops/redline:v1.0.0-arm64-standard" 
    "keepdevops/redline:v1.0.0-amd64-standard"
    "redline-webgui-ultra-slim:arm64"
    "redline-webgui-ultra-slim:amd64"
    "redline-webgui-optimized:latest"
    "redline-webgui-ultra-slim-final:arm64"
    "redline-webgui-ultra-slim-fixed:arm64"
)

port=8100
successful=0
failed=0

for image in "${images_to_test[@]}"; do
    if quick_test "$image" $port; then
        ((successful++))
    else
        ((failed++))
    fi
    ((port++))
done

echo ""
echo "🎯 BATCH TEST RESULTS"
echo "===================="
echo "Tested: ${#images_to_test[@]} images"
echo "Working: $successful"
echo "Failed: $failed"
echo ""

if [ -s /tmp/working_images.txt ]; then
    echo "✅ WORKING IMAGES:"
    cat /tmp/working_images.txt | grep -v "^$" | while IFS='|' read -r image size status; do
        echo "  • $image ($size)"
    done
fi

if [ -s /tmp/failed_images.txt ]; then
    echo ""
    echo "❌ FAILED IMAGES:"
    cat /tmp/failed_images.txt | grep -v "^$" | while IFS='|' read -r image size status; do
        echo "  • $image ($size)"
    done
fi

# Cleanup temp files
rm -f /tmp/working_images.txt /tmp/failed_images.txt

echo ""
echo "🚀 Next: Test remaining development images..."
