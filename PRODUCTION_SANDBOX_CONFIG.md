# Production Environment with Sandbox/Test Mode

This guide shows how to run REDLINE in production mode (`FLASK_ENV=production`) while using Stripe test mode and a lenient license server configuration.

## Configuration Overview

### Stripe Sandbox/Test Mode
- Use Stripe **test keys** (`sk_test_` and `pk_test_`) instead of live keys
- All payments are simulated - no real charges
- Perfect for testing payment flows in production environment

### License Server Test Mode
- Set `REQUIRE_LICENSE_SERVER=false` to allow access even if license server is unavailable
- License server still validates licenses, but won't block access if it's down
- Useful for development/testing scenarios

## Environment Variables

### For Stripe Test Mode in Production:

```bash
# Stripe Test Keys (from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_YOUR_TEST_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_TEST_WEBHOOK_SECRET

# Pricing Configuration
HOURS_PER_DOLLAR=0.2  # 1 hour = $5
PAYMENT_CURRENCY=usd
```

### For License Server Test Mode:

```bash
# License Server Configuration
LICENSE_SERVER_URL=http://localhost:5001
REQUIRE_LICENSE_SERVER=false  # Allow access even if license server is down

# Payment Enforcement (optional - set to false to allow access without payment)
ENFORCE_PAYMENT=false  # Set to true in real production
```

### Production Environment:

```bash
# Flask Production Mode
FLASK_ENV=production
ENV=production
```

## Quick Setup

### Option 1: Create .env File

1. Copy the template:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and set:
   ```bash
   FLASK_ENV=production
   ENV=production
   
   # Stripe Test Keys
   STRIPE_SECRET_KEY=sk_test_YOUR_KEY
   STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   
   # License Server (lenient mode)
   LICENSE_SERVER_URL=http://localhost:5001
   REQUIRE_LICENSE_SERVER=false
   ENFORCE_PAYMENT=false
   ```

3. Start Redline:
   ```bash
   bash start_redline.sh
   ```

### Option 2: Set Environment Variables Directly

```bash
export FLASK_ENV=production
export ENV=production
export STRIPE_SECRET_KEY=sk_test_YOUR_KEY
export STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
export STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
export LICENSE_SERVER_URL=http://localhost:5001
export REQUIRE_LICENSE_SERVER=false
export ENFORCE_PAYMENT=false

bash start_redline.sh
```

## Getting Stripe Test Keys

1. Go to https://dashboard.stripe.com
2. **Toggle to "Test mode"** (top right)
3. Go to **Developers** → **API keys**
4. Copy:
   - **Secret key** (starts with `sk_test_`)
   - **Publishable key** (starts with `pk_test_`)

## Getting Stripe Test Webhook Secret

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks: `stripe listen --forward-to localhost:8080/payments/webhook`
4. Copy the webhook secret (starts with `whsec_`)

Or use Stripe Dashboard:
1. Go to **Developers** → **Webhooks**
2. Add endpoint: `http://localhost:8080/payments/webhook`
3. Select events: `checkout.session.completed`
4. Copy signing secret

## Verification

### Check Stripe Configuration:
```bash
python3 -c "
import os
import sys
sys.path.insert(0, '.')
from redline.payment.config import PaymentConfig
print('Stripe Secret Key:', '✅ Test Mode' if PaymentConfig.STRIPE_SECRET_KEY.startswith('sk_test_') else '❌ Not Test Mode')
print('Stripe Publishable Key:', '✅ Test Mode' if PaymentConfig.STRIPE_PUBLISHABLE_KEY.startswith('pk_test_') else '❌ Not Test Mode')
print('Valid:', PaymentConfig.validate())
"
```

### Check License Server:
```bash
curl http://localhost:5001/health
```

### Check Environment:
```bash
ps eww -p $(pgrep -f "gunicorn.*web_app" | head -1) | grep -E "FLASK_ENV|ENV="
```

## Production vs Test Mode Comparison

| Feature | Production (Live) | Test/Sandbox |
|---------|-------------------|--------------|
| Stripe Keys | `sk_live_`, `pk_live_` | `sk_test_`, `pk_test_` |
| Payments | Real charges | Simulated only |
| License Server | `REQUIRE_LICENSE_SERVER=true` | `REQUIRE_LICENSE_SERVER=false` |
| Payment Enforcement | `ENFORCE_PAYMENT=true` | `ENFORCE_PAYMENT=false` |
| Environment | `FLASK_ENV=production` | `FLASK_ENV=production` |

## Important Notes

1. **Test keys don't charge real money** - Safe for testing
2. **License server can be lenient** - Won't block access if down
3. **Production environment still enabled** - Uses minified assets, optimizations
4. **Switch to live keys** when ready for real payments

## Switching to Real Production

When ready for real payments:

1. **Get Stripe Live Keys**:
   - Go to Stripe Dashboard
   - Toggle to **"Live mode"**
   - Copy live keys (`sk_live_`, `pk_live_`)

2. **Update Environment**:
   ```bash
   STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_KEY
   STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_KEY
   REQUIRE_LICENSE_SERVER=true
   ENFORCE_PAYMENT=true
   ```

3. **Restart Redline**





