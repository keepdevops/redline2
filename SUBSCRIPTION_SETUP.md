# Stripe Subscription Setup Guide

## Overview

You now have a complete Stripe Checkout subscription page for REDLINE with metered billing ($5/hour usage-based pricing).

## Files Created

### Templates (HTML Pages)
1. **`redline/web/templates/subscription.html`** - Main subscription landing page
   - Modern gradient design
   - Email input form
   - Pricing information
   - Feature list
   - Stripe Checkout integration

2. **`redline/web/templates/subscription_success.html`** - Success page after checkout
   - Welcome message
   - Next steps guide
   - Dashboard link
   - Billing portal link

3. **`redline/web/templates/subscription_cancel.html`** - Cancelled checkout page
   - Try again button
   - FAQ section
   - Support information

### Backend Routes
1. **`redline/web/routes/payments_checkout.py`** - Updated with new route:
   - `POST /payments/create-subscription-checkout` - Creates Stripe Checkout Session for subscriptions

2. **`redline/web/routes/payments_tab.py`** - Updated with new routes:
   - `GET /payments/subscription` - Display subscription landing page
   - `GET /payments/subscription-success` - Handle successful checkout
   - `GET /payments/subscription-cancel` - Handle cancelled checkout

3. **`redline/payment/config.py`** - Updated with:
   - `STRIPE_PRICE_ID_METERED` environment variable

## Required Environment Variables

Add these to your `.env` file or environment:

```bash
# Stripe Keys (get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_xxxxx  # Or sk_live_xxxxx for production
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx  # Or pk_live_xxxxx for production
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # From webhook setup

# Stripe Metered Price ID (from Step 3 you just completed)
STRIPE_PRICE_ID_METERED=price_xxxxx  # The price ID from your metered product
```

## How to Use

### 1. Access the Subscription Page

Open your browser and navigate to:
```
http://localhost:8080/payments/subscription
```

Or in production:
```
https://yourdomain.com/payments/subscription
```

### 2. Subscribe Flow

1. User enters their email address
2. Clicks "Subscribe Now"
3. Redirects to Stripe Checkout (hosted by Stripe)
4. User enters payment details
5. Completes payment
6. Redirects to `/payments/subscription-success`

### 3. Test in Development

**Using Stripe Test Mode:**

1. Make sure you're using test mode keys (`sk_test_...` and `pk_test_...`)
2. Visit the subscription page
3. Enter any email (e.g., `test@example.com`)
4. Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date (e.g., 12/25)
   - Any 3-digit CVC (e.g., 123)
   - Any ZIP code (e.g., 12345)
5. Complete checkout
6. You'll be redirected to the success page

**Test Cards:**
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
```

### 4. Webhook Setup (Important!)

For subscriptions to work properly in production, you **must** set up webhooks:

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Enter your webhook URL:
   ```
   https://yourdomain.com/payments/webhook
   ```
4. Select these events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Signing secret** → Set as `STRIPE_WEBHOOK_SECRET`

### 5. Test Webhooks Locally

Install Stripe CLI:
```bash
brew install stripe/stripe-cli/stripe
```

Forward webhooks to local server:
```bash
stripe listen --forward-to localhost:8080/payments/webhook
```

Trigger test events:
```bash
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
```

## Routes Summary

| Route | Method | Description |
|-------|--------|-------------|
| `/payments/subscription` | GET | Display subscription page |
| `/payments/create-subscription-checkout` | POST | Create Stripe Checkout Session |
| `/payments/subscription-success` | GET | Success page after checkout |
| `/payments/subscription-cancel` | GET | Cancelled checkout page |

## Next Steps

### Option 1: Continue with Infrastructure Setup

If you're following the migration plan, continue with:
- Step 4: Configure S3/R2 Storage
- Step 5: Set Up Modal
- Step 6: Configure Render

### Option 2: Test Subscription Page Now

1. Set the required environment variables
2. Start your Flask server:
   ```bash
   python web_app.py
   ```
3. Visit `http://localhost:8080/payments/subscription`
4. Test the subscription flow with Stripe test cards

### Option 3: Integrate with Supabase Auth

Once you have Supabase set up:
1. The subscription page will automatically create Supabase users
2. User email from checkout → Supabase Auth signup
3. Stripe customer_id → Stored in Supabase PostgreSQL
4. JWT tokens → Used for authentication

## Features

✅ **Modern UI**: Clean, gradient design with responsive layout
✅ **Stripe Checkout**: Secure, hosted payment page (PCI compliant)
✅ **Metered Billing**: Pay-per-use at $5/hour
✅ **Monthly Invoicing**: Automatic invoices from Stripe
✅ **Cancel Anytime**: No commitment, no cancellation fees
✅ **Success/Cancel Pages**: Professional user flow
✅ **Error Handling**: Comprehensive error messages
✅ **Email Validation**: Client-side validation
✅ **Loading States**: UX improvements during checkout

## Troubleshooting

### Error: "Stripe is not available"
**Solution**: Install stripe package
```bash
pip install stripe
```

### Error: "Subscription pricing not configured"
**Solution**: Set `STRIPE_PRICE_ID_METERED` environment variable
```bash
export STRIPE_PRICE_ID_METERED=price_xxxxx
```

### Error: "Payment configuration is invalid"
**Solution**: Set Stripe API keys
```bash
export STRIPE_SECRET_KEY=sk_test_xxxxx
export STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
```

### Checkout redirects to wrong URL
**Solution**: Check `request.host_url` is correct. If behind a proxy, configure Flask:
```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
```

## Production Checklist

Before going live:

- [ ] Switch to live Stripe keys (`sk_live_...`, `pk_live_...`)
- [ ] Set up production webhook endpoint
- [ ] Test webhook delivery
- [ ] Verify success/cancel URLs are correct
- [ ] Enable HTTPS (required for Stripe Checkout)
- [ ] Test subscription creation end-to-end
- [ ] Test subscription cancellation
- [ ] Verify invoices are generated
- [ ] Set up email notifications

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Metered Billing](https://stripe.com/docs/billing/subscriptions/usage-based)
- [Stripe Test Cards](https://stripe.com/docs/testing)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)

---

**Need Help?** Check the main migration plan at `/Users/caribou/.claude/plans/floating-swinging-sparrow.md`
