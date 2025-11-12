# 🚀 Vercel Integration Quick Start

## TL;DR - Deploy REDLINE to Vercel in 3 Steps

### Step 1: Deploy Backend (Railway - Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Deploy Docker container
railway init
railway up --docker-image keepdevops/redline:latest

# Get your URL
railway domain
# Copy this URL - you'll need it for Step 2
```

### Step 2: Configure Vercel
```bash
# Edit vercel.json and replace YOUR_BACKEND_URL with your Railway URL
# Or use the deployment script:
./deploy_vercel.sh
```

### Step 3: Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel
vercel login

# Deploy
vercel --prod
```

---

## 🎯 Alternative: One-Command Deployment

### Using Railway + Vercel Scripts
```bash
# Deploy backend to Railway
./deploy_backend_railway.sh

# Deploy frontend to Vercel (after updating backend URL)
./deploy_vercel.sh
```

---

## 📋 Manual Configuration

### 1. Update `vercel.json`
Replace `YOUR_BACKEND_URL` with your actual backend URL:
```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-app.railway.app/api/$1"
    }
  ]
}
```

### 2. Set Environment Variables in Vercel
- Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- Add: `REDLINE_BACKEND_URL` = `https://your-app.railway.app`

### 3. Deploy
```bash
vercel --prod
```

---

## ✅ Verify Deployment

```bash
# Test backend
curl https://your-app.railway.app/health

# Test Vercel proxy
curl https://your-vercel-app.vercel.app/health

# Test API
curl https://your-vercel-app.vercel.app/api/status
```

---

## 🔧 Troubleshooting

### CORS Errors
Add to your Flask app (`web_app.py`):
```python
from flask_cors import CORS
CORS(app, origins=["https://your-vercel-app.vercel.app"])
```

### 404 Errors
- Check that `vercel.json` routes are correct
- Verify backend URL is accessible
- Check Vercel deployment logs

### Timeout Issues
- Vercel functions have 10s timeout (Hobby) or 60s (Pro)
- For long operations, use background jobs

---

## 📚 Full Documentation
See `VERCEL_INTEGRATION_GUIDE.md` for complete details.

