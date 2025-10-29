#!/usr/bin/env bash

# REDLINE ARM64 Docker Images Simple Test
# Builds and tests Docker image variants one by one for ARM64

set -e

echo "🚀 REDLINE ARM64 Docker Images Test"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_build() { echo -e "${PURPLE}🔨 $1${NC}"; }

# Configuration
BASE_NAME="redline-test"
PORT=8080

# Cleanup function
cleanup() {
    log_info "Cleaning up containers..."
    docker stop ${BASE_NAME}-simple 2>/dev/null || true
    docker rm ${BASE_NAME}-simple 2>/dev/null || true
    docker stop ${BASE_NAME}-ultra-slim 2>/dev/null || true
    docker rm ${BASE_NAME}-ultra-slim 2>/dev/null || true
    docker stop ${BASE_NAME}-compiled 2>/dev/null || true
    docker rm ${BASE_NAME}-compiled 2>/dev/null || true
}

trap cleanup EXIT

# Test function
test_variant() {
    local variant=$1
    local dockerfile=$2
    local image_name="${BASE_NAME}-${variant}"
    local container_name="${BASE_NAME}-${variant}"
    
    echo ""
    echo "=========================================="
    log_build "Testing: ${variant}"
    log_build "Dockerfile: ${dockerfile}"
    echo "=========================================="
    
    # Check if dockerfile exists
    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found: $dockerfile"
        return 1
    fi
    
    # Build image
    log_build "Building ${variant} image for ARM64..."
    local build_start=$(date +%s)
    
    if docker build --platform linux/arm64 -f "$dockerfile" -t "$image_name" . 2>&1; then
        local build_end=$(date +%s)
        local build_time=$((build_end - build_start))
        log_success "Build completed in ${build_time}s"
        
        # Get image size
        local size=$(docker images "$image_name" --format "{{.Size}}")
        log_info "Image size: $size"
    else
        log_error "Build failed for $variant"
        return 1
    fi
    
    # Find available port
    local test_port=$PORT
    while lsof -Pi :$test_port -sTCP:LISTEN -t >/dev/null 2>&1; do
        ((test_port++))
    done
    
    log_info "Using port: $test_port"
    
    # Start container
    log_info "Starting container..."
    local start_time=$(date +%s)
    
    if docker run -d \
        --name "$container_name" \
        --platform linux/arm64 \
        -p "${test_port}:8080" \
        -v "${PWD}/data:/app/data" \
        "$image_name"; then
        log_success "Container started"
    else
        log_error "Failed to start container"
        return 1
    fi
    
    # Wait for container to be ready
    log_info "Waiting for container to be ready..."
    local ready=false
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ] && [ "$ready" != "true" ]; do
        if curl -sf "http://localhost:${test_port}/health" >/dev/null 2>&1; then
            ready=true
            local end_time=$(date +%s)
            local startup_time=$((end_time - start_time))
            log_success "Container ready in ${startup_time}s"
        else
            sleep 2
            ((attempts++))
        fi
    done
    
    if [ "$ready" != "true" ]; then
        log_error "Container failed to become ready"
        docker logs "$container_name" | head -20
        return 1
    fi
    
    # Test main application
    log_info "Testing main application..."
    if curl -sf "http://localhost:${test_port}/" >/dev/null 2>&1; then
        log_success "Main application accessible"
    else
        log_error "Main application not accessible"
        return 1
    fi
    
    # Test Custom API Builder
    log_info "Testing Custom API Builder..."
    if curl -sf "http://localhost:${test_port}/custom-api/" >/dev/null 2>&1; then
        log_success "Custom API Builder accessible"
    else
        log_error "Custom API Builder not accessible"
        return 1
    fi
    
    # Test Custom API endpoints
    log_info "Testing Custom API list endpoint..."
    local list_response=$(curl -s "http://localhost:${test_port}/custom-api/list" 2>/dev/null)
    if echo "$list_response" | grep -q '"count"'; then
        log_success "Custom API endpoints working"
    else
        log_error "Custom API endpoints not working"
        echo "Response: $list_response"
        return 1
    fi
    
    # Create test API
    log_info "Creating test Custom API..."
    local create_response=$(curl -s -X POST "http://localhost:${test_port}/custom-api/create" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test API",
            "endpoint": "/test",
            "method": "POST", 
            "processing_logic": "calculation",
            "parameters": [
                {"name": "calculation_type", "type": "string", "required": true, "default_value": "basic_math"},
                {"name": "a", "type": "float", "required": true},
                {"name": "b", "type": "float", "required": true},
                {"name": "operation", "type": "string", "required": true, "default_value": "add"}
            ]
        }' 2>/dev/null)
    
    if echo "$create_response" | grep -q "created successfully"; then
        log_success "Custom API created successfully"
    else
        log_error "Custom API creation failed"
        echo "Response: $create_response"
        return 1
    fi
    
    # Wait for API registration
    sleep 3
    
    # Test the custom API
    log_info "Testing created Custom API..."
    local api_response=$(curl -s -X POST "http://localhost:${test_port}/api/custom/test" \
        -H "Content-Type: application/json" \
        -d '{"calculation_type": "basic_math", "a": 15, "b": 10, "operation": "add"}' 2>/dev/null)
    
    if echo "$api_response" | grep -q '"result": 25'; then
        log_success "Custom API working! (15 + 10 = 25 ✓)"
    else
        log_error "Custom API execution failed"
        echo "Response: $api_response"
        return 1
    fi
    
    # Stop container
    log_info "Stopping container..."
    docker stop "$container_name" >/dev/null 2>&1 || true
    docker rm "$container_name" >/dev/null 2>&1 || true
    
    log_success "✅ ${variant} variant PASSED all tests!"
    return 0
}

# Main execution
echo "🔍 Available Docker variants:"
echo ""

# Test each variant
variants_passed=0
total_variants=0

# Test 1: Simple variant
if [ -f "Dockerfile.webgui.simple" ]; then
    ((total_variants++))
    if test_variant "simple" "Dockerfile.webgui.simple"; then
        ((variants_passed++))
    fi
fi

# Test 2: Ultra-slim variant  
if [ -f "Dockerfile.webgui.ultra-slim" ]; then
    ((total_variants++))
    if test_variant "ultra-slim" "Dockerfile.webgui.ultra-slim"; then
        ((variants_passed++))
    fi
fi

# Test 3: Compiled variant
if [ -f "Dockerfile.webgui.compiled" ]; then
    ((total_variants++))
    if test_variant "compiled" "Dockerfile.webgui.compiled"; then
        ((variants_passed++))
    fi
fi

# Test 4: Compiled-optimized variant
if [ -f "Dockerfile.webgui.compiled-optimized" ]; then
    ((total_variants++))
    if test_variant "compiled-optimized" "Dockerfile.webgui.compiled-optimized"; then
        ((variants_passed++))
    fi
fi

echo ""
echo "🎯 FINAL RESULTS"
echo "================="
echo "Variants tested: $total_variants"
echo "Variants passed: $variants_passed"
echo ""

if [ $variants_passed -eq $total_variants ] && [ $total_variants -gt 0 ]; then
    log_success "🎉 ALL ARM64 VARIANTS PASSED!"
    echo ""
    echo "✅ All Docker images work perfectly with Custom API integration"
    echo "✅ Ready for production deployment on ARM64 platforms"
    echo "✅ Custom API Builder fully functional across all variants"
    exit 0
elif [ $variants_passed -gt 0 ]; then
    log_error "⚠️  Some variants passed ($variants_passed/$total_variants)"
    exit 1
else
    log_error "❌ All variants failed"
    exit 1
fi
