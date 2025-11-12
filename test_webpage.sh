#!/bin/bash
# Test localhost:8080 webpage endpoints

echo "🌐 Testing localhost:8080 Webpage"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $name... "
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" == "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} Status: $status"
        return 0
    else
        echo -e "${RED}✗${NC} Status: $status (expected $expected_code)"
        return 1
    fi
}

test_json_endpoint() {
    local name=$1
    local url=$2
    local header=$3
    
    echo -n "Testing $name... "
    if [ -z "$header" ]; then
        response=$(curl -s "$url")
    else
        response=$(curl -s -H "$header" "$url")
    fi
    
    # Check if valid JSON
    echo "$response" | python3 -m json.tool > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Valid JSON response"
        echo "$response" | python3 -m json.tool | head -5
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Not JSON or error"
        echo "$response" | head -3
        return 1
    fi
}

# Test public endpoints
echo "📋 Public Endpoints:"
test_endpoint "Health Check" "http://localhost:8080/health"
test_endpoint "Main Page" "http://localhost:8080/"
test_endpoint "Dashboard" "http://localhost:8080/dashboard"
test_endpoint "Register Page" "http://localhost:8080/register"
test_endpoint "Payment Tab" "http://localhost:8080/payments/"

echo ""
echo "📋 API Endpoints:"
test_json_endpoint "Payment Packages" "http://localhost:8080/payments/packages"

echo ""
echo "📋 Protected Endpoints (should require license):"
echo -n "Testing /data/files without license... "
response=$(curl -s http://localhost:8080/data/files)
if echo "$response" | grep -q "License key is required\|error"; then
    echo -e "${GREEN}✓${NC} Correctly requires license"
else
    echo -e "${YELLOW}⚠${NC} May not be protected"
fi

echo ""
echo "📋 Testing Access Control:"
echo -n "Testing with invalid license... "
response=$(curl -s -H "X-License-Key: RL-INVALID-KEY" http://localhost:8080/data/files)
if echo "$response" | grep -q "Invalid license\|403\|error"; then
    echo -e "${GREEN}✓${NC} Correctly blocked"
else
    echo -e "${RED}✗${NC} Not blocked"
fi

echo ""
echo "✅ Webpage testing complete!"
echo ""
echo "🌐 Open in browser: http://localhost:8080"

