#!/bin/bash
# Setup script for Stripe webhook forwarding using Stripe CLI

echo "🔗 Stripe Webhook Setup"
echo "======================="
echo ""

# Check if Stripe CLI is installed
if ! command -v stripe &> /dev/null; then
    echo "❌ Stripe CLI not found"
    echo ""
    echo "Install Stripe CLI:"
    echo "  macOS: brew install stripe/stripe-cli/stripe"
    echo "  Linux: See https://github.com/stripe/stripe-cli/releases"
    echo "  Windows: See https://github.com/stripe/stripe-cli/releases"
    echo ""
    exit 1
fi

echo "✅ Stripe CLI found: $(stripe --version)"
echo ""

# Check if logged in
if ! stripe config --list &> /dev/null; then
    echo "⚠️  Not logged in to Stripe CLI"
    echo ""
    echo "Logging in..."
    stripe login
    echo ""
fi

# Check if web app is running
if ! lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Web app not running on port 8080"
    echo ""
    echo "Start web app in another terminal:"
    echo "  python3 web_app.py"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Web app is running on port 8080"
echo ""

# Start webhook forwarding
echo "Starting webhook forwarding..."
echo "Webhook endpoint: http://localhost:8080/payments/webhook"
echo ""
echo "📋 IMPORTANT: Copy the webhook signing secret shown below"
echo "   and add it to your .env file as STRIPE_WEBHOOK_SECRET"
echo ""
echo "Press Ctrl+C to stop webhook forwarding"
echo ""
echo "----------------------------------------"
echo ""

# Forward webhooks
stripe listen --forward-to localhost:8080/payments/webhook

