#!/bin/bash

# Fix Docker Compose distutils error script

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

print_header "FIXING DOCKER COMPOSE DISTUTILS ERROR"
echo ""

# Check Python version
echo "Python version:"
python3 --version

# Check if distutils is available
echo ""
echo "Checking distutils availability..."
python3 -c "import distutils" 2>/dev/null && echo "✅ distutils available" || echo "❌ distutils missing"

echo ""
echo "📦 INSTALLING MISSING DISTUTILS..."

# Install python3-distutils
echo "Installing python3-distutils..."
sudo apt update
sudo apt install -y python3-distutils python3-setuptools python3-pip

# Also install setuptools as it often includes distutils
echo "Installing setuptools..."
pip3 install setuptools

echo ""
echo "✅ VERIFICATION:"
python3 -c "import distutils" 2>/dev/null && echo "✅ distutils now available" || echo "❌ distutils still missing"

echo ""
echo "🔄 REINSTALLING DOCKER COMPOSE..."

# Remove existing Docker Compose
echo "Removing existing Docker Compose..."
sudo apt remove -y docker-compose docker-compose-plugin 2>/dev/null || true
pip3 uninstall -y docker-compose 2>/dev/null || true

# Install Docker Compose via pip (most reliable with distutils)
echo "Installing Docker Compose via pip..."
pip3 install docker-compose

# Create symlink if needed
if [ ! -f /usr/local/bin/docker-compose ]; then
    echo "Creating symlink..."
    sudo ln -sf $(which docker-compose) /usr/local/bin/docker-compose 2>/dev/null || true
fi

echo ""
echo "🧪 TESTING DOCKER COMPOSE..."
if command -v docker-compose >/dev/null 2>&1; then
    echo "Testing docker-compose command..."
    docker-compose --version 2>/dev/null && echo "✅ Docker Compose working" || echo "❌ Docker Compose still has issues"
else
    echo "❌ Docker Compose not found"
fi

echo ""
echo "🔧 ALTERNATIVE SOLUTION (if above doesn't work):"
echo "Use Docker Compose V2 (docker compose instead of docker-compose):"
echo "sudo apt install docker-compose-plugin"
echo "docker compose --version"

echo ""
echo "✅ Distutils fix completed"
echo "Try running: ./start_compose.sh"
