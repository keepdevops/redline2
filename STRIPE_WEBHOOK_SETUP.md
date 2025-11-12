# Stripe Webhook Setup Guide

## Overview

Webhooks allow Stripe to notify your application when payment events occur. For local development, you need to expose your local webhook endpoint to Stripe.

## Option 1: Stripe CLI (Recommended)

The Stripe CLI forwards webhook events from Stripe to your local server.

### Installation

**macOS (Homebrew):**
```bash
brew install stripe/stripe-cli/stripe
```

**Linux:**
```bash
# Download latest release
wget https://github.com/stripe/stripe-cli/releases/latest/download/stripe_*_linux_x86_64.tar.gz
tar -xvf stripe_*_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin/
```

**Windows:**
Download from: https://github.com/stripe/stripe-cli/releases

### Authentication

1. Login to Stripe CLI:
   ```bash
   stripe login
   ```
   This opens a browser to authorize the CLI.

2. Verify login:
   ```bash
   stripe config --list
   ```

### Forward Webhooks to Local Server

1. Start your web app (if not already running):
   ```bash
   python3 web_app.py
   ```

2. In a separate terminal, forward webhooks:
   ```bash
   stripe listen --forward-to localhost:8080/payments/webhook
   ```

3. The CLI will display a webhook signing secret:
   ```
   > Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
   ```

4. **Copy this secret** and add to your `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

5. Restart your web app to load the new secret.

### Test Webhook Delivery

1. Trigger a test event:
   ```bash
   stripe trigger checkout.session.completed
   ```

2. Check your web app logs for webhook processing.

### Using the Setup Script

We provide a helper script:

```bash
./setup_stripe_webhook.sh
```

This script:
- Checks if Stripe CLI is installed
- Starts webhook forwarding
- Displays the webhook secret
- Provides instructions for configuration

## Option 2: Ngrok (Alternative)

Ngrok creates a public tunnel to your local server.

### Installation

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### Setup

1. Sign up at https://ngrok.com (free account)

2. Get your authtoken from dashboard and configure:
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

3. Start your web app:
   ```bash
   python3 web_app.py
   ```

4. In another terminal, start ngrok:
   ```bash
   ngrok http 8080
   ```

5. Copy the forwarding URL (e.g., `https://abc123.ngrok.io`)

6. In Stripe Dashboard:
   - Go to **Developers** → **Webhooks**
   - Add endpoint: `https://abc123.ngrok.io/payments/webhook`
   - Select events: `checkout.session.completed`
   - Copy the webhook signing secret

7. Add secret to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

**Note**: Free ngrok URLs change on restart. For production, use a static domain or Stripe CLI.

## Option 3: Production Setup

For production deployment:

1. Deploy your web app to a public URL (e.g., `https://yourdomain.com`)

2. In Stripe Dashboard:
   - Go to **Developers** → **Webhooks**
   - Add endpoint: `https://yourdomain.com/payments/webhook`
   - Select events: `checkout.session.completed`
   - Copy the webhook signing secret

3. Set webhook secret in production environment variables

## Webhook Endpoint Configuration

Your webhook endpoint is already implemented at:
- **Route**: `/payments/webhook`
- **Method**: `POST`
- **File**: `redline/web/routes/payments.py`

The endpoint:
- Verifies webhook signature
- Handles `checkout.session.completed` events
- Adds hours to license
- Logs payment to database

## Testing Webhooks

### Manual Test

1. Create a test checkout session (via API or frontend)
2. Complete payment with test card
3. Check webhook logs in Stripe Dashboard
4. Verify hours added to license

### Using Stripe CLI

```bash
# Trigger checkout.session.completed event
stripe trigger checkout.session.completed

# View webhook events
stripe events list

# View specific event
stripe events retrieve evt_xxxxxxxxxxxxx
```

### Verify Webhook Processing

Check your application logs for:
```
INFO - Added X hours to license LICENSE_KEY via webhook
```

Check license balance:
```bash
curl "http://localhost:5001/api/licenses/LICENSE_KEY/hours"
```

## Troubleshooting

### "Webhook secret not configured"
- Ensure `STRIPE_WEBHOOK_SECRET` is set in environment
- Restart web app after setting secret
- Verify secret matches Stripe CLI or dashboard

### "Invalid signature"
- Webhook secret doesn't match
- Check that you're using the correct secret for your endpoint
- If using Stripe CLI, use the CLI-generated secret, not dashboard secret

### "Webhook not received"
- Check webhook forwarding is running (Stripe CLI)
- Verify ngrok tunnel is active
- Check firewall/network settings
- Verify webhook URL is correct

### "Event not handled"
- Check that `checkout.session.completed` event is selected
- Verify webhook handler code is correct
- Check application logs for errors

## Security Notes

1. **Always verify webhook signatures** - Your code already does this
2. **Use HTTPS in production** - Required for webhook security
3. **Keep webhook secret secure** - Never expose in client code
4. **Monitor webhook failures** - Set up alerts in Stripe dashboard

## Next Steps

After webhook setup:
1. Test webhook delivery (see testing section above)
2. Create test license
3. Test complete payment flow

