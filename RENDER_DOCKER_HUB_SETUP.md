# Render Setup Using Docker Hub
**Quick Guide:** Deploy REDLINE to Render using Docker Hub image

---

## 🎯 Overview

Render supports deploying directly from Docker Hub images. This is the **fastest way** to deploy REDLINE without building from source.

**Docker Image:** `keepdevops/redline:latest` (or specific version tags)

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Render Service

1. **Go to Render Dashboard**
   - https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**

2. **Select Docker Image Option**
   - Choose **"Deploy an existing image from a registry"**
   - **Image URL**: `keepdevops/redline:latest`
   - Click **"Connect"**

3. **Configure Service**
   - **Name**: `redline-backend` (or your preferred name)
   - **Region**: Choose closest to users (e.g., "Oregon (US West)")
   - **Plan**: 
     - **Starter** ($7/month) - Always-on, recommended
     - **Free** - Spins down after inactivity

4. **Click "Create Web Service"**

---

### Step 2: Configure Docker Command

Render will auto-detect the command, but you can customize:

**Docker Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --worker-class gthread --access-logfile - --error-logfile - web_app:create_app()
```

**Why these settings:**
- `--workers 1`: DuckDB requires single worker
- `--threads 4`: Handle concurrent requests
- `--timeout 120`: Allow longer operations
- `--worker-class gthread`: Thread-based workers

---

### Step 3: Add Environment Variables

Go to **Environment** tab → **Add Environment Variable**

**Required Variables:**

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=web_app.py
PORT=8080
HOST=0.0.0.0

# Gunicorn Configuration
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120

# Security Keys (Generate these!)
SECRET_KEY=<generate-with-openssl-rand-hex-32>
LICENSE_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Stripe (Production Keys)
STRIPE_SECRET_KEY=sk_live_<your-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

**Generate Security Keys:**
```bash
# Run this twice to get two keys
openssl rand -hex 32
```

**Optional: Cloudflare R2 Storage**
```bash
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY>
S3_SECRET_KEY=<R2_SECRET_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

---

### Step 4: Verify Deployment

1. **Check Service Status**
   - Should show **"Live"** (green badge)
   - Service URL: `https://redline-backend-xxxx.onrender.com`

2. **Test Health Endpoint**
   ```bash
   curl https://redline-backend-xxxx.onrender.com/health
   ```
   Should return: `{"status":"ok"}` or `{"status":"healthy"}`

3. **Check Logs**
   - Render Dashboard → Your Service → Logs
   - Look for: "REDLINE Web application created successfully"

---

## 📋 Available Docker Images

### Latest Version
```
keepdevops/redline:latest
```

### Specific Versions
```
keepdevops/redline:2.1.0
keepdevops/redline:20251119
```

### Image Variants

**Bytecode-Optimized (Recommended for Production):**
```
keepdevops/redline:latest
```
- Python bytecode compiled
- Source files removed
- Smaller image size
- Better performance

**Development (with source):**
```
keepdevops/redline:dev
```
- Includes source files
- Easier debugging
- Larger image size

---

## 🔧 Advanced Configuration

### Using render.yaml (Alternative Method)

If you prefer configuration as code:

**Create `render.yaml`:**
```yaml
services:
  - type: web
    name: redline-backend
    env: docker
    # Docker Hub image
    image: keepdevops/redline:latest
    dockerCommand: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --worker-class gthread --access-logfile - --error-logfile - web_app:create_app()
    plan: starter
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_APP
        value: web_app.py
      - key: PORT
        value: "8080"
      - key: HOST
        value: 0.0.0.0
      - key: GUNICORN_WORKERS
        value: "1"
      - key: GUNICORN_THREADS
        value: "4"
      - key: GUNICORN_TIMEOUT
        value: "120"
```

**Then:**
1. Push `render.yaml` to GitHub
2. Connect GitHub repo in Render
3. Render will auto-detect and use `render.yaml`

---

## 🔄 Updating Docker Image

### Method 1: Manual Update (Dashboard)

1. Render Dashboard → Your Service → Settings
2. Scroll to **"Docker Image"**
3. Update image tag (e.g., `keepdevops/redline:2.1.0`)
4. Click **"Save Changes"**
5. Render will redeploy automatically

### Method 2: Auto-Deploy on New Tag

1. Render Dashboard → Your Service → Settings
2. Enable **"Auto-Deploy"**
3. Set to deploy on new Docker Hub tags
4. Render will automatically deploy when new image is pushed

---

## 🐳 Docker Hub Image Details

### Image Repository
**Docker Hub:** https://hub.docker.com/r/keepdevops/redline

### Image Tags
- `latest` - Latest stable release
- `2.1.0` - Version 2.1.0
- `20251119` - Date-based tag
- `dev` - Development version

### Image Size
- **Bytecode version**: ~500-600 MB
- **Development version**: ~700-800 MB

### Base Image
- Python 3.11-slim
- Includes all dependencies
- Pre-compiled bytecode

---

## ⚙️ Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_APP` | Flask app entry point | `web_app.py` |
| `PORT` | Port to listen on | `8080` |
| `HOST` | Host to bind to | `0.0.0.0` |
| `SECRET_KEY` | Flask secret key | `(generate)` |
| `LICENSE_SECRET_KEY` | License server key | `(generate)` |

### Gunicorn Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GUNICORN_WORKERS` | Number of workers | `1` (required for DuckDB) |
| `GUNICORN_THREADS` | Threads per worker | `4` |
| `GUNICORN_TIMEOUT` | Request timeout (seconds) | `120` |

### Stripe Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook secret | `whsec_...` |
| `HOURS_PER_DOLLAR` | Pricing (hours per $1) | `0.2` (=$5/hour) |
| `PAYMENT_CURRENCY` | Payment currency | `usd` |

### Storage Variables (Optional)

| Variable | Description | Example |
|----------|-------------|---------|
| `USE_S3_STORAGE` | Enable S3/R2 storage | `true` |
| `S3_BUCKET` | Bucket name | `redline-data` |
| `S3_ACCESS_KEY` | Access key ID | `(from R2)` |
| `S3_SECRET_KEY` | Secret access key | `(from R2)` |
| `S3_REGION` | Region | `auto` (for R2) |
| `S3_ENDPOINT_URL` | Endpoint URL | `https://<id>.r2.cloudflarestorage.com` |

---

## 🚨 Troubleshooting

### Service Won't Start

**Check Logs:**
- Render Dashboard → Your Service → Logs
- Look for errors or stack traces

**Common Issues:**
1. **Missing environment variables**
   - Ensure all required variables are set
   - Check `SECRET_KEY` and `LICENSE_SECRET_KEY` are set

2. **Port conflicts**
   - Ensure `PORT=8080` is set
   - Render uses `$PORT` automatically

3. **Docker image not found**
   - Verify image exists: `docker pull keepdevops/redline:latest`
   - Check image tag is correct

### Health Check Failing

**Note:** Health check is disabled in `render.yaml` (DuckDB constraint)

**If you need health checks:**
1. Render Dashboard → Your Service → Settings
2. **Health Check Path**: `/health`
3. **Health Check Timeout**: `100` seconds

**But:** DuckDB single-worker constraint may cause issues with health checks.

### Slow Startup

**Free Tier:**
- Service spins down after 15 minutes of inactivity
- First request takes 30-60 seconds (cold start)
- Upgrade to Starter plan ($7/month) for always-on

**Starter Plan:**
- Service stays running
- No cold starts
- Better for production

---

## 📊 Render Plans Comparison

| Plan | Cost | Always-On | RAM | CPU | Best For |
|------|------|-----------|-----|-----|----------|
| **Free** | $0 | ❌ No | 512MB | 0.1 | Testing |
| **Starter** | $7/mo | ✅ Yes | 512MB | 0.5 | Production |
| **Professional** | $25/mo | ✅ Yes | 2GB | 1.0 | High Traffic |

**Recommendation:** Use **Starter** plan for production with subscription model.

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Docker Hub image exists (`keepdevops/redline:latest`)
- [ ] Render account created
- [ ] Stripe keys ready (production)
- [ ] Security keys generated

### Deployment
- [ ] Service created in Render
- [ ] Docker image configured
- [ ] Docker command set
- [ ] Environment variables added
- [ ] Service deployed successfully

### Post-Deployment
- [ ] Service status: "Live"
- [ ] Health endpoint returns 200
- [ ] Test subscription flow
- [ ] Verify Stripe webhook works
- [ ] Check logs for errors

---

## 🔗 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Docker Hub**: https://hub.docker.com/r/keepdevops/redline
- **Render Docs**: https://render.com/docs
- **REDLINE Docs**: See `RENDER_DEPLOYMENT_GUIDE.md`

---

## 🎯 Next Steps After Render Setup

1. ✅ **Set up Cloudflare DNS** (see `ADD_CLOUDFLARE_TO_EXISTING_RENDER.md`)
2. ✅ **Configure Cloudflare R2** (see `CLOUDFLARE_R2_SETUP.md`)
3. ✅ **Set up Stripe Webhook** (see `WHERE_TO_PUT_STRIPE_KEYS.md`)
4. ✅ **Test subscription flow**

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
