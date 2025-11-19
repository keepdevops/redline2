#!/bin/bash
# Setup REDLINE for Production Environment with Sandbox/Test Mode
# This configures Stripe test mode and lenient license server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Setting up REDLINE Production Environment with Sandbox Mode"
echo "=============================================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Using existing .env file"
        exit 0
    fi
fi

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file
cat > .env << EOF
# REDLINE Production Environment with Sandbox/Test Mode
# Generated: $(date)

# Flask Configuration
FLASK_ENV=production
ENV=production
DEBUG=false
SECRET_KEY=${SECRET_KEY}

# Stripe Test Mode (Sandbox)
# Get keys from: https://dashboard.stripe.com/test/apikeys
# Make sure you're in TEST MODE (toggle in top right)
STRIPE_SECRET_KEY=sk_test_YOUR_TEST_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_TEST_WEBHOOK_SECRET_HERE
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd

# License Server (Lenient Mode for Testing)
LICENSE_SERVER_URL=http://localhost:5001
REQUIRE_LICENSE_SERVER=false
ENFORCE_PAYMENT=false

# CORS Configuration
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
EOF

echo "✅ Created .env file with production sandbox configuration"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your Stripe test keys:"
echo "   - STRIPE_SECRET_KEY=sk_test_..."
echo "   - STRIPE_PUBLISHABLE_KEY=pk_test_..."
echo "   - STRIPE_WEBHOOK_SECRET=whsec_..."
echo ""
echo "2. Get Stripe test keys from:"
echo "   https://dashboard.stripe.com/test/apikeys"
echo ""
echo "3. Start REDLINE:"
echo "   bash start_redline.sh"
echo ""
echo "📚 See PRODUCTION_SANDBOX_CONFIG.md for detailed instructions"





