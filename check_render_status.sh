#!/bin/bash
# Check if Render service is running

echo "🔍 Checking Render Service Status"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get Render URL
echo "Enter your Render service URL (e.g., https://redline-xxxx.onrender.com):"
read -p "URL: " RENDER_URL

if [ -z "$RENDER_URL" ]; then
    echo -e "${RED}❌ No URL provided${NC}"
    echo ""
    echo "To find your Render URL:"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Click on your service"
    echo "3. Copy the URL from the top of the page"
    exit 1
fi

# Remove trailing slash
RENDER_URL="${RENDER_URL%/}"

echo ""
echo "Testing Render service..."
echo ""

# Test health endpoint
echo "1. Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${RENDER_URL}/health" 2>/dev/null)

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Health check: OK (200)${NC}"
    HEALTH_BODY=$(curl -s --max-time 10 "${RENDER_URL}/health" 2>/dev/null)
    echo "   Response: $HEALTH_BODY"
else
    echo -e "${RED}❌ Health check: Failed (HTTP $HEALTH_RESPONSE)${NC}"
fi

echo ""

# Test root endpoint
echo "2. Testing root endpoint..."
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${RENDER_URL}/" 2>/dev/null)

if [ "$ROOT_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Root endpoint: OK (200)${NC}"
elif [ "$ROOT_RESPONSE" = "301" ] || [ "$ROOT_RESPONSE" = "302" ]; then
    echo -e "${YELLOW}⚠️  Root endpoint: Redirect ($ROOT_RESPONSE)${NC}"
else
    echo -e "${RED}❌ Root endpoint: Failed (HTTP $ROOT_RESPONSE)${NC}"
fi

echo ""

# Test status endpoint
echo "3. Testing /status endpoint..."
STATUS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${RENDER_URL}/status" 2>/dev/null)

if [ "$STATUS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Status endpoint: OK (200)${NC}"
    STATUS_BODY=$(curl -s --max-time 10 "${RENDER_URL}/status" 2>/dev/null)
    echo "   Response: $STATUS_BODY" | head -c 200
    echo ""
else
    echo -e "${RED}❌ Status endpoint: Failed (HTTP $STATUS_RESPONSE)${NC}"
fi

echo ""

# Summary
echo "==================================="
echo "Summary:"
echo ""

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Render service appears to be RUNNING${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Visit: ${RENDER_URL}"
    echo "2. Check Render Dashboard: https://dashboard.render.com"
    echo "3. Review logs in Render Dashboard → Logs tab"
else
    echo -e "${RED}❌ Render service appears to be DOWN or UNREACHABLE${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Render Dashboard: https://dashboard.render.com"
    echo "2. Look for service status (should be 'Live')"
    echo "3. Check logs for errors"
    echo "4. Verify environment variables are set"
    echo "5. Check if service is paused (free tier spins down after inactivity)"
fi

echo ""
echo "Render Dashboard: https://dashboard.render.com"
echo ""

