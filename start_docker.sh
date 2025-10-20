#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Docker Services..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not available, cannot start Docker services"
    echo "💡 Use start_web.sh for web interface instead"
    exit 1
fi

# Check if docker-compose.yml exists
if [[ -f "docker-compose.yml" ]]; then
    docker-compose up -d
    echo "✅ REDLINE Docker services started"
    echo "🌐 Web interface: http://localhost:8080"
else
    echo "❌ docker-compose.yml not found"
    echo "💡 Use start_web.sh for web interface instead"
fi
