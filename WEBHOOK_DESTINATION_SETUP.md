# Webhook Destination Setup Guide

## What is a Webhook Destination?

A **webhook destination** is the URL where Stripe sends webhook events (like payment completions). You need to create this destination in Stripe Dashboard and point it to your application's webhook endpoint.

## Your Webhook Endpoint

Your Redline application already has a webhook endpoint configured:

- **Route**: `/payments/webhook`
- **Full URL (Local)**: `http://localhost:8080/payments/webhook`
- **Full URL (Production)**: `https://yourdomain.com/payments/webhook`
- **Method**: `POST`
- **File**: `redline/web/routes/payments_webhook.py`

## How to Create Webhook Destination in Stripe

### For Local Development (Test Mode)

#### Option 1: Using Stripe CLI (Recommended)

The Stripe CLI automatically creates a webhook destination and forwards events to your local server:

```bash
# 1. Install Stripe CLI
brew install stripe/stripe-cli/stripe

# 2. Login
stripe login

# 3. Start webhook forwarding (this creates the destination automatically)
stripe listen --forward-to localhost:8080/payments/webhook
```

The CLI will show you a webhook secret - copy this to your `.env` file.

#### Option 2: Using Stripe Dashboard + Ngrok

1. **Start ngrok to expose your local server:**
   ```bash
   ngrok http 8080
   ```
   Copy the forwarding URL (e.g., `https://abc123.ngrok.io`)

2. **Create webhook destination in Stripe Dashboard:**
   - Go to: https://dashboard.stripe.com/test/webhooks
   - Click **"Add endpoint"**
   - Enter endpoint URL: `https://abc123.ngrok.io/payments/webhook`
   - Click **"Add endpoint"**

3. **Select events:**
   - Click on the endpoint
   - Select events: `checkout.session.completed`
   - Click **"Add events"**

4. **Get webhook secret:**
   - Click on the endpoint
   - Click **"Reveal"** next to "Signing secret"
   - Copy the `whsec_...` secret

5. **Add to `.env`:**
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

### For Production

1. **Deploy your application** to a public URL (e.g., `https://yourdomain.com`)

2. **Create webhook destination in Stripe Dashboard:**
   - Go to: https://dashboard.stripe.com/webhooks (make sure you're in **Live mode**)
   - Click **"Add endpoint"**
   - Enter endpoint URL: `https://yourdomain.com/payments/webhook`
   - Click **"Add endpoint"**

3. **Select events:**
   - Click on the endpoint
   - Go to **"Select events to listen to"**
   - Select:
     - ✅ `checkout.session.completed` (required)
     - ✅ `payment_intent.succeeded` (optional)
     - ✅ `payment_intent.payment_failed` (optional)
   - Click **"Add events"**

4. **Get webhook secret:**
   - Click on the endpoint
   - Scroll to **"Signing secret"** section
   - Click **"Reveal"**
   - Copy the `whsec_...` secret

5. **Add to production environment variables:**
   - Render: Dashboard → Environment → Add `STRIPE_WEBHOOK_SECRET`
   - Heroku: `heroku config:set STRIPE_WEBHOOK_SECRET=whsec_...`
   - Docker: Add to `.env` file

## Step-by-Step: Create Webhook Destination in Stripe Dashboard

### Step 1: Navigate to Webhooks

1. Go to: https://dashboard.stripe.com
2. **Select mode:**
   - **Test mode**: https://dashboard.stripe.com/test/webhooks
   - **Live mode**: https://dashboard.stripe.com/webhooks
3. Toggle in top right shows current mode

### Step 2: Add Endpoint

1. Click **"Add endpoint"** button
2. Enter your webhook URL:
   ```
   https://yourdomain.com/payments/webhook
   ```
   Or for local with ngrok:
   ```
   https://abc123.ngrok.io/payments/webhook
   ```
3. Click **"Add endpoint"**

### Step 3: Select Events

1. Click on your newly created endpoint
2. Click **"Select events to listen to"** or **"Add events"**
3. Search and select:
   - ✅ `checkout.session.completed` (required)
   - Optionally: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Click **"Add events"**

### Step 4: Get Webhook Secret

1. Click on your webhook endpoint (in the list)
2. Scroll down to **"Signing secret"** section
3. Click **"Reveal"** button
4. **Copy the secret** (starts with `whsec_`)
5. **Important**: This secret is different for test and live modes

### Step 5: Configure Your Application

**For Local (.env file):**
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**For Production (Environment Variables):**
- Add `STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx` to your hosting platform

### Step 6: Restart Application

After adding the webhook secret:
```bash
# Docker
docker-compose restart

# Local
bash start_redline.sh
```

## Webhook Destination URL Format

Your webhook destination URL should be:

```
https://yourdomain.com/payments/webhook
```

**Important:**
- Must use `https://` (not `http://`) for production
- Must include `/payments/webhook` path
- Must be publicly accessible (not localhost, unless using Stripe CLI or ngrok)

## What Happens When You Create a Destination?

1. **Stripe stores the URL** - Stripe will send webhook events to this URL
2. **Events are queued** - When events occur (like payment completion), Stripe sends them to your endpoint
3. **Your app receives events** - Your `/payments/webhook` route handles the events
4. **Hours are added** - When `checkout.session.completed` is received, hours are added to the license

## Verify Webhook Destination is Working

### Test with Stripe CLI

```bash
# Trigger a test event
stripe trigger checkout.session.completed

# Check your app logs
tail -f redline_web.log | grep webhook
```

### Check Stripe Dashboard

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click on your endpoint
3. View **"Recent deliveries"** tab
4. You should see successful deliveries (200 status)

### Check Application Logs

```bash
# Look for webhook processing
tail -f redline_web.log | grep -i "webhook\|checkout.session"
```

Expected log message:
```
INFO - Added X hours to license LICENSE_KEY via webhook
```

## Multiple Webhook Destinations

You can create multiple webhook destinations:

- **Test mode destination**: For development/testing
- **Live mode destination**: For production
- **Different events**: Different endpoints for different event types

**Note**: Each destination has its own webhook secret. Make sure you use the correct secret for each environment.

## Troubleshooting

### "Webhook destination not receiving events"

1. **Check URL is correct:**
   - Verify the URL in Stripe Dashboard matches your actual endpoint
   - Test: `curl https://yourdomain.com/payments/webhook` (should return 405 or similar, not 404)

2. **Check SSL certificate:**
   - Production webhooks require HTTPS
   - Verify SSL is valid: `curl -I https://yourdomain.com`

3. **Check firewall/network:**
   - Ensure Stripe can reach your server
   - Check if port 443 (HTTPS) is open

4. **Check Stripe Dashboard:**
   - Go to Webhooks → Your endpoint → Recent deliveries
   - Look for failed deliveries and error messages

### "Invalid signature" error

- Webhook secret doesn't match
- Make sure you're using the correct secret for the endpoint
- If using Stripe CLI, use CLI secret (not dashboard secret)

### "Webhook not configured" error

- `STRIPE_WEBHOOK_SECRET` not set in environment
- Check `.env` file or environment variables
- Restart app after adding secret

## Quick Reference

**Create Destination (Stripe Dashboard):**
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. Enter: `https://yourdomain.com/payments/webhook`
4. Select events: `checkout.session.completed`
5. Get secret: Click endpoint → Reveal → Copy `whsec_...`

**Create Destination (Stripe CLI):**
```bash
stripe listen --forward-to localhost:8080/payments/webhook
# Copy the whsec_... secret shown
```

**Your Endpoint:**
- Route: `/payments/webhook`
- Method: `POST`
- File: `redline/web/routes/payments_webhook.py`

