#!/bin/bash

# REDLINE Web-Based GUI Stop Script
# Stops and removes the REDLINE Docker container

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

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_header "Stopping REDLINE Web-Based GUI"

# Check if container exists
if ! docker ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^redline-webgui$"; then
    print_warning "REDLINE container not found"
    echo "Container may have already been stopped or removed"
    exit 0
fi

# Check if container is running
if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^redline-webgui$"; then
    print_status "Stopping container..."
    docker stop redline-webgui
    
    if [ $? -eq 0 ]; then
        print_success "Container stopped"
    else
        print_warning "Failed to stop container (may already be stopped)"
    fi
else
    print_status "Container was already stopped"
fi

# Ask if user wants to remove the container
echo ""
read -p "Remove container? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing container..."
    docker rm redline-webgui
    
    if [ $? -eq 0 ]; then
        print_success "Container removed"
    else
        print_warning "Failed to remove container"
    fi
else
    print_status "Container kept (data preserved)"
    print_status "To remove: docker rm redline-webgui"
fi

echo ""
print_success "REDLINE stopped"
echo "To start again: ./start_webgui.sh"
