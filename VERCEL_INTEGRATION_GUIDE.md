# Vercel Integration Guide for REDLINE

This guide explains how to integrate your `redline:latest` Docker container with Vercel.

## ⚠️ Important Note

Vercel **does not directly support Docker containers**. However, there are several approaches to integrate your REDLINE application with Vercel:

## 🎯 Recommended Approach: Hybrid Deployment

Deploy the Docker container on a Docker-compatible platform (Railway, Render, Fly.io) and use Vercel for the frontend with API proxying.

### Option 1: Vercel Frontend + External Backend (Recommended)

**Architecture:**
- **Backend**: Deploy `keepdevops/redline:latest` on Railway/Render/Fly.io
- **Frontend**: Deploy static assets and API proxy on Vercel

**Steps:**

1. **Deploy Docker Container on Railway/Render:**
   ```bash
   # On Railway or Render, use:
   docker run -d \
     -p 8080:8080 \
     -e FLASK_ENV=production \
     keepdevops/redline:latest
   ```

2. **Get your backend URL** (e.g., `https://redline-backend.railway.app`)

3. **Configure Vercel** (see `vercel.json` below)

### Option 2: Vercel Serverless Functions (Requires Refactoring)

Convert Flask routes to Vercel serverless functions. This requires significant refactoring but provides better Vercel integration.

### Option 3: Vercel Edge Functions + External Backend

Use Vercel Edge Functions to proxy requests to your Docker container backend.

---

## 📁 Configuration Files

### `vercel.json` - Vercel Configuration

This configuration proxies API requests to your Docker container backend:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-url.railway.app/api/$1"
    },
    {
      "src": "/data/(.*)",
      "dest": "https://your-backend-url.railway.app/data/$1"
    },
    {
      "src": "/download/(.*)",
      "dest": "https://your-backend-url.railway.app/download/$1"
    },
    {
      "src": "/analysis/(.*)",
      "dest": "https://your-backend-url.railway.app/analysis/$1"
    },
    {
      "src": "/converter/(.*)",
      "dest": "https://your-backend-url.railway.app/converter/$1"
    },
    {
      "src": "/settings/(.*)",
      "dest": "https://your-backend-url.railway.app/settings/$1"
    },
    {
      "src": "/tasks/(.*)",
      "dest": "https://your-backend-url.railway.app/tasks/$1"
    },
    {
      "src": "/health",
      "dest": "https://your-backend-url.railway.app/health"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "REDLINE_BACKEND_URL": "https://your-backend-url.railway.app"
  }
}
```

### `package.json` - Build Configuration

```json
{
  "name": "redline-vercel",
  "version": "1.0.0",
  "scripts": {
    "build": "echo 'Static build complete'",
    "start": "echo 'Vercel deployment ready'"
  },
  "dependencies": {}
}
```

---

## 🚀 Quick Start: Deploy to Railway + Vercel

### Step 1: Deploy Backend to Railway

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Create `railway.json`:**
   ```json
   {
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile"
     },
     "deploy": {
       "startCommand": "gunicorn -w 2 -b 0.0.0.0:$PORT web_app:app",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

3. **Or use Docker image directly:**
   ```bash
   railway init
   railway up --docker-image keepdevops/redline:latest
   ```

4. **Get your Railway URL** (e.g., `https://redline-production.up.railway.app`)

### Step 2: Deploy Frontend to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Update `vercel.json`** with your Railway backend URL

3. **Deploy:**
   ```bash
   vercel --prod
   ```

---

## 🔧 Alternative: Render Deployment

### Deploy to Render (Docker Support)

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: redline-backend
       env: docker
       dockerfilePath: ./Dockerfile
       dockerContext: .
       dockerCommand: gunicorn -w 2 -b 0.0.0.0:$PORT web_app:app
       envVars:
         - key: FLASK_ENV
           value: production
         - key: PORT
           value: 8080
       healthCheckPath: /health
   ```

2. **Or use Docker image:**
   - Go to Render Dashboard
   - Create New Web Service
   - Select "Docker" and enter: `keepdevops/redline:latest`
   - Set port: `8080`

---

## 🌐 Environment Variables

Set these in both Vercel and your backend platform:

**Vercel:**
- `REDLINE_BACKEND_URL` - Your backend URL
- `NEXT_PUBLIC_API_URL` - Public API URL (if using Next.js)

**Backend (Railway/Render):**
- `FLASK_ENV=production`
- `FLASK_APP=web_app.py`
- `PORT=8080`
- `SECRET_KEY` - Generate a secure key
- `REDIS_URL` - (Optional) For Celery tasks

---

## 📝 Serverless Function Approach (Advanced)

If you want to use Vercel serverless functions directly, you'll need to:

1. **Create API routes in `api/` directory:**
   ```
   api/
   ├── status.py
   ├── upload.py
   ├── convert.py
   └── ...
   ```

2. **Each function imports from your Docker container or uses the backend API**

3. **Example `api/status.py`:**
   ```python
   from http.server import BaseHTTPRequestHandler
   import requests
   import os

   class handler(BaseHTTPRequestHandler):
       def do_GET(self):
           backend_url = os.environ.get('REDLINE_BACKEND_URL')
           response = requests.get(f'{backend_url}/api/status')
           self.send_response(200)
           self.send_header('Content-type', 'application/json')
           self.end_headers()
           self.wfile.write(response.content)
           return
   ```

---

## 🔍 Testing the Integration

1. **Test Backend:**
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Test Vercel Proxy:**
   ```bash
   curl https://your-vercel-app.vercel.app/health
   ```

3. **Test API Endpoints:**
   ```bash
   curl https://your-vercel-app.vercel.app/api/status
   ```

---

## 🎯 Recommended Platform Comparison

| Platform | Docker Support | Cost | Ease of Use | Recommendation |
|----------|---------------|------|-------------|----------------|
| **Railway** | ✅ Yes | Pay-as-you-go | ⭐⭐⭐⭐⭐ | **Best for Docker** |
| **Render** | ✅ Yes | Free tier available | ⭐⭐⭐⭐ | Good alternative |
| **Fly.io** | ✅ Yes | Free tier | ⭐⭐⭐ | Good for global |
| **Vercel** | ❌ No | Free tier | ⭐⭐⭐⭐⭐ | **Best for frontend** |

---

## 📚 Additional Resources

- [Railway Docker Guide](https://docs.railway.app/deploy/dockerfiles)
- [Render Docker Guide](https://render.com/docs/docker)
- [Vercel Routing](https://vercel.com/docs/concepts/routing)
- [Vercel Serverless Functions](https://vercel.com/docs/concepts/functions)

---

## 🆘 Troubleshooting

### CORS Issues
Add CORS headers in your Flask app:
```python
from flask_cors import CORS
CORS(app, origins=["https://your-vercel-app.vercel.app"])
```

### WebSocket/SocketIO Issues
Vercel doesn't support WebSockets. Consider:
- Using polling mode for SocketIO
- Deploying SocketIO on the same backend platform

### Timeout Issues
Vercel has function timeout limits. For long-running tasks:
- Use background jobs (Celery)
- Return job IDs and poll for status

---

## ✅ Next Steps

1. Choose your backend platform (Railway recommended)
2. Deploy `keepdevops/redline:latest` to backend
3. Update `vercel.json` with backend URL
4. Deploy frontend to Vercel
5. Test the integration
6. Configure custom domain (optional)

