#!/bin/bash

# REDLINE Docker Hub Push Fix Script
# Handles repository creation and proper tagging

set -e

echo "🔧 REDLINE Docker Hub Push Fix"
echo "==============================="
echo ""

# Get current Docker Hub username
echo "🔍 Checking Docker Hub login..."
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon not running"
    exit 1
fi

# Try to get username from docker info
USERNAME=$(docker system info --format '{{.Username}}' 2>/dev/null || echo "")

if [ -z "$USERNAME" ]; then
    echo "❌ Not logged into Docker Hub"
    echo ""
    echo "Please run: docker login"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Logged in as: $USERNAME"
echo ""

# Check if we need to retag images
if [ "$USERNAME" != "keepdevops" ]; then
    echo "🏷️  Retagging images for username: $USERNAME"
    echo ""
    
    # Retag all images
    docker tag redline-webgui-compiled:amd64 $USERNAME/redline:v1.0.0-amd64-standard
    docker tag redline-webgui-compiled-optimized:amd64 $USERNAME/redline:v1.0.0-amd64-optimized
    docker tag redline-webgui-compiled:arm64 $USERNAME/redline:v1.0.0-arm64-standard
    docker tag redline-webgui-compiled-optimized:arm64 $USERNAME/redline:v1.0.0-arm64-optimized
    
    echo "✅ Images retagged for $USERNAME/redline"
    echo ""
fi

# Show images to push
echo "📦 Images ready to push:"
docker images $USERNAME/redline:v1.0.0-* --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
echo ""

# Check if repository exists by trying a small push test
echo "🔍 Checking if repository $USERNAME/redline exists..."
if docker push $USERNAME/redline:v1.0.0-amd64-optimized --quiet >/dev/null 2>&1; then
    echo "✅ Repository exists and accessible"
else
    echo "❌ Repository doesn't exist or no push access"
    echo ""
    echo "📋 To fix this:"
    echo "1. Go to: https://hub.docker.com/repository/create"
    echo "2. Repository name: redline"
    echo "3. Visibility: Public"
    echo "4. Click 'Create'"
    echo ""
    echo "Or create via command line:"
    echo "curl -X POST https://hub.docker.com/v2/repositories/ \\"
    echo "  -H \"Authorization: JWT \$(docker login --username $USERNAME --password-stdin <<< 'YOUR_PASSWORD' 2>&1 | grep 'Login Succeeded')\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"name\": \"redline\", \"namespace\": \"$USERNAME\", \"is_private\": false}'"
    echo ""
    read -p "Press Enter after creating the repository..."
fi

echo ""
echo "🚀 Starting push of optimized images (most important)..."
echo ""

# Push AMD64 optimized (most important for Dell)
echo "📤 Pushing AMD64 optimized (Dell machine)..."
docker push $USERNAME/redline:v1.0.0-amd64-optimized
echo "✅ AMD64 optimized pushed successfully"
echo ""

# Push ARM64 optimized (most important for Apple Silicon)
echo "📤 Pushing ARM64 optimized (Apple Silicon)..."
docker push $USERNAME/redline:v1.0.0-arm64-optimized
echo "✅ ARM64 optimized pushed successfully"
echo ""

echo "🎉 Critical images pushed successfully!"
echo ""
echo "📋 Available Docker Images:"
echo "  • $USERNAME/redline:v1.0.0-amd64-optimized   (Dell machine - Production)"
echo "  • $USERNAME/redline:v1.0.0-arm64-optimized   (Apple Silicon - Production)"
echo ""
echo "🔗 Docker Hub Repository: https://hub.docker.com/r/$USERNAME/redline"
echo ""
echo "📖 Usage Examples:"
echo ""
echo "For Dell Machine:"
echo "  docker pull $USERNAME/redline:v1.0.0-amd64-optimized"
echo "  docker run -d --name redline-webgui -p 8080:8080 $USERNAME/redline:v1.0.0-amd64-optimized"
echo ""
echo "For Apple Silicon:"
echo "  docker pull $USERNAME/redline:v1.0.0-arm64-optimized"
echo "  docker run -d --name redline-webgui -p 8080:8080 $USERNAME/redline:v1.0.0-arm64-optimized"
echo ""

# Ask about standard images
echo "❓ Push standard images too? (4.6GB each, for development)"
read -p "Push standard images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Pushing AMD64 standard..."
    docker push $USERNAME/redline:v1.0.0-amd64-standard
    echo "📤 Pushing ARM64 standard..."
    docker push $USERNAME/redline:v1.0.0-arm64-standard
    echo "✅ All images pushed!"
else
    echo "⏭️  Skipped standard images (can push later if needed)"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Update GitHub release notes with: $USERNAME/redline"
echo "2. Create GitHub release with native installations"
echo "3. Test complete workflow"
echo ""
