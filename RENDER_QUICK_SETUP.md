# Render Quick Setup Guide

## Step-by-Step: Creating Web Service on Render

### Step 1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### Step 2: Choose Deployment Method

**Option A: Docker Image (Recommended - Fastest)**
- Select **"Deploy an existing image from a registry"**
- **Image URL**: `keepdevops/redline:latest`
- Click **"Connect"**

**Option B: GitHub Repository**
- Click **"Connect account"** (if not connected)
- Select your repository
- Render will auto-detect `render.yaml`

### Step 3: Configure Service

- **Name**: `redline-backend` (or your preferred name)
- **Region**: Choose closest to users (e.g., "Oregon (US West)")
- **Branch**: `main` (if using Git)
- **Root Directory**: `.` (root of repo)
- **Plan**: 
  - **Starter** ($7/month) - Recommended to start
  - **Professional** ($25/month) - For higher traffic

### Step 4: Click "Create Web Service"

Render will start deploying. This takes 2-5 minutes.

---

## After Service is Created: Add Environment Variables

### Navigate to Environment Tab

1. Click on your service name in Render dashboard
2. Go to **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**

### Required Variables (Copy & Paste)

**1. Application Configuration:**
```
FLASK_ENV=production
FLASK_APP=web_app.py
PORT=8080
HOST=0.0.0.0
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
```

**2. Security Keys (Generate First!):**

Open terminal and run:
```bash
openssl rand -hex 32
```
Run twice to get two keys, then add:

```
SECRET_KEY=<paste-first-generated-key>
LICENSE_SECRET_KEY=<paste-second-generated-key>
```

**3. Stripe Production Keys:**

Get from https://dashboard.stripe.com/apikeys (Live mode):
```
STRIPE_SECRET_KEY=sk_live_<your-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
HOURS_PER_DOLLAR=0.2
PAYMENT_CURRENCY=usd
```

**4. Cloudflare R2 (Optional - Add Later if Needed):**
```
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY>
S3_SECRET_KEY=<R2_SECRET_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

**5. CORS (Important for Production):**
```
CORS_ORIGINS=https://app.redfindat.com,https://redfindat.com
```

### After Adding Variables

1. **Save Changes** - Render will automatically redeploy
2. **Wait for Deployment** - Check "Events" tab for progress
3. **View Logs** - Check "Logs" tab for any errors

---

## Verify Service is Running

### Check Service Status

1. Go to service dashboard
2. Status should show **"Live"** (green)
3. Service URL will be: `https://redline-backend-xxxx.onrender.com`

### Test Health Endpoint

```bash
curl https://redline-backend-xxxx.onrender.com/health
```

Should return: `{"status": "healthy"}` or similar

### Test in Browser

Open: `https://redline-backend-xxxx.onrender.com`

Should see REDLINE web interface.

---

## Next Steps After Render is Running

1. **Set up Cloudflare R2** (see `CLOUDFLARE_R2_SETUP.md`)
2. **Configure DNS** (see `CLOUDFLARE_DNS_SETUP.md`)
3. **Set up Stripe Webhook** (see `STRIPE_WEBHOOK_PRODUCTION.md`)

---

## Troubleshooting

### Service Won't Start

- Check **Logs** tab for errors
- Verify all required environment variables are set
- Ensure Docker image exists: `keepdevops/redline:latest`

### Health Check Failing

- Healthcheck is disabled in `render.yaml` (DuckDB constraint)
- Service should still work - check logs

### Port Issues

- Ensure `PORT=8080` is set
- Render uses `$PORT` variable automatically

---

## Quick Reference

**Render Dashboard**: https://dashboard.render.com  
**Service URL Format**: `https://<service-name>-xxxx.onrender.com`  
**Environment Variables**: Service → Environment tab  
**Logs**: Service → Logs tab  
**Events**: Service → Events tab

