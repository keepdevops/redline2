#!/usr/bin/env bash

# Simple test of functional REDLINE Docker images

echo "🧪 Testing Existing Functional REDLINE Images"
echo "=============================================="
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
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Cleanup function
cleanup() {
    echo "Cleaning up test containers..."
    docker stop redline-test-1 2>/dev/null || true
    docker rm redline-test-1 2>/dev/null || true
}
trap cleanup EXIT

# Test single image
test_single_image() {
    local image=$1
    local port=$2
    local container_name="redline-test-1"
    
    echo ""
    echo "=========================================="
    log_info "Testing: $image"
    echo "=========================================="
    
    # Check if image exists
    if ! docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        log_error "Image not found: $image"
        return 1
    fi
    
    # Get image size
    local size=$(docker images "$image" --format "{{.Size}}")
    log_info "Image size: $size"
    
    # Start container
    log_info "Starting container on port $port..."
    if ! docker run -d --name "$container_name" -p "${port}:8080" -v "${PWD}/data:/app/data" "$image" >/dev/null 2>&1; then
        log_error "Failed to start container"
        return 1
    fi
    
    # Wait for startup
    log_info "Waiting for container to start..."
    local ready=false
    local attempts=0
    
    while [ $attempts -lt 15 ] && [ "$ready" != "true" ]; do
        if curl -sf "http://localhost:${port}/health" >/dev/null 2>&1; then
            ready=true
            log_success "Health check passed"
        elif curl -sf "http://localhost:${port}/" >/dev/null 2>&1; then
            ready=true
            log_success "Main page accessible"
        else
            sleep 2
            ((attempts++))
        fi
    done
    
    if [ "$ready" != "true" ]; then
        log_error "Container startup failed"
        echo "Container logs:"
        docker logs "$container_name" | tail -5
        return 1
    fi
    
    # Test endpoints
    local base_url="http://localhost:${port}"
    local results=""
    
    # Test main page
    if curl -sf "${base_url}/" >/dev/null 2>&1; then
        results+="✅ Main "
    else
        results+="❌ Main "
    fi
    
    # Test health
    if curl -sf "${base_url}/health" >/dev/null 2>&1; then
        results+="✅ Health "
    else
        results+="❌ Health "
    fi
    
    # Test status
    if curl -sf "${base_url}/status" >/dev/null 2>&1; then
        results+="✅ Status "
    else
        results+="❌ Status "
    fi
    
    # Test dashboard
    if curl -sf "${base_url}/dashboard" >/dev/null 2>&1; then
        results+="✅ Dashboard "
    else
        results+="❌ Dashboard "
    fi
    
    # Test data tab
    if curl -sf "${base_url}/data/" >/dev/null 2>&1; then
        results+="✅ Data "
    else
        results+="❌ Data "
    fi
    
    # Test API
    if curl -sf "${base_url}/api/status" >/dev/null 2>&1; then
        results+="✅ API"
    else
        results+="❌ API"
    fi
    
    log_success "Test results: $results"
    
    # Stop container
    docker stop "$container_name" >/dev/null 2>&1
    docker rm "$container_name" >/dev/null 2>&1
    
    echo "$image|$size|$results"
    return 0
}

# Main execution
echo "Available REDLINE images:"
docker images | grep redline | head -10
echo ""

# Test priority images (most likely to work)
images_to_test=(
    "keepdevops/redline:v1.0.0-arm64-optimized"
    "keepdevops/redline:v1.0.0-amd64-optimized"
    "keepdevops/redline:v1.0.0-amd64-standard"
    "redline-webgui:latest"
    "redline-webgui:amd64"
)

successful_tests=()
failed_tests=()
port=8090

for image in "${images_to_test[@]}"; do
    if result=$(test_single_image "$image" $port); then
        successful_tests+=("$result")
        log_success "✅ $image - PASSED"
    else
        failed_tests+=("$image")
        log_error "❌ $image - FAILED"
    fi
    ((port++))
    echo ""
done

# Results summary
echo ""
echo "🎯 FINAL RESULTS"
echo "================"
echo ""

if [ ${#successful_tests[@]} -gt 0 ]; then
    echo "✅ WORKING IMAGES:"
    echo ""
    printf "%-45s %-12s %s\n" "IMAGE" "SIZE" "FEATURES"
    echo "$(printf '%.0s-' {1..80})"
    
    for result in "${successful_tests[@]}"; do
        IFS='|' read -r image size features <<< "$result"
        printf "%-45s %-12s %s\n" "$image" "$size" "$features"
    done
    
    echo ""
    log_success "Found ${#successful_tests[@]} working images!"
    
    # Recommend best one
    if [ ${#successful_tests[@]} -gt 0 ]; then
        best_image=$(echo "${successful_tests[0]}" | cut -d'|' -f1)
        echo ""
        echo "🏆 RECOMMENDED FOR USE:"
        echo "docker run -d -p 8080:8080 -v \$(pwd)/data:/app/data $best_image"
    fi
else
    log_error "No working images found"
fi

if [ ${#failed_tests[@]} -gt 0 ]; then
    echo ""
    echo "❌ FAILED IMAGES:"
    for failed in "${failed_tests[@]}"; do
        echo "  • $failed"
    done
fi

echo ""
echo "💡 NOTE: These images lack Custom API functionality (built before integration)"
echo "   But they provide solid core REDLINE features for financial data analysis"
echo ""
