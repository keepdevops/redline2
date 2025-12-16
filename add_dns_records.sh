#!/bin/bash
# Script to add DNS records for Render and redfindat.com using Cloudflare API
# This script adds CNAME records pointing Render services to redfindat.com subdomains

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "☁️  Cloudflare DNS Setup for Render + redfindat.com"
echo "=================================================="
echo ""

# Check if required tools are installed
command -v curl >/dev/null 2>&1 || { echo -e "${RED}❌ curl is required but not installed.${NC}"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo -e "${YELLOW}⚠️  jq is recommended for JSON parsing. Install with: brew install jq${NC}"; }

# Get Cloudflare credentials
if [ -z "$CF_API_EMAIL" ]; then
    read -p "Enter your Cloudflare email: " CF_API_EMAIL
fi

if [ -z "$CF_API_KEY" ]; then
    read -sp "Enter your Cloudflare API key: " CF_API_KEY
    echo ""
fi

if [ -z "$CF_ZONE_ID" ]; then
    read -p "Enter your Cloudflare Zone ID for redfindat.com (or press Enter to auto-detect): " CF_ZONE_ID
fi

DOMAIN="redfindat.com"

# Auto-detect Zone ID if not provided
if [ -z "$CF_ZONE_ID" ]; then
    echo "🔍 Detecting Zone ID for ${DOMAIN}..."
    CF_ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=${DOMAIN}" \
        -H "X-Auth-Email: ${CF_API_EMAIL}" \
        -H "X-Auth-Key: ${CF_API_KEY}" \
        -H "Content-Type: application/json" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    
    if [ -z "$CF_ZONE_ID" ]; then
        echo -e "${RED}❌ Could not find Zone ID for ${DOMAIN}${NC}"
        echo "Please add the domain to Cloudflare first or provide Zone ID manually"
        exit 1
    fi
    echo -e "${GREEN}✅ Found Zone ID: ${CF_ZONE_ID}${NC}"
fi

# Get Render service URL
read -p "Enter your Render service URL (e.g., redline-xxxx.onrender.com): " RENDER_URL
if [ -z "$RENDER_URL" ]; then
    echo -e "${RED}❌ Render URL is required!${NC}"
    exit 1
fi

# Remove https:// if present
RENDER_URL="${RENDER_URL#https://}"
RENDER_URL="${RENDER_URL#http://}"
RENDER_URL="${RENDER_URL%/}"

echo ""
echo -e "${GREEN}✅ Configuration:${NC}"
echo "   Domain: ${DOMAIN}"
echo "   Render URL: ${RENDER_URL}"
echo "   Zone ID: ${CF_ZONE_ID}"
echo ""

# Function to add DNS record
add_dns_record() {
    local name=$1
    local target=$2
    local record_type=${3:-CNAME}
    local proxied=${4:-true}
    
    echo "📝 Adding DNS record: ${name}.${DOMAIN} → ${target}"
    
    # Check if record already exists
    EXISTING=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records?type=${record_type}&name=${name}.${DOMAIN}" \
        -H "X-Auth-Email: ${CF_API_EMAIL}" \
        -H "X-Auth-Key: ${CF_API_KEY}" \
        -H "Content-Type: application/json")
    
    if echo "$EXISTING" | grep -q '"id"'; then
        echo -e "${YELLOW}⚠️  Record ${name}.${DOMAIN} already exists${NC}"
        read -p "   Update existing record? (y/n): " UPDATE
        if [ "$UPDATE" != "y" ]; then
            echo "   Skipping..."
            return 0
        fi
        
        # Update existing record
        RECORD_ID=$(echo "$EXISTING" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
        RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${RECORD_ID}" \
            -H "X-Auth-Email: ${CF_API_EMAIL}" \
            -H "X-Auth-Key: ${CF_API_KEY}" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"${record_type}\",\"name\":\"${name}\",\"content\":\"${target}\",\"ttl\":1,\"proxied\":${proxied}}")
    else
        # Create new record
        RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records" \
            -H "X-Auth-Email: ${CF_API_EMAIL}" \
            -H "X-Auth-Key: ${CF_API_KEY}" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"${record_type}\",\"name\":\"${name}\",\"content\":\"${target}\",\"ttl\":1,\"proxied\":${proxied}}")
    fi
    
    # Check response
    if echo "$RESPONSE" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Successfully added/updated ${name}.${DOMAIN}${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to add record${NC}"
        echo "$RESPONSE" | grep -o '"message":"[^"]*' | cut -d'"' -f4 || echo "$RESPONSE"
        return 1
    fi
}

# Add DNS records
echo "🚀 Adding DNS records..."
echo ""

# Main app subdomain
add_dns_record "app" "${RENDER_URL}" "CNAME" "true"

# Root domain (using @)
add_dns_record "@" "${RENDER_URL}" "CNAME" "true"

# WWW subdomain (redirects to root)
add_dns_record "www" "${DOMAIN}" "CNAME" "true"

echo ""
echo "=========================================="
echo "✅ DNS Records Added!"
echo "=========================================="
echo ""
echo "Records configured:"
echo "  • app.${DOMAIN} → ${RENDER_URL}"
echo "  • ${DOMAIN} → ${RENDER_URL}"
echo "  • www.${DOMAIN} → ${DOMAIN}"
echo ""
echo "Next steps:"
echo "  1. Wait 5-15 minutes for DNS propagation"
echo "  2. Configure SSL/TLS in Cloudflare Dashboard:"
echo "     https://dash.cloudflare.com → ${DOMAIN} → SSL/TLS → Overview"
echo "     Set to: Full (strict)"
echo "  3. Test your setup:"
echo "     curl -I https://app.${DOMAIN}/health"
echo ""
echo "Cloudflare Dashboard: https://dash.cloudflare.com"
echo ""

