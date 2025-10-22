#!/bin/bash

# REDLINE Docker Compose Startup Script
# Simple web app + web GUI setup

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

print_header "STARTING REDLINE WITH DOCKER COMPOSE"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose not found!"
    print_status "Please run: ./install_redline_fixed.sh and choose option 4"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon not running!"
    print_status "Please start Docker: sudo systemctl start docker"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found!"
    print_status "Please run: ./install_redline_fixed.sh and choose option 4"
    exit 1
fi

print_status "Starting REDLINE services..."

# Start services
docker-compose up -d

# Check if services started successfully
if [ $? -eq 0 ]; then
    print_success "Services started successfully!"
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Web App:     http://localhost:8080"
    echo "  🖥️  Web GUI:     http://localhost:6080"
    echo "  🔑 VNC Password: redline123"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop:      docker-compose down"
    echo ""
    
    # Wait a moment and check service status
    sleep 5
    print_status "Checking service status..."
    docker-compose ps
else
    print_error "Failed to start services!"
    print_status "Check logs: docker-compose logs"
    exit 1
fi
