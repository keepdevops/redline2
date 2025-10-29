#!/bin/bash

# REDLINE Ultra Slim Docker Hub Push Script
# Push the new ultra-slim images (70% smaller ARM64!)

set -e

echo "🚀 REDLINE Ultra Slim Docker Hub Push"
echo "====================================="
echo ""

# Check Docker Hub login
if ! docker info | grep -q "Username:"; then
    echo "❌ Not logged into Docker Hub!"
    echo ""
    echo "Please run: docker login"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Docker Hub login confirmed"
echo ""

echo "📊 ULTRA SLIM SIZE ACHIEVEMENTS:"
echo "  ARM64: 4.72GB → 1.40GB (70% smaller!)"
echo "  AMD64: 1.71GB → 1.40GB (18% smaller)"
echo ""

# Load and tag ultra slim images
echo "🏷️ Loading and tagging ultra slim images..."
echo ""

echo "Loading AMD64 ultra slim..."
docker load -i redline-webgui-ultra-slim-amd64.tar
docker tag redline-webgui-ultra-slim:amd64 keepdevops/redline:v1.0.0-amd64-ultra-slim

echo "Loading ARM64 ultra slim..."
docker load -i redline-webgui-ultra-slim-arm64.tar
docker tag redline-webgui-ultra-slim:arm64 keepdevops/redline:v1.0.0-arm64-ultra-slim

echo ""
echo "📦 Images ready to push:"
docker images keepdevops/redline:v1.0.0-*ultra-slim --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
echo ""

# Ask for confirmation
read -p "🚀 Push ultra slim images to Docker Hub? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Push cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting Docker Hub push (much faster with smaller images!)..."
echo ""

# Push AMD64 ultra slim (most important for Dell machine)
echo "📤 Pushing AMD64 ultra slim (Dell machine - 1.40GB)..."
docker push keepdevops/redline:v1.0.0-amd64-ultra-slim
echo "✅ AMD64 ultra slim pushed successfully"
echo ""

# Push ARM64 ultra slim (much smaller now!)
echo "📤 Pushing ARM64 ultra slim (Apple Silicon - 1.40GB, was 4.72GB!)..."
docker push keepdevops/redline:v1.0.0-arm64-ultra-slim
echo "✅ ARM64 ultra slim pushed successfully"
echo ""

echo "🎉 Ultra Slim Images Pushed to Docker Hub Successfully!"
echo ""
echo "📋 Available Docker Images:"
echo "  Production (Ultra Slim):"
echo "  • keepdevops/redline:v1.0.0-amd64-ultra-slim   (Dell machine - 1.40GB)"
echo "  • keepdevops/redline:v1.0.0-arm64-ultra-slim   (Apple Silicon - 1.40GB)"
echo ""
echo "  Development (Full Features):"
echo "  • keepdevops/redline:v1.0.0-amd64-optimized    (Dell machine - 1.71GB)"
echo "  • keepdevops/redline:v1.0.0-arm64-optimized    (Apple Silicon - 4.72GB)"
echo ""
echo "🔗 Docker Hub Repository: https://hub.docker.com/r/keepdevops/redline"
echo ""
echo "📖 Usage Examples:"
echo ""
echo "For Dell Machine (Production - Ultra Slim):"
echo "  docker pull keepdevops/redline:v1.0.0-amd64-ultra-slim"
echo "  docker run -d --name redline-webgui -p 8080:8080 keepdevops/redline:v1.0.0-amd64-ultra-slim"
echo ""
echo "For Apple Silicon (Production - Ultra Slim):"
echo "  docker pull keepdevops/redline:v1.0.0-arm64-ultra-slim"
echo "  docker run -d --name redline-webgui -p 8080:8080 keepdevops/redline:v1.0.0-arm64-ultra-slim"
echo ""
echo "🎯 Benefits of Ultra Slim:"
echo "  • ⚡ Same 20% performance improvement"
echo "  • 📦 70% smaller ARM64 downloads"
echo "  • 💾 Faster Docker Hub push/pull"
echo "  • 🔒 Smaller attack surface"
echo "  • 💰 Lower bandwidth costs"
echo ""

echo "🔄 Next Steps:"
echo "1. Update GitHub release notes with ultra slim options"
echo "2. Test the deployed images"
echo "3. Update documentation"
echo ""
