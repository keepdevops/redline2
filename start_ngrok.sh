#!/bin/bash
# Start REDLINE with ngrok tunnel
# Usage: ./start_ngrok.sh

set -e

echo "🚀 Starting REDLINE with ngrok..."
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed."
    echo ""
    echo "Install ngrok:"
    echo "  macOS:   brew install ngrok/ngrok/ngrok"
    echo "  Linux:   See https://ngrok.com/download"
    echo "  Windows: Download from https://ngrok.com/download"
    exit 1
fi

# Stop existing container if running
if docker ps -a --format '{{.Names}}' | grep -q "^redline-ngrok$"; then
    echo "🛑 Stopping existing container..."
    docker stop redline-ngrok 2>/dev/null || true
    docker rm redline-ngrok 2>/dev/null || true
fi

# Start REDLINE container
echo "🐳 Starting REDLINE container..."
docker run -d \
  --name redline-ngrok \
  -p 8080:8080 \
  -e FLASK_ENV=production \
  -e FLASK_APP=web_app.py \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  -e CORS_ORIGINS="https://*.ngrok-free.app,https://*.ngrok.io" \
  keepdevops/redline:latest

# Wait for container to be ready
echo "⏳ Waiting for REDLINE to start..."
for i in {1..30}; do
    if curl -f http://localhost:8080/health &> /dev/null; then
        echo "✅ REDLINE is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  REDLINE may not be ready yet, but continuing..."
    fi
    sleep 1
done

# Check if ngrok auth token is set
if [ -z "$NGROK_AUTH_TOKEN" ]; then
    echo ""
    echo "⚠️  NGROK_AUTH_TOKEN not set."
    echo "   Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    read -p "Enter your ngrok auth token (or press Enter to skip): " TOKEN
    if [ -n "$TOKEN" ]; then
        ngrok config add-authtoken "$TOKEN"
        export NGROK_AUTH_TOKEN="$TOKEN"
    fi
fi

# Start ngrok
echo ""
echo "🌐 Starting ngrok tunnel..."
echo "   Access ngrok web interface at: http://localhost:4040"
echo "   Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    docker stop redline-ngrok 2>/dev/null || true
    docker rm redline-ngrok 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start ngrok
ngrok http 8080

