# Complete Stripe Setup and Test Payment Flow

## Step-by-Step Guide

### Step 1: Get Stripe Test API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Ensure you're in **Test mode** (toggle in top right)
3. Copy your **Secret Key** (starts with `sk_test_`)
4. Copy your **Publishable Key** (starts with `pk_test_`)

### Step 2: Update .env File

Edit your `.env` file and replace the placeholder values:

```bash
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_6fb9ac4b56b5e274e8bff1b3b115711f3d01b6d577816558ad05ba2ac6d45681
```

**Note**: The webhook secret is already configured from Stripe CLI.

### Step 3: Verify Configuration

```bash
python3 -c "from redline.payment.config import PaymentConfig; print('Valid:', PaymentConfig.validate())"
```

Expected: `Valid: True`

### Step 4: Start Services

**Terminal 1 - License Server:**
```bash
python3 licensing/server/license_server.py
```

**Terminal 2 - Web App:**
```bash
python3 web_app.py
```

**Terminal 3 - Stripe CLI (for webhooks):**
```bash
stripe listen --forward-to localhost:8080/payments/webhook
```

### Step 5: Create Test License

```bash
python3 create_test_license.py
```

Save the license key that's displayed.

### Step 6: Test Checkout Creation

```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "hours": 10
  }'
```

Expected response:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

### Step 7: Complete Payment

1. Open the `checkout_url` in your browser
2. Use test card: `4242 4242 4242 4242`
3. Expiry: `12/34`
4. CVC: `123`
5. ZIP: `12345`
6. Complete payment

### Step 8: Verify Payment

**Check Balance:**
```bash
curl "http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY"
```

Expected:
```json
{
  "hours_remaining": 10.0,
  "license_key": "..."
}
```

**Check Stripe CLI:**
- Should show `[200] POST http://localhost:8080/payments/webhook`
- Webhook processed successfully

**Check Web App Logs:**
- Should show: "Added 10.0 hours to license ... via webhook"

## Quick Test Script

Run the automated test:
```bash
python3 test_stripe_payment.py
```

This will:
- Verify Stripe configuration
- Check services are running
- Create test license
- Test checkout creation
- Guide you through payment completion

## Troubleshooting

### "Payment configuration is invalid"
- Check that API keys are set in `.env`
- Verify keys start with `sk_test_` and `pk_test_`
- Restart web app after updating `.env`

### "Cannot create checkout"
- Verify Stripe keys are correct
- Check web app logs for errors
- Ensure web app is running

### "Webhook not received"
- Check Stripe CLI is running
- Verify webhook secret matches
- Check web app logs

### "Hours not added"
- Check license server is running
- Verify webhook was processed
- Check license server logs

## Success Checklist

- [ ] Stripe test account created
- [ ] API keys added to .env
- [ ] Configuration validates successfully
- [ ] All services running
- [ ] Test license created
- [ ] Checkout session created
- [ ] Payment completed
- [ ] Webhook received (200)
- [ ] Hours added to license
- [ ] Balance check shows correct hours

