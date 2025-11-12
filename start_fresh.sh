#!/bin/bash
# Start REDLINE services from scratch

echo "🔄 Starting REDLINE Services from Scratch"
echo "=========================================="
echo ""

# Check if services are already running
echo "📋 Checking for running services..."
LICENSE_PID=$(lsof -ti:5001 2>/dev/null)
WEB_PID=$(lsof -ti:8080 2>/dev/null)

if [ ! -z "$LICENSE_PID" ]; then
    echo "⚠️  License server already running on port 5001 (PID: $LICENSE_PID)"
    echo "   Stopping it..."
    kill $LICENSE_PID 2>/dev/null
    sleep 2
fi

if [ ! -z "$WEB_PID" ]; then
    echo "⚠️  Web app already running on port 8080 (PID: $WEB_PID)"
    echo "   Stopping it..."
    kill $WEB_PID 2>/dev/null
    sleep 2
fi

echo ""
echo "✅ All services stopped"
echo ""
echo "🚀 Starting services..."
echo ""

# Start license server in background
echo "1️⃣  Starting License Server (port 5001)..."
python3 licensing/server/license_server.py > /tmp/license_server.log 2>&1 &
LICENSE_PID=$!
sleep 3

# Check if license server started
if ps -p $LICENSE_PID > /dev/null; then
    echo "   ✅ License server started (PID: $LICENSE_PID)"
else
    echo "   ❌ License server failed to start"
    echo "   Check logs: tail -f /tmp/license_server.log"
    exit 1
fi

# Start web app in background
echo ""
echo "2️⃣  Starting Web App (port 8080)..."
python3 web_app.py > /tmp/web_app.log 2>&1 &
WEB_PID=$!
sleep 5

# Check if web app started
if ps -p $WEB_PID > /dev/null; then
    echo "   ✅ Web app started (PID: $WEB_PID)"
else
    echo "   ❌ Web app failed to start"
    echo "   Check logs: tail -f /tmp/web_app.log"
    kill $LICENSE_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📊 Service Status:"
echo "   License Server: http://localhost:5001 (PID: $LICENSE_PID)"
echo "   Web App:        http://localhost:8080 (PID: $WEB_PID)"
echo ""
echo "📝 Logs:"
echo "   License Server: tail -f /tmp/license_server.log"
echo "   Web App:        tail -f /tmp/web_app.log"
echo ""
echo "🧪 To test access control:"
echo "   python3 test_access_control.py"
echo ""
echo "🛑 To stop services:"
echo "   kill $LICENSE_PID $WEB_PID"
echo ""

