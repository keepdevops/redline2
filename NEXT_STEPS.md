# Next Steps - Complete Payment Flow Testing

## Current Status ✅

- ✅ Payment integration code implemented
- ✅ All tests passing (8/8)
- ✅ Stripe API keys configured in .env
- ✅ Webhook secret configured
- ✅ License server running (port 5001)
- ✅ Documentation complete

## Immediate Next Steps

### Step 1: Start Web App

In a new terminal:
```bash
cd /Users/caribou/redline
python3 web_app.py
```

Expected output:
```
Starting server on 0.0.0.0:8080
```

### Step 2: Start Stripe CLI (for webhooks)

In another terminal:
```bash
stripe listen --forward-to localhost:8080/payments/webhook
```

Copy the webhook secret if it's different (should already be in .env).

### Step 3: Create Test License

In another terminal:
```bash
cd /Users/caribou/redline
python3 create_test_license.py
```

Save the license key that's displayed.

### Step 4: Test Payment Flow

**Option A: Automated Test**
```bash
python3 test_stripe_payment.py
```

**Option B: Manual Test**

1. Create checkout session:
```bash
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "hours": 10
  }'
```

2. Open the `checkout_url` in your browser

3. Complete payment with test card:
   - Card: `4242 4242 4242 4242`
   - Expiry: `12/34`
   - CVC: `123`
   - ZIP: `12345`

4. Verify hours added:
```bash
curl "http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY"
```

### Step 5: Verify Everything Works

Check:
- ✅ Payment completed successfully
- ✅ Webhook received (`[200]` in Stripe CLI)
- ✅ Hours added to license
- ✅ Balance check shows correct hours
- ✅ Payment logged to database

## After Testing Successfully

### Option 1: Deploy to Production
- Choose hosting platform (Railway, Render, etc.)
- Set up production Stripe keys
- Configure production webhooks
- Deploy both services

### Option 2: Add Features
- User dashboard
- Payment history UI
- Usage analytics
- Email notifications

### Option 3: Documentation
- User guide
- API documentation
- Admin guide
- Deployment guide

## Quick Reference

- **License Server**: http://localhost:5001 (already running)
- **Web App**: http://localhost:8080 (start with `python3 web_app.py`)
- **Stripe CLI**: `stripe listen --forward-to localhost:8080/payments/webhook`
- **Test Scripts**: `test_stripe_payment.py`, `create_test_license.py`
- **Documentation**: `STRIPE_PAYMENT_TESTING.md`, `COMPLETE_STRIPE_SETUP.md`

## Troubleshooting

If services won't start:
- Check ports aren't in use: `lsof -Pi :8080` or `lsof -Pi :5001`
- Verify dependencies: `pip3 install -r requirements.txt`
- Check logs for errors

If payment doesn't work:
- Verify Stripe keys are set: `python3 -c "from redline.payment.config import PaymentConfig; print(PaymentConfig.validate())"`
- Check webhook forwarding is running
- Verify license server is accessible

