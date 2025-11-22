#!/bin/bash
# REDLINE License Server Stop Script
# Stops the license server running on port 5001

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🛑 Stopping REDLINE License Server"
echo "==================================="
echo ""

# Function to get license server PID
get_license_server_pid() {
    lsof -ti:5001 2>/dev/null || echo ""
}

# Check if license server is running
PID=$(get_license_server_pid)

if [ -z "$PID" ]; then
    echo -e "${YELLOW}⚠️  License Server is not running${NC}"
    exit 0
fi

echo -e "Found License Server (PID: ${BLUE}$PID${NC})"
echo -e "${YELLOW}Stopping...${NC}"

# Try graceful shutdown first
kill $PID 2>/dev/null

# Wait a moment
sleep 2

# Check if still running
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}Process still running, forcing shutdown...${NC}"
    kill -9 $PID 2>/dev/null || pkill -9 -f "license_server.py" 2>/dev/null
    sleep 1
fi

# Verify it's stopped
if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ License Server stopped successfully${NC}"
else
    echo -e "${RED}❌ Failed to stop License Server${NC}"
    echo "   Try manually: pkill -9 -f license_server.py"
    exit 1
fi






