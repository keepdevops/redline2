#!/bin/bash
# REDLINE Vercel Deployment Script
# This script helps deploy REDLINE to Vercel with backend on Railway/Render

set -e

echo "🚀 REDLINE Vercel Deployment Helper"
echo "===================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel:"
    vercel login
fi

# Get backend URL
echo ""
echo "📝 Configuration:"
read -p "Enter your backend URL (e.g., https://redline.railway.app): " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend URL is required!"
    exit 1
fi

# Update vercel.json with backend URL
echo ""
echo "🔧 Updating vercel.json with backend URL..."
sed -i.bak "s|YOUR_BACKEND_URL|$BACKEND_URL|g" vercel.json
sed -i.bak "s|YOUR_BACKEND_URL|$BACKEND_URL|g" package.json 2>/dev/null || true

# Clean up backup files
rm -f vercel.json.bak package.json.bak 2>/dev/null || true

echo "✅ Configuration updated!"
echo ""

# Ask for deployment type
echo "Select deployment type:"
echo "1) Preview deployment (test)"
echo "2) Production deployment"
read -p "Choice [1-2]: " DEPLOY_TYPE

case $DEPLOY_TYPE in
    1)
        echo ""
        echo "🚀 Deploying to Vercel (preview)..."
        vercel
        ;;
    2)
        echo ""
        echo "🚀 Deploying to Vercel (production)..."
        vercel --prod
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test your deployment at the URL provided above"
echo "2. Configure custom domain in Vercel dashboard (optional)"
echo "3. Set environment variables in Vercel dashboard:"
echo "   - REDLINE_BACKEND_URL=$BACKEND_URL"
echo ""
echo "🔍 Test your deployment:"
echo "   curl https://your-app.vercel.app/health"
echo ""

