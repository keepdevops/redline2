#!/usr/bin/env bash

# REDLINE ARM64 Docker Images Comprehensive Test
# Builds and tests all Docker image variants for ARM64 architecture
# Tests Custom API functionality in each image

set -e

echo "🚀 REDLINE ARM64 Docker Images Comprehensive Test"
echo "================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_build() {
    echo -e "${PURPLE}🔨 $1${NC}"
}

log_test() {
    echo -e "${CYAN}🧪 $1${NC}"
}

# Configuration
BASE_NAME="redline-test"
PORT_BASE=8080
TEST_TIMEOUT=60
BUILD_TIMEOUT=600

# Docker image variants to test
declare -A DOCKER_VARIANTS=(
    ["simple"]="Dockerfile.webgui.simple"
    ["ultra-slim"]="Dockerfile.webgui.ultra-slim"
    ["compiled-optimized"]="Dockerfile.webgui.compiled-optimized"
    ["compiled"]="Dockerfile.webgui.compiled"
)

# Results tracking
declare -A BUILD_RESULTS
declare -A TEST_RESULTS
declare -A IMAGE_SIZES
declare -A STARTUP_TIMES

# Cleanup function
cleanup() {
    log_info "Cleaning up containers and images..."
    for variant in "${!DOCKER_VARIANTS[@]}"; do
        docker stop "${BASE_NAME}-${variant}" 2>/dev/null || true
        docker rm "${BASE_NAME}-${variant}" 2>/dev/null || true
    done
}

# Set trap for cleanup
trap cleanup EXIT

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is busy
    else
        return 0  # Port is available
    fi
}

# Function to find available port
find_available_port() {
    local base_port=$1
    local port=$base_port
    while ! check_port $port; do
        ((port++))
        if [ $port -gt $((base_port + 100)) ]; then
            log_error "No available ports found in range ${base_port}-${port}"
            return 1
        fi
    done
    echo $port
}

# Function to build Docker image
build_image() {
    local variant=$1
    local dockerfile=$2
    local image_name="${BASE_NAME}-${variant}"
    
    log_build "Building ${variant} image using ${dockerfile}..."
    
    local start_time=$(date +%s)
    
    if timeout $BUILD_TIMEOUT docker build \
        --platform linux/arm64 \
        -f "$dockerfile" \
        -t "$image_name" \
        . >/dev/null 2>&1; then
        
        local end_time=$(date +%s)
        local build_time=$((end_time - start_time))
        
        # Get image size
        local size=$(docker images "$image_name" --format "{{.Size}}")
        IMAGE_SIZES[$variant]=$size
        
        BUILD_RESULTS[$variant]="SUCCESS (${build_time}s)"
        log_success "${variant} image built successfully in ${build_time}s (Size: ${size})"
        return 0
    else
        BUILD_RESULTS[$variant]="FAILED"
        log_error "${variant} image build failed"
        return 1
    fi
}

# Function to test Docker image
test_image() {
    local variant=$1
    local image_name="${BASE_NAME}-${variant}"
    local container_name="${BASE_NAME}-${variant}"
    
    log_test "Testing ${variant} image..."
    
    # Find available port
    local port=$(find_available_port $PORT_BASE)
    if [ $? -ne 0 ]; then
        TEST_RESULTS[$variant]="PORT_ERROR"
        return 1
    fi
    
    local base_url="http://localhost:${port}"
    local start_time=$(date +%s)
    
    # Start container
    log_info "Starting ${variant} container on port ${port}..."
    if ! docker run -d \
        --name "$container_name" \
        --platform linux/arm64 \
        -p "${port}:8080" \
        -v "${PWD}/data:/app/data" \
        "$image_name" >/dev/null 2>&1; then
        
        TEST_RESULTS[$variant]="START_FAILED"
        log_error "${variant} container failed to start"
        return 1
    fi
    
    # Wait for container to be ready
    log_info "Waiting for ${variant} container to be ready..."
    local ready=false
    local attempts=0
    local max_attempts=$((TEST_TIMEOUT / 2))
    
    while [ $attempts -lt $max_attempts ] && [ "$ready" != "true" ]; do
        if curl -sf "${base_url}/health" >/dev/null 2>&1; then
            ready=true
            local end_time=$(date +%s)
            local startup_time=$((end_time - start_time))
            STARTUP_TIMES[$variant]="${startup_time}s"
            log_success "${variant} container ready in ${startup_time}s"
        else
            sleep 2
            ((attempts++))
        fi
    done
    
    if [ "$ready" != "true" ]; then
        TEST_RESULTS[$variant]="TIMEOUT"
        log_error "${variant} container failed to become ready within ${TEST_TIMEOUT}s"
        docker logs "$container_name" | tail -10
        return 1
    fi
    
    # Test main application
    log_test "Testing ${variant} main application..."
    if ! curl -sf "${base_url}/" >/dev/null 2>&1; then
        TEST_RESULTS[$variant]="MAIN_APP_FAILED"
        log_error "${variant} main application not accessible"
        return 1
    fi
    
    # Test Custom API Builder page
    log_test "Testing ${variant} Custom API Builder..."
    if ! curl -sf "${base_url}/custom-api/" >/dev/null 2>&1; then
        TEST_RESULTS[$variant]="CUSTOM_API_PAGE_FAILED"
        log_error "${variant} Custom API Builder page not accessible"
        return 1
    fi
    
    # Test Custom API endpoints
    log_test "Testing ${variant} Custom API endpoints..."
    local list_response=$(curl -s "${base_url}/custom-api/list" 2>/dev/null)
    if ! echo "$list_response" | grep -q '"count"'; then
        TEST_RESULTS[$variant]="CUSTOM_API_ENDPOINTS_FAILED"
        log_error "${variant} Custom API endpoints not working"
        return 1
    fi
    
    # Create and test a custom API
    log_test "Creating test Custom API in ${variant}..."
    local create_response=$(curl -s -X POST "${base_url}/custom-api/create" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Calculator '${variant}'",
            "endpoint": "/test-calc-'${variant}'",
            "method": "POST",
            "description": "Test calculator for '${variant}' variant",
            "processing_logic": "calculation",
            "parameters": [
                {
                    "name": "calculation_type",
                    "type": "string",
                    "required": true,
                    "default_value": "basic_math"
                },
                {
                    "name": "a",
                    "type": "float",
                    "required": true
                },
                {
                    "name": "b",
                    "type": "float",
                    "required": true
                },
                {
                    "name": "operation",
                    "type": "string",
                    "required": true,
                    "default_value": "add"
                }
            ]
        }' 2>/dev/null)
    
    if ! echo "$create_response" | grep -q "created successfully"; then
        TEST_RESULTS[$variant]="CUSTOM_API_CREATE_FAILED"
        log_error "${variant} Custom API creation failed"
        return 1
    fi
    
    # Wait a moment for API to be registered
    sleep 2
    
    # Test the created custom API
    log_test "Testing created Custom API in ${variant}..."
    local api_response=$(curl -s -X POST "${base_url}/api/custom/test-calc-${variant}" \
        -H "Content-Type: application/json" \
        -d '{
            "calculation_type": "basic_math",
            "a": 10,
            "b": 5,
            "operation": "add"
        }' 2>/dev/null)
    
    if echo "$api_response" | grep -q '"result": 15'; then
        TEST_RESULTS[$variant]="SUCCESS"
        log_success "${variant} all tests passed! (10 + 5 = 15 ✓)"
        return 0
    else
        TEST_RESULTS[$variant]="CUSTOM_API_EXECUTION_FAILED"
        log_error "${variant} Custom API execution failed"
        log_error "Response: $api_response"
        return 1
    fi
}

# Function to stop and remove container
cleanup_container() {
    local variant=$1
    local container_name="${BASE_NAME}-${variant}"
    
    log_info "Cleaning up ${variant} container..."
    docker stop "$container_name" >/dev/null 2>&1 || true
    docker rm "$container_name" >/dev/null 2>&1 || true
}

# Main test execution
echo "🔍 Checking available Docker files..."
for variant in "${!DOCKER_VARIANTS[@]}"; do
    dockerfile="${DOCKER_VARIANTS[$variant]}"
    if [ -f "$dockerfile" ]; then
        log_success "Found $dockerfile"
    else
        log_error "Missing $dockerfile"
        unset DOCKER_VARIANTS[$variant]
    fi
done

echo ""
echo "🏗️ BUILDING ALL ARM64 IMAGES"
echo "============================="

# Build all images
for variant in "${!DOCKER_VARIANTS[@]}"; do
    dockerfile="${DOCKER_VARIANTS[$variant]}"
    echo ""
    build_image "$variant" "$dockerfile"
done

echo ""
echo "🧪 TESTING ALL ARM64 IMAGES"
echo "============================"

# Test all images
for variant in "${!DOCKER_VARIANTS[@]}"; do
    if [ "${BUILD_RESULTS[$variant]}" = "SUCCESS"* ]; then
        echo ""
        test_image "$variant"
        cleanup_container "$variant"
    else
        TEST_RESULTS[$variant]="SKIPPED (build failed)"
        log_warning "Skipping ${variant} test due to build failure"
    fi
done

echo ""
echo "📊 COMPREHENSIVE TEST RESULTS"
echo "=============================="
echo ""

# Results table header
printf "%-20s %-25s %-15s %-12s %-12s %s\n" "VARIANT" "BUILD STATUS" "TEST RESULT" "IMAGE SIZE" "STARTUP" "DOCKERFILE"
echo "$(printf '%.0s-' {1..120})"

# Results table data
for variant in "${!DOCKER_VARIANTS[@]}"; do
    dockerfile="${DOCKER_VARIANTS[$variant]}"
    build_status="${BUILD_RESULTS[$variant]:-NOT_BUILT}"
    test_status="${TEST_RESULTS[$variant]:-NOT_TESTED}"
    image_size="${IMAGE_SIZES[$variant]:-N/A}"
    startup_time="${STARTUP_TIMES[$variant]:-N/A}"
    
    # Color coding
    if [[ "$build_status" == "SUCCESS"* && "$test_status" == "SUCCESS" ]]; then
        color=$GREEN
    elif [[ "$build_status" == "FAILED" || "$test_status" == *"FAILED" ]]; then
        color=$RED
    else
        color=$YELLOW
    fi
    
    printf "${color}%-20s %-25s %-15s %-12s %-12s %s${NC}\n" \
        "$variant" "$build_status" "$test_status" "$image_size" "$startup_time" "$dockerfile"
done

echo ""
echo "🎯 SUMMARY"
echo "=========="

# Count results
successful_builds=0
successful_tests=0
total_variants=${#DOCKER_VARIANTS[@]}

for variant in "${!DOCKER_VARIANTS[@]}"; do
    if [[ "${BUILD_RESULTS[$variant]}" == "SUCCESS"* ]]; then
        ((successful_builds++))
    fi
    if [[ "${TEST_RESULTS[$variant]}" == "SUCCESS" ]]; then
        ((successful_tests++))
    fi
done

echo "📈 Build Results: ${successful_builds}/${total_variants} successful"
echo "🧪 Test Results: ${successful_tests}/${total_variants} successful"

if [ $successful_tests -eq $total_variants ]; then
    echo ""
    log_success "🎉 ALL ARM64 IMAGES PASSED! Your Custom API integration works perfectly across all variants!"
    echo ""
    echo "🚀 Ready for production deployment on ARM64 platforms (Apple Silicon, ARM servers)"
    exit 0
elif [ $successful_tests -gt 0 ]; then
    echo ""
    log_warning "⚠️  Some images passed, some failed. Check individual results above."
    exit 1
else
    echo ""
    log_error "❌ All tests failed. Check the build and test logs above."
    exit 1
fi
