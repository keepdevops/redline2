# 🚀 Ngrok Quick Start for REDLINE

## TL;DR - Expose Your Docker Container in 30 Seconds

```bash
# 1. Start container
docker run -d -p 8080:8080 --name redline keepdevops/redline:latest

# 2. Start ngrok
ngrok http 8080

# 3. Use the URL from ngrok output
# Example: https://abc123.ngrok-free.app
```

---

## 📋 Prerequisites

1. **Docker** installed and running
2. **ngrok** installed
   ```bash
   # macOS
   brew install ngrok/ngrok/ngrok
   
   # Or download from https://ngrok.com/download
   ```

3. **Ngrok account** (free at https://ngrok.com)
   - Get auth token from dashboard

---

## 🎯 Step-by-Step

### Step 1: Get Ngrok Auth Token
1. Sign up at https://ngrok.com (free)
2. Go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your auth token

### Step 2: Configure Ngrok
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 3: Start REDLINE
```bash
docker run -d \
  -p 8080:8080 \
  -e FLASK_ENV=production \
  --name redline \
  keepdevops/redline:latest
```

### Step 4: Start Ngrok
```bash
ngrok http 8080
```

### Step 5: Use Your Public URL
Ngrok will show you a URL like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8080
```

Use this URL to access your app from anywhere!

---

## 🔧 Using the Script

```bash
# Make executable
chmod +x start_ngrok.sh

# Run
./start_ngrok.sh
```

This script:
- ✅ Starts the Docker container
- ✅ Waits for it to be ready
- ✅ Starts ngrok tunnel
- ✅ Handles cleanup on exit

---

## 🌐 Access Points

- **Your App**: Use the ngrok URL (e.g., `https://abc123.ngrok-free.app`)
- **Ngrok Dashboard**: `http://localhost:4040` (inspect requests)

---

## ⚠️ Important Notes

1. **Free Tier Limitations:**
   - Random URLs (change on restart)
   - 8-hour session timeout
   - Warning page for visitors
   - Limited bandwidth

2. **For Production:**
   - Use Railway, Render, or Fly.io instead
   - See `DOCKER_DEPLOYMENT_ALTERNATIVES.md`

3. **Security:**
   - Add authentication for sensitive apps
   - Monitor ngrok dashboard
   - Don't expose production data

---

## 🆘 Troubleshooting

### Container Not Starting
```bash
# Check logs
docker logs redline

# Check if port is in use
lsof -i :8080
```

### Ngrok Not Working
```bash
# Check if ngrok is authenticated
ngrok config check

# Test local connection first
curl http://localhost:8080/health
```

### CORS Errors
Add ngrok domains to CORS:
```bash
docker run -d \
  -p 8080:8080 \
  -e CORS_ORIGINS="https://*.ngrok-free.app,https://*.ngrok.io" \
  keepdevops/redline:latest
```

---

## 📚 Next Steps

- **For Testing:** Ngrok is perfect! ✅
- **For Production:** Use Railway, Render, or Fly.io
- **For Custom Domain:** Upgrade ngrok plan or use Cloudflare Tunnel

---

**Quick Tip:** Keep the ngrok terminal open - closing it stops the tunnel!

