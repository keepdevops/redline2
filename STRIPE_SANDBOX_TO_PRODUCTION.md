# Moving Stripe from Sandbox to Production
**Guide:** Migrate REDLINE from Stripe test mode to production mode

---

## 🎯 Overview

This guide covers moving from Stripe **test/sandbox mode** to **production mode** for live payments.

**Key Changes:**
- Test keys (`sk_test_...`, `pk_test_...`) → Production keys (`sk_live_...`, `pk_live_...`)
- Test webhook secret → Production webhook secret
- Test mode payments → Real payments

---

## ⚠️ Important Warnings

### Before Going Live

1. **Test Everything First**
   - ✅ Test all payment flows in sandbox
   - ✅ Verify webhook handling works
   - ✅ Test subscription model
   - ✅ Verify hour tracking

2. **Real Money**
   - ⚠️ Production mode uses **real credit cards**
   - ⚠️ Real charges will be made
   - ⚠️ Real money will be transferred

3. **Compliance**
   - ✅ Ensure you have proper business setup
   - ✅ Check local payment regulations
   - ✅ Set up proper tax handling (if needed)

---

## 📋 Step-by-Step Migration

### Step 1: Get Production Stripe Keys

1. **Go to Stripe Dashboard**
   - https://dashboard.stripe.com
   - **Important:** Toggle to **"Live mode"** (top right)
   - You'll see a warning - click "Activate live mode"

2. **Get API Keys**
   - Go to: **Developers** → **API keys**
   - You'll see two keys:
     - **Publishable key**: `pk_live_...` (starts with `pk_live_`)
     - **Secret key**: `sk_live_...` (starts with `sk_live_`)

3. **Copy Both Keys**
   - Click "Reveal test key" if needed
   - Copy the **Publishable key** (`pk_live_...`)
   - Copy the **Secret key** (`sk_live_...`)
   - **Save securely** - you'll need these

---

### Step 2: Update Environment Variables

#### For Render (Production)

1. **Go to Render Dashboard**
   - https://dashboard.render.com
   - Select your service
   - Go to **Environment** tab

2. **Update Stripe Keys**
   - Find `STRIPE_SECRET_KEY`
   - **Old value**: `sk_test_...`
   - **New value**: `sk_live_...` (your production secret key)
   - Click **"Save Changes"**

   - Find `STRIPE_PUBLISHABLE_KEY`
   - **Old value**: `pk_test_...`
   - **New value**: `pk_live_...` (your production publishable key)
   - Click **"Save Changes"**

3. **Verify Other Variables**
   - `HOURS_PER_DOLLAR=0.2` (should be set)
   - `PAYMENT_CURRENCY=usd` (should be set)

4. **Render Will Auto-Redeploy**
   - Changes trigger automatic redeploy
   - Wait for deployment to complete
   - Check logs for errors

#### For Local Development (Optional)

If you have a local `.env` file:

```bash
# .env file
STRIPE_SECRET_KEY=sk_live_<your-production-secret-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-production-publishable-key>
STRIPE_WEBHOOK_SECRET=whsec_<production-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

**Important:** Keep test keys in a separate file (`.env.test`) for development.

---

### Step 3: Set Up Production Webhook

**Critical:** Production webhook is different from test webhook!

1. **Go to Stripe Dashboard (Live Mode)**
   - Make sure you're in **"Live mode"** (top right)
   - Go to: **Developers** → **Webhooks**

2. **Add Endpoint**
   - Click **"Add endpoint"**
   - **Endpoint URL**: `https://your-render-service.onrender.com/payments/webhook`
   - Or if using custom domain: `https://app.yourdomain.com/payments/webhook`

3. **Select Events**
   - Click **"Select events"**
   - Choose: `checkout.session.completed`
   - Click **"Add events"**

4. **Get Webhook Secret**
   - After creating endpoint, click on it
   - Click **"Reveal"** next to "Signing secret"
   - Copy the secret: `whsec_...` (starts with `whsec_`)
   - **Save this immediately** - shown only once!

5. **Update Environment Variable**
   - Render Dashboard → Environment
   - Find `STRIPE_WEBHOOK_SECRET`
   - **Old value**: `whsec_...` (test webhook secret)
   - **New value**: `whsec_...` (production webhook secret)
   - Click **"Save Changes"**

6. **Test Webhook**
   - In Stripe Dashboard → Webhooks → Your endpoint
   - Click **"Send test webhook"**
   - Select: `checkout.session.completed`
   - Check Render logs to verify receipt

---

### Step 4: Update Frontend (If Needed)

If your frontend has hardcoded Stripe keys:

1. **Check Frontend Code**
   - Look for `pk_test_...` in JavaScript files
   - Update to `pk_live_...` (production publishable key)

2. **Or Use Environment Variable**
   - Better: Use environment variable
   - Frontend reads from backend API
   - No hardcoded keys needed

**Note:** Publishable keys are safe to expose in frontend code, but using environment variables is better practice.

---

### Step 5: Verify Configuration

1. **Check Environment Variables**
   ```bash
   # In Render Dashboard → Environment, verify:
   STRIPE_SECRET_KEY=sk_live_... ✅
   STRIPE_PUBLISHABLE_KEY=pk_live_... ✅
   STRIPE_WEBHOOK_SECRET=whsec_... ✅
   HOURS_PER_DOLLAR=0.2 ✅
   PAYMENT_CURRENCY=usd ✅
   ```

2. **Test Health Endpoint**
   ```bash
   curl https://your-service.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

3. **Check Logs**
   - Render Dashboard → Logs
   - Look for: "Stripe initialized" or similar
   - No errors about invalid API keys

---

### Step 6: Test Production Flow (Carefully!)

**⚠️ Warning:** This will charge real money!

1. **Use Test Card First**
   - Stripe provides test cards even in production
   - Use: `4242 4242 4242 4242`
   - Any future expiry date
   - Any CVC

2. **Test Payment Flow**
   - Register a user
   - Go to payment page
   - Enter test card: `4242 4242 4242 4242`
   - Complete checkout
   - Verify webhook received
   - Check hours were added

3. **Verify in Stripe Dashboard**
   - Stripe Dashboard → Payments (Live mode)
   - Should see test payment
   - Check webhook deliveries

---

## 🔄 Key Differences: Test vs Production

### Test Mode (Sandbox)

| Feature | Test Mode |
|---------|-----------|
| **API Keys** | `sk_test_...`, `pk_test_...` |
| **Webhook Secret** | `whsec_...` (test endpoint) |
| **Payments** | Fake/test cards only |
| **Money** | No real charges |
| **Dashboard** | Test mode toggle |
| **Use Case** | Development, testing |

### Production Mode (Live)

| Feature | Production Mode |
|---------|-----------------|
| **API Keys** | `sk_live_...`, `pk_live_...` |
| **Webhook Secret** | `whsec_...` (production endpoint) |
| **Payments** | Real credit cards |
| **Money** | Real charges, real transfers |
| **Dashboard** | Live mode toggle |
| **Use Case** | Real customers, real payments |

---

## 📝 Migration Checklist

### Pre-Migration
- [ ] All features tested in sandbox
- [ ] Webhook handling verified
- [ ] Subscription model working
- [ ] Business/legal setup complete
- [ ] Tax handling configured (if needed)

### Migration Steps
- [ ] Stripe account activated for live mode
- [ ] Production API keys obtained
- [ ] Production webhook endpoint created
- [ ] Production webhook secret obtained
- [ ] Environment variables updated in Render
- [ ] Service redeployed successfully
- [ ] Logs checked for errors

### Post-Migration Testing
- [ ] Test payment with test card (4242 4242 4242 4242)
- [ ] Verify webhook received
- [ ] Verify hours added to license
- [ ] Check Stripe Dashboard for payment
- [ ] Verify no errors in logs

### Go-Live
- [ ] Remove test mode warnings (if any)
- [ ] Update documentation
- [ ] Monitor first real payments closely
- [ ] Set up alerts for errors

---

## 🚨 Common Issues & Solutions

### Issue 1: "Invalid API Key" Error

**Symptoms:**
- Logs show: "Invalid API Key provided"
- Payments fail

**Solution:**
1. Verify you're using `sk_live_...` (not `sk_test_...`)
2. Check for typos in environment variable
3. Ensure no spaces around `=` in environment variable
4. Restart service after updating variables

### Issue 2: Webhook Not Receiving Events

**Symptoms:**
- Payments complete but hours not added
- Webhook logs show no events

**Solution:**
1. Verify webhook URL is correct (production URL)
2. Check webhook secret matches production secret
3. Ensure webhook is in "Live mode" (not test mode)
4. Test webhook manually from Stripe Dashboard

### Issue 3: Test Cards Not Working in Production

**Symptoms:**
- Test card `4242 4242 4242 4242` fails in production

**Solution:**
- Test cards work in production too!
- If failing, check:
  1. Card number is correct
  2. Expiry date is in future
  3. CVC is 3 digits
  4. Stripe account is fully activated

### Issue 4: Environment Variables Not Updating

**Symptoms:**
- Updated variables but still using old keys

**Solution:**
1. Render auto-redeploys on env var changes
2. Wait for deployment to complete
3. Check deployment logs
4. Verify variables in Render Dashboard
5. Restart service manually if needed

---

## 🔐 Security Best Practices

### Production Keys

1. **Never Commit to Git**
   - ✅ Use environment variables
   - ❌ Never hardcode in code
   - ❌ Never commit to repository

2. **Rotate Keys Regularly**
   - Rotate secret keys every 90 days
   - Update webhook secret if compromised
   - Use Stripe Dashboard → API keys → Rotate

3. **Limit Access**
   - Only give production keys to trusted team members
   - Use separate keys for different environments
   - Monitor API key usage in Stripe Dashboard

4. **Monitor Usage**
   - Set up Stripe alerts
   - Monitor for unusual activity
   - Review payment logs regularly

---

## 📊 Stripe Dashboard: Test vs Live

### Switching Between Modes

**In Stripe Dashboard:**
- Top right corner: Toggle between "Test mode" and "Live mode"
- **Test mode**: Gray/blue indicator
- **Live mode**: Green indicator

**Important:**
- Test and Live modes are completely separate
- Keys are different
- Webhooks are different
- Payments are separate

### Viewing Payments

**Test Mode:**
- Dashboard → Payments (Test mode)
- Shows only test payments
- No real money

**Live Mode:**
- Dashboard → Payments (Live mode)
- Shows real payments
- Real money transfers

---

## 🎯 Quick Reference

### Production Keys Format

```
Secret Key:      sk_live_51AbC123...
Publishable Key: pk_live_51XyZ789...
Webhook Secret:  whsec_AbCdEf123...
```

### Test Keys Format (for comparison)

```
Secret Key:      sk_test_51AbC123...
Publishable Key: pk_test_51XyZ789...
Webhook Secret:  whsec_AbCdEf123... (different from production)
```

### Environment Variables Template

```bash
# Production
STRIPE_SECRET_KEY=sk_live_<your-production-secret-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-production-publishable-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-production-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

---

## ✅ Post-Migration Verification

### 1. Check Service Status
```bash
curl https://your-service.onrender.com/health
```

### 2. Verify Stripe Keys
- Check Render logs for "Stripe initialized"
- No "Invalid API Key" errors

### 3. Test Webhook
- Stripe Dashboard → Webhooks → Send test webhook
- Check Render logs for webhook receipt

### 4. Test Payment (with test card)
- Use test card: `4242 4242 4242 4242`
- Complete checkout
- Verify hours added
- Check Stripe Dashboard for payment

---

## 🔗 Useful Links

- **Stripe Dashboard (Live)**: https://dashboard.stripe.com (toggle to Live mode)
- **Stripe API Keys**: https://dashboard.stripe.com/apikeys (Live mode)
- **Stripe Webhooks**: https://dashboard.stripe.com/webhooks (Live mode)
- **Stripe Test Cards**: https://stripe.com/docs/testing
- **Stripe Documentation**: https://stripe.com/docs

---

## 📝 Summary

**Migration Steps:**
1. ✅ Get production API keys from Stripe Dashboard (Live mode)
2. ✅ Create production webhook endpoint
3. ✅ Get production webhook secret
4. ✅ Update environment variables in Render
5. ✅ Test with test card (4242 4242 4242 4242)
6. ✅ Verify everything works
7. ✅ Go live!

**Time Required:** 15-30 minutes

**Difficulty:** ⭐⭐ Easy (mostly configuration)

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
