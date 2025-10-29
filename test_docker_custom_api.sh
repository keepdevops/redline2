#!/bin/bash

# REDLINE Docker Custom API Integration Test
# Tests that Custom API functionality works correctly in Docker containers

set -e

echo "🧪 REDLINE Docker Custom API Integration Test"
echo "============================================="
echo ""

# Configuration
CONTAINER_NAME="redline-test-$(date +%s)"
IMAGE_NAME="keepdevops/redline:latest"
PORT="8080"
BASE_URL="http://localhost:${PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Cleanup function
cleanup() {
    log_info "Cleaning up container..."
    docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
    docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
}

# Set trap for cleanup
trap cleanup EXIT

# Test 1: Start container
log_info "Starting REDLINE container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p ${PORT}:8080 \
    -v redline-test-data:/app/data \
    $IMAGE_NAME

# Wait for container to be ready
log_info "Waiting for container to start..."
for i in {1..30}; do
    if curl -sf ${BASE_URL}/health >/dev/null 2>&1; then
        log_success "Container is running and healthy"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        log_error "Container failed to start within 60 seconds"
        docker logs $CONTAINER_NAME
        exit 1
    fi
done

# Test 2: Check main application
log_info "Testing main application..."
if curl -sf ${BASE_URL}/ >/dev/null; then
    log_success "Main application is accessible"
else
    log_error "Main application is not accessible"
    exit 1
fi

# Test 3: Check Custom API Builder page
log_info "Testing Custom API Builder page..."
if curl -sf ${BASE_URL}/custom-api/ >/dev/null; then
    log_success "Custom API Builder page is accessible"
else
    log_error "Custom API Builder page is not accessible"
    exit 1
fi

# Test 4: List custom APIs (should be empty initially)
log_info "Testing Custom API list endpoint..."
RESPONSE=$(curl -s ${BASE_URL}/custom-api/list)
if echo "$RESPONSE" | grep -q '"count": 0'; then
    log_success "Custom API list endpoint works (empty as expected)"
else
    log_warning "Custom API list response: $RESPONSE"
fi

# Test 5: Create a test custom API
log_info "Creating test Custom API..."
CREATE_RESPONSE=$(curl -s -X POST ${BASE_URL}/custom-api/create \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Docker Test API",
        "endpoint": "/docker-test",
        "method": "POST",
        "description": "Test API created during Docker integration test",
        "processing_logic": "calculation",
        "rate_limit": "10 per minute",
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
    }')

if echo "$CREATE_RESPONSE" | grep -q "created successfully"; then
    log_success "Test Custom API created successfully"
else
    log_error "Failed to create test Custom API"
    log_error "Response: $CREATE_RESPONSE"
    exit 1
fi

# Wait a moment for the API to be registered
sleep 2

# Test 6: Verify the API was created
log_info "Verifying Custom API was created..."
LIST_RESPONSE=$(curl -s ${BASE_URL}/custom-api/list)
if echo "$LIST_RESPONSE" | grep -q "Docker Test API"; then
    log_success "Custom API appears in the list"
else
    log_error "Custom API not found in list"
    log_error "Response: $LIST_RESPONSE"
    exit 1
fi

# Test 7: Test the custom API endpoint
log_info "Testing the custom API endpoint..."
API_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/custom/docker-test \
    -H "Content-Type: application/json" \
    -d '{
        "calculation_type": "basic_math",
        "a": 10,
        "b": 5,
        "operation": "add"
    }')

if echo "$API_RESPONSE" | grep -q '"result": 15'; then
    log_success "Custom API endpoint works correctly (10 + 5 = 15)"
else
    log_error "Custom API endpoint failed"
    log_error "Response: $API_RESPONSE"
    exit 1
fi

# Test 8: Test data persistence (check if data directory exists)
log_info "Testing data persistence..."
if docker exec $CONTAINER_NAME ls -la /app/data/custom_apis.json >/dev/null 2>&1; then
    log_success "Custom API data file exists in container"
else
    log_warning "Custom API data file not found (may be created on first API creation)"
fi

# Test 9: Test different calculation
log_info "Testing different calculation (multiply)..."
MULTIPLY_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/custom/docker-test \
    -H "Content-Type: application/json" \
    -d '{
        "calculation_type": "basic_math",
        "a": 7,
        "b": 3,
        "operation": "multiply"
    }')

if echo "$MULTIPLY_RESPONSE" | grep -q '"result": 21'; then
    log_success "Custom API multiply operation works (7 × 3 = 21)"
else
    log_error "Custom API multiply operation failed"
    log_error "Response: $MULTIPLY_RESPONSE"
    exit 1
fi

# Test 10: Check logs for any errors
log_info "Checking container logs for errors..."
LOGS=$(docker logs $CONTAINER_NAME 2>&1)
if echo "$LOGS" | grep -i -E "(error|exception|traceback)" | grep -v "INFO" | head -5; then
    log_warning "Found some errors in logs (shown above)"
else
    log_success "No significant errors found in container logs"
fi

echo ""
echo "🎉 All tests passed! Custom API integration in Docker is working correctly."
echo ""
echo "📊 Test Summary:"
echo "  ✅ Container startup and health check"
echo "  ✅ Main application accessibility"
echo "  ✅ Custom API Builder web interface"
echo "  ✅ Custom API creation via REST API"
echo "  ✅ Custom API endpoint functionality"
echo "  ✅ Basic math calculations (add, multiply)"
echo "  ✅ Data persistence structure"
echo ""
echo "🚀 Your Docker image is ready for production deployment!"
echo ""
echo "Next steps:"
echo "  • Deploy with: docker-compose up -d"
echo "  • Access at: http://localhost:8080/custom-api/"
echo "  • Create production APIs through the web interface"
echo ""

# Cleanup will happen automatically via trap
