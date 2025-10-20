#!/bin/bash
set -e

# REDLINE Web Interface Entrypoint
# Optimized for web-only deployment

echo "🚀 Starting REDLINE Web Interface..."

# Function to handle shutdown gracefully
cleanup() {
    echo "🛑 Shutting down REDLINE Web Interface..."
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Set default environment variables
export WEB_PORT=${WEB_PORT:-8080}
export FLASK_APP=web_app.py
export FLASK_ENV=production
export FLASK_DEBUG=0

# Create necessary directories
mkdir -p data data/converted data/downloaded data/stooq_format

# Start the web application
echo "🌐 Starting Flask web server on port $WEB_PORT..."
python web_app.py &
WEB_PID=$!

# Wait for the web server to start
sleep 5

# Check if the web server is running
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "❌ Failed to start web server"
    exit 1
fi

echo "✅ REDLINE Web Interface started successfully"
echo "🌐 Web interface available at: http://localhost:$WEB_PORT"

# Wait for the web server process
wait $WEB_PID
