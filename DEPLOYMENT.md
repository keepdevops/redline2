# 🚀 VarioSync Cloud-Native Deployment Guide

Complete deployment guide for VarioSync using the cloud-native stack:
- **Render.com** - Web hosting
- **Modal** - Serverless processing
- **Supabase** - Auth & PostgreSQL database
- **Stripe** - Subscription billing
- **Cloudflare R2** - Object storage (or AWS S3)
- **DuckDB** - In-process analytics

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deploy to Render](#quick-deploy-to-render)
3. [Manual Setup Guide](#manual-setup-guide)
4. [Local Development with Docker](#local-development-with-docker)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

Before deploying, you need accounts and API keys from:

### 1. **Supabase** (Authentication & Database)
- [ ] Sign up at https://supabase.com
- [ ] Create new project
- [ ] Get credentials from: Project Settings → API
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_KEY`
  - `SUPABASE_JWT_SECRET`
- [ ] Run SQL schema: `setup_supabase_schema.sql`

### 2. **Stripe** (Payments)
- [ ] Sign up at https://stripe.com
- [ ] Get API keys from: Developers → API keys
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
- [ ] Create metered product:
  - Products → Add Product → "VarioSync Subscription"
  - Add Price → Usage-based → Per unit
  - Copy `STRIPE_PRICE_ID_METERED`
- [ ] Set up webhook (after Render deployment):
  - Developers → Webhooks → Add endpoint
  - URL: `https://your-app.onrender.com/payments/webhook`
  - Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.payment_*`
  - Copy `STRIPE_WEBHOOK_SECRET`

### 3. **Cloudflare R2** (Storage) - RECOMMENDED
- [ ] Sign up at https://cloudflare.com
- [ ] Create R2 bucket:
  - R2 → Create bucket → Name: `variosync-1`
- [ ] Create API token:
  - R2 → Manage R2 API Tokens → Create API Token
  - Copy `S3_ACCESS_KEY` and `S3_SECRET_KEY`
  - Copy account ID from dashboard URL
  - Endpoint: `https://{account-id}.r2.cloudflarestorage.com`

**Alternative: AWS S3**
- Sign up at https://aws.amazon.com
- Create S3 bucket
- Create IAM user with S3 access
- Get access keys

### 4. **Modal** (Serverless Processing)
- [ ] Sign up at https://modal.com
- [ ] Create token:
  - Settings → Tokens → Create token
  - Copy `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`

### 5. **Render** (Web Hosting)
- [ ] Sign up at https://render.com
- [ ] Connect GitHub account

---

## 🚀 Quick Deploy to Render

### Option A: One-Click Deploy (Blueprint)

1. **Click this button:**
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

2. **Fill in environment variables** in Render dashboard

3. **Done!** Your app will be live at `https://your-app.onrender.com`

### Option B: Manual Deploy via Dashboard

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy VarioSync cloud stack"
   git push origin spring
   ```

2. **Create Web Service in Render:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `spring` branch

3. **Configure Build:**
   - **Environment:** Docker
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Context:** `.`

4. **Set Environment Variables:**
   - Copy all variables from `.env.example`
   - Paste into Render dashboard (Environment tab)
   - **IMPORTANT:** Use real values, not placeholders!

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Visit your app URL when deployment succeeds

---

## 🔧 Manual Setup Guide

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/redline.git
cd redline
git checkout spring
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your actual credentials
nano .env  # or use your preferred editor
```

Fill in all required values (see [Environment Variables](#environment-variables) section).

### Step 3: Set Up Supabase Database

```bash
# Install Supabase CLI (optional)
npm install -g supabase

# Or run SQL manually
psql -h db.xxx.supabase.co -U postgres < setup_supabase_schema.sql
```

Alternatively, paste `setup_supabase_schema.sql` into Supabase SQL Editor.

### Step 4: Deploy Modal Functions

```bash
# Install Modal CLI
pip install modal

# Authenticate
modal token new

# Deploy processing functions
cd redline/processing
modal deploy modal_app.py
```

### Step 5: Configure Stripe Webhook

After Render deployment:

```bash
# Get your Render URL
RENDER_URL="https://your-app.onrender.com"

# Add webhook endpoint in Stripe Dashboard
# URL: $RENDER_URL/payments/webhook
# Events: All subscription and invoice events
```

### Step 6: Test Deployment

```bash
# Health check
curl https://your-app.onrender.com/health

# Should return: {"status": "healthy", "version": "3.0.0"}
```

---

## 🐳 Local Development with Docker

### Quick Start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit with your credentials
nano .env

# 3. Build and run
docker-compose -f docker-compose.cloud.yml up --build

# 4. Access app
open http://localhost:8080
```

### With Local PostgreSQL (Optional)

```bash
# Start with local database
docker-compose -f docker-compose.cloud.yml --profile local-db up

# Access PostgreSQL
psql -h localhost -U variosync -d variosync_dev
```

### With Redis Cache (Optional)

```bash
# Start with Redis
docker-compose -f docker-compose.cloud.yml --profile cache up
```

### Development Workflow

```bash
# Watch logs
docker-compose -f docker-compose.cloud.yml logs -f

# Restart after code changes
docker-compose -f docker-compose.cloud.yml restart

# Stop all services
docker-compose -f docker-compose.cloud.yml down
```

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | `eyJhbG...` |
| `SUPABASE_SERVICE_KEY` | Supabase service key | `eyJhbG...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` |
| `STRIPE_PRICE_ID_METERED` | Metered price ID | `price_...` |
| `S3_BUCKET` | Storage bucket name | `variosync-1` |
| `S3_ACCESS_KEY` | Storage access key | `...` |
| `S3_SECRET_KEY` | Storage secret key | `...` |
| `S3_ENDPOINT_URL` | Storage endpoint | R2 or S3 URL |
| `MODAL_TOKEN_ID` | Modal token ID | `ak-...` |
| `MODAL_TOKEN_SECRET` | Modal token secret | `as-...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GUNICORN_WORKERS` | `1` | Number of workers |
| `GUNICORN_THREADS` | `4` | Threads per worker |
| `DUCKDB_THREADS` | `4` | DuckDB threads |
| `LOG_LEVEL` | `INFO` | Logging level |
| `SMTP_ENABLED` | `false` | Enable emails |

---

## 🔍 Troubleshooting

### Build Fails

**Error:** `Failed to build docker image`

**Solution:**
```bash
# Check Docker daemon is running
docker info

# Try building locally first
docker build -t variosync-test .

# Check build logs
docker-compose -f docker-compose.cloud.yml build --progress=plain
```

### Environment Variables Not Set

**Error:** `KeyError: 'SUPABASE_URL'`

**Solution:**
- Ensure all required variables are set in Render dashboard
- Check for typos in variable names
- Restart service after adding variables

### Stripe Webhook Fails

**Error:** `Webhook signature verification failed`

**Solution:**
1. Ensure `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard
2. Webhook URL must be publicly accessible
3. Use Stripe CLI for local testing:
   ```bash
   stripe listen --forward-to localhost:8080/payments/webhook
   ```

### S3/R2 Connection Fails

**Error:** `Unable to connect to S3`

**Solution:**
- Verify endpoint URL is correct
- Check access key and secret key
- Ensure bucket exists
- For R2: Verify account ID in endpoint URL

### Modal Functions Not Working

**Error:** `Modal function not found`

**Solution:**
```bash
# Verify Modal is authenticated
modal token verify

# Redeploy functions
cd redline/processing
modal deploy modal_app.py

# Check logs
modal app logs modal_app
```

### Database Connection Issues

**Error:** `Cannot connect to Supabase`

**Solution:**
- Verify Supabase project is not paused
- Check database credentials
- Ensure SQL schema is applied
- Test connection:
  ```bash
  psql "$SUPABASE_URL" -c "SELECT 1"
  ```

---

## 📊 Health Checks

### Endpoints

- **Health:** `GET /health` - Service status
- **Status:** `GET /api/status` - Detailed status
- **Metrics:** `GET /metrics` - Application metrics (if enabled)

### Example

```bash
# Basic health check
curl https://your-app.onrender.com/health

# Response
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2026-01-07T12:00:00Z"
}
```

---

## 🎯 Production Checklist

Before going live:

- [ ] All environment variables set in Render
- [ ] Supabase database schema applied
- [ ] Stripe webhook configured with production keys
- [ ] S3/R2 bucket created and accessible
- [ ] Modal functions deployed
- [ ] HTTPS enabled (automatic with Render)
- [ ] Custom domain configured (optional)
- [ ] Error monitoring set up (Sentry, etc.)
- [ ] Backup strategy for database
- [ ] Rate limiting configured
- [ ] Security headers enabled

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Supabase Guides](https://supabase.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Modal Documentation](https://modal.com/docs)
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2/)

---

## 🆘 Support

Need help? Check these resources:

- **Documentation:** This file
- **Issues:** https://github.com/your-org/redline/issues
- **Email:** support@variosync.com

---

**Last Updated:** 2026-01-07
**VarioSync Version:** 3.0.0
