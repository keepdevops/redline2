# Cloudflare Deployment Guide for REDLINE with Subscription Model
**Version:** 2.1.0  
**Date:** November 19, 2025

---

## Overview

This guide covers deploying REDLINE on Cloudflare infrastructure with a subscription-based payment model. Cloudflare offers multiple deployment options, each with different trade-offs.

---

## 🏗️ Deployment Architecture Options

### Option 1: Cloudflare Pages + Backend Proxy (Recommended)
**Best for:** Full Flask app with subscription model

```
User Request
    ↓
Cloudflare DNS (your-domain.com)
    ↓
Cloudflare Pages (Frontend Static Assets)
    ↓
Cloudflare Workers (API Proxy)
    ↓
Backend Service (Render/Railway)
    ├── Flask App
    ├── Stripe Integration
    ├── License Server
    └── R2 Storage
```

**Pros:**
- ✅ Full Flask app support
- ✅ Cloudflare CDN for static assets
- ✅ DDoS protection
- ✅ SSL/TLS automatic
- ✅ Global edge network

**Cons:**
- ⚠️ Backend still needs separate hosting (Render/Railway)
- ⚠️ Additional cost for backend hosting

---

### Option 2: Cloudflare Workers (Python Workers)
**Best for:** API-only deployment

```
User Request
    ↓
Cloudflare Workers (Python Runtime)
    ├── API Routes
    ├── Stripe Integration
    └── R2 Storage
```

**Pros:**
- ✅ True serverless
- ✅ Global edge deployment
- ✅ Pay-per-request pricing
- ✅ No cold starts

**Cons:**
- ⚠️ Limited runtime (10ms CPU time on free tier)
- ⚠️ No long-running processes
- ⚠️ Limited Python library support
- ⚠️ DuckDB may not work (needs file system)

---

### Option 3: Hybrid - Pages + Workers + External Backend
**Best for:** Production deployment with subscription

```
User Request
    ↓
Cloudflare Pages (Static Frontend)
    ↓
Cloudflare Workers (API Gateway)
    ├── Routes to Workers (lightweight)
    └── Routes to Backend (heavy operations)
    ↓
External Backend (Render/Railway)
    └── Flask App (full features)
```

**Pros:**
- ✅ Best of both worlds
- ✅ Edge-optimized routing
- ✅ Full Flask features available
- ✅ Subscription model works

**Cons:**
- ⚠️ More complex setup
- ⚠️ Multiple services to manage

---

## 🎯 Recommended: Option 1 (Pages + Backend Proxy)

This is the **recommended approach** for REDLINE with subscription model.

---

## 📋 Step-by-Step Deployment

### Step 1: Set Up Cloudflare Account & Domain

1. **Register/Transfer Domain to Cloudflare**
   - Go to https://dash.cloudflare.com
   - Add your domain (e.g., `redfindat.com`)
   - Update nameservers if needed

2. **Enable Required Services**
   - **Pages**: For frontend hosting
   - **Workers**: For API proxying (optional)
   - **R2**: For file storage (see CLOUDFLARE_R2_SETUP.md)

---

### Step 2: Deploy Backend to Render/Railway

**Why:** Cloudflare Workers has limitations for full Flask apps. Use Render/Railway for backend.

1. **Deploy to Render** (Recommended)
   ```bash
   # Use existing render.yaml or deploy via dashboard
   # Image: keepdevops/redline:latest
   # Plan: Starter ($7/month) or Professional ($25/month)
   ```

2. **Get Backend URL**
   - Render service URL: `https://redline-xxxx.onrender.com`
   - Note this URL for Cloudflare configuration

3. **Configure Environment Variables in Render**
   ```bash
   FLASK_ENV=production
   ENV=production
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   USE_S3_STORAGE=true
   S3_BUCKET=redline-data
   S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
   S3_ACCESS_KEY=<R2_ACCESS_KEY>
   S3_SECRET_KEY=<R2_SECRET_KEY>
   S3_REGION=auto
   LICENSE_SERVER_URL=http://license-server:5001
   REQUIRE_LICENSE_SERVER=false  # For sandbox
   ```

**Reference:** See `RENDER_DEPLOYMENT_GUIDE.md` for detailed steps.

---

### Step 3: Set Up Cloudflare Pages (Frontend)

1. **Create Pages Project**
   - Go to Cloudflare Dashboard → Pages
   - Click **"Create a project"**
   - Connect GitHub repository (or upload manually)

2. **Build Configuration**
   ```yaml
   Build command: (leave empty - static files)
   Build output directory: redline/web/static
   Root directory: /
   ```

3. **Environment Variables**
   ```bash
   REDLINE_BACKEND_URL=https://redline-xxxx.onrender.com
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```

4. **Custom Domain**
   - Add custom domain: `app.redfindat.com` or `redfindat.com`
   - Cloudflare automatically provisions SSL

---

### Step 4: Set Up Cloudflare Workers (API Proxy)

**Purpose:** Route API requests to backend, handle CORS, add rate limiting.

1. **Create Worker**
   ```bash
   # Install Wrangler CLI
   npm install -g wrangler
   
   # Login to Cloudflare
   wrangler login
   ```

2. **Create Worker Script** (`worker.js`):
   ```javascript
   export default {
     async fetch(request, env) {
       const url = new URL(request.url);
       const backendUrl = env.BACKEND_URL || 'https://redline-xxxx.onrender.com';
       
       // Proxy API requests to backend
       if (url.pathname.startsWith('/api/') || 
           url.pathname.startsWith('/data/') ||
           url.pathname.startsWith('/payments/') ||
           url.pathname.startsWith('/download/') ||
           url.pathname.startsWith('/analysis/') ||
           url.pathname.startsWith('/converter/')) {
         
         // Forward request to backend
         const backendRequest = new Request(
           `${backendUrl}${url.pathname}${url.search}`,
           {
             method: request.method,
             headers: request.headers,
             body: request.body
           }
         );
         
         const response = await fetch(backendRequest);
         
         // Add CORS headers
         const newResponse = new Response(response.body, response);
         newResponse.headers.set('Access-Control-Allow-Origin', '*');
         newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
         newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-License-Key');
         
         return newResponse;
       }
       
       // For static assets, return 404 (handled by Pages)
       return new Response('Not Found', { status: 404 });
     }
   };
   ```

3. **Deploy Worker**
   ```bash
   # Create wrangler.toml
   cat > wrangler.toml << EOF
   name = "redline-api-proxy"
   main = "worker.js"
   compatibility_date = "2024-01-01"
   
   [vars]
   BACKEND_URL = "https://redline-xxxx.onrender.com"
   EOF
   
   # Deploy
   wrangler deploy
   ```

4. **Route Worker to Domain**
   - Cloudflare Dashboard → Workers & Pages → Routes
   - Add route: `app.redfindat.com/api/*` → `redline-api-proxy`
   - Add route: `app.redfindat.com/data/*` → `redline-api-proxy`
   - Add route: `app.redfindat.com/payments/*` → `redline-api-proxy`

---

### Step 5: Configure DNS

1. **Add DNS Records**
   - Go to Cloudflare Dashboard → DNS → Records
   
   | Type | Name | Target | Proxy | TTL |
   |------|------|--------|-------|-----|
   | CNAME | `app` | `redline-xxxx.onrender.com` | Proxied ✅ | Auto |
   | CNAME | `@` | `redline-xxxx.onrender.com` | Proxied ✅ | Auto |
   | CNAME | `www` | `redfindat.com` | Proxied ✅ | Auto |

2. **SSL/TLS Settings**
   - SSL/TLS → Overview
   - Set to **Full (strict)** for end-to-end encryption

---

### Step 6: Configure Stripe Webhook for Cloudflare

**Important:** Stripe webhooks need to reach your backend.

1. **Option A: Direct to Backend** (Recommended)
   - Stripe Dashboard → Webhooks
   - Endpoint: `https://redline-xxxx.onrender.com/payments/webhook`
   - Events: `checkout.session.completed`
   - Get webhook secret: `whsec_...`

2. **Option B: Through Cloudflare Worker**
   - Create webhook worker that forwards to backend
   - More complex but adds Cloudflare features

**Use Option A** - simpler and more reliable.

---

### Step 7: Subscription Model Configuration

1. **Update Frontend for Cloudflare**
   - Frontend should use backend URL from environment
   - Stripe publishable key from environment
   - License key management via API

2. **Backend Configuration**
   - Stripe keys in Render environment variables
   - License server URL configured
   - Payment webhook endpoint accessible

3. **Test Subscription Flow**
   ```
   1. User registers → Gets license key
   2. User purchases hours → Stripe checkout
   3. Stripe webhook → Backend adds hours
   4. User uses app → Hours deducted
   5. Balance tracked → Displayed in UI
   ```

---

## 💰 Cloudflare Pricing for Subscription Model

### Cloudflare Costs

| Service | Free Tier | Paid Plans | Notes |
|---------|-----------|------------|-------|
| **Pages** | ✅ Unlimited | $20/month (Pro) | Free tier sufficient |
| **Workers** | 100K requests/day | $5/month (Workers Paid) | Free tier may be enough |
| **R2 Storage** | 10GB free | $0.015/GB/month | Very affordable |
| **DNS** | ✅ Free | ✅ Free | Always free |
| **SSL/TLS** | ✅ Free | ✅ Free | Always free |
| **DDoS Protection** | ✅ Free | ✅ Free | Always free |

### Total Cloudflare Cost Estimate

**Free Tier (Small Scale):**
- Pages: $0
- Workers: $0 (if < 100K requests/day)
- R2: $0 (if < 10GB storage)
- **Total: $0/month**

**Paid Tier (Production):**
- Pages Pro: $20/month
- Workers Paid: $5/month
- R2: ~$1-5/month (depending on storage)
- **Total: ~$26-30/month**

**Plus Backend Hosting:**
- Render Starter: $7/month
- **Total Combined: ~$33-37/month**

---

## 🔧 Configuration Files

### `wrangler.toml` (Cloudflare Worker)
```toml
name = "redline-api-proxy"
main = "worker.js"
compatibility_date = "2024-01-01"

[env.production]
vars = { BACKEND_URL = "https://redline-xxxx.onrender.com" }

[env.production.routes]
pattern = "app.redfindat.com/api/*"
zone_name = "redfindat.com"
```

### `_redirects` (Cloudflare Pages)
```
/api/*  https://redline-api-proxy.redfindat.workers.dev/api/:splat  200
/data/*  https://redline-api-proxy.redfindat.workers.dev/data/:splat  200
/payments/*  https://redline-api-proxy.redfindat.workers.dev/payments/:splat  200
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Domain registered with Cloudflare
- [ ] Cloudflare account created
- [ ] R2 bucket created (see CLOUDFLARE_R2_SETUP.md)
- [ ] Backend deployed to Render/Railway
- [ ] Stripe account configured (production keys)
- [ ] License server deployed (if using)

### Deployment Steps
- [ ] Deploy backend to Render/Railway
- [ ] Configure backend environment variables
- [ ] Create Cloudflare Pages project
- [ ] Deploy frontend to Cloudflare Pages
- [ ] Create Cloudflare Worker for API proxy
- [ ] Configure DNS records
- [ ] Set up SSL/TLS (Full strict)
- [ ] Configure Stripe webhook
- [ ] Test subscription flow

### Post-Deployment
- [ ] Test health endpoint
- [ ] Test file upload/download
- [ ] Test payment checkout
- [ ] Verify webhook receives events
- [ ] Monitor Cloudflare Analytics
- [ ] Set up error tracking

---

## 🔍 Monitoring & Analytics

### Cloudflare Analytics

1. **Pages Analytics**
   - Page views
   - Build times
   - Deploy history

2. **Workers Analytics**
   - Request count
   - Error rate
   - CPU time
   - Response times

3. **R2 Analytics**
   - Storage usage
   - Operation counts
   - Egress (free!)

### Application Monitoring

1. **Backend Logs** (Render)
   - Application logs
   - Error tracking
   - Performance metrics

2. **Stripe Dashboard**
   - Payment events
   - Webhook deliveries
   - Customer subscriptions

---

## 🛠️ Troubleshooting

### Common Issues

1. **API Requests Failing**
   - Check Worker routes are configured
   - Verify backend URL is correct
   - Check CORS headers in Worker

2. **Webhook Not Receiving Events**
   - Verify webhook URL is accessible
   - Check webhook secret matches
   - Review Stripe webhook logs

3. **Static Assets Not Loading**
   - Check Pages build output directory
   - Verify file paths in HTML
   - Check Cloudflare cache settings

4. **SSL Certificate Issues**
   - Ensure DNS is proxied (orange cloud)
   - Wait 5-15 minutes for certificate
   - Check SSL/TLS mode (Full strict)

---

## 📊 Performance Optimization

### Cloudflare Features

1. **Caching**
   - Static assets cached at edge
   - API responses can be cached (with care)
   - Cache rules in Workers

2. **Compression**
   - Automatic Brotli/Gzip
   - Reduces bandwidth costs

3. **Image Optimization**
   - Cloudflare Images (paid)
   - Automatic image optimization

4. **Minification**
   - Already implemented in Docker build
   - Cloudflare can further optimize

---

## 🔐 Security Considerations

1. **API Keys**
   - Store in Cloudflare Workers secrets
   - Never expose in frontend code
   - Use environment variables

2. **CORS**
   - Configure in Worker
   - Restrict to your domain
   - Handle preflight requests

3. **Rate Limiting**
   - Cloudflare rate limiting (paid)
   - Or implement in Worker
   - Or use backend rate limiting

4. **DDoS Protection**
   - Automatic with Cloudflare
   - Free tier includes basic protection

---

## 📝 Next Steps

1. **Choose Deployment Option**
   - Recommended: Pages + Backend Proxy
   - Alternative: Full Workers (if app is simplified)

2. **Set Up Infrastructure**
   - Deploy backend first
   - Then set up Cloudflare services
   - Configure DNS last

3. **Test Subscription Flow**
   - Register user
   - Purchase hours
   - Verify webhook
   - Test usage tracking

4. **Monitor and Optimize**
   - Track costs
   - Monitor performance
   - Optimize caching
   - Scale as needed

---

## 🎯 Subscription Model on Cloudflare

### How It Works

1. **User Registration**
   - User registers via frontend
   - Backend creates license key
   - License stored in database

2. **Payment Processing**
   - User clicks "Purchase Hours"
   - Frontend calls Stripe checkout
   - Stripe redirects to payment
   - Webhook notifies backend

3. **Hour Management**
   - Hours added to license
   - Usage tracked per session
   - Balance displayed in UI

4. **Access Control**
   - License key required for API
   - Hours checked before operations
   - Access denied if no hours

### Configuration

**Backend (Render):**
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
HOURS_PER_DOLLAR=0.2  # $5/hour
PAYMENT_CURRENCY=usd
```

**Frontend (Cloudflare Pages):**
```bash
REDLINE_BACKEND_URL=https://redline-xxxx.onrender.com
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
