#!/bin/bash

# Docker Compose Troubleshooting Script

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

print_header() {
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_header "DOCKER COMPOSE TROUBLESHOOTING"
echo ""

# 1. Check Docker daemon
print_status "1. Checking Docker daemon..."
if docker info >/dev/null 2>&1; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon not running!"
    print_status "Start with: sudo systemctl start docker"
    exit 1
fi

echo ""

# 2. Check Docker Compose
print_status "2. Checking Docker Compose..."
if command -v docker-compose >/dev/null 2>&1; then
    print_success "Docker Compose available: $(docker-compose --version)"
else
    print_error "Docker Compose not found!"
    exit 1
fi

echo ""

# 3. Check docker-compose.yml
print_status "3. Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml exists"
    
    # Check syntax
    if docker-compose config >/dev/null 2>&1; then
        print_success "docker-compose.yml syntax is valid"
    else
        print_error "docker-compose.yml has syntax errors!"
        print_status "Run: docker-compose config"
        exit 1
    fi
else
    print_error "docker-compose.yml not found!"
    exit 1
fi

echo ""

# 4. Check Dockerfile
print_status "4. Checking Dockerfile..."
if [ -f "Dockerfile.webgui.universal" ]; then
    print_success "Dockerfile.webgui.universal exists"
elif [ -f "Dockerfile.webgui.simple" ]; then
    print_success "Dockerfile.webgui.simple exists"
elif [ -f "Dockerfile.webgui" ]; then
    print_success "Dockerfile.webgui exists"
else
    print_error "No suitable Dockerfile found!"
    print_status "Available Dockerfiles:"
    ls -la Dockerfile* 2>/dev/null || echo "No Dockerfiles found"
fi

echo ""

# 5. Check port conflicts
print_status "5. Checking port conflicts..."
if netstat -tuln 2>/dev/null | grep -q ":8080 "; then
    print_warning "Port 8080 is in use"
    netstat -tuln | grep ":8080"
fi

if netstat -tuln 2>/dev/null | grep -q ":6080 "; then
    print_warning "Port 6080 is in use"
    netstat -tuln | grep ":6080"
fi

echo ""

# 6. Check Docker images
print_status "6. Checking Docker images..."
if docker images | grep -q "redline-webgui"; then
    print_success "redline-webgui image exists"
else
    print_warning "redline-webgui image not found - will be built"
fi

echo ""

# 7. Check Docker containers
print_status "7. Checking existing containers..."
if docker ps -a | grep -q "redline-web-app"; then
    print_warning "redline-web-app container exists"
    print_status "Existing containers:"
    docker ps -a | grep redline
fi

echo ""

# 8. Try to start services with verbose output
print_status "8. Attempting to start services with verbose output..."
print_status "Running: docker-compose up -d"
docker-compose up -d

echo ""

# 9. Check service status
print_status "9. Checking service status..."
docker-compose ps

echo ""

# 10. Show logs if there are issues
print_status "10. Checking logs..."
if docker-compose ps | grep -q "Exit"; then
    print_error "Some services failed to start!"
    print_status "Recent logs:"
    docker-compose logs --tail=20
else
    print_success "Services appear to be running"
fi

echo ""
print_status "Troubleshooting complete!"
print_status "If issues persist, check: docker-compose logs -f"
