# Stripe Troubleshooting for Render Deployment

## Common Issues and Solutions

### Issue: "Cannot use Stripe" or "Payment configuration is invalid"

This means Stripe environment variables are missing or incorrect in Render.

## Step 1: Check Render Environment Variables

1. Go to Render Dashboard → Your Service
2. Click **"Environment"** tab
3. Verify these variables exist:

**Required Stripe Variables:**
```
STRIPE_SECRET_KEY=sk_live_... (or sk_test_... for testing)
STRIPE_PUBLISHABLE_KEY=pk_live_... (or pk_test_... for testing)
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

**Optional (but recommended for production):**
```
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Step 2: Get Stripe Keys

### For Production (Live Mode)

1. Go to https://dashboard.stripe.com
2. **Toggle to "Live mode"** (top right - switch from "Test mode")
3. Go to **Developers** → **API keys**
4. Copy:
   - **Secret key** (starts with `sk_live_`)
   - **Publishable key** (starts with `pk_live_`)

### For Testing (Test Mode)

1. Go to https://dashboard.stripe.com
2. **Ensure "Test mode" is ON** (top right)
3. Go to **Developers** → **API keys**
4. Copy:
   - **Secret key** (starts with `sk_test_`)
   - **Publishable key** (starts with `pk_test_`)

## Step 3: Add Variables to Render

1. In Render Dashboard → Your Service → **Environment** tab
2. Click **"Add Environment Variable"**
3. Add each variable one by one:

**Variable 1:**
- **Key**: `STRIPE_SECRET_KEY`
- **Value**: `sk_live_...` (paste your secret key)
- Click **"Save Changes"**

**Variable 2:**
- **Key**: `STRIPE_PUBLISHABLE_KEY`
- **Value**: `pk_live_...` (paste your publishable key)
- Click **"Save Changes"**

**Variable 3:**
- **Key**: `HOURS_PER_DOLLAR`
- **Value**: `0.2`
- Click **"Save Changes"**

**Variable 4:**
- **Key**: `PAYMENT_CURRENCY`
- **Value**: `usd`
- Click **"Save Changes"**

## Step 4: Verify Stripe Package is Installed

The Docker image should include `stripe` package. Check Render logs:

1. Go to **Logs** tab
2. Look for any import errors related to `stripe`
3. If you see "Stripe is not available", the package might be missing

**Fix**: The `Dockerfile.webgui.bytecode` should include `stripe` in requirements. If not, add it to `requirements.txt` and rebuild.

## Step 5: Test Stripe Integration

### Check Payment Configuration

```bash
# Test from your local machine
curl https://your-service.onrender.com/payments/packages
```

**Expected Response:**
```json
{
  "packages": {
    "small": {"hours": 5, "price": 25, "name": "5 Hours Pack"},
    "medium": {"hours": 10, "price": 45, "name": "10 Hours Pack"},
    ...
  }
}
```

**Error Response (if Stripe not configured):**
```json
{
  "error": "Payment configuration is invalid. Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY."
}
```

### Check Application Logs

1. Go to Render Dashboard → Your Service → **Logs** tab
2. Look for:
   - ✅ "Stripe initialized" or similar success messages
   - ❌ "Payment configuration issues" warnings
   - ❌ "STRIPE_SECRET_KEY is not set" errors

## Common Errors and Fixes

### Error: "Payment configuration is invalid"

**Cause**: Missing `STRIPE_SECRET_KEY` or `STRIPE_PUBLISHABLE_KEY`

**Fix**: 
1. Add both variables to Render environment
2. Ensure keys start with `sk_live_` or `sk_test_` (secret) and `pk_live_` or `pk_test_` (publishable)
3. Redeploy service (Render auto-redeploys when env vars change)

### Error: "Stripe is not available"

**Cause**: `stripe` Python package not installed

**Fix**:
1. Check `requirements.txt` includes `stripe`
2. Rebuild Docker image if needed
3. Verify in logs that package is installed

### Error: "Invalid API key"

**Cause**: Wrong Stripe key format or using test keys in production

**Fix**:
- Ensure keys match the mode (test vs live)
- Check for typos or extra spaces
- Regenerate keys in Stripe Dashboard if needed

### Error: "Webhook secret not configured"

**Cause**: `STRIPE_WEBHOOK_SECRET` is missing (optional but recommended)

**Fix**:
1. Set up webhook in Stripe Dashboard (see `STRIPE_WEBHOOK_PRODUCTION.md`)
2. Add `STRIPE_WEBHOOK_SECRET` to Render environment

## Quick Checklist

- [ ] `STRIPE_SECRET_KEY` is set in Render environment
- [ ] `STRIPE_PUBLISHABLE_KEY` is set in Render environment
- [ ] `HOURS_PER_DOLLAR=0.2` is set
- [ ] `PAYMENT_CURRENCY=usd` is set
- [ ] Keys are correct format (`sk_live_...` or `sk_test_...`)
- [ ] Service has been redeployed after adding variables
- [ ] No errors in Render logs related to Stripe

## Testing Stripe Integration

### 1. Test Payment Packages Endpoint

```bash
curl https://your-service.onrender.com/payments/packages
```

Should return package list, not an error.

### 2. Test Create Checkout (requires license key)

```bash
curl -X POST https://your-service.onrender.com/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR_LICENSE_KEY",
    "hours": 5
  }'
```

Should return checkout session URL, not configuration error.

### 3. Test in Browser

1. Go to `https://your-service.onrender.com/payments/`
2. Should see payment interface
3. Should be able to select packages
4. Should redirect to Stripe Checkout when purchasing

## Still Not Working?

1. **Check Render Logs** for specific error messages
2. **Verify Environment Variables** are saved (no typos)
3. **Test with Test Mode Keys** first (easier to debug)
4. **Check Stripe Dashboard** for API key status
5. **Redeploy Service** after adding variables

## Need Help?

Check these files:
- `PRODUCTION_ENV_TEMPLATE.md` - Complete environment variables list
- `STRIPE_WEBHOOK_PRODUCTION.md` - Webhook setup guide
- `RENDER_DEPLOYMENT_GUIDE.md` - Full Render setup

