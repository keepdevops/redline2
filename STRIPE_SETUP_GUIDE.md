# Stripe Account Setup Guide

## Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Click "Sign up" or "Start now"
3. Create your account (email, password)
4. Complete account verification (email, phone, business details)

## Step 2: Get Test API Keys

### Access Test Mode

1. Log into Stripe Dashboard: https://dashboard.stripe.com
2. Ensure you're in **Test mode** (toggle in top right should show "Test mode")
3. If not in test mode, click the toggle to switch

### Get API Keys

1. Navigate to **Developers** → **API keys** (or go to https://dashboard.stripe.com/test/apikeys)
2. You'll see two keys:

**Publishable Key** (starts with `pk_test_`)
- This is safe to expose in frontend code
- Copy this key

**Secret Key** (starts with `sk_test_`)
- Click "Reveal test key" to see it
- **Keep this secret** - never commit to git or expose publicly
- Copy this key

### Get Webhook Secret

1. Navigate to **Developers** → **Webhooks** (or https://dashboard.stripe.com/test/webhooks)
2. Click **"Add endpoint"** or use existing endpoint
3. Enter your webhook URL:
   - Local testing: `http://localhost:8080/payments/webhook` (use Stripe CLI - see webhook setup guide)
   - Production: `https://yourdomain.com/payments/webhook`
4. Select events to listen for:
   - `checkout.session.completed` (required)
   - Optionally: `payment_intent.succeeded`, `payment_intent.payment_failed`
5. Click **"Add endpoint"**
6. After creating, click on the endpoint to view details
7. Click **"Reveal"** next to "Signing secret" to get webhook secret (starts with `whsec_`)
8. Copy this secret

## Step 3: Configure Environment Variables

### Option A: Create .env File (Recommended for Local)

1. Copy the template:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and add your Stripe keys:
   ```bash
   STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
   STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
   ```

3. **Important**: Add `.env` to `.gitignore` to prevent committing secrets:
   ```bash
   echo ".env" >> .gitignore
   ```

### Option B: Export Environment Variables

```bash
export STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
export STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
export STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

## Step 4: Verify Configuration

Run the payment configuration test:

```bash
python3 -c "from redline.payment.config import PaymentConfig; print('Valid:', PaymentConfig.validate())"
```

Expected output: `Valid: True` (if keys are set correctly)

## Step 5: Test Card Numbers

Stripe provides test card numbers for testing payments:

### Successful Payments

- **Visa**: `4242 4242 4242 4242`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`

**Expiry**: Any future date (e.g., `12/34`)
**CVC**: Any 3 digits (e.g., `123`)
**ZIP**: Any 5 digits (e.g., `12345`)

### Declined Payments (for Testing)

- **Card declined**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`
- **Expired card**: `4000 0000 0000 0069`

### 3D Secure (SCA) Testing

- **Requires authentication**: `4000 0025 0000 3155`
- **Authentication fails**: `4000 0000 0000 3055`

## Step 6: Test Mode vs Live Mode

### Test Mode (Current Setup)
- Use `pk_test_` and `sk_test_` keys
- No real charges
- Test cards work
- Perfect for development

### Live Mode (Production)
- Use `pk_live_` and `sk_live_` keys
- Real charges
- Real cards only
- Switch only when ready for production

## Security Best Practices

1. **Never commit API keys to git**
   - Use `.env` file (in `.gitignore`)
   - Use environment variables
   - Use secret management services in production

2. **Use test keys for development**
   - Always use test mode during development
   - Test keys start with `test_` prefix

3. **Rotate keys if exposed**
   - If keys are accidentally exposed, regenerate them in Stripe dashboard
   - Update all environments immediately

4. **Use webhook signatures**
   - Always verify webhook signatures
   - Never trust webhook data without verification

5. **Monitor API usage**
   - Check Stripe dashboard regularly
   - Set up alerts for unusual activity

## Troubleshooting

### "Invalid API Key"
- Check that you copied the full key (including `sk_test_` prefix)
- Ensure no extra spaces or newlines
- Verify you're using test keys in test mode

### "Webhook secret not configured"
- Ensure `STRIPE_WEBHOOK_SECRET` is set in environment
- Verify webhook endpoint is created in Stripe dashboard
- Check webhook secret matches the endpoint

### "Payment configuration is invalid"
- Run: `python3 -c "from redline.payment.config import PaymentConfig; PaymentConfig.validate()"`
- Check that all three Stripe keys are set
- Verify keys are not empty strings

## Next Steps

After setting up Stripe:
1. Set up webhook endpoint (see `STRIPE_WEBHOOK_SETUP.md`)
2. Create test license (see `create_test_license.py`)
3. Test payment flow (see `STRIPE_PAYMENT_TESTING.md`)

## Resources

- Stripe Dashboard: https://dashboard.stripe.com
- Stripe API Docs: https://stripe.com/docs/api
- Stripe Testing: https://stripe.com/docs/testing
- Stripe Webhooks: https://stripe.com/docs/webhooks

