# Complete Cloud Deployment Guide for REDLINE

## Overview

This is the master guide for deploying REDLINE to production using Render, Cloudflare R2, and Cloudflare DNS. This guide combines all setup steps into a single workflow.

## Architecture

```
User Request
    ↓
Cloudflare DNS (redfindat.com)
    ↓
Cloudflare Proxy (SSL, DDoS protection)
    ↓
Render Service (Flask App)
    ├── DuckDB Database (local storage)
    ├── Stripe API (payments)
    └── Cloudflare R2 (file storage)
```

## Prerequisites

1. **Domain**: `redfindat.com` registered with Cloudflare
2. **Render Account**: https://render.com
3. **Stripe Account**: Production mode enabled
4. **Cloudflare Account**: R2 access enabled

## Deployment Steps

### Step 1: Deploy to Render

**Time**: 10-15 minutes

1. **Create Render Service**
   - Go to https://dashboard.render.com
   - New + → Web Service
   - Use Docker image: `keepdevops/redline:20251101`
   - Plan: Starter ($7/month)

2. **Configure Environment Variables**
   - See `PRODUCTION_ENV_TEMPLATE.md` for complete list
   - Minimum required:
     - `GUNICORN_WORKERS=1`
     - `SECRET_KEY` (generate)
     - `LICENSE_SECRET_KEY` (generate)
     - `STRIPE_SECRET_KEY` (production)
     - `STRIPE_PUBLISHABLE_KEY` (production)

3. **Verify Deployment**
   - Check service is "Live"
   - Test: `https://your-service.onrender.com/health`
   - Review logs for errors

**Reference**: See `RENDER_DEPLOYMENT_GUIDE.md` for detailed steps.

### Step 2: Set Up Cloudflare R2 Storage

**Time**: 10 minutes

1. **Create R2 Bucket**
   - Cloudflare Dashboard → R2
   - Create bucket: `redline-data`

2. **Get API Credentials**
   - R2 → Manage R2 API Tokens
   - Create token with read/write permissions
   - Save Access Key ID and Secret Access Key

3. **Get Endpoint URL**
   - Format: `https://<account-id>.r2.cloudflarestorage.com`
   - Find Account ID in Cloudflare Dashboard → Overview

4. **Add to Render Environment**
   ```bash
   USE_S3_STORAGE=true
   S3_BUCKET=redline-data
   S3_ACCESS_KEY=<R2_ACCESS_KEY>
   S3_SECRET_KEY=<R2_SECRET_KEY>
   S3_REGION=auto
   S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
   ```

**Reference**: See `CLOUDFLARE_R2_SETUP.md` for detailed steps.

### Step 3: Configure Cloudflare DNS

**Time**: 5-10 minutes

1. **Add CNAME Record**
   - Cloudflare Dashboard → DNS → Records
   - Type: CNAME
   - Name: `app`
   - Target: `your-service.onrender.com`
   - Proxy: Enabled (orange cloud)

2. **Configure SSL/TLS**
   - SSL/TLS → Overview
   - Mode: Full or Full (strict)

3. **Verify DNS**
   - Wait 5-15 minutes for propagation
   - Test: `curl https://app.redfindat.com/health`

**Reference**: See `CLOUDFLARE_DNS_SETUP.md` for detailed steps.

### Step 4: Configure Stripe Webhook

**Time**: 10 minutes

1. **Create Production Webhook**
   - Stripe Dashboard → Webhooks (Live mode)
   - Add endpoint: `https://app.redfindat.com/payments/webhook`
   - Select event: `checkout.session.completed`

2. **Get Webhook Secret**
   - Copy webhook signing secret (starts with `whsec_`)

3. **Add to Render Environment**
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_<your-secret>
   ```

4. **Test Webhook**
   - Stripe Dashboard → Send test webhook
   - Check Render logs for processing

**Reference**: See `STRIPE_WEBHOOK_PRODUCTION.md` for detailed steps.

### Step 5: Final Verification

**Time**: 10 minutes

1. **Test Application**
   - Access: `https://app.redfindat.com`
   - Verify SSL certificate is active
   - Test data download (Yahoo Finance)
   - Test file upload (should store in R2)

2. **Test Payments**
   - Create test checkout
   - Complete payment
   - Verify webhook processes
   - Check hours are credited

3. **Monitor Logs**
   - Render Dashboard → Logs
   - Check for errors
   - Verify all services connected

## Complete Environment Variables

See `PRODUCTION_ENV_TEMPLATE.md` for the complete list. Minimum required:

```bash
# Application
FLASK_ENV=production
GUNICORN_WORKERS=1
GUNICORN_THREADS=4

# Security
SECRET_KEY=<generated>
LICENSE_SECRET_KEY=<generated>

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
HOURS_PER_DOLLAR=0.2

# R2 Storage
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_KEY>
S3_SECRET_KEY=<R2_SECRET>
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# CORS
CORS_ORIGINS=https://app.redfindat.com
```

## Cost Summary

**Monthly Costs:**
- Render Starter: $7.00
- Cloudflare R2: $0-1.50 (first 10GB free)
- Cloudflare DNS/SSL: $0.00
- **Total: $7-8.50/month**

See `COST_TRACKING_AND_MARKUP.md` for detailed cost analysis.

## Troubleshooting

### Service Not Accessible

1. Check Render service status
2. Verify DNS propagation (5-15 minutes)
3. Check SSL certificate is active
4. Review Render logs for errors

### Storage Not Working

1. Verify R2 credentials in Render
2. Check R2 bucket exists
3. Verify endpoint URL format
4. Test R2 connection from application

### Payments Not Working

1. Verify Stripe keys are production (not test)
2. Check webhook endpoint is correct
3. Verify webhook secret matches
4. Check Render logs for webhook processing

## Quick Reference

### Key URLs

- **Application**: https://app.redfindat.com
- **Render Dashboard**: https://dashboard.render.com
- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **Stripe Dashboard**: https://dashboard.stripe.com

### Documentation Files

- `RENDER_DEPLOYMENT_GUIDE.md` - Render setup
- `CLOUDFLARE_R2_SETUP.md` - R2 storage setup
- `CLOUDFLARE_DNS_SETUP.md` - DNS configuration
- `STRIPE_WEBHOOK_PRODUCTION.md` - Webhook setup
- `PRODUCTION_ENV_TEMPLATE.md` - Environment variables
- `COST_TRACKING_AND_MARKUP.md` - Cost analysis

### Support

- **Email**: keepdevops@gmail.com
- **Issues**: Check logs in Render Dashboard
- **Documentation**: See individual guide files

## Success Checklist

- [ ] Render service deployed and running
- [ ] Environment variables configured
- [ ] R2 bucket created and connected
- [ ] DNS records configured
- [ ] SSL certificate active
- [ ] Stripe webhook configured
- [ ] Application accessible at https://app.redfindat.com
- [ ] Data downloads working
- [ ] File storage working (R2)
- [ ] Payments processing correctly
- [ ] Webhooks receiving events

## Next Steps

After deployment:

1. Monitor costs (see `COST_TRACKING_AND_MARKUP.md`)
2. Set up usage alerts
3. Configure monitoring
4. Review security settings
5. Plan for scaling if needed

---

**Domain**: redfindat.com  
**Application**: https://app.redfindat.com  
**Monthly Cost**: $7-8.50  
**Status**: Production Ready

