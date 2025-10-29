#!/usr/bin/env bash

# Test final batch of REDLINE Docker images

echo "🧪 Testing Final Batch of REDLINE Images"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Cleanup function
cleanup() {
    docker stop redline-final-test 2>/dev/null || true
    docker rm redline-final-test 2>/dev/null || true
}
trap cleanup EXIT

# Ultra-quick test function
ultra_quick_test() {
    local image=$1
    local port=$2
    
    echo -n "Testing $image... "
    
    # Check if image exists
    if ! docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        log_error "NOT FOUND"
        return 1
    fi
    
    # Start container
    if ! docker run -d --name "redline-final-test" -p "${port}:8080" "$image" >/dev/null 2>&1; then
        log_error "START FAILED"
        return 1
    fi
    
    # Ultra-quick check (5 seconds max)
    local ready=false
    for i in {1..5}; do
        if curl -sf "http://localhost:${port}/health" >/dev/null 2>&1 || curl -sf "http://localhost:${port}/" >/dev/null 2>&1; then
            ready=true
            break
        fi
        sleep 1
    done
    
    # Stop container immediately
    docker stop "redline-final-test" >/dev/null 2>&1
    docker rm "redline-final-test" >/dev/null 2>&1
    
    if [ "$ready" = "true" ]; then
        local size=$(docker images "$image" --format "{{.Size}}")
        log_success "WORKING ($size)"
        return 0
    else
        log_error "NO RESPONSE"
        return 1
    fi
}

# Final batch of images
final_images=(
    "redline-webgui-ultra-slim:latest-arm64"
    "redline-webgui-ultra-slim:latest"
    "redline-webgui-ultra-slim:v1.0.0-multiplatform"
    "redline-webgui-optimized:v1.0.0-multiplatform"
    "redline-webgui-compiled-optimized:arm64"
    "redline-webgui-compiled-optimized:amd64"
    "redline-webgui-compiled:arm64"
    "redline-webgui-compiled:amd64"
)

working_count=0
port=8110

for image in "${final_images[@]}"; do
    if ultra_quick_test "$image" $port; then
        ((working_count++))
    fi
    ((port++))
done

echo ""
echo "🎯 FINAL BATCH RESULTS"
echo "====================="
echo "Tested: ${#final_images[@]} images"
echo "Working: $working_count"
echo "Failed: $((${#final_images[@]} - working_count))"

echo ""
echo "🏁 COMPLETE TESTING SUMMARY"
echo "==========================="
echo "Total images tested across all batches: ~20+"
echo "Total working images found: 1 + $working_count"
echo ""
if [ $working_count -gt 0 ]; then
    echo "✅ Great! Found additional working images!"
else
    echo "💡 Only 1 working image confirmed: keepdevops/redline:v1.0.0-arm64-optimized"
fi
