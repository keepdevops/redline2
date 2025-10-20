#!/bin/bash

# Script to clear browser cache and start Flask web app
# Usage: ./start_web_app.sh

echo "🚀 Starting Redline Web App Setup..."

# Function to clear browser cache
clear_browser_cache() {
    echo "🧹 Clearing browser cache..."
    
    # Clear Safari cache
    echo "  - Clearing Safari cache..."
    osascript -e 'tell application "Safari" to quit' 2>/dev/null
    sleep 2
    
    # Try to clear Safari cache directories
    rm -rf ~/Library/Caches/com.apple.Safari/* 2>/dev/null
    rm -rf ~/Library/Safari/LocalStorage/* 2>/dev/null
    rm -rf ~/Library/Safari/Databases/* 2>/dev/null
    
    # Clear Chrome cache (if exists)
    echo "  - Clearing Chrome cache..."
    rm -rf ~/Library/Caches/Google/Chrome/* 2>/dev/null
    
    # Clear Firefox cache (if exists)
    echo "  - Clearing Firefox cache..."
    rm -rf ~/Library/Caches/Firefox/* 2>/dev/null
    
    # Clear Edge cache (if exists)
    echo "  - Clearing Edge cache..."
    rm -rf ~/Library/Caches/com.microsoft.edgemac/* 2>/dev/null
    
    echo "✅ Browser cache cleared"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        echo "   Stopping existing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 2
    fi
}

# Function to start Flask app
start_flask_app() {
    echo "🌐 Starting Flask web application..."
    
    # Check if web_app.py exists
    if [ ! -f "web_app.py" ]; then
        echo "❌ Error: web_app.py not found in current directory"
        exit 1
    fi
    
    # Check and free up port 5000 (default Flask port)
    check_port 5000
    
    # Set Flask environment variables
    export FLASK_APP=web_app.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export WEB_PORT=5000
    
    echo "📡 Starting Flask server on http://localhost:5000"
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    # Start Flask app in background and capture PID
    python3 web_app.py &
    FLASK_PID=$!
    
    # Save PID to file for easy stopping
    echo $FLASK_PID > flask_app.pid
    
    # Wait a moment for Flask to start
    sleep 3
    
    # Check if Flask started successfully
    if ps -p $FLASK_PID > /dev/null; then
        echo "✅ Flask application started successfully (PID: $FLASK_PID)"
        echo "🌐 Open your browser and navigate to: http://localhost:5000"
        echo "📝 Flask PID saved to: flask_app.pid"
        
        # Try to open browser automatically
        echo "🔗 Opening browser..."
        open http://localhost:5000 2>/dev/null || echo "   Please manually open http://localhost:5000 in your browser"
        
        # Keep script running to show logs
        echo "📊 Flask logs (Press Ctrl+C to stop):"
        echo "----------------------------------------"
        wait $FLASK_PID
    else
        echo "❌ Failed to start Flask application"
        exit 1
    fi
}

# Main execution
echo "=========================================="
echo "🚀 Redline Web App Startup Script"
echo "=========================================="

# Clear browser cache
clear_browser_cache

# Start Flask application
start_flask_app