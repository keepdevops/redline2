# Setting Up DNS for Multiple Render Services
**Guide:** Configure Cloudflare DNS for multiple Render services

---

## 🎯 Overview

If you have **multiple Render services** (e.g., main app, API, license server), you need **one CNAME record per service**, each pointing to a different subdomain.

---

## 📊 Architecture Example

### Single Service (Current)
```
app.redfindat.com → redline-backend.onrender.com
```

### Multiple Services (Advanced)
```
app.redfindat.com    → redline-backend.onrender.com    (Main app)
api.redfindat.com    → redline-api.onrender.com        (API service)
license.redfindat.com → redline-license.onrender.com   (License server)
```

---

## 🔧 Setup for Multiple Services

### Step 1: Identify Your Render Services

List all your Render services and their URLs:

| Service | Render URL | Purpose |
|--------|------------|---------|
| Main App | `redline-backend.onrender.com` | Web interface |
| API | `redline-api.onrender.com` | API endpoints |
| License Server | `redline-license.onrender.com` | License validation |

---

### Step 2: Create CNAME Records for Each Service

**In Cloudflare Dashboard:**
1. Go to: DNS → Records
2. Add one CNAME record for each service

**Example Setup:**

#### Record 1: Main Application
- **Type**: CNAME
- **Name**: `app`
- **Target**: `redline-backend.onrender.com`
- **Proxy**: ✅ Proxied (orange cloud)
- **TTL**: Auto
- **Result**: `app.redfindat.com` → Main app

#### Record 2: API Service
- **Type**: CNAME
- **Name**: `api`
- **Target**: `redline-api.onrender.com`
- **Proxy**: ✅ Proxied (orange cloud)
- **TTL**: Auto
- **Result**: `api.redfindat.com` → API service

#### Record 3: License Server
- **Type**: CNAME
- **Name**: `license`
- **Target**: `redline-license.onrender.com`
- **Proxy**: ✅ Proxied (orange cloud)
- **TTL**: Auto
- **Result**: `license.redfindat.com` → License server

---

## 📋 Complete DNS Records Example

### Multiple Services Setup

```
Type    Name        Target                          Proxy   Purpose
CNAME   app         redline-backend.onrender.com    ✅      Main application
CNAME   api         redline-api.onrender.com        ✅      API service
CNAME   license     redline-license.onrender.com    ✅      License server
CNAME   www         redfindat.com                   ✅      WWW redirect
```

### Result URLs

- `https://app.redfindat.com` → Main REDLINE application
- `https://api.redfindat.com` → API endpoints
- `https://license.redfindat.com` → License server
- `https://www.redfindat.com` → Redirects to main

---

## 🏗️ Common Multi-Service Architectures

### Architecture 1: Separate API Service

**Use Case:** API separated from main app

```
app.redfindat.com    → redline-web.onrender.com     (Frontend + Web UI)
api.redfindat.com    → redline-api.onrender.com     (REST API)
```

**DNS Records:**
- CNAME `app` → `redline-web.onrender.com`
- CNAME `api` → `redline-api.onrender.com`

---

### Architecture 2: License Server Separate

**Use Case:** License server on separate Render service

```
app.redfindat.com      → redline-backend.onrender.com    (Main app)
license.redfindat.com  → redline-license.onrender.com    (License server)
```

**DNS Records:**
- CNAME `app` → `redline-backend.onrender.com`
- CNAME `license` → `redline-license.onrender.com`

**Update Environment Variable:**
```bash
LICENSE_SERVER_URL=https://license.redfindat.com
```

---

### Architecture 3: Microservices Setup

**Use Case:** Multiple specialized services

```
app.redfindat.com      → redline-web.onrender.com        (Web UI)
api.redfindat.com      → redline-api.onrender.com        (API)
worker.redfindat.com   → redline-worker.onrender.com     (Background jobs)
license.redfindat.com  → redline-license.onrender.com    (License)
```

**DNS Records:**
- CNAME `app` → `redline-web.onrender.com`
- CNAME `api` → `redline-api.onrender.com`
- CNAME `worker` → `redline-worker.onrender.com`
- CNAME `license` → `redline-license.onrender.com`

---

## ⚙️ Configuration Updates

### Update Environment Variables

When using multiple services, update environment variables:

#### Main App Service
```bash
# If license server is separate
LICENSE_SERVER_URL=https://license.redfindat.com

# If API is separate
API_BASE_URL=https://api.redfindat.com
```

#### API Service
```bash
# If main app is separate
FRONTEND_URL=https://app.redfindat.com
```

#### License Server
```bash
# License server configuration
PORT=5001
HOST=0.0.0.0
```

---

## 🔄 Single vs Multiple Services

### Single Service (Simpler) ✅

**Pros:**
- ✅ Easier to manage
- ✅ One DNS record
- ✅ Lower cost
- ✅ Simpler deployment

**Cons:**
- ⚠️ All traffic to one service
- ⚠️ Harder to scale individual components

**Best For:**
- Small to medium applications
- Starting out
- Simple architectures

**DNS Setup:**
```
CNAME app → redline-backend.onrender.com
```

---

### Multiple Services (More Flexible)

**Pros:**
- ✅ Independent scaling
- ✅ Separate deployments
- ✅ Better isolation
- ✅ Specialized services

**Cons:**
- ⚠️ More complex setup
- ⚠️ More DNS records
- ⚠️ Higher cost (multiple services)
- ⚠️ More to manage

**Best For:**
- Large applications
- Microservices architecture
- Need independent scaling

**DNS Setup:**
```
CNAME app     → redline-backend.onrender.com
CNAME api     → redline-api.onrender.com
CNAME license → redline-license.onrender.com
```

---

## 📝 Step-by-Step: Adding Another Service

### Example: Adding API Service

1. **Create API Service on Render**
   - Render Dashboard → New → Web Service
   - Deploy your API service
   - Get URL: `redline-api.onrender.com`

2. **Add DNS Record in Cloudflare**
   - Cloudflare Dashboard → DNS → Records
   - Click "Add record"
   - **Type**: CNAME
   - **Name**: `api`
   - **Target**: `redline-api.onrender.com`
   - **Proxy**: ✅ Proxied
   - Click "Save"

3. **Wait for DNS Propagation**
   - 5-15 minutes

4. **Test**
   ```bash
   curl https://api.redfindat.com/health
   ```

5. **Update Environment Variables**
   - In main app, update API URL if needed
   - Or configure API gateway/routing

---

## 🎯 Recommended Setup for REDLINE

### Current Setup (Single Service) ✅

**Recommended for most cases:**

```
app.redfindat.com → redline-backend.onrender.com
```

**Why:**
- REDLINE is designed as a single application
- All features in one service
- Simpler to manage
- Lower cost

**DNS Record:**
- One CNAME: `app` → `redline-backend.onrender.com`

---

### Advanced Setup (If Needed)

**Only if you need separate services:**

```
app.redfindat.com      → redline-web.onrender.com       (Web UI)
license.redfindat.com   → redline-license.onrender.com  (License server)
```

**When to use:**
- License server needs separate scaling
- Different deployment schedules
- Separate monitoring/alerting

**DNS Records:**
- CNAME `app` → `redline-web.onrender.com`
- CNAME `license` → `redline-license.onrender.com`

---

## ✅ Quick Reference

### One Service = One CNAME Record

```
Service Count    DNS Records Needed
1 service    →   1 CNAME record
2 services   →   2 CNAME records
3 services   →   3 CNAME records
N services   →   N CNAME records
```

### Subdomain Naming

Use descriptive subdomains:
- `app` - Main application
- `api` - API service
- `license` - License server
- `worker` - Background workers
- `admin` - Admin panel
- `cdn` - CDN/static assets

---

## 🔗 Related Guides

- **Single Service Setup**: See `SETUP_CLOUDFLARE_DNS_REDFINAT.md`
- **Render Deployment**: See `RENDER_DOCKER_HUB_SETUP.md`
- **Multiple Services**: This guide

---

## 📝 Summary

**Answer:** Yes, you need **one CNAME record per Render service**.

**Example:**
- 1 service → 1 CNAME record
- 2 services → 2 CNAME records
- 3 services → 3 CNAME records

**Each service gets its own subdomain:**
- `app.redfindat.com` → Main app
- `api.redfindat.com` → API service
- `license.redfindat.com` → License server

**For REDLINE:** Most users only need **one service** (main app), so **one CNAME record** is sufficient.

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
