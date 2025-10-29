#!/bin/bash

# REDLINE Docker Hub Push Script
# This script pushes all compiled Docker images to Docker Hub

set -e

echo "🐳 REDLINE Docker Hub Push Script"
echo "=================================="
echo ""

# Check if user is logged in to Docker Hub
echo "🔐 Checking Docker Hub login..."
if ! docker info | grep -q "Username:"; then
    echo "❌ Not logged in to Docker Hub!"
    echo ""
    echo "Please run: docker login"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Docker Hub login confirmed"
echo ""

# Display images to be pushed
echo "📦 Images to push:"
docker images keepdevops/redline:v1.0.0-* --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
echo ""

# Ask for confirmation
read -p "🚀 Push all 4 images to Docker Hub? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Push cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting Docker Hub push..."
echo ""

# Push AMD64 optimized (most important for Dell machine)
echo "📤 Pushing AMD64 optimized (recommended for Dell)..."
docker push keepdevops/redline:v1.0.0-amd64-optimized
echo "✅ AMD64 optimized pushed successfully"
echo ""

# Push ARM64 optimized (most important for Apple Silicon)
echo "📤 Pushing ARM64 optimized (recommended for Apple Silicon)..."
docker push keepdevops/redline:v1.0.0-arm64-optimized
echo "✅ ARM64 optimized pushed successfully"
echo ""

# Push AMD64 standard (development)
echo "📤 Pushing AMD64 standard (development)..."
docker push keepdevops/redline:v1.0.0-amd64-standard
echo "✅ AMD64 standard pushed successfully"
echo ""

# Push ARM64 standard (development)
echo "📤 Pushing ARM64 standard (development)..."
docker push keepdevops/redline:v1.0.0-arm64-standard
echo "✅ ARM64 standard pushed successfully"
echo ""

echo "🎉 All Docker images pushed to Docker Hub successfully!"
echo ""
echo "📋 Docker Hub Images:"
echo "  • keepdevops/redline:v1.0.0-amd64-optimized   (Dell machine - Production)"
echo "  • keepdevops/redline:v1.0.0-arm64-optimized   (Apple Silicon - Production)"
echo "  • keepdevops/redline:v1.0.0-amd64-standard    (Dell machine - Development)"
echo "  • keepdevops/redline:v1.0.0-arm64-standard    (Apple Silicon - Development)"
echo ""
echo "🔗 Docker Hub Repository: https://hub.docker.com/r/keepdevops/redline"
echo ""
echo "📖 Usage Examples:"
echo ""
echo "For Dell Machine (Production):"
echo "  docker pull keepdevops/redline:v1.0.0-amd64-optimized"
echo "  docker run -d --name redline-webgui -p 8080:8080 keepdevops/redline:v1.0.0-amd64-optimized"
echo ""
echo "For Apple Silicon (Production):"
echo "  docker pull keepdevops/redline:v1.0.0-arm64-optimized"
echo "  docker run -d --name redline-webgui -p 8080:8080 keepdevops/redline:v1.0.0-arm64-optimized"
echo ""
