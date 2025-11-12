#!/bin/bash
# Start REDLINE Web App

echo "🚀 Starting REDLINE Web App..."
echo "=============================="
echo ""

cd /Users/caribou/redline

# Check if already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Web app already running on port 8080"
    echo "   PID: $(lsof -Pi :8080 -sTCP:LISTEN -t)"
    echo ""
    echo "To stop it: pkill -f web_app.py"
    exit 0
fi

# Start web app
echo "Starting web app on http://localhost:8080..."
python3 web_app.py
