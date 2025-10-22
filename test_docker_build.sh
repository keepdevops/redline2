#!/bin/bash

# Test script to verify Docker build works

echo "🧪 TESTING DOCKER BUILD"
echo "======================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✅ Docker is running"

# Test the simplified Dockerfile
echo ""
echo "Testing simplified Dockerfile..."

if [ -f "Dockerfile.webgui.simple" ]; then
    echo "✅ Dockerfile.webgui.simple found"
    
    # Try to build (just test the first few steps)
    echo "Testing Docker build (first few steps)..."
    docker build -f Dockerfile.webgui.simple --target=base -t redline-webgui-test . || {
        echo "❌ Docker build failed"
        echo "Trying alternative approach..."
        
        # Try building with more verbose output
        docker build -f Dockerfile.webgui.simple -t redline-webgui-test . --progress=plain
    }
else
    echo "❌ Dockerfile.webgui.simple not found"
fi

echo ""
echo "✅ Docker build test completed"