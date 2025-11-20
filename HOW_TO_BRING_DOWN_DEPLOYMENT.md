# How to Bring Down a Deployment
**Guide:** Stop or remove deployments on different platforms

---

## 🐳 Docker / Docker Compose

### Stop Containers (Keep Data)
```bash
# Stop all containers
docker-compose down

# Stop specific service
docker-compose stop redline-web-dev

# Stop all containers (force)
docker-compose kill
```

### Remove Everything (Including Volumes)
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove everything including images
docker-compose down -v --rmi all
```

### For Your Setup
```bash
# Stop Redline services
cd ~/redline
docker-compose -f docker-compose-full-dev.yml down

# Stop and remove volumes (clears data)
docker-compose -f docker-compose-full-dev.yml down -v
```

---

## ☁️ Render

### Method 1: Via Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your service
3. Click **"Manual Deploy"** → **"Suspend"**
   - Or click **"Settings"** → **"Suspend Service"**

### Method 2: Via Render CLI (if installed)
```bash
# List services
render services list

# Suspend service
render services suspend <service-id>
```

### Method 3: Delete Service
1. Render Dashboard → Your Service
2. Click **"Settings"**
3. Scroll down → **"Delete Service"**
4. Confirm deletion

**Note:** Deleting removes the service permanently. Suspending keeps it but stops it.

---

## 🌐 Cloudflare Pages

### Suspend Deployment
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Pages**
3. Click on your project
4. Go to **"Settings"** → **"Builds & deployments"**
5. Toggle **"Pause builds"** to ON

### Delete Project
1. Cloudflare Dashboard → Pages
2. Click on your project
3. Go to **"Settings"** → **"General"**
4. Scroll down → **"Delete project"**
5. Confirm deletion

---

## 🔧 Cloudflare Workers

### Delete Worker
1. Cloudflare Dashboard → Workers & Pages
2. Click on your worker
3. Go to **"Settings"**
4. Scroll down → **"Delete Worker"**
5. Confirm deletion

### Via Wrangler CLI
```bash
# Delete worker
wrangler delete redline-api-proxy

# Or with environment
wrangler delete redline-api-proxy --env production
```

---

## 📊 Quick Reference

### Docker
```bash
# Stop
docker-compose down

# Stop + Remove volumes
docker-compose down -v

# Stop + Remove everything
docker-compose down -v --rmi all
```

### Render
- **Suspend:** Dashboard → Service → Suspend
- **Delete:** Dashboard → Service → Settings → Delete

### Cloudflare Pages
- **Pause:** Dashboard → Pages → Project → Settings → Pause builds
- **Delete:** Dashboard → Pages → Project → Settings → Delete

### Cloudflare Workers
- **Delete:** Dashboard → Workers → Worker → Settings → Delete
- **CLI:** `wrangler delete <worker-name>`

---

## ⚠️ Important Notes

### Before Bringing Down

1. **Backup Data**
   - Export databases
   - Save environment variables
   - Download important files

2. **Check Dependencies**
   - Other services depending on this?
   - DNS records pointing to it?
   - Webhooks configured?

3. **Document Configuration**
   - Save `.env` files
   - Note service URLs
   - Record environment variables

### Docker Volumes
- `docker-compose down` → Keeps volumes (data preserved)
- `docker-compose down -v` → Removes volumes (data deleted)

### Render Services
- **Suspend:** Service stops but can be resumed
- **Delete:** Service removed permanently (can recreate)

### Cloudflare
- **Pause:** Builds stop, site still accessible
- **Delete:** Everything removed permanently

---

## 🔄 Restart After Bringing Down

### Docker
```bash
docker-compose up -d
```

### Render
- Resume suspended service from dashboard
- Or redeploy if deleted

### Cloudflare Pages
- Unpause builds from dashboard
- Or redeploy if deleted

---

## 📋 Checklist

Before bringing down:
- [ ] Backup important data
- [ ] Save environment variables
- [ ] Document service URLs
- [ ] Check dependent services
- [ ] Notify users (if production)

After bringing down:
- [ ] Verify service is stopped
- [ ] Check DNS (if applicable)
- [ ] Update documentation
- [ ] Clean up unused resources

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
