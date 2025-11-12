#!/bin/bash
# Stop all REDLINE services

echo "🛑 Stopping all REDLINE services..."
echo ""

# Find and kill license server
LICENSE_PIDS=$(lsof -ti:5001 2>/dev/null)
if [ ! -z "$LICENSE_PIDS" ]; then
    echo "Stopping License Server (PID: $LICENSE_PIDS)..."
    kill $LICENSE_PIDS 2>/dev/null
    sleep 1
fi

# Find and kill web app
WEB_PIDS=$(lsof -ti:8080 2>/dev/null)
if [ ! -z "$WEB_PIDS" ]; then
    echo "Stopping Web App (PID: $WEB_PIDS)..."
    kill $WEB_PIDS 2>/dev/null
    sleep 1
fi

# Also kill by process name
pkill -f "license_server.py" 2>/dev/null
pkill -f "web_app.py" 2>/dev/null

sleep 2

# Verify
if [ -z "$(lsof -ti:5001 2>/dev/null)" ] && [ -z "$(lsof -ti:8080 2>/dev/null)" ]; then
    echo "✅ All services stopped"
else
    echo "⚠️  Some services may still be running"
    echo "   Check manually: lsof -i:5001 -i:8080"
fi

