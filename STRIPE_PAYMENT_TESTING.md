# Stripe Payment Testing Guide

## Prerequisites Checklist

Before testing, ensure:

- [ ] Stripe account created (see `STRIPE_SETUP_GUIDE.md`)
- [ ] Stripe test API keys obtained
- [ ] Environment variables configured (`.env` file)
- [ ] License server running (`python3 licensing/server/license_server.py`)
- [ ] Web app running (`python3 web_app.py`)
- [ ] Webhook forwarding set up (see `STRIPE_WEBHOOK_SETUP.md`)

## Quick Test

Run the automated test suite:

```bash
python3 test_stripe_payment.py
```

This will:
1. Verify Stripe configuration
2. Check services are running
3. Create a test license
4. Test package retrieval
5. Create a checkout session

## Step-by-Step Manual Testing

### Step 1: Verify Configuration

```bash
# Check Stripe config
python3 -c "from redline.payment.config import PaymentConfig; print('Valid:', PaymentConfig.validate())"
```

Expected: `Valid: True`

### Step 2: Create Test License

```bash
python3 create_test_license.py
```

This creates a license with 0 hours (to test purchase flow).

Save the license key:
```bash
export TEST_LICENSE_KEY=RL-XXXXXXXX-XXXXXXXX-XXXXXXXX
```

### Step 3: Start Webhook Forwarding

**Option A: Using Stripe CLI (Recommended)**

```bash
./setup_stripe_webhook.sh
```

Or manually:
```bash
stripe listen --forward-to localhost:8080/payments/webhook
```

Copy the webhook secret and add to `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

Restart web app to load new secret.

**Option B: Using Ngrok**

```bash
ngrok http 8080
```

Add webhook endpoint in Stripe Dashboard:
- URL: `https://your-ngrok-url.ngrok.io/payments/webhook`
- Events: `checkout.session.completed`

### Step 4: Get Payment Packages

```bash
curl http://localhost:8080/payments/packages | python3 -m json.tool
```

Expected: List of 4 packages (5h, 10h, 20h, 50h)

### Step 5: Create Checkout Session

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "hours": 10
  }' | python3 -m json.tool
```

Expected response:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

### Step 6: Complete Payment

1. Open the `checkout_url` in your browser
2. Use test card: `4242 4242 4242 4242`
3. Expiry: Any future date (e.g., `12/34`)
4. CVC: Any 3 digits (e.g., `123`)
5. ZIP: Any 5 digits (e.g., `12345`)
6. Complete payment

### Step 7: Verify Payment

**Check Balance:**
```bash
curl "http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY" | python3 -m json.tool
```

Expected:
```json
{
  "hours_remaining": 10.0,
  "license_key": "..."
}
```

**Or use test script:**
```bash
python3 test_stripe_payment.py --verify 10 --license-key YOUR_LICENSE_KEY
```

### Step 8: Verify Webhook Processing

Check web app logs for:
```
INFO - Added 10.0 hours to license RL-... via webhook
```

Check Stripe CLI output (if using):
```
2024-XX-XX XX:XX:XX  --> checkout.session.completed [200]
```

## Test Scenarios

### Scenario 1: Successful Payment

1. Create checkout for 10 hours
2. Complete payment with `4242 4242 4242 4242`
3. Verify hours added to license
4. Verify payment logged to database

**Expected Result**: 10 hours added, payment logged

### Scenario 2: Payment Failure

1. Create checkout for 10 hours
2. Use declined card: `4000 0000 0000 0002`
3. Verify payment fails
4. Verify no hours added

**Expected Result**: Payment declined, no hours added

### Scenario 3: Webhook Processing

1. Complete successful payment
2. Check webhook received (Stripe CLI or Dashboard)
3. Verify webhook processed (check logs)
4. Verify hours added via webhook

**Expected Result**: Webhook received and processed, hours added

### Scenario 4: Multiple Purchases

1. Purchase 10 hours
2. Verify balance: 10 hours
3. Purchase 20 more hours
4. Verify balance: 30 hours

**Expected Result**: Hours accumulate correctly

## Testing Different Packages

### Small Package (5 hours, $25)

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "package_id": "small"
  }'
```

### Medium Package (10 hours, $45)

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "package_id": "medium"
  }'
```

### Large Package (20 hours, $80)

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "package_id": "large"
  }'
```

### XLarge Package (50 hours, $180)

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "package_id": "xlarge"
  }'
```

### Custom Hours

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "hours": 15
  }'
```

## Test Card Numbers

### Successful Payments

- **Visa**: `4242 4242 4242 4242`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`

### Declined Payments

- **Card declined**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`
- **Expired card**: `4000 0000 0000 0069`

### 3D Secure (SCA)

- **Requires authentication**: `4000 0025 0000 3155`
- **Authentication fails**: `4000 0000 0000 3055`

## Troubleshooting

### "Payment configuration is invalid"

**Problem**: Stripe keys not configured

**Solution**:
1. Check `.env` file exists
2. Verify keys are set correctly
3. Ensure no extra spaces or quotes
4. Restart web app

### "Webhook secret not configured"

**Problem**: `STRIPE_WEBHOOK_SECRET` not set

**Solution**:
1. Start Stripe CLI: `stripe listen --forward-to localhost:8080/payments/webhook`
2. Copy webhook secret
3. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`
4. Restart web app

### "Invalid signature" in webhook

**Problem**: Webhook secret doesn't match

**Solution**:
1. If using Stripe CLI, use CLI-generated secret
2. If using Stripe Dashboard, use dashboard secret
3. Don't mix them - use one or the other

### Payment succeeds but hours not added

**Problem**: Webhook not processed

**Solution**:
1. Check webhook forwarding is running
2. Check web app logs for errors
3. Verify license server is running
4. Check webhook endpoint is accessible

### "Cannot connect to license server"

**Problem**: License server not running

**Solution**:
```bash
python3 licensing/server/license_server.py
```

### "Cannot connect to web app"

**Problem**: Web app not running

**Solution**:
```bash
python3 web_app.py
```

## Verification Checklist

After completing a test payment:

- [ ] Payment completed successfully
- [ ] Webhook received (check Stripe CLI or Dashboard)
- [ ] Webhook processed (check web app logs)
- [ ] Hours added to license (check balance)
- [ ] Payment logged to database (check usage_storage)
- [ ] Balance check returns correct hours

## Next Steps

After successful testing:

1. Test with different packages
2. Test payment failures
3. Test webhook retries
4. Test concurrent payments
5. Prepare for production deployment

## Production Checklist

Before going live:

- [ ] Switch to live Stripe keys (`pk_live_` and `sk_live_`)
- [ ] Set up production webhook endpoint
- [ ] Configure production webhook secret
- [ ] Test with real (small) payment
- [ ] Set up monitoring and alerts
- [ ] Review security settings

