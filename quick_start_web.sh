#!/bin/bash

# Quick Start Script for REDLINE Flask Web Application
# Simple script to start the web app with minimal configuration

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [PORT]"
    echo ""
    echo "Options:"
    echo "  PORT     Port number to run on (default: 8082)"
    echo "  -h, --help   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Start on default port 8082"
    echo "  $0 8080      # Start on port 8080"
    exit 0
fi

echo "🚀 Starting REDLINE Flask Web Application..."

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install flask flask-socketio flask-compress
fi

# Check if pandas is installed (required by REDLINE)
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "📦 Installing pandas..."
    pip3 install pandas
fi

# Set default port
export WEB_PORT=${1:-8082}
export HOST="0.0.0.0"
export DEBUG="false"

# Kill existing process on port if any
if lsof -ti :$WEB_PORT >/dev/null 2>&1; then
    echo "🔄 Stopping existing process on port $WEB_PORT..."
    kill -9 $(lsof -ti :$WEB_PORT) 2>/dev/null || true
    sleep 2
fi

# Create data directories if they don't exist
mkdir -p data/uploads data/converted logs

echo "🌐 Starting Flask app on port $WEB_PORT..."
echo "📱 Access your app at: http://localhost:$WEB_PORT"
echo "🎨 Look for the floating palette button (🎨) to customize colors!"
echo ""
echo "Press Ctrl+C to stop the application"

# Start the Flask application
python3 web_app.py
