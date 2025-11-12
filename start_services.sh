#!/bin/bash
# Start REDLINE services for testing

echo "🚀 Starting REDLINE Services"
echo "=============================="
echo ""

# Check if flask-cors is installed
echo "📋 Checking dependencies..."
python3 -c "import flask_cors" 2>/dev/null || {
    echo "⚠️  Installing flask-cors..."
    pip3 install flask-cors --quiet
}

# Function to start license server
start_license_server() {
    echo "📡 Starting License Server on port 5001..."
    cd /Users/caribou/redline
    python3 licensing/server/license_server.py &
    LICENSE_PID=$!
    echo "   License Server PID: $LICENSE_PID"
    sleep 2
    # Check if it's running
    if ps -p $LICENSE_PID > /dev/null; then
        echo "   ✅ License Server started"
    else
        echo "   ❌ License Server failed to start"
        return 1
    fi
}

# Function to start web app
start_web_app() {
    echo "🌐 Starting Web App on port 8080..."
    cd /Users/caribou/redline
    python3 web_app.py &
    WEB_PID=$!
    echo "   Web App PID: $WEB_PID"
    sleep 3
    # Check if it's running
    if ps -p $WEB_PID > /dev/null; then
        echo "   ✅ Web App started"
    else
        echo "   ❌ Web App failed to start"
        return 1
    fi
}

# Check if services are already running
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  License Server already running on port 5001"
else
    start_license_server || exit 1
fi

if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Web App already running on port 8080"
else
    start_web_app || exit 1
fi

echo ""
echo "✅ Both services are running!"
echo ""
echo "📡 License Server: http://localhost:5001"
echo "🌐 Web App: http://localhost:8080"
echo ""
echo "To stop services, run:"
echo "  pkill -f license_server.py"
echo "  pkill -f web_app.py"
echo ""
echo "Or press Ctrl+C to stop this script (services will continue running)"

