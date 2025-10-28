#!/bin/bash
#
# REDLINE Ubuntu Test Script for Optimized Docker Build
# Tests the optimized Docker build on Ubuntu test machine
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check system requirements
check_requirements() {
    print_header "Checking System Requirements"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        exit 1
    fi
    print_success "Docker installed: $(docker --version)"
    
    # Check Docker Compose (optional)
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose installed: $(docker-compose --version)"
    else
        print_warning "Docker Compose not installed (optional)"
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 5 ]; then
        print_warning "Low disk space: ${AVAILABLE_SPACE}G available (need at least 5G)"
    else
        print_success "Sufficient disk space: ${AVAILABLE_SPACE}G"
    fi
    
    # Check available memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 2 ]; then
        print_warning "Low memory: ${TOTAL_MEM}G available (recommend at least 2G)"
    else
        print_success "Sufficient memory: ${TOTAL_MEM}G"
    fi
}

# Clean up previous test containers
cleanup() {
    print_header "Cleaning Up Previous Tests"
    
    if docker ps -a --format "{{.Names}}" | grep -q "^redline-webgui-test$"; then
        docker stop redline-webgui-test >/dev/null 2>&1 || true
        docker rm redline-webgui-test >/dev/null 2>&1 || true
        print_success "Removed old test container"
    fi
    
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "redline-webgui:latest"; then
        read -p "Remove existing redline-webgui:latest image? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker rmi redline-webgui:latest
            print_success "Removed existing image"
        fi
    fi
}

# Build the optimized Docker image
build_image() {
    print_header "Building Optimized Docker Image"
    
    print_status "Building image with BuildKit cache..."
    DOCKER_BUILDKIT=1 docker build -f Dockerfile.webgui.simple -t redline-webgui:latest . || {
        print_error "Docker build failed"
        exit 1
    }
    
    # Show image size
    IMAGE_SIZE=$(docker images redline-webgui:latest --format "{{.Size}}")
    print_success "Image built successfully: ${IMAGE_SIZE}"
    
    # Show layers
    print_status "Image layers:"
    docker history redline-webgui:latest --format "table {{.CreatedBy}}\t{{.Size}}" | head -10
}

# Test the container
test_container() {
    print_header "Testing Container"
    
    # Start container
    print_status "Starting container..."
    docker run -d \
        --name redline-webgui-test \
        -p 8080:8080 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        --restart unless-stopped \
        redline-webgui:latest || {
        print_error "Failed to start container"
        exit 1
    }
    
    print_success "Container started"
    
    # Wait for health check
    print_status "Waiting for application to be healthy..."
    for i in {1..30}; do
        if docker exec redline-webgui-test curl -sf http://localhost:8080/health >/dev/null 2>&1; then
            print_success "Application is healthy"
            break
        fi
        sleep 1
    done
    
    # Check container status
    CONTAINER_STATUS=$(docker inspect redline-webgui-test --format='{{.State.Status}}')
    print_status "Container status: $CONTAINER_STATUS"
    
    # Show running processes
    print_status "Running processes (should show 2 Gunicorn workers):"
    docker exec redline-webgui-test ps aux | grep -E '(gunicorn|python)' | grep -v grep
    
    # Show container stats
    print_status "Container resource usage:"
    docker stats redline-webgui-test --no-stream
    
    # Test web interface
    print_status "Testing web interface..."
    if curl -sf http://localhost:8080/ >/dev/null; then
        print_success "Web interface is accessible"
    else
        print_error "Web interface not accessible"
    fi
}

# Test features
test_features() {
    print_header "Testing Application Features"
    
    # Test health endpoint
    print_status "Testing /health endpoint..."
    curl -sf http://localhost:8080/health >/dev/null && print_success "Health check passed" || print_error "Health check failed"
    
    # Test API status
    print_status "Testing /api/status endpoint..."
    curl -sf http://localhost:8080/api/status >/dev/null && print_success "API status endpoint works" || print_error "API status failed"
    
    # Check for minified assets
    print_status "Checking for minified assets..."
    docker exec redline-webgui-test ls -lh /app/redline/web/static/js/*.min.js >/dev/null 2>&1 && \
        print_success "Minified JavaScript files found" || print_warning "Minified JavaScript not found"
    docker exec redline-webgui-test ls -lh /app/redline/web/static/css/*.min.css >/dev/null 2>&1 && \
        print_success "Minified CSS files found" || print_warning "Minified CSS not found"
    
    # Check Gunicorn workers
    print_status "Checking Gunicorn workers..."
    WORKER_COUNT=$(docker exec redline-webgui-test ps aux | grep -c '[g]unicorn.*worker' || true)
    if [ "$WORKER_COUNT" -ge 2 ]; then
        print_success "Gunicorn workers running: $WORKER_COUNT"
    else
        print_warning "Expected 2 Gunicorn workers, found: $WORKER_COUNT"
    fi
    
    # Test database connectivity
    print_status "Testing database connectivity..."
    docker exec redline-webgui-test python3 -c "from redline.database.connector import DatabaseConnector; db = DatabaseConnector(); print('Database available:', db.is_available())" && \
        print_success "Database connectivity works" || print_warning "Database connectivity issue"
}

# Performance test
test_performance() {
    print_header "Performance Testing"
    
    # Test concurrent requests
    print_status "Testing concurrent request handling..."
    for i in {1..10}; do
        curl -sf http://localhost:8080/health >/dev/null &
    done
    wait
    
    # Response time test
    print_status "Testing response time..."
    START_TIME=$(date +%s%N)
    curl -sf http://localhost:8080/health >/dev/null
    END_TIME=$(date +%s%N)
    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
    print_success "Health endpoint response time: ${RESPONSE_TIME}ms"
    
    # Container resource usage
    print_status "Resource usage after load:"
    docker stats redline-webgui-test --no-stream
}

# Show logs
show_logs() {
    print_header "Container Logs (last 20 lines)"
    docker logs --tail 20 redline-webgui-test
}

# Main execution
main() {
    print_header "REDLINE Optimized Docker Test on Ubuntu"
    echo ""
    
    check_requirements
    cleanup
    build_image
    test_container
    test_features
    test_performance
    show_logs
    
    echo ""
    print_header "Test Complete"
    echo ""
    print_success "Container is running at: http://localhost:8080"
    echo ""
    print_status "Useful commands:"
    echo "  View logs:     docker logs -f redline-webgui-test"
    echo "  Stop container: docker stop redline-webgui-test"
    echo "  Remove container: docker rm redline-webgui-test"
    echo "  Shell access:   docker exec -it redline-webgui-test bash"
    echo ""
}

# Run main
main

