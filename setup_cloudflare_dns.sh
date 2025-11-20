#!/bin/bash
# Interactive script to set up Cloudflare DNS for existing Render deployment

set -e

echo "☁️  Cloudflare DNS Setup for REDLINE"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "This script will guide you through setting up Cloudflare DNS for your Render service."
echo ""
echo "Prerequisites:"
echo "  ✅ Render service is running"
echo "  ✅ You have a domain name"
echo "  ✅ Cloudflare account (or will create one)"
echo ""

# Get Render URL
read -p "Enter your Render service URL (e.g., https://redline-xxxx.onrender.com): " RENDER_URL
if [ -z "$RENDER_URL" ]; then
    echo -e "${RED}❌ Render URL is required!${NC}"
    exit 1
fi

# Remove https:// if present
RENDER_URL="${RENDER_URL#https://}"
RENDER_URL="${RENDER_URL#http://}"
RENDER_URL="${RENDER_URL%/}"

echo ""
echo -e "${GREEN}✅ Render URL: ${RENDER_URL}${NC}"
echo ""

# Get domain
read -p "Enter your domain name (e.g., redfindat.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Domain name is required!${NC}"
    exit 1
fi

# Remove www. if present
DOMAIN="${DOMAIN#www.}"

echo ""
echo -e "${GREEN}✅ Domain: ${DOMAIN}${NC}"
echo ""

# Check if domain is already in Cloudflare
echo "Checking if domain is in Cloudflare..."
echo ""

# Instructions
echo "=========================================="
echo "STEP-BY-STEP INSTRUCTIONS"
echo "=========================================="
echo ""

echo -e "${BLUE}STEP 1: Add Domain to Cloudflare${NC}"
echo "----------------------------------------"
echo "1. Go to: https://dash.cloudflare.com"
echo "2. Click 'Add a site' (top right)"
echo "3. Enter your domain: ${DOMAIN}"
echo "4. Click 'Add site'"
echo "5. Select a plan (Free plan is fine)"
echo "6. Click 'Continue'"
echo ""

read -p "Press Enter when domain is added to Cloudflare..."

echo ""
echo -e "${BLUE}STEP 2: Update Nameservers${NC}"
echo "----------------------------------------"
echo "Cloudflare will show you nameservers like:"
echo "  • alice.ns.cloudflare.com"
echo "  • bob.ns.cloudflare.com"
echo ""
echo "1. Copy these nameservers"
echo "2. Go to your domain registrar (where you bought ${DOMAIN})"
echo "3. Update nameservers to Cloudflare's nameservers"
echo "4. Wait 5-15 minutes for DNS propagation"
echo ""

read -p "Press Enter when nameservers are updated..."

echo ""
echo -e "${BLUE}STEP 3: Add DNS Record${NC}"
echo "----------------------------------------"
echo "1. In Cloudflare Dashboard, go to: DNS → Records"
echo "2. Click 'Add record'"
echo ""
echo "Configure the record:"
echo "  Type: CNAME"
echo "  Name: app (or @ for root domain)"
echo "  Target: ${RENDER_URL}"
echo "  Proxy status: ✅ Proxied (orange cloud ON)"
echo "  TTL: Auto"
echo ""
echo "3. Click 'Save'"
echo ""

read -p "Press Enter when DNS record is added..."

echo ""
echo -e "${BLUE}STEP 4: Configure SSL/TLS${NC}"
echo "----------------------------------------"
echo "1. In Cloudflare Dashboard, go to: SSL/TLS → Overview"
echo "2. Set encryption mode to: 'Full (strict)'"
echo "3. Cloudflare will automatically provision SSL certificate"
echo "4. Wait 5-15 minutes for certificate to be active"
echo ""

read -p "Press Enter when SSL is configured..."

echo ""
echo -e "${BLUE}STEP 5: Test Your Setup${NC}"
echo "----------------------------------------"
echo ""

# Determine the subdomain
read -p "What subdomain did you use? (app, www, or @ for root): " SUBDOMAIN
if [ "$SUBDOMAIN" = "@" ] || [ -z "$SUBDOMAIN" ]; then
    TEST_URL="https://${DOMAIN}"
else
    TEST_URL="https://${SUBDOMAIN}.${DOMAIN}"
fi

echo ""
echo "Testing your setup..."
echo ""

# Test health endpoint
echo "Testing: ${TEST_URL}/health"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${TEST_URL}/health" 2>/dev/null || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Health check: SUCCESS (HTTP 200)${NC}"
    HEALTH_BODY=$(curl -s --max-time 10 "${TEST_URL}/health" 2>/dev/null)
    echo "   Response: $HEALTH_BODY"
elif [ "$HEALTH_RESPONSE" = "000" ]; then
    echo -e "${YELLOW}⚠️  Health check: Cannot connect (DNS may still be propagating)${NC}"
    echo "   This is normal if you just set up DNS. Wait 5-15 minutes and try again."
else
    echo -e "${YELLOW}⚠️  Health check: HTTP ${HEALTH_RESPONSE}${NC}"
    echo "   This might be normal if DNS is still propagating or SSL is still provisioning."
fi

echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo -e "${GREEN}Your Cloudflare DNS is configured!${NC}"
echo ""
echo "Summary:"
echo "  Domain: ${DOMAIN}"
echo "  Render URL: ${RENDER_URL}"
echo "  Test URL: ${TEST_URL}"
echo ""
echo "Next Steps:"
echo "  1. Wait 5-15 minutes for DNS/SSL to fully propagate"
echo "  2. Test: curl ${TEST_URL}/health"
echo "  3. Visit: ${TEST_URL} in your browser"
echo "  4. (Optional) Update Stripe webhook URL to use custom domain"
echo ""
echo "Cloudflare Dashboard: https://dash.cloudflare.com"
echo "Render Dashboard: https://dashboard.render.com"
echo ""

