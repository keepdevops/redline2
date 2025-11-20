#!/bin/bash
# Deploy REDLINE to Cloudflare with Subscription Model
# This script helps deploy the backend and set up Cloudflare services

set -e

echo "☁️  REDLINE Cloudflare Deployment with Subscription"
echo "===================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}⚠️  Wrangler CLI not found${NC}"
    echo "Install with: npm install -g wrangler"
    echo "Or: brew install cloudflare/cloudflare/cloudflare"
    exit 1
fi

echo -e "${GREEN}✅ Wrangler CLI found${NC}"

# Check if logged in to Cloudflare
if ! wrangler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Cloudflare${NC}"
    echo "Logging in..."
    wrangler login
fi

echo -e "${GREEN}✅ Logged in to Cloudflare${NC}"

# Get backend URL
echo ""
read -p "Enter your backend URL (e.g., https://redline-xxxx.onrender.com): " BACKEND_URL
if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend URL is required!${NC}"
    exit 1
fi

# Update wrangler.toml with backend URL
echo ""
echo "📝 Updating wrangler.toml with backend URL..."
sed -i.bak "s|BACKEND_URL = \".*\"|BACKEND_URL = \"$BACKEND_URL\"|g" wrangler.toml
echo -e "${GREEN}✅ Updated wrangler.toml${NC}"

# Deploy Worker
echo ""
echo "🚀 Deploying Cloudflare Worker..."
wrangler deploy

echo ""
echo -e "${GREEN}✅ Worker deployed successfully!${NC}"
echo ""
echo "📋 Next Steps:"
echo "1. Configure routes in Cloudflare Dashboard:"
echo "   - Workers & Pages → Routes"
echo "   - Add route: app.yourdomain.com/api/* → redline-api-proxy"
echo "   - Add route: app.yourdomain.com/data/* → redline-api-proxy"
echo "   - Add route: app.yourdomain.com/payments/* → redline-api-proxy"
echo ""
echo "2. Set up Cloudflare Pages for frontend:"
echo "   - Pages → Create project"
echo "   - Connect GitHub repo or upload static files"
echo ""
echo "3. Configure DNS:"
echo "   - DNS → Records"
echo "   - Add CNAME: app → your-backend.onrender.com (Proxied)"
echo ""
echo "4. Configure Stripe webhook:"
echo "   - Stripe Dashboard → Webhooks"
echo "   - Endpoint: $BACKEND_URL/payments/webhook"
echo ""
echo "5. Test subscription flow:"
echo "   - Register user"
echo "   - Purchase hours"
echo "   - Verify webhook receives events"
echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"

