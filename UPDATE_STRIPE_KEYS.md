# Update Stripe API Keys in .env

## Quick Fix

Your `.env` file needs actual Stripe test API keys. Here's how to update it:

### Step 1: Get Your Stripe Test Keys

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Make sure you're in **Test mode** (toggle in top right)
3. Copy your **Secret Key** (starts with `sk_test_`)
4. Copy your **Publishable Key** (starts with `pk_test_`)

### Step 2: Edit .env File

Open `.env` in your editor and update these lines:

```bash
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_PUBLISHABLE_KEY_HERE
```

Replace `YOUR_ACTUAL_SECRET_KEY_HERE` and `YOUR_ACTUAL_PUBLISHABLE_KEY_HERE` with your actual keys.

### Step 3: Verify

After updating, verify the keys are loaded:

```bash
python3 -c "
import os
import sys
sys.path.insert(0, '.')
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if '#' in value:
                    value = value.split('#')[0].strip()
                os.environ[key.strip()] = value.strip()

from redline.payment.config import PaymentConfig
print('Secret Key:', '✅ Set' if PaymentConfig.STRIPE_SECRET_KEY.startswith('sk_test_') else '❌ Not set')
print('Publishable Key:', '✅ Set' if PaymentConfig.STRIPE_PUBLISHABLE_KEY.startswith('pk_test_') else '❌ Not set')
print('Valid:', PaymentConfig.validate())
"
```

Expected output:
```
Secret Key: ✅ Set
Publishable Key: ✅ Set
Valid: True
```

### Step 4: Restart Web App

After updating keys, restart your web app:

```bash
# Stop current web app (Ctrl+C)
# Then restart:
python3 web_app.py
```

## Important Notes

- **Never commit .env to git** - it contains secrets
- Use **test keys** (`sk_test_` and `pk_test_`) for development
- Use **live keys** (`sk_live_` and `pk_live_`) only in production
- The webhook secret is already configured from Stripe CLI

## Troubleshooting

### "Keys not loading"
- Check `.env` file exists in project root
- Verify no extra spaces around `=`
- Ensure keys don't have quotes around them
- Restart web app after updating

### "Invalid key format"
- Secret keys must start with `sk_test_` or `sk_live_`
- Publishable keys must start with `pk_test_` or `pk_live_`
- No spaces or special characters

### "Configuration still invalid"
- Check both keys are set
- Verify keys are not placeholders
- Restart web app to reload environment

