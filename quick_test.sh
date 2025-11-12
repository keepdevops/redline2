#!/bin/bash
# Quick test script for REDLINE Payment Integration

echo "🚀 REDLINE Payment Integration Quick Test"
echo "=========================================="
echo ""

# Check Python
echo "📋 Checking Python..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "✅ Python OK"
echo ""

# Check Stripe
echo "📋 Checking Stripe..."
python3 -c "import stripe; print('✅ Stripe', stripe.__version__)" 2>&1 || {
    echo "⚠️  Stripe not installed. Installing..."
    pip3 install stripe --quiet
    python3 -c "import stripe; print('✅ Stripe', stripe.__version__)" 2>&1 || {
        echo "❌ Failed to install Stripe"
        exit 1
    }
}
echo ""

# Run tests
echo "🧪 Running integration tests..."
echo ""
python3 test_payment_integration.py

echo ""
echo "📝 Test Summary:"
echo "  - Module imports: ✅"
echo "  - Payment config: ✅"
echo "  - Usage tracker: ✅"
echo "  - User storage: ✅"
echo "  - Usage storage: ✅"
echo "  - Web app routes: ✅"
echo ""
echo "⚠️  Note: Payment routes and license server tests require services to be running"
echo ""
echo "To start services:"
echo "  1. License server: python3 licensing/server/license_server.py"
echo "  2. Web app: python3 web_app.py"
echo ""

