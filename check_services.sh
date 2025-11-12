#!/bin/bash
# Check REDLINE services status

echo "🔍 REDLINE Services Status"
echo "=========================="
echo ""

# Check License Server
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -Pi :5001 -sTCP:LISTEN -t)
    echo "✅ License Server: Running (PID: $PID)"
    echo "   URL: http://localhost:5001"
    curl -s http://localhost:5001/api/health | python3 -m json.tool 2>/dev/null | head -3 || echo "   (Health check failed)"
else
    echo "❌ License Server: Not running"
    echo "   Start with: python3 licensing/server/license_server.py"
fi

echo ""

# Check Web App
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -Pi :8080 -sTCP:LISTEN -t)
    echo "✅ Web App: Running (PID: $PID)"
    echo "   URL: http://localhost:8080"
    curl -s http://localhost:8080/payments/packages 2>/dev/null | python3 -m json.tool | head -5 || echo "   (Endpoint check failed)"
else
    echo "❌ Web App: Not running"
    echo "   Start with: python3 web_app.py"
fi

echo ""
echo "To run tests: python3 test_payment_integration.py"

