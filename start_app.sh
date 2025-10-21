#!/bin/bash

# REDLINE Web GUI Startup Script
# Starts Redis server and Flask application

set -e

echo "=== REDLINE Web GUI Startup ==="

# Set environment variables for proper Docker binding
export HOST=0.0.0.0
export WEB_PORT=8080
export DEBUG=false

echo "Environment variables set:"
echo "  HOST=$HOST"
echo "  WEB_PORT=$WEB_PORT"
echo "  DEBUG=$DEBUG"

# Start Redis server in background
echo "Starting Redis server..."
redis-server --daemonize yes --bind 127.0.0.1 --port 6379

# Wait a moment for Redis to start
sleep 2

# Check if Redis is running
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis server started successfully"
else
    echo "❌ Redis server failed to start"
    exit 1
fi

# Start Flask application
echo "Starting Flask application on $HOST:$WEB_PORT..."
exec python3.9 web_app_safe.py
