#!/bin/bash

# Fix Docker Compose installation script

echo "🔧 FIXING DOCKER COMPOSE INSTALLATION"
echo "====================================="
echo ""

# Check current Docker Compose status
echo "Current Docker Compose status:"
if command -v docker-compose > /dev/null 2>&1; then
    echo "Found: $(which docker-compose)"
    docker-compose --version 2>/dev/null || echo "Error: Cannot get version"
else
    echo "Docker Compose not found in PATH"
fi

echo ""
echo "🔍 Checking for conflicting installations..."

# Check for pip installation
if pip3 show docker-compose > /dev/null 2>&1; then
    echo "Found pip installation:"
    pip3 show docker-compose | grep Version
fi

# Check for apt installation
if dpkg -l | grep -q docker-compose; then
    echo "Found apt installation:"
    dpkg -l | grep docker-compose
fi

echo ""
echo "🧹 CLEANING UP CONFLICTING INSTALLATIONS..."

# Remove pip installation if it exists
if pip3 show docker-compose > /dev/null 2>&1; then
    echo "Removing pip installation..."
    pip3 uninstall -y docker-compose || true
fi

# Remove apt installation if it exists
if dpkg -l | grep -q docker-compose; then
    echo "Removing apt installation..."
    sudo apt remove -y docker-compose || true
fi

# Remove any standalone installations
if [ -f "/usr/local/bin/docker-compose" ]; then
    echo "Removing standalone installation..."
    sudo rm -f /usr/local/bin/docker-compose
fi

echo ""
echo "📦 INSTALLING DOCKER COMPOSE PROPERLY..."

# Install via apt (recommended for Ubuntu 24.04)
echo "Installing via apt..."
sudo apt update
sudo apt install -y docker-compose

# Verify installation
echo ""
echo "✅ VERIFICATION:"
if command -v docker-compose > /dev/null 2>&1; then
    echo "Docker Compose installed successfully:"
    docker-compose --version
else
    echo "❌ Installation failed, trying alternative method..."
    
    # Try standalone installation as fallback
    echo "Installing standalone version..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    if command -v docker-compose > /dev/null 2>&1; then
        echo "✅ Standalone installation successful:"
        docker-compose --version
    else
        echo "❌ All installation methods failed"
        exit 1
    fi
fi

echo ""
echo "🧪 TESTING DOCKER COMPOSE..."
docker-compose --help > /dev/null 2>&1 && echo "✅ Docker Compose working correctly" || echo "❌ Docker Compose still has issues"

echo ""
echo "✅ Docker Compose installation fix completed"
