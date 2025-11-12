#!/bin/bash
# Deploy REDLINE to Fly.io

set -e

echo "✈️  REDLINE Fly.io Deployment"
echo "=============================="
echo ""

# Check if Fly CLI is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly CLI not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io:"
    flyctl auth login
fi

echo ""
echo "📦 Deploying REDLINE to Fly.io..."
echo ""

# Check if app exists
if flyctl apps list | grep -q "redline"; then
    echo "✅ App 'redline' already exists"
    read -p "Update existing app? (y/n): " UPDATE_APP
    if [ "$UPDATE_APP" != "y" ]; then
        echo "Exiting..."
        exit 0
    fi
else
    echo "🚀 Creating new Fly.io app..."
    flyctl launch --image keepdevops/redline:latest --no-deploy --name redline
fi

# Set environment variables
echo ""
echo "🔧 Setting environment variables..."
flyctl secrets set \
    FLASK_ENV=production \
    FLASK_APP=web_app.py \
    PORT=8080 \
    HOST=0.0.0.0

# Generate secret key if needed
read -p "Generate new SECRET_KEY? (y/n): " GEN_KEY
if [ "$GEN_KEY" = "y" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    flyctl secrets set SECRET_KEY="$SECRET_KEY"
    echo "✅ SECRET_KEY set"
fi

# Deploy
echo ""
echo "🚀 Deploying..."
flyctl deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Your Fly.io URL:"
flyctl status --app redline | grep "Hostname" || flyctl open --app redline
echo ""
echo "🔍 Test your deployment:"
echo "   curl https://redline.fly.dev/health"
echo ""

