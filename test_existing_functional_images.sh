#!/usr/bin/env bash

# REDLINE Existing Functional Images Testing
# Tests remaining Docker images to identify the best working ones

set -e

echo "🧪 REDLINE Existing Functional Images Testing"
echo "============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_test() { echo -e "${CYAN}🧪 $1${NC}"; }

# Test configuration
PORT_BASE=8090
TEST_TIMEOUT=30

# Results tracking
declare -a TESTED_IMAGES
declare -a WORKING_IMAGES
declare -a FAILED_IMAGES

# Cleanup function
cleanup() {
    log_info "Cleaning up test containers..."
    for container in $(docker ps -aq --filter "name=redline-test-*"); do
        docker stop $container 2>/dev/null || true
        docker rm $container 2>/dev/null || true
    done
}

trap cleanup EXIT

# Find available port
find_available_port() {
    local base_port=$1
    local port=$base_port
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        ((port++))
    done
    echo $port
}

# Test individual image
test_image() {
    local image_name=$1
    local test_name=$2
    local container_name="redline-test-$(echo $test_name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
    
    echo ""
    echo "=========================================="
    log_test "Testing: $image_name"
    log_info "Test Name: $test_name"
    echo "=========================================="
    
    TESTED_IMAGES+=("$image_name")
    
    # Find available port
    local port=$(find_available_port $PORT_BASE)
    ((PORT_BASE++))
    
    log_info "Using port: $port"
    
    # Start container
    log_info "Starting container..."
    if ! docker run -d \
        --name "$container_name" \
        -p "${port}:8080" \
        -v "${PWD}/data:/app/data" \
        "$image_name" >/dev/null 2>&1; then
        log_error "Failed to start container"
        FAILED_IMAGES+=("$image_name - Failed to start")
        return 1
    fi
    
    # Wait for container to be ready
    log_info "Waiting for container to be ready..."
    local ready=false
    local attempts=0
    local max_attempts=$((TEST_TIMEOUT / 2))
    
    while [ $attempts -lt $max_attempts ] && [ "$ready" != "true" ]; do
        if curl -sf "http://localhost:${port}/health" >/dev/null 2>&1; then
            ready=true
            log_success "Container healthy"
        elif curl -sf "http://localhost:${port}/" >/dev/null 2>&1; then
            ready=true
            log_success "Container responding (no health endpoint)"
        else
            sleep 2
            ((attempts++))
        fi
    done
    
    if [ "$ready" != "true" ]; then
        log_error "Container failed to become ready"
        echo "Container logs:"
        docker logs "$container_name" | tail -10
        FAILED_IMAGES+=("$image_name - Startup timeout")
        return 1
    fi
    
    # Test basic functionality
    local base_url="http://localhost:${port}"
    local test_results=""
    
    # Test 1: Main page
    log_test "Testing main page..."
    if curl -sf "${base_url}/" >/dev/null 2>&1; then
        log_success "Main page accessible"
        test_results+="✅ Main page | "
    else
        log_warning "Main page not accessible"
        test_results+="❌ Main page | "
    fi
    
    # Test 2: Health endpoint
    log_test "Testing health endpoint..."
    local health_response=$(curl -s "${base_url}/health" 2>/dev/null)
    if echo "$health_response" | grep -q "healthy\|running"; then
        log_success "Health endpoint working"
        test_results+="✅ Health | "
    else
        log_warning "Health endpoint not working"
        test_results+="❌ Health | "
    fi
    
    # Test 3: Status endpoint
    log_test "Testing status endpoint..."
    local status_response=$(curl -s "${base_url}/status" 2>/dev/null)
    if echo "$status_response" | grep -q "status\|running"; then
        log_success "Status endpoint working"
        test_results+="✅ Status | "
    else
        log_warning "Status endpoint not working"
        test_results+="❌ Status | "
    fi
    
    # Test 4: Dashboard
    log_test "Testing dashboard..."
    if curl -sf "${base_url}/dashboard" >/dev/null 2>&1; then
        log_success "Dashboard accessible"
        test_results+="✅ Dashboard | "
    else
        log_warning "Dashboard not accessible"
        test_results+="❌ Dashboard | "
    fi
    
    # Test 5: Data tab
    log_test "Testing data tab..."
    if curl -sf "${base_url}/data/" >/dev/null 2>&1; then
        log_success "Data tab accessible"
        test_results+="✅ Data | "
    else
        log_warning "Data tab not accessible"
        test_results+="❌ Data | "
    fi
    
    # Test 6: API endpoints
    log_test "Testing API endpoints..."
    local api_response=$(curl -s "${base_url}/api/status" 2>/dev/null)
    if echo "$api_response" | grep -q "status\|running\|data_loader"; then
        log_success "API endpoints working"
        test_results+="✅ API | "
    else
        log_warning "API endpoints not working"
        test_results+="❌ API | "
    fi
    
    # Get image size
    local image_size=$(docker images "$image_name" --format "{{.Size}}")
    
    # Stop container
    docker stop "$container_name" >/dev/null 2>&1 || true
    docker rm "$container_name" >/dev/null 2>&1 || true
    
    # Record results
    WORKING_IMAGES+=("$image_name | $image_size | $test_results")
    log_success "Test completed for $test_name"
    
    return 0
}

# Main testing execution
echo "🔍 Identifying functional images to test..."

# List of images to test (functional ones from our analysis)
declare -A TEST_IMAGES=(
    ["keepdevops/redline:v1.0.0-arm64-optimized"]="ARM64 Optimized"
    ["keepdevops/redline:v1.0.0-amd64-optimized"]="AMD64 Optimized" 
    ["keepdevops/redline:v1.0.0-arm64-standard"]="ARM64 Standard"
    ["keepdevops/redline:v1.0.0-amd64-standard"]="AMD64 Standard"
    ["keepdevops/redline:v1.0.0-amd64-ultra-slim"]="AMD64 Ultra-Slim"
    ["redline-webgui:latest"]="Latest WebGUI"
    ["redline-webgui:amd64"]="AMD64 WebGUI"
)

echo "Found ${#TEST_IMAGES[@]} images to test"
echo ""

# Test each image
for image in "${!TEST_IMAGES[@]}"; do
    test_name="${TEST_IMAGES[$image]}"
    
    # Check if image exists
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        test_image "$image" "$test_name"
    else
        log_warning "Image not found: $image"
        FAILED_IMAGES+=("$image - Not found")
    fi
done

# Results summary
echo ""
echo "📊 COMPREHENSIVE TEST RESULTS"
echo "=============================="
echo ""

printf "%-40s %-12s %-50s\n" "IMAGE" "SIZE" "TEST RESULTS"
echo "$(printf '%.0s-' {1..120})"

for result in "${WORKING_IMAGES[@]}"; do
    IFS='|' read -r image size tests <<< "$result"
    printf "%-40s %-12s %-50s\n" "$image" "$size" "$tests"
done

echo ""
echo "🎯 SUMMARY"
echo "=========="
echo "Total images tested: ${#TESTED_IMAGES[@]}"
echo "Working images: $((${#WORKING_IMAGES[@]}))"
echo "Failed images: $((${#FAILED_IMAGES[@]}))"

if [ ${#FAILED_IMAGES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Failed Images:"
    for failed in "${FAILED_IMAGES[@]}"; do
        echo "  • $failed"
    done
fi

echo ""
echo "🏆 RECOMMENDATIONS"
echo "=================="

if [ ${#WORKING_IMAGES[@]} -gt 0 ]; then
    echo "✅ Best performing images for production use:"
    echo ""
    
    # Find images with most green checkmarks
    local best_count=0
    local best_image=""
    
    for result in "${WORKING_IMAGES[@]}"; do
        local checkmarks=$(echo "$result" | grep -o "✅" | wc -l)
        if [ $checkmarks -gt $best_count ]; then
            best_count=$checkmarks
            best_image="$result"
        fi
    done
    
    if [ -n "$best_image" ]; then
        IFS='|' read -r image size tests <<< "$best_image"
        echo "🥇 Top Performer: $image"
        echo "   Size: $size"
        echo "   Features: $tests"
        echo ""
        echo "🚀 Quick start with best image:"
        echo "docker run -d -p 8080:8080 -v \$(pwd)/data:/app/data $image"
    fi
else
    echo "❌ No fully functional images found"
    echo "💡 Consider building fresh images with current codebase"
fi

echo ""
echo "💡 Note: These images were built before Custom API integration"
echo "   They lack Custom API Builder functionality but provide solid core features"
echo ""
