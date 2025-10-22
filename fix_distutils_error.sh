#!/bin/bash

# Fix Docker Compose distutils error script

echo "🔧 FIXING DOCKER COMPOSE DISTUTILS ERROR"
echo "========================================"
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
sudo apt install -y python3-distutils

# Also install setuptools as it often includes distutils
echo "Installing setuptools..."
sudo apt install -y python3-setuptools

# Install via pip as well (often needed)
echo "Installing setuptools via pip..."
pip3 install setuptools

echo ""
echo "✅ VERIFICATION:"
python3 -c "import distutils" 2>/dev/null && echo "✅ distutils now available" || echo "❌ distutils still missing"

echo ""
echo "🧪 TESTING DOCKER COMPOSE..."
if command -v docker-compose > /dev/null 2>&1; then
    echo "Testing docker-compose command..."
    docker-compose --version 2>/dev/null && echo "✅ Docker Compose working" || echo "❌ Docker Compose still has issues"
else
    echo "❌ Docker Compose not found"
fi

echo ""
echo "🔧 ALTERNATIVE SOLUTION (if above doesn't work):"
echo "Install Docker Compose via pip instead of apt:"
echo "pip3 install docker-compose"

echo ""
echo "✅ Distutils fix completed"
