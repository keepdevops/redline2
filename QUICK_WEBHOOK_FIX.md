# Quick Webhook Fix

## Issue
Webhook endpoint returning 500 error because `STRIPE_WEBHOOK_SECRET` is not set.

## Solution

### Step 1: Add Webhook Secret to .env

Your webhook secret from Stripe CLI:
```
whsec_6fb9ac4b56b5e274e8bff1b3b115711f3d01b6d577816558ad05ba2ac6d45681
```

Add to `.env` file:
```bash
STRIPE_WEBHOOK_SECRET=whsec_6fb9ac4b56b5e274e8bff1b3b115711f3d01b6d577816558ad05ba2ac6d45681
```

### Step 2: Restart Web App

The web app needs to be restarted to load the new environment variable:

1. Stop the current web app (Ctrl+C in the terminal running it)
2. Restart it:
   ```bash
   python3 web_app.py
   ```

### Step 3: Verify

After restarting, trigger a test webhook:
```bash
stripe trigger checkout.session.completed
```

You should see `[200]` instead of `[500]` in the Stripe CLI output.

## Quick Command

If `.env` file exists:
```bash
echo "STRIPE_WEBHOOK_SECRET=whsec_6fb9ac4b56b5e274e8bff1b3b115711f3d01b6d577816558ad05ba2ac6d45681" >> .env
```

If `.env` doesn't exist:
```bash
cp env.template .env
# Then edit .env and add the webhook secret
```

