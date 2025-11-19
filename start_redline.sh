#!/bin/bash
# REDLINE Startup Script
# Starts license server and web app with Gunicorn

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo "✅ Environment variables loaded"
fi

echo "🚀 Starting REDLINE Services"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start license server
start_license_server() {
    echo -e "${YELLOW}📡 Starting License Server on port 5001...${NC}"
    
    if check_port 5001; then
        echo -e "${YELLOW}⚠️  License Server already running on port 5001${NC}"
        return 0
    fi
    
    nohup python3 licensing/server/license_server.py > license_server.log 2>&1 &
    LICENSE_PID=$!
    
    sleep 2
    
    if ps -p $LICENSE_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ License Server started (PID: $LICENSE_PID)${NC}"
        return 0
    else
        echo -e "${RED}❌ License Server failed to start${NC}"
        echo "   Check license_server.log for errors"
        return 1
    fi
}

# Function to start web app
start_web_app() {
    echo -e "${YELLOW}🌐 Starting Web App on port 8080...${NC}"
    
    if check_port 8080; then
        echo -e "${YELLOW}⚠️  Web App already running on port 8080${NC}"
        return 0
    fi
    
    nohup env FLASK_ENV=production ENV=production gunicorn -c gunicorn.conf.py web_app:app > redline_web.log 2>&1 &
    WEB_PID=$!
    
    sleep 3
    
    if ps -p $WEB_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Web App started (PID: $WEB_PID)${NC}"
        return 0
    else
        echo -e "${RED}❌ Web App failed to start${NC}"
        echo "   Check redline_web.log for errors"
        return 1
    fi
}

# Start services
start_license_server || exit 1
start_web_app || exit 1

echo ""
echo -e "${GREEN}✅ REDLINE is running!${NC}"
echo ""
echo "📡 License Server: http://localhost:5001"
echo "🌐 Web App: http://localhost:8080"
echo ""
echo "📋 Logs:"
echo "   License Server: tail -f license_server.log"
echo "   Web App: tail -f redline_web.log"
echo ""
echo "🛑 To stop services:"
echo "   pkill -f 'gunicorn.*web_app'"
echo "   pkill -f 'license_server.py'"
echo ""
