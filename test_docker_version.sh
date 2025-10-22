#!/bin/bash

# Test script to verify Docker version compatibility

echo "🧪 TESTING DOCKER VERSION COMPATIBILITY"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✅ Docker is running"

# Check Docker version
echo ""
echo "Docker version information:"
docker --version

# Extract version numbers
docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
docker_major=$(echo $docker_version | cut -d. -f1)
docker_minor=$(echo $docker_version | cut -d. -f2)

echo "Major version: $docker_major"
echo "Minor version: $docker_minor"

# Check Buildx support
echo ""
echo "Checking Buildx support..."

if [ "$docker_major" -gt 20 ] || ([ "$docker_major" -eq 20 ] && [ "$docker_minor" -ge 10 ]); then
    echo "✅ Modern Docker detected (Buildx supported)"
    
    # Test Buildx
    if docker buildx version > /dev/null 2>&1; then
        echo "✅ Buildx is available"
        
        # Test Buildx without --platform flag
        echo "Testing Buildx without --platform flag..."
        docker buildx build --help | grep -q "platform" && echo "✅ --platform flag supported" || echo "⚠️ --platform flag not supported"
    else
        echo "❌ Buildx not available"
    fi
else
    echo "⚠️ Older Docker detected (Buildx may not be supported)"
    echo "Will use regular docker build"
fi

# Test universal Dockerfile
echo ""
echo "Testing universal Dockerfile..."

if [ -f "Dockerfile.webgui.universal" ]; then
    echo "✅ Dockerfile.webgui.universal found"
    
    # Test syntax
    echo "Testing Dockerfile syntax..."
    docker build --file Dockerfile.webgui.universal --target=base --dry-run . 2>/dev/null || {
        echo "❌ Dockerfile syntax error"
        exit 1
    }
    
    echo "✅ Dockerfile syntax is correct"
else
    echo "❌ Dockerfile.webgui.universal not found"
fi

echo ""
echo "✅ Docker version compatibility test completed"
