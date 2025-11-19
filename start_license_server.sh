#!/bin/bash
# REDLINE License Server Startup Script
# Starts the license server on port 5001

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo "✅ Environment variables loaded"
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚀 REDLINE License Server"
echo "=========================="
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to get license server PID
get_license_server_pid() {
    lsof -ti:5001 2>/dev/null || echo ""
}

# Check if license server is already running
if check_port 5001; then
    PID=$(get_license_server_pid)
    echo -e "${YELLOW}⚠️  License Server already running on port 5001${NC}"
    echo -e "   PID: ${BLUE}$PID${NC}"
    echo ""
    read -p "Do you want to stop it and start a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🛑 Stopping existing license server...${NC}"
        kill $PID 2>/dev/null || pkill -f "license_server.py" 2>/dev/null
        sleep 2
    else
        echo "Keeping existing license server running."
        exit 0
    fi
fi

# Start license server
echo -e "${YELLOW}📡 Starting License Server on port 5001...${NC}"

# Get port from environment or use default
LICENSE_SERVER_PORT=${LICENSE_SERVER_PORT:-5001}

# Start in background with logging
nohup python3 licensing/server/license_server.py > license_server.log 2>&1 &
LICENSE_PID=$!

# Wait a moment for it to start
sleep 3

# Check if license server started successfully
if ps -p $LICENSE_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ License Server started successfully${NC}"
    echo -e "   PID: ${BLUE}$LICENSE_PID${NC}"
    echo -e "   Port: ${BLUE}$LICENSE_SERVER_PORT${NC}"
    echo -e "   URL: ${BLUE}http://localhost:$LICENSE_SERVER_PORT${NC}"
    echo ""
    
    # Test health endpoint
    sleep 1
    if curl -s http://localhost:$LICENSE_SERVER_PORT/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        HEALTH_RESPONSE=$(curl -s http://localhost:$LICENSE_SERVER_PORT/api/health)
        LICENSES_COUNT=$(echo $HEALTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('licenses_count', 'unknown'))" 2>/dev/null || echo "unknown")
        echo -e "   Licenses loaded: ${BLUE}$LICENSES_COUNT${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check not yet available (may need a moment)${NC}"
    fi
    
    echo ""
    echo "📝 Useful commands:"
    echo "   View logs:     tail -f license_server.log"
    echo "   Check status:  curl http://localhost:$LICENSE_SERVER_PORT/api/health"
    echo "   Stop server:   pkill -f license_server.py"
    echo "   Or use:        ./stop_license_server.sh"
    echo ""
else
    echo -e "${RED}❌ License Server failed to start${NC}"
    echo ""
    echo "📝 Check logs for errors:"
    echo "   tail -20 license_server.log"
    echo ""
    if [ -f license_server.log ]; then
        echo "Last 20 lines of log:"
        tail -20 license_server.log
    fi
    exit 1
fi


