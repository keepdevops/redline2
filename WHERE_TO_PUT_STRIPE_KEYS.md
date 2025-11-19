# Where to Put Stripe Keys

## Quick Answer

**Put Stripe keys in the `.env` file** in the root directory of your project.

## Step-by-Step Guide

### Step 1: Create `.env` File (if it doesn't exist)

```bash
# Copy the template
cp env.template .env
```

### Step 2: Edit `.env` File

Open `.env` in your editor and find these lines (around line 37-44):

```bash
# Payment Configuration (Stripe)
# Get these from https://dashboard.stripe.com/test/apikeys (Test mode)
STRIPE_SECRET_KEY=sk_test_your-secret-key-here
STRIPE_PUBLISHABLE_KEY=pk_test_your-publishable-key-here
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret-here
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

### Step 3: Replace with Your Actual Keys

Replace the placeholder values with your actual Stripe keys:

```bash
STRIPE_SECRET_KEY=sk_test_51AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
STRIPE_PUBLISHABLE_KEY=pk_test_51AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdefghijklmnopqrstuvwxyz
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

### Step 4: Save and Restart

After saving `.env`:
- **Local**: Restart the app (`bash start_redline.sh` or `python3 web_app.py`)
- **Docker**: Restart containers (`docker-compose restart`)

## Where to Get Stripe Keys

### For Test Mode (Sandbox/Development)

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Make sure **"Test mode"** is ON (toggle in top right)
3. Copy:
   - **Secret Key** (starts with `sk_test_`)
   - **Publishable Key** (starts with `pk_test_`)

### For Live Mode (Production)

1. Go to: https://dashboard.stripe.com/apikeys
2. Make sure **"Live mode"** is ON (toggle in top right)
3. Copy:
   - **Secret Key** (starts with `sk_live_`)
   - **Publishable Key** (starts with `pk_live_`)

### Webhook Secret

1. Go to: https://dashboard.stripe.com/test/webhooks (or `/webhooks` for live)
2. Click on your webhook endpoint
3. Click **"Reveal"** next to "Signing secret"
4. Copy the secret (starts with `whsec_`)

## Different Deployment Scenarios

### Scenario 1: Local Development (No Docker)

**Location**: `.env` file in project root

```bash
# .env file
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

The `start_redline.sh` script automatically loads `.env` file.

### Scenario 2: Docker (docker-compose)

**Location**: `.env` file in project root

```bash
# .env file
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

The `docker-compose.yml` reads from `.env` using `${STRIPE_SECRET_KEY:-}` syntax.

**Verify it's working:**
```bash
docker-compose config | grep STRIPE
```

### Scenario 3: Production (Render, Heroku, etc.)

**Location**: Environment Variables in hosting platform

**For Render:**
1. Go to Render Dashboard → Your Service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add each variable:
   - `STRIPE_SECRET_KEY` = `sk_live_...`
   - `STRIPE_PUBLISHABLE_KEY` = `pk_live_...`
   - `STRIPE_WEBHOOK_SECRET` = `whsec_...`
   - `HOURS_PER_DOLLAR` = `0.2`
   - `PAYMENT_CURRENCY` = `usd`

**For Heroku:**
```bash
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_...
```

### Scenario 4: Direct Environment Variables

You can also set them directly in your shell:

```bash
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

Then start the app:
```bash
bash start_redline.sh
```

## File Locations Summary

| Deployment Type | File Location | Example |
|----------------|---------------|---------|
| Local (No Docker) | `.env` in project root | `/Users/caribou/redline/.env` |
| Docker Compose | `.env` in project root | `/Users/caribou/redline/.env` |
| Render | Environment Variables (Dashboard) | Render Dashboard → Environment |
| Heroku | Environment Variables (CLI) | `heroku config:set` |
| Direct | Shell environment | `export STRIPE_SECRET_KEY=...` |

## Verify Keys Are Loaded

### Check if keys are loaded:

```bash
python3 -c "
import os
import sys
sys.path.insert(0, '.')

# Load .env if exists
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if '#' in value:
                    value = value.split('#')[0].strip()
                os.environ[key.strip()] = value.strip()

from redline.payment.config import PaymentConfig
print('✅ Secret Key:', 'Set' if PaymentConfig.STRIPE_SECRET_KEY else '❌ Not Set')
print('✅ Publishable Key:', 'Set' if PaymentConfig.STRIPE_PUBLISHABLE_KEY else '❌ Not Set')
print('✅ Valid:', PaymentConfig.validate())
"
```

### Expected Output:
```
✅ Secret Key: Set
✅ Publishable Key: Set
✅ Valid: True
```

## Important Security Notes

1. **Never commit `.env` to git** - It contains secrets
2. **Check `.gitignore`** - Make sure `.env` is listed
3. **Use test keys** (`sk_test_`, `pk_test_`) for development
4. **Use live keys** (`sk_live_`, `pk_live_`) only in production
5. **Keep keys secret** - Don't share or expose publicly

## Troubleshooting

### Keys not working?

1. **Check file exists:**
   ```bash
   ls -la .env
   ```

2. **Check keys are set:**
   ```bash
   grep STRIPE .env
   ```

3. **Check no extra spaces:**
   ```bash
   # Should be: STRIPE_SECRET_KEY=sk_test_...
   # NOT: STRIPE_SECRET_KEY = sk_test_... (spaces around =)
   ```

4. **Restart after changes:**
   ```bash
   # Docker
   docker-compose restart
   
   # Local
   bash start_redline.sh
   ```

5. **Check logs for errors:**
   ```bash
   tail -f redline_web.log | grep -i stripe
   ```

## Quick Reference

**File to edit**: `.env` (in project root)

**Lines to update** (around line 40-44):
```bash
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
```

**Get keys from**: https://dashboard.stripe.com/test/apikeys

**Restart after**: Always restart the app after changing keys

