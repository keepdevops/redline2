#!/bin/bash

# Test Docker Compose Installation Script

echo "🧪 TESTING DOCKER COMPOSE INSTALLATION"
echo "======================================"
echo ""

# Test Python dependencies
echo "📋 Testing Python dependencies:"
python3 -c "import distutils" 2>/dev/null && echo "✅ distutils available" || echo "❌ distutils missing"
python3 -c "import setuptools" 2>/dev/null && echo "✅ setuptools available" || echo "❌ setuptools missing"

echo ""

# Test Docker Compose
echo "🐳 Testing Docker Compose:"
if command -v docker-compose >/dev/null 2>&1; then
    echo "✅ Docker Compose installed: $(docker-compose --version)"
    
    # Test Docker Compose functionality
    echo ""
    echo "🔧 Testing Docker Compose functionality:"
    timeout 10 docker-compose --help >/dev/null 2>&1 && echo "✅ Docker Compose responds" || echo "❌ Docker Compose not responding"
    
    # Test Docker Compose config
    if [ -f "docker-compose.yml" ]; then
        echo ""
        echo "📝 Testing docker-compose.yml syntax:"
        docker-compose config >/dev/null 2>&1 && echo "✅ docker-compose.yml syntax is valid" || echo "❌ docker-compose.yml has syntax errors"
    else
        echo "⚠️ docker-compose.yml not found"
    fi
else
    echo "❌ Docker Compose not found"
fi

echo ""

# Test Docker daemon
echo "🔧 Testing Docker daemon:"
if docker info >/dev/null 2>&1; then
    echo "✅ Docker daemon running"
else
    echo "❌ Docker daemon not running"
    echo "   Start with: sudo systemctl start docker"
fi

echo ""
echo "🎯 If all tests pass, Docker Compose installation is working!"