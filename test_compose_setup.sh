#!/bin/bash

# Test Docker Compose Setup Script

echo "🧪 TESTING DOCKER COMPOSE SETUP"
echo "==============================="
echo ""

# Check if files exist
echo "📋 Checking required files:"
[ -f "docker-compose.yml" ] && echo "✅ docker-compose.yml exists" || echo "❌ docker-compose.yml missing"
[ -f "start_compose.sh" ] && echo "✅ start_compose.sh exists" || echo "❌ start_compose.sh missing"
[ -f "Dockerfile.webgui.simple" ] && echo "✅ Dockerfile.webgui.simple exists" || echo "❌ Dockerfile.webgui.simple missing"

echo ""

# Check Docker Compose
echo "🐳 Checking Docker Compose:"
if command -v docker-compose >/dev/null 2>&1; then
    echo "✅ Docker Compose installed: $(docker-compose --version)"
else
    echo "❌ Docker Compose not found"
fi

echo ""

# Check Docker daemon
echo "🔧 Checking Docker daemon:"
if docker info >/dev/null 2>&1; then
    echo "✅ Docker daemon running"
else
    echo "❌ Docker daemon not running"
fi

echo ""

# Test Docker Compose syntax
echo "📝 Testing Docker Compose syntax:"
if docker-compose config >/dev/null 2>&1; then
    echo "✅ docker-compose.yml syntax is valid"
else
    echo "❌ docker-compose.yml has syntax errors"
    echo "Run: docker-compose config"
fi

echo ""
echo "🚀 Ready to test! Run: ./start_compose.sh"
