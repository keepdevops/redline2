# Production Environment Variables Template for Render

## Overview

This document provides a complete template of all environment variables needed for REDLINE production deployment on Render with Cloudflare R2 and Stripe integration.

## Required Environment Variables

### Application Configuration

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=web_app.py
PORT=8080
HOST=0.0.0.0

# Gunicorn Configuration (DuckDB requires single worker)
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
```

### Security Keys

```bash
# Flask Secret Key (REQUIRED - Generate secure random key)
# Generate: openssl rand -hex 32
SECRET_KEY=<generate-secure-random-key-here>

# License Server Secret Key (REQUIRED)
# Generate: openssl rand -hex 32
LICENSE_SECRET_KEY=<generate-secure-random-key-here>
```

### Cloudflare R2 Storage Configuration

```bash
# Enable S3-compatible storage (R2 uses S3 API)
USE_S3_STORAGE=true

# R2 Bucket Configuration
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY_ID>
S3_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

**Note**: Variable names say "S3" but we're using Cloudflare R2. R2 is S3-compatible, so boto3 works with the endpoint URL.

### Stripe Production Configuration

```bash
# Stripe Production Keys (from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_<your-production-secret-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-production-publishable-key>

# Stripe Webhook Secret (from production webhook endpoint)
STRIPE_WEBHOOK_SECRET=whsec_<your-production-webhook-secret>

# Pricing Configuration
HOURS_PER_DOLLAR=0.2  # 1 hour = $5 (0.2 hours per dollar)
PAYMENT_CURRENCY=usd
```

### Optional: API Keys for Data Sources

```bash
# Alpha Vantage (optional - for enhanced data sources)
ALPHA_VANTAGE_API_KEY=<your-alpha-vantage-key>

# Finnhub (optional - for enhanced data sources)
FINNHUB_API_KEY=<your-finnhub-key>

# IEX Cloud (optional - for enhanced data sources)
IEX_CLOUD_API_KEY=<your-iex-cloud-key>
```

**Note**: These are optional. Yahoo Finance works without API keys.

### License Server Configuration

```bash
# License Server URL (if using separate license server)
LICENSE_SERVER_URL=http://localhost:5001

# Access Control
ENFORCE_PAYMENT=true  # Block access when hours are 0
REQUIRE_LICENSE_SERVER=false  # Set to true if license server is required
```

### Usage Tracking

```bash
# Usage Check Interval (seconds)
USAGE_CHECK_INTERVAL=30
```

### CORS Configuration

```bash
# Allowed CORS Origins (comma-separated)
CORS_ORIGINS=https://app.redfindat.com,https://redfindat.com
```

### Email Configuration (Optional)

```bash
# Email Configuration (for sending license keys)
SMTP_ENABLED=false  # Set to true to enable email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

## Complete Template

Copy this complete template and fill in the values:

```bash
# ============================================
# REDLINE Production Environment Variables
# ============================================

# Application
FLASK_ENV=production
FLASK_APP=web_app.py
PORT=8080
HOST=0.0.0.0

# Gunicorn (DuckDB requires GUNICORN_WORKERS=1)
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120

# Security (GENERATE NEW KEYS - DO NOT USE DEFAULTS)
SECRET_KEY=<generate-with-openssl-rand-hex-32>
LICENSE_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Cloudflare R2 Storage
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY_ID>
S3_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# Stripe Production
STRIPE_SECRET_KEY=sk_live_<your-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd

# Optional API Keys
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
IEX_CLOUD_API_KEY=

# License Server
LICENSE_SERVER_URL=http://localhost:5001
ENFORCE_PAYMENT=true
REQUIRE_LICENSE_SERVER=false

# Usage Tracking
USAGE_CHECK_INTERVAL=30

# CORS
CORS_ORIGINS=https://app.redfindat.com,https://redfindat.com

# Email (Optional)
SMTP_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=
```

## How to Set in Render

### Method 1: Render Dashboard

1. Go to Render Dashboard → Your Service
2. Click **Environment** tab
3. Click **"Add Environment Variable"**
4. Enter **Key** and **Value**
5. Click **"Save Changes"**
6. Service will automatically redeploy

### Method 2: Render CLI (if available)

```bash
# Set environment variable
render env:set STRIPE_SECRET_KEY=sk_live_...

# Set multiple variables
render env:set STRIPE_SECRET_KEY=sk_live_... STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## Security Checklist

- [ ] All secret keys are generated (not default values)
- [ ] Stripe keys are production keys (not test keys)
- [ ] R2 credentials are stored securely
- [ ] API keys are optional (only if using those services)
- [ ] CORS origins are restricted to your domain
- [ ] No secrets committed to git
- [ ] Environment variables set in Render (not in code)

## Key Generation

### Generate Secret Keys

```bash
# Generate Flask SECRET_KEY
openssl rand -hex 32

# Generate LICENSE_SECRET_KEY
openssl rand -hex 32

# Example output:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Get Stripe Keys

1. Go to https://dashboard.stripe.com/apikeys
2. Ensure **Live mode** (not test mode)
3. Copy **Secret key** (starts with `sk_live_`)
4. Copy **Publishable key** (starts with `pk_live_`)

### Get R2 Credentials

1. Go to Cloudflare Dashboard → R2 → Manage R2 API Tokens
2. Create new API token
3. Copy **Access Key ID**
4. Copy **Secret Access Key** (shown only once!)

## Verification

### Test Environment Variables

After setting variables in Render:

1. **Check Service Logs**
   - Go to Render Dashboard → Logs
   - Look for configuration errors
   - Verify variables are loaded

2. **Test Application**
   - Access `https://app.redfindat.com/health`
   - Should return 200 OK
   - Check logs for any missing variable warnings

3. **Test Storage**
   - Upload a test file
   - Verify it appears in R2 bucket

4. **Test Payments**
   - Create test checkout
   - Verify Stripe connection works

## Troubleshooting

### Variable Not Loading

1. **Check Variable Name**
   - Ensure exact match (case-sensitive)
   - No extra spaces

2. **Check Service Restart**
   - Render redeploys on env var changes
   - Wait for deployment to complete

3. **Check Logs**
   - Look for "environment variable not set" errors
   - Verify variable is in Render dashboard

### Secret Key Issues

1. **Generate New Keys**
   - Use `openssl rand -hex 32`
   - Never use default/example values

2. **Verify Key Format**
   - SECRET_KEY: 64 hex characters
   - LICENSE_SECRET_KEY: 64 hex characters
   - Stripe keys: Start with `sk_live_` or `pk_live_`

## Quick Reference

### Required Variables (Minimum)

```bash
FLASK_ENV=production
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
SECRET_KEY=<generated>
LICENSE_SECRET_KEY=<generated>
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Optional but Recommended

```bash
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_KEY>
S3_SECRET_KEY=<R2_SECRET>
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
CORS_ORIGINS=https://app.redfindat.com
```

---

**Service**: Render  
**Domain**: app.redfindat.com  
**Storage**: Cloudflare R2  
**Payments**: Stripe

