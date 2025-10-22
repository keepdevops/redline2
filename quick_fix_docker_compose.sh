#!/bin/bash

# Quick Docker Compose Fix Script for Test Machine

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

print_header "QUICK DOCKER COMPOSE FIX"
echo ""

# Step 1: Remove existing installations
print_status "Step 1: Cleaning existing installations..."
sudo apt remove -y docker-compose docker-compose-plugin 2>/dev/null || true
pip3 uninstall -y docker-compose 2>/dev/null || true

# Step 2: Install Python dependencies
print_status "Step 2: Installing Python dependencies..."
sudo apt update
sudo apt install -y python3-distutils python3-setuptools python3-pip
pip3 install setuptools

# Step 3: Install Docker Compose via pip (most reliable)
print_status "Step 3: Installing Docker Compose via pip..."
pip3 install docker-compose

# Step 4: Create symlink if needed
if [ ! -f /usr/local/bin/docker-compose ]; then
    print_status "Creating symlink..."
    sudo ln -sf $(which docker-compose) /usr/local/bin/docker-compose 2>/dev/null || true
fi

# Step 5: Verify installation
print_status "Step 4: Verifying installation..."
if command -v docker-compose >/dev/null 2>&1; then
    print_success "Docker Compose installed successfully"
    docker-compose --version
else
    print_error "Docker Compose installation failed"
    exit 1
fi

# Step 6: Test functionality
print_status "Step 5: Testing functionality..."
timeout 10 docker-compose --help >/dev/null 2>&1 && print_success "Docker Compose is working" || print_warning "Docker Compose may have issues"

echo ""
print_success "Fix completed! Try Option 4 again: ./install_redline_fixed.sh"
