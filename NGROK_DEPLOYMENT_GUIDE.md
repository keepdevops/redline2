# 🌐 Ngrok Deployment Guide for REDLINE

Ngrok is a tunneling service that exposes your local Docker container to the internet. It's perfect for **testing, demos, and development**, but not recommended for production.

## 🎯 What is Ngrok?

Ngrok creates a secure tunnel from the internet to your local machine, allowing you to:
- Test your Docker container with a public URL
- Share your app temporarily
- Demo your application
- Develop with webhooks from external services

## ⚠️ Important Notes

**Ngrok is NOT a hosting platform:**
- ❌ Your computer must be running
- ❌ Not suitable for production
- ❌ Free tier has limitations (session timeouts, random URLs)
- ✅ Great for testing and demos
- ✅ Quick setup

## 🚀 Quick Start

### Option 1: Run Docker + Ngrok Locally

```bash
# 1. Start your Docker container locally
docker run -d \
  -p 8080:8080 \
  -e FLASK_ENV=production \
  --name redline-local \
  keepdevops/redline:latest

# 2. Install ngrok
# macOS
brew install ngrok/ngrok/ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok

# Windows
# Download from https://ngrok.com/download

# 3. Start ngrok tunnel
ngrok http 8080
```

You'll get a public URL like: `https://abc123.ngrok-free.app`

---

### Option 2: Using Docker Compose with Ngrok

Create `docker-compose.ngrok.yml`:

```yaml
version: '3.8'

services:
  redline:
    image: keepdevops/redline:latest
    container_name: redline-ngrok
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - PORT=8080
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ngrok:
    image: ngrok/ngrok:latest
    container_name: redline-ngrok-tunnel
    command: start --all --config /etc/ngrok.yml
    volumes:
      - ./ngrok.yml:/etc/ngrok.yml
    depends_on:
      - redline
    ports:
      - "4040:4040"  # Ngrok web interface
```

Start with:
```bash
docker-compose -f docker-compose.ngrok.yml up -d
```

---

## 🔧 Advanced Configuration

### Ngrok Configuration File (`ngrok.yml`)

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN  # Get from ngrok.com

tunnels:
  redline:
    addr: 8080
    proto: http
    bind_tls: true
    inspect: true
    hostname: your-custom-domain.ngrok.io  # Requires paid plan
```

### Using with Custom Domain (Paid Plan)

```bash
# Start with custom domain
ngrok http 8080 --domain=your-custom-domain.ngrok.io
```

### Using with Authentication

```bash
# Basic auth
ngrok http 8080 --basic-auth="username:password"

# OAuth (requires paid plan)
ngrok http 8080 --oauth="google"
```

---

## 📋 Setup Scripts

### Quick Start Script

```bash
#!/bin/bash
# start_ngrok.sh - Start REDLINE with ngrok

echo "🚀 Starting REDLINE with ngrok..."

# Start Docker container
docker run -d \
  -p 8080:8080 \
  -e FLASK_ENV=production \
  --name redline-ngrok \
  keepdevops/redline:latest

# Wait for container to be ready
echo "⏳ Waiting for REDLINE to start..."
sleep 5

# Check health
curl -f http://localhost:8080/health || echo "⚠️  Container not ready yet"

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 8080

# Cleanup on exit
trap "docker stop redline-ngrok && docker rm redline-ngrok" EXIT
```

---

## 🎯 Use Cases

### 1. **Local Testing with Public URL**
```bash
# Test webhooks, OAuth callbacks, etc.
docker run -d -p 8080:8080 keepdevops/redline:latest
ngrok http 8080
# Use the ngrok URL for testing
```

### 2. **Quick Demo**
```bash
# Share your app temporarily
ngrok http 8080
# Share the ngrok URL with others
```

### 3. **Development with Webhooks**
```bash
# Test webhook integrations
ngrok http 8080
# Configure webhook URL in external service
```

### 4. **Mobile Testing**
```bash
# Test on mobile devices
ngrok http 8080
# Access from your phone using the ngrok URL
```

---

## 🔐 Security Considerations

### Free Tier Limitations
- ⚠️ Random URLs (change on restart)
- ⚠️ Session timeouts (8 hours)
- ⚠️ Limited bandwidth
- ⚠️ No custom domains
- ⚠️ Warning page for visitors

### Paid Tier Benefits
- ✅ Custom domains
- ✅ Reserved domains
- ✅ No session timeouts
- ✅ Higher bandwidth
- ✅ No warning page
- ✅ IP whitelisting

### Security Best Practices
1. **Use authentication** for sensitive apps
2. **Set up firewall rules** to restrict access
3. **Use HTTPS** (ngrok provides this automatically)
4. **Monitor ngrok dashboard** for suspicious activity
5. **Don't use for production** - use proper hosting

---

## 🛠️ Ngrok Alternatives

### 1. **Cloudflare Tunnel (Free)**
```bash
# Install cloudflared
brew install cloudflared  # macOS
# or download from cloudflare.com

# Create tunnel
cloudflared tunnel --url http://localhost:8080
```

### 2. **LocalTunnel (Free)**
```bash
npm install -g localtunnel
lt --port 8080
```

### 3. **Serveo (Free)**
```bash
ssh -R 80:localhost:8080 serveo.net
```

### 4. **Bore (Free, Open Source)**
```bash
# Install bore
cargo install bore-cli

# Create tunnel
bore local 8080 --to bore.pub
```

---

## 📊 Comparison: Ngrok vs Alternatives

| Feature | Ngrok | Cloudflare Tunnel | LocalTunnel | Serveo |
|---------|-------|-------------------|-------------|--------|
| **Free Tier** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Custom Domain** | 💰 Paid | ✅ Free | ❌ No | ❌ No |
| **HTTPS** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Stability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 Production Alternatives

While ngrok is great for testing, for production consider:

1. **Railway** - Easiest Docker deployment
2. **Render** - Great free tier
3. **Fly.io** - Global edge network
4. **Google Cloud Run** - Serverless Docker
5. **DigitalOcean** - Simple pricing

See `DOCKER_DEPLOYMENT_ALTERNATIVES.md` for details.

---

## 📝 Example: Complete Setup

```bash
# 1. Get ngrok auth token (free at ngrok.com)
export NGROK_AUTH_TOKEN="your_token_here"
ngrok config add-authtoken $NGROK_AUTH_TOKEN

# 2. Start REDLINE container
docker run -d \
  -p 8080:8080 \
  -e FLASK_ENV=production \
  -e CORS_ORIGINS="https://*.ngrok-free.app" \
  --name redline \
  keepdevops/redline:latest

# 3. Start ngrok
ngrok http 8080

# 4. Access your app
# Use the URL from ngrok output (e.g., https://abc123.ngrok-free.app)
```

---

## 🔍 Monitoring

### Ngrok Web Interface
Access at: `http://localhost:4040` (when ngrok is running)

Features:
- Request inspection
- Replay requests
- View headers and responses
- Monitor traffic

### Check Container Status
```bash
# Check if container is running
docker ps | grep redline

# Check logs
docker logs redline-ngrok

# Check health
curl http://localhost:8080/health
```

---

## 🆘 Troubleshooting

### Ngrok URL Not Working
```bash
# Check if container is running
docker ps

# Check container logs
docker logs redline-ngrok

# Test local connection
curl http://localhost:8080/health
```

### CORS Errors
Add ngrok URL to CORS_ORIGINS:
```bash
docker run -d \
  -p 8080:8080 \
  -e CORS_ORIGINS="https://*.ngrok-free.app,https://*.ngrok.io" \
  keepdevops/redline:latest
```

### Port Already in Use
```bash
# Use different port
docker run -d -p 8081:8080 keepdevops/redline:latest
ngrok http 8081
```

---

## ✅ Quick Reference

```bash
# Start REDLINE
docker run -d -p 8080:8080 --name redline keepdevops/redline:latest

# Start ngrok
ngrok http 8080

# Stop everything
docker stop redline && docker rm redline
# Ctrl+C to stop ngrok
```

---

## 📚 Resources

- [Ngrok Documentation](https://ngrok.com/docs)
- [Ngrok Pricing](https://ngrok.com/pricing)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [LocalTunnel](https://localtunnel.github.io/www/)

---

**Remember:** Ngrok is for **testing and demos**. For production, use a proper hosting platform like Railway, Render, or Fly.io!

