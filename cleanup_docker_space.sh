#!/bin/bash
# Clean up Docker disk space to fix "No space left on device" error

set -e

echo "🧹 Docker Disk Space Cleanup"
echo "============================"
echo ""

# Show current usage
echo "📊 Current Docker disk usage:"
docker system df
echo ""

# Ask for confirmation
read -p "This will remove unused Docker resources. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 0
fi

echo ""
echo "🧹 Cleaning up Docker resources..."

# Remove unused volumes (21.58GB available)
echo "1. Removing unused volumes..."
docker volume prune -f

# Remove unused images
echo "2. Removing unused images..."
docker image prune -a -f

# Remove build cache
echo "3. Removing build cache..."
docker builder prune -a -f

# Remove stopped containers
echo "4. Removing stopped containers..."
docker container prune -f

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Updated Docker disk usage:"
docker system df
echo ""
echo "🔄 Next steps:"
echo "1. Restart Redline: docker-compose restart"
echo "2. Or rebuild: docker-compose up -d --build"
echo ""

