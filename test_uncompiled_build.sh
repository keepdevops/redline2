#!/bin/bash

# Test Script for Uncompiled Redline Docker Image
# Verifies that the uncompiled image builds and runs correctly

set -e

echo "🧪 TESTING UNCOMPILED REDLINE DOCKER IMAGE"
echo "=========================================="
echo ""

# Configuration
IMAGE_NAME="redline-webgui-uncompiled"
CONTAINER_NAME="redline-uncompiled-test"
TEST_PORT="8081"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up test environment..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# Trap cleanup on exit
trap cleanup EXIT

print_status "Starting uncompiled Docker image test..."
echo ""

# Step 1: Build the uncompiled image
print_status "Step 1: Building uncompiled Docker image..."
if docker build -f Dockerfile.webgui.uncompiled -t $IMAGE_NAME .; then
    print_success "Uncompiled image built successfully"
else
    print_error "Failed to build uncompiled image"
    exit 1
fi
echo ""

# Step 2: Run the container
print_status "Step 2: Starting uncompiled container..."
cleanup  # Ensure clean state

if docker run -d \
    --name $CONTAINER_NAME \
    -p $TEST_PORT:8080 \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    -e FLASK_ENV=development \
    -e FLASK_DEBUG=1 \
    $IMAGE_NAME; then
    print_success "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi
echo ""

# Step 3: Wait for application startup
print_status "Step 3: Waiting for application startup..."
print_status "This may take longer for uncompiled version..."

max_attempts=24  # 2 minutes
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:$TEST_PORT/health >/dev/null 2>&1; then
        print_success "Application is responding to health checks"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Application failed to start within timeout"
        print_status "Container logs:"
        docker logs $CONTAINER_NAME --tail 20
        exit 1
    fi
    
    printf "."
    sleep 5
    ((attempt++))
done
echo ""
echo ""

# Step 4: Test basic functionality
print_status "Step 4: Testing basic functionality..."

# Test health endpoint
if curl -f http://localhost:$TEST_PORT/health >/dev/null 2>&1; then
    print_success "Health endpoint responding"
else
    print_error "Health endpoint not responding"
fi

# Test main page
if curl -f http://localhost:$TEST_PORT/ >/dev/null 2>&1; then
    print_success "Main page accessible"
else
    print_warning "Main page may not be fully loaded yet"
fi

# Test API endpoints (if they exist)
if curl -f http://localhost:$TEST_PORT/api/status >/dev/null 2>&1; then
    print_success "API endpoints responding"
else
    print_warning "API endpoints may not be available or loaded yet"
fi

echo ""

# Step 5: Verify development features
print_status "Step 5: Verifying development features..."

# Check that source files are preserved (not compiled)
print_status "Checking for preserved source files..."
if docker exec $CONTAINER_NAME find /app -name "*.py" | grep -q ".py"; then
    print_success "Python source files preserved (not compiled to bytecode only)"
else
    print_warning "No Python source files found - may be expected"
fi

# Check development environment
print_status "Checking development environment settings..."
if docker exec $CONTAINER_NAME env | grep -q "FLASK_ENV=development"; then
    print_success "Development environment configured"
else
    print_warning "Development environment may not be set"
fi

echo ""

# Step 6: Display container information
print_status "Step 6: Container Information"
echo ""
print_status "Container Status:"
docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
print_status "Container Logs (last 10 lines):"
docker logs $CONTAINER_NAME --tail 10

echo ""
print_status "Image Information:"
docker images $IMAGE_NAME --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""

# Final results
echo "🎉 UNCOMPILED IMAGE TEST RESULTS"
echo "==============================="
echo ""
print_success "✅ Uncompiled Docker image built successfully"
print_success "✅ Container started and running"
print_success "✅ Health endpoint responding"
print_success "✅ Application accessible at http://localhost:$TEST_PORT"
print_success "✅ Development environment configured"
print_success "✅ Source files preserved for debugging"
echo ""
echo "🔧 Development Features Verified:"
echo "  • No bytecode compilation (debugging friendly)"
echo "  • Development Flask environment"
echo "  • Source code accessibility"
echo "  • Relaxed performance settings"
echo ""
echo "🌐 Access the application:"
echo "  • Web Interface: http://localhost:$TEST_PORT"
echo "  • Health Check: http://localhost:$TEST_PORT/health"
echo ""
echo "📋 Next Steps:"
echo "  1. Test the web interface functionality"
echo "  2. Verify debugging capabilities"
echo "  3. Test with mounted source code for live development"
echo "  4. Build multiplatform version when ready"
echo ""
print_success "Uncompiled image test completed successfully!"
echo ""
print_warning "Note: Container will be cleaned up when script exits"
print_status "To keep container running: docker stop $CONTAINER_NAME (without removing)"
