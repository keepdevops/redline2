#!/bin/bash
# Manual test for expired license protection

echo "🧪 Manual Test: Expired License Protection"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Create a test license${NC}"
echo "Creating license with 10 hours..."
LICENSE_OUTPUT=$(python3 create_test_license.py --hours 10 2>&1)
LICENSE_KEY=$(echo "$LICENSE_OUTPUT" | grep "License Key:" | awk '{print $3}')

if [ -z "$LICENSE_KEY" ]; then
    echo -e "${RED}✗ Failed to create license${NC}"
    exit 1
fi

echo -e "${GREEN}✓ License created: $LICENSE_KEY${NC}"
echo ""

echo -e "${BLUE}Step 2: Verify license works (should work)${NC}"
echo "Testing balance endpoint..."
BALANCE_RESPONSE=$(curl -s "http://localhost:8080/payments/balance?license_key=$LICENSE_KEY")
BALANCE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/payments/balance?license_key=$LICENSE_KEY")

if [ "$BALANCE_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Balance check works (Status: $BALANCE_STATUS)${NC}"
    echo "$BALANCE_RESPONSE" | python3 -m json.tool 2>/dev/null | head -5
else
    echo -e "${RED}✗ Balance check failed (Status: $BALANCE_STATUS)${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Manually expire the license${NC}"
echo "Setting expiration date to yesterday..."
python3 << EOF
import json
from datetime import datetime, timedelta

license_file = 'licenses.json'
license_key = '$LICENSE_KEY'

with open(license_file, 'r') as f:
    licenses = json.load(f)

if license_key in licenses:
    old_expires = licenses[license_key]['expires']
    licenses[license_key]['expires'] = (datetime.now() - timedelta(days=1)).isoformat()
    new_expires = licenses[license_key]['expires']
    
    with open(license_file, 'w') as f:
        json.dump(licenses, f, indent=2)
    
    print(f"Old expiration: {old_expires}")
    print(f"New expiration: {new_expires}")
    print("License expired successfully")
else:
    print("License not found in file")
EOF

echo ""
echo -e "${YELLOW}⚠️  Restarting license server to reload licenses...${NC}"
pkill -f "license_server.py" 2>/dev/null
sleep 2
python3 licensing/server/license_server.py > /tmp/license_server.log 2>&1 &
sleep 3
echo -e "${GREEN}✓ License server restarted${NC}"

echo ""
echo -e "${BLUE}Step 4: Verify license is expired${NC}"
echo "Validating license via license server..."
VALIDATION_RESPONSE=$(curl -s -X POST "http://localhost:5001/api/licenses/$LICENSE_KEY/validate" \
    -H "Content-Type: application/json" \
    -d '{}')

echo "$VALIDATION_RESPONSE" | python3 -m json.tool

if echo "$VALIDATION_RESPONSE" | grep -q "expired"; then
    echo -e "${GREEN}✓ License is correctly marked as expired${NC}"
else
    echo -e "${RED}✗ License validation issue${NC}"
fi
echo ""

echo -e "${BLUE}Step 5: Try to check balance (should be BLOCKED)${NC}"
BALANCE_RESPONSE=$(curl -s "http://localhost:8080/payments/balance?license_key=$LICENSE_KEY")
BALANCE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/payments/balance?license_key=$LICENSE_KEY")

echo "Status Code: $BALANCE_STATUS"
echo "Response:"
echo "$BALANCE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$BALANCE_RESPONSE"

if [ "$BALANCE_STATUS" == "403" ]; then
    echo -e "${GREEN}✓ Balance check correctly blocked (403 Forbidden)${NC}"
else
    echo -e "${RED}✗ Balance check not blocked (Status: $BALANCE_STATUS)${NC}"
fi
echo ""

echo -e "${BLUE}Step 6: Try to create checkout (should be BLOCKED)${NC}"
CHECKOUT_RESPONSE=$(curl -s -X POST "http://localhost:8080/payments/create-checkout" \
    -H "Content-Type: application/json" \
    -d "{\"license_key\": \"$LICENSE_KEY\", \"hours\": 10}")

CHECKOUT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8080/payments/create-checkout" \
    -H "Content-Type: application/json" \
    -d "{\"license_key\": \"$LICENSE_KEY\", \"hours\": 10}")

echo "Status Code: $CHECKOUT_STATUS"
echo "Response:"
echo "$CHECKOUT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CHECKOUT_RESPONSE"

if [ "$CHECKOUT_STATUS" == "403" ]; then
    echo -e "${GREEN}✓ Checkout creation correctly blocked (403 Forbidden)${NC}"
else
    echo -e "${RED}✗ Checkout creation not blocked (Status: $CHECKOUT_STATUS)${NC}"
fi
echo ""

echo -e "${BLUE}Step 7: Test in browser${NC}"
echo "Open these URLs in your browser:"
echo ""
echo "1. Payment Tab:"
echo "   http://localhost:8080/payments/"
echo ""
echo "2. Enter license key: $LICENSE_KEY"
echo ""
echo "3. Try to purchase hours - should see error about expired license"
echo ""

echo "=========================================="
echo "Test Summary:"
echo "=========================================="
echo ""
echo "License Key: $LICENSE_KEY"
echo ""
if [ "$BALANCE_STATUS" == "403" ] && [ "$CHECKOUT_STATUS" == "403" ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo "Expired licenses are correctly blocked from:"
    echo "  - Checking balance"
    echo "  - Creating checkout sessions"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Balance Status: $BALANCE_STATUS (expected: 403)"
    echo "Checkout Status: $CHECKOUT_STATUS (expected: 403)"
fi
echo ""

