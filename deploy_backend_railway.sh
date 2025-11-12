#!/bin/bash
# Deploy REDLINE Docker container to Railway
# This script helps deploy keepdevops/redline:latest to Railway

set -e

echo "🚂 REDLINE Railway Deployment Helper"
echo "====================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo ""
echo "📦 Deploying REDLINE Docker container to Railway..."
echo ""

# Initialize Railway project if not already done
if [ ! -f ".railway/project.json" ]; then
    echo "🔧 Initializing Railway project..."
    railway init
fi

# Link to existing project or create new
echo ""
read -p "Do you want to link to an existing Railway project? (y/n): " LINK_EXISTING

if [ "$LINK_EXISTING" = "y" ]; then
    railway link
else
    echo "Creating new Railway project..."
fi

# Deploy using Docker image
echo ""
echo "🚀 Deploying keepdevops/redline:latest..."
echo ""

# Option 1: Use Docker image directly
read -p "Deploy using Docker image directly? (y/n): " USE_IMAGE

if [ "$USE_IMAGE" = "y" ]; then
    echo "📝 Note: Railway will pull keepdevops/redline:latest"
    echo "   Make sure your railway.json is configured correctly"
    railway up
else
    # Option 2: Build from Dockerfile
    echo "📦 Building from Dockerfile..."
    railway up --dockerfile Dockerfile
fi

# Set environment variables
echo ""
echo "🔧 Setting environment variables..."
railway variables set FLASK_ENV=production
railway variables set FLASK_APP=web_app.py
railway variables set HOST=0.0.0.0

# Generate secret key if needed
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
railway variables set SECRET_KEY="$SECRET_KEY"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Your Railway URL:"
railway domain
echo ""
echo "🔍 Test your deployment:"
echo "   curl https://your-app.railway.app/health"
echo ""
echo "💡 Next steps:"
echo "1. Copy your Railway URL"
echo "2. Update vercel.json with this URL"
echo "3. Deploy to Vercel using deploy_vercel.sh"
echo ""

