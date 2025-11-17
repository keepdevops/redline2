# Stripe Webhook Production Setup for app.redfindat.com

## Overview

This guide covers setting up Stripe webhooks for production deployment on `app.redfindat.com`.

## Prerequisites

1. **Stripe Account** (production mode)
   - Go to https://dashboard.stripe.com
   - Switch to **Live mode** (not test mode)

2. **Domain Configured**
   - `app.redfindat.com` is accessible via HTTPS
   - SSL certificate is active
   - Application is deployed and running

3. **Render Service Running**
   - Application accessible at `https://app.redfindat.com`
   - Health endpoint working: `https://app.redfindat.com/health`

## Step 1: Create Production Webhook Endpoint

### In Stripe Dashboard

1. **Navigate to Webhooks**
   - Go to https://dashboard.stripe.com/webhooks
   - Ensure you're in **Live mode** (toggle in top right)

2. **Add Endpoint**
   - Click **"Add endpoint"** button
   - Enter endpoint URL: `https://app.redfindat.com/payments/webhook`
   - Click **"Add endpoint"**

3. **Select Events**
   - Click on the newly created endpoint
   - Go to **"Select events to listen to"**
   - Select these events:
     - ✅ `checkout.session.completed` (required)
     - ✅ `payment_intent.succeeded` (optional, for additional tracking)
     - ✅ `payment_intent.payment_failed` (optional, for error handling)

4. **Save Events**
   - Click **"Add events"**
   - Webhook endpoint is now active

## Step 2: Get Webhook Signing Secret

1. **View Endpoint Details**
   - Click on your webhook endpoint
   - Scroll to **"Signing secret"** section

2. **Reveal Secret**
   - Click **"Reveal"** button next to "Signing secret"
   - Copy the secret (starts with `whsec_`)
   - **Important**: This is different from test mode secret

3. **Save Secret Securely**
   - Store in password manager
   - Do NOT commit to git
   - Will be added to Render environment variables

## Step 3: Configure Render Environment Variables

### Add to Render Dashboard

1. **Go to Render Dashboard**
   - Navigate to your service
   - Go to **Environment** tab

2. **Add Webhook Secret**
   - Click **"Add Environment Variable"**
   - **Key**: `STRIPE_WEBHOOK_SECRET`
   - **Value**: `whsec_...` (your production webhook secret)
   - Click **"Save Changes"**

3. **Verify Other Stripe Variables**
   - `STRIPE_SECRET_KEY` = `sk_live_...` (production key)
   - `STRIPE_PUBLISHABLE_KEY` = `pk_live_...` (production key)
   - `STRIPE_WEBHOOK_SECRET` = `whsec_...` (production webhook secret)

4. **Redeploy Service**
   - Render will automatically redeploy when environment variables change
   - Or manually trigger redeploy from dashboard

## Step 4: Test Webhook

### Using Stripe Dashboard

1. **Send Test Event**
   - Go to webhook endpoint details
   - Click **"Send test webhook"**
   - Select event: `checkout.session.completed`
   - Click **"Send test webhook"**

2. **Check Logs**
   - Go to Render Dashboard → Logs
   - Look for webhook processing messages
   - Should see: "Webhook received and processed"

### Using Stripe CLI (Alternative)

```bash
# Install Stripe CLI (if not installed)
# macOS: brew install stripe/stripe-cli/stripe
# Linux: See https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks to production (for testing)
stripe listen --forward-to https://app.redfindat.com/payments/webhook

# Trigger test event
stripe trigger checkout.session.completed
```

## Step 5: Verify Webhook Processing

### Check Application Logs

1. **View Render Logs**
   - Go to Render Dashboard → Your Service → Logs
   - Look for webhook-related messages

2. **Expected Log Messages**
   ```
   INFO: Stripe webhook received
   INFO: Processing checkout.session.completed event
   INFO: Hours added to license: RL-XXXXX
   ```

### Test Complete Payment Flow

1. **Create Test Payment**
   - Go to `https://app.redfindat.com/payments/`
   - Enter license key
   - Purchase hours (use test card: 4242 4242 4242 4242)

2. **Verify Webhook Processing**
   - Check Render logs for webhook event
   - Verify hours were added to license
   - Check license balance via API

3. **Check Stripe Dashboard**
   - Go to Stripe Dashboard → Webhooks
   - View webhook delivery logs
   - Should show successful deliveries (200 status)

## Webhook Endpoint Details

### Endpoint URL
```
https://app.redfindat.com/payments/webhook
```

### Supported Events

| Event | Required | Description |
|-------|----------|-------------|
| `checkout.session.completed` | ✅ Yes | Triggered when payment is completed |
| `payment_intent.succeeded` | Optional | Additional payment confirmation |
| `payment_intent.payment_failed` | Optional | Payment failure notification |

### Webhook Handler

**Location**: `redline/web/routes/payments.py`  
**Route**: `/payments/webhook`  
**Method**: POST  
**Authentication**: Stripe signature verification

## Security Considerations

### Webhook Signature Verification

The application automatically verifies webhook signatures:

```python
# In payments.py
event = stripe.Webhook.construct_event(
    payload, sig_header, STRIPE_WEBHOOK_SECRET
)
```

**Important**: Never disable signature verification in production.

### HTTPS Required

- Webhooks must use HTTPS (not HTTP)
- Cloudflare provides automatic SSL
- Stripe requires HTTPS for production webhooks

### Secret Management

- ✅ Store `STRIPE_WEBHOOK_SECRET` in Render environment variables
- ✅ Never commit to git
- ✅ Use different secrets for test and production
- ✅ Rotate secrets if compromised

## Troubleshooting

### Webhook Not Receiving Events

1. **Check Endpoint URL**
   - Verify URL is correct: `https://app.redfindat.com/payments/webhook`
   - Test endpoint is accessible: `curl https://app.redfindat.com/health`

2. **Check SSL Certificate**
   - Ensure SSL is active and valid
   - Check Cloudflare SSL/TLS mode (should be Full or Full strict)

3. **Check Stripe Dashboard**
   - Go to Webhooks → Your endpoint
   - View delivery logs
   - Check for error messages

### Webhook Signature Verification Failed

1. **Verify Secret**
   - Check `STRIPE_WEBHOOK_SECRET` in Render environment
   - Ensure it matches Stripe Dashboard secret
   - Ensure it's production secret (not test secret)

2. **Check Application Logs**
   - Look for "Signature verification failed" errors
   - Verify webhook secret is loaded correctly

### Hours Not Added After Payment

1. **Check Webhook Delivery**
   - Go to Stripe Dashboard → Webhooks → Delivery logs
   - Verify webhook was delivered (200 status)

2. **Check Application Logs**
   - Look for webhook processing messages
   - Check for errors in license server communication

3. **Test License Server**
   - Verify license server is accessible
   - Test license server API directly

## Production vs Test Mode

### Test Mode Webhook
- **URL**: `http://localhost:8080/payments/webhook` (local)
- **Secret**: Starts with `whsec_test_...`
- **Use**: Development and testing

### Production Mode Webhook
- **URL**: `https://app.redfindat.com/payments/webhook`
- **Secret**: Starts with `whsec_live_...` or `whsec_...`
- **Use**: Live payments from real customers

**Important**: Use production webhook secret in Render environment variables.

## Monitoring

### Stripe Dashboard

1. **Webhook Delivery Logs**
   - Go to Webhooks → Your endpoint → Delivery logs
   - View success/failure rates
   - Check response times

2. **Event Logs**
   - View all webhook events
   - Filter by event type
   - Check for errors

### Application Monitoring

1. **Render Logs**
   - Monitor webhook processing
   - Check for errors
   - Track processing times

2. **Application Metrics**
   - Track successful payments
   - Monitor hours added
   - Check license server communication

## Quick Reference

### Stripe Dashboard URLs

- **Webhooks**: https://dashboard.stripe.com/webhooks
- **API Keys**: https://dashboard.stripe.com/apikeys
- **Events**: https://dashboard.stripe.com/events

### Environment Variables (Render)

```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Test Commands

```bash
# Test webhook endpoint
curl -X POST https://app.redfindat.com/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check health
curl https://app.redfindat.com/health
```

## Next Steps

After webhook is configured:

1. ✅ Test with real payment (small amount)
2. ✅ Verify hours are added correctly
3. ✅ Monitor webhook delivery logs
4. ✅ Set up alerts for webhook failures
5. ✅ Document webhook retry policy

---

**Production Webhook URL**: https://app.redfindat.com/payments/webhook  
**Required Event**: `checkout.session.completed`  
**Secret Location**: Render environment variable `STRIPE_WEBHOOK_SECRET`

