#!/bin/bash

# Script to stop Flask web app and clear browser cache
# Usage: ./stop_web_app.sh

echo "🛑 Stopping Redline Web App..."

# Function to stop Flask app
stop_flask_app() {
    echo "🌐 Stopping Flask web application..."
    
    # Method 1: Stop using PID file
    if [ -f "flask_app.pid" ]; then
        FLASK_PID=$(cat flask_app.pid)
        if ps -p $FLASK_PID > /dev/null 2>&1; then
            echo "  - Stopping Flask process (PID: $FLASK_PID)..."
            kill $FLASK_PID 2>/dev/null
            sleep 2
            
            # Force kill if still running
            if ps -p $FLASK_PID > /dev/null 2>&1; then
                echo "  - Force stopping Flask process..."
                kill -9 $FLASK_PID 2>/dev/null
            fi
            echo "✅ Flask application stopped"
        else
            echo "⚠️  Flask process not found (may have already stopped)"
        fi
        rm -f flask_app.pid
    else
        echo "⚠️  No PID file found, searching for Flask processes..."
    fi
    
    # Method 2: Stop any remaining Flask/web_app.py processes
    echo "  - Searching for any remaining Flask processes..."
    PIDS=$(pgrep -f "python.*web_app.py" 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo "  - Found Flask processes: $PIDS"
        echo $PIDS | xargs kill -9 2>/dev/null
        echo "✅ Remaining Flask processes stopped"
    fi
    
    # Method 3: Stop any process on port 5000
    echo "  - Checking port 5000..."
    PORT_PID=$(lsof -ti:5000 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "  - Found process on port 5000 (PID: $PORT_PID)"
        kill -9 $PORT_PID 2>/dev/null
        echo "✅ Process on port 5000 stopped"
    fi
    
    # Method 4: Stop any process on port 8080 (original port)
    echo "  - Checking port 8080..."
    PORT_PID=$(lsof -ti:8080 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "  - Found process on port 8080 (PID: $PORT_PID)"
        kill -9 $PORT_PID 2>/dev/null
        echo "✅ Process on port 8080 stopped"
    fi
    
    # Verify Flask is stopped
    if ! pgrep -f "python.*web_app.py" > /dev/null; then
        echo "✅ All Flask processes stopped successfully"
    else
        echo "⚠️  Some Flask processes may still be running"
    fi
}

# Function to clear browser cache
clear_browser_cache() {
    echo "🧹 Clearing browser cache..."
    
    # Close Safari first
    echo "  - Closing Safari..."
    osascript -e 'tell application "Safari" to quit' 2>/dev/null
    
    # Close Chrome (if running)
    echo "  - Closing Chrome..."
    osascript -e 'tell application "Google Chrome" to quit' 2>/dev/null
    
    # Close Firefox (if running)
    echo "  - Closing Firefox..."
    osascript -e 'tell application "Firefox" to quit' 2>/dev/null
    
    # Wait for browsers to close
    sleep 3
    
    # Clear Safari cache
    echo "  - Clearing Safari cache..."
    rm -rf ~/Library/Caches/com.apple.Safari/* 2>/dev/null
    rm -rf ~/Library/Safari/LocalStorage/* 2>/dev/null
    rm -rf ~/Library/Safari/Databases/* 2>/dev/null
    rm -rf ~/Library/Safari/WebKitCache/* 2>/dev/null
    
    # Clear Chrome cache
    echo "  - Clearing Chrome cache..."
    rm -rf ~/Library/Caches/Google/Chrome/* 2>/dev/null
    rm -rf ~/Library/Application\ Support/Google/Chrome/Default/Cache/* 2>/dev/null
    
    # Clear Firefox cache
    echo "  - Clearing Firefox cache..."
    rm -rf ~/Library/Caches/Firefox/* 2>/dev/null
    rm -rf ~/Library/Application\ Support/Firefox/Profiles/*/cache2/* 2>/dev/null
    
    # Clear Edge cache
    echo "  - Clearing Edge cache..."
    rm -rf ~/Library/Caches/com.microsoft.edgemac/* 2>/dev/null
    
    # Clear system DNS cache
    echo "  - Clearing DNS cache..."
    sudo dscacheutil -flushcache 2>/dev/null
    sudo killall -HUP mDNSResponder 2>/dev/null
    
    echo "✅ Browser cache cleared"
}

# Function to clean up temporary files
cleanup_temp_files() {
    echo "🧽 Cleaning up temporary files..."
    
    # Remove Python cache files
    find . -name "*.pyc" -delete 2>/dev/null
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    
    # Remove Flask session files
    rm -rf instance/ 2>/dev/null
    rm -rf .flask_session/ 2>/dev/null
    
    # Remove any temporary web files
    rm -f flask_app.pid 2>/dev/null
    
    echo "✅ Temporary files cleaned"
}

# Main execution
echo "=========================================="
echo "🛑 Redline Web App Shutdown Script"
echo "=========================================="

# Stop Flask application
stop_flask_app

# Clear browser cache
clear_browser_cache

# Clean up temporary files
cleanup_temp_files

echo ""
echo "🎉 Redline Web App shutdown complete!"
echo "   - Flask application stopped"
echo "   - Browser cache cleared"
echo "   - Temporary files cleaned"
echo ""
echo "To restart the web app, run: ./start_web_app.sh"
