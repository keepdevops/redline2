#!/bin/bash

# Test script to verify Docker Buildx works

echo "🧪 TESTING DOCKER BUILDX"
echo "======================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✅ Docker is running"

# Check if Buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "❌ Docker Buildx not available"
    echo "Installing Docker Buildx..."
    docker buildx install || {
        echo "❌ Failed to install Docker Buildx"
        exit 1
    }
fi

echo "✅ Docker Buildx is available"

# Create a test builder
echo ""
echo "Creating test builder..."
docker buildx create --name test-builder --use 2>/dev/null || docker buildx use test-builder 2>/dev/null || true

# Test Buildx
echo ""
echo "Testing Buildx..."
docker buildx inspect --bootstrap || {
    echo "❌ Buildx inspection failed"
    exit 1
}

echo "✅ Buildx is working"

# Test the Buildx-compatible Dockerfile
echo ""
echo "Testing Buildx-compatible Dockerfile..."

if [ -f "Dockerfile.webgui.buildx" ]; then
    echo "✅ Dockerfile.webgui.buildx found"
    
    # Test build (just syntax check)
    echo "Testing Dockerfile syntax..."
    docker buildx build --file Dockerfile.webgui.buildx --target=base --dry-run . || {
        echo "❌ Dockerfile syntax error"
        exit 1
    }
    
    echo "✅ Dockerfile syntax is correct"
else
    echo "❌ Dockerfile.webgui.buildx not found"
fi

echo ""
echo "✅ Docker Buildx test completed"
