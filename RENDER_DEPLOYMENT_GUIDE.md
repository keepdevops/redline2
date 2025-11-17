# Render Deployment Guide for REDLINE

## Overview

This guide covers deploying REDLINE to Render cloud platform using the bytecode-optimized Docker image.

## Prerequisites

1. **Render Account**
   - Sign up at https://render.com
   - Free tier available (750 hours/month)

2. **Docker Image**
   - Image: `keepdevops/redline:20251101`
   - Available on Docker Hub

3. **Cloudflare R2** (optional but recommended)
   - R2 bucket created
   - API credentials obtained

4. **Stripe Account** (for payments)
   - Production API keys
   - Webhook endpoint configured

## Step 1: Create Render Service

### Option A: Via Render Dashboard

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository or Use Docker Image**
   
   **Option 1: Docker Image (Recommended)**
   - Select **"Deploy an existing image from a registry"**
   - **Image URL**: `keepdevops/redline:20251101`
   - Click **"Connect"**

   **Option 2: GitHub Repository**
   - Connect your GitHub repository
   - Render will use `render.yaml` for configuration

3. **Configure Service**
   - **Name**: `redline-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (if using Git)
   - **Root Directory**: `.` (root of repo)

4. **Select Plan**
   - **Starter**: $7/month (recommended for start)
   - **Professional**: $25/month (for higher traffic)

5. **Click "Create Web Service"**

### Option B: Via render.yaml (If Using Git)

If you have `render.yaml` in your repository:

1. **Push to GitHub**
   ```bash
   git add render.yaml
   git commit -m "Add Render configuration"
   git push
   ```

2. **Connect Repository in Render**
   - Render will automatically detect `render.yaml`
   - Service will be created from configuration

## Step 2: Configure Environment Variables

### Required Variables

Go to Render Dashboard → Your Service → Environment → Add Environment Variable

**Application:**
```bash
FLASK_ENV=production
FLASK_APP=web_app.py
PORT=8080
HOST=0.0.0.0
```

**Gunicorn (DuckDB requires single worker):**
```bash
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
```

**Security (Generate new keys):**
```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
LICENSE_SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

**Stripe Production:**
```bash
STRIPE_SECRET_KEY=sk_live_<your-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

**Cloudflare R2 (Optional):**
```bash
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY>
S3_SECRET_KEY=<R2_SECRET_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

**Optional API Keys:**
```bash
ALPHA_VANTAGE_API_KEY=<optional>
FINNHUB_API_KEY=<optional>
IEX_CLOUD_API_KEY=<optional>
```

**CORS:**
```bash
CORS_ORIGINS=https://app.redfindat.com,https://redfindat.com
```

See `PRODUCTION_ENV_TEMPLATE.md` for complete template.

## Step 3: Verify Deployment

### Check Service Status

1. **View Service Dashboard**
   - Go to Render Dashboard → Your Service
   - Check service status (should be "Live")

2. **View Logs**
   - Click **"Logs"** tab
   - Look for startup messages
   - Verify no errors

3. **Test Health Endpoint**
   ```bash
   curl https://your-service.onrender.com/health
   ```
   
   **Expected**: `{"status": "healthy"}` or similar

### Common Issues

**Service Not Starting:**
- Check logs for errors
- Verify environment variables are set
- Ensure Docker image is accessible

**Health Check Failing:**
- Healthcheck is disabled in render.yaml (DuckDB constraint)
- Service should still work without healthcheck

**Port Issues:**
- Ensure `PORT=8080` is set
- Render automatically assigns port via `$PORT` variable

## Step 4: Configure Custom Domain (Optional)

### Add Custom Domain in Render

1. **Go to Service Settings**
   - Render Dashboard → Your Service → Settings
   - Scroll to **"Custom Domains"**

2. **Add Domain**
   - Click **"Add Custom Domain"**
   - Enter: `app.redfindat.com`
   - Click **"Save"**

3. **Configure DNS**
   - Render will provide DNS instructions
   - Add CNAME record in Cloudflare (see CLOUDFLARE_DNS_SETUP.md)

**Note**: Using Cloudflare DNS is recommended (see CLOUDFLARE_DNS_SETUP.md)

## Step 5: Monitor and Maintain

### View Metrics

1. **Service Metrics**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

2. **Logs**
   - Real-time logs
   - Error tracking
   - Application output

### Update Service

1. **Update Environment Variables**
   - Changes trigger automatic redeploy
   - Wait for deployment to complete

2. **Update Docker Image**
   - Push new image to Docker Hub
   - Update `image` in render.yaml (if using)
   - Or manually update in Render dashboard

3. **Redeploy**
   - Manual redeploy: Dashboard → Manual Deploy
   - Auto-deploy: Enabled if using Git

## render.yaml Configuration

The `render.yaml` file is configured for production:

```yaml
services:
  - type: web
    name: redline-backend
    env: docker
    image: keepdevops/redline:20251101
    dockerCommand: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --worker-class gthread web_app:create_app()
    plan: starter
    envVars:
      - key: FLASK_ENV
        value: production
      - key: GUNICORN_WORKERS
        value: "1"
      - key: GUNICORN_THREADS
        value: "4"
```

**Key Points:**
- Uses bytecode image: `keepdevops/redline:20251101`
- Gunicorn workers: 1 (DuckDB requirement)
- Gunicorn threads: 4 (for concurrency)
- Healthcheck: Disabled (causes DuckDB issues)

## Cost Management

### Render Plans

| Plan | Cost | Features |
|------|------|----------|
| **Free** | $0 | 750 hours/month, spins down after inactivity |
| **Starter** | $7/month | Always-on, 512MB RAM, 0.5 CPU |
| **Professional** | $25/month | Always-on, 2GB RAM, 1 CPU |

**Recommendation**: Start with Starter ($7/month) for production.

### Cost Optimization

1. **Use Free Tier for Testing**
   - 750 hours/month free
   - Good for development/testing

2. **Monitor Usage**
   - Check Render dashboard for usage
   - Upgrade only if needed

3. **Optimize Storage**
   - Use R2 free tier (10GB)
   - Monitor storage usage

## Troubleshooting

### Service Won't Start

1. **Check Logs**
   - View Render logs for errors
   - Look for missing environment variables

2. **Verify Docker Image**
   - Ensure image exists: `keepdevops/redline:20251101`
   - Check Docker Hub for image availability

3. **Check Environment Variables**
   - Verify all required variables are set
   - Check for typos in variable names

### Application Errors

1. **DuckDB Lock Errors**
   - Ensure `GUNICORN_WORKERS=1` is set
   - Check logs for lock conflict messages

2. **Permission Errors**
   - Render handles permissions automatically
   - Check if custom file paths are writable

3. **Database Errors**
   - Verify DuckDB can create database files
   - Check storage permissions

### Performance Issues

1. **Slow Response Times**
   - Check Render service metrics
   - Consider upgrading to Professional plan
   - Optimize database queries

2. **Memory Issues**
   - Monitor memory usage in Render dashboard
   - Consider upgrading plan if needed

## Quick Reference

### Render Dashboard URLs

- **Dashboard**: https://dashboard.render.com
- **Services**: https://dashboard.render.com/services
- **Logs**: Render Dashboard → Your Service → Logs

### Service URL Format

```
https://<service-name>.onrender.com
```

### Common Commands

```bash
# Test service health
curl https://your-service.onrender.com/health

# Check service status
# (via Render Dashboard)
```

## Next Steps

After deployment:

1. ✅ Configure Cloudflare DNS (see CLOUDFLARE_DNS_SETUP.md)
2. ✅ Set up R2 storage (see CLOUDFLARE_R2_SETUP.md)
3. ✅ Configure Stripe webhook (see STRIPE_WEBHOOK_PRODUCTION.md)
4. ✅ Test application functionality
5. ✅ Monitor costs and usage

---

**Service**: Render Web Service  
**Image**: keepdevops/redline:20251101  
**Plan**: Starter ($7/month) or Professional ($25/month)

