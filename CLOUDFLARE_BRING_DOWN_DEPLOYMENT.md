# How to Bring Down Cloudflare Deployments
**Guide:** Stop or remove Cloudflare Pages and Workers

---

## 🌐 Cloudflare Pages

### Method 1: Suspend/Pause Builds (Recommended)

**Keeps the site but stops new deployments:**

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **"Workers & Pages"** → **"Pages"**
3. Click on your project (e.g., `redfindat-splash`)
4. Go to **"Settings"** tab
5. Scroll to **"Builds & deployments"**
6. Toggle **"Pause builds"** to **ON**
7. Click **"Save"**

**Result:**
- ✅ Existing site stays live
- ✅ No new builds triggered
- ✅ Can resume anytime

---

### Method 2: Delete Project (Permanent)

**Completely removes the project:**

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **"Workers & Pages"** → **"Pages"**
3. Click on your project
4. Go to **"Settings"** tab
5. Scroll to bottom → **"General"** section
6. Click **"Delete project"**
7. Type project name to confirm
8. Click **"Delete"**

**Result:**
- ⚠️ Project completely removed
- ⚠️ All deployments deleted
- ⚠️ Cannot be undone
- ⚠️ DNS records may need manual cleanup

---

## 🔧 Cloudflare Workers

### Method 1: Delete Worker

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **"Workers & Pages"** → **"Workers"**
3. Click on your worker (e.g., `redline-api-proxy`)
4. Go to **"Settings"** tab
5. Scroll to bottom → **"Delete Worker"**
6. Type worker name to confirm
7. Click **"Delete"**

**Result:**
- ⚠️ Worker completely removed
- ⚠️ Routes automatically removed
- ⚠️ Cannot be undone

---

### Method 2: Via Wrangler CLI

```bash
# Delete worker
wrangler delete redline-api-proxy

# Delete with specific environment
wrangler delete redline-api-proxy --env production

# Confirm deletion when prompted
```

---

## 🗺️ DNS Records

### Remove DNS Records

**Important:** Even after deleting Pages/Workers, DNS records may still exist.

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select your domain (e.g., `redfindat.com`)
3. Go to **"DNS"** → **"Records"**
4. Find records pointing to:
   - Pages: `@` or `www` CNAME to Pages URL
   - Workers: `app` or `api` CNAME to Workers URL
5. Click **"Delete"** on each record
6. Confirm deletion

**Common records to remove:**
- `@` → Pages URL (root domain)
- `www` → Pages URL
- `app` → Worker URL
- `api` → Worker URL

---

## 📋 Step-by-Step: Complete Removal

### For Cloudflare Pages (Splash Page)

1. **Pause Builds** (optional, if you want to keep site)
   - Dashboard → Pages → Project → Settings → Pause builds

2. **Delete Project** (if removing completely)
   - Dashboard → Pages → Project → Settings → Delete project

3. **Remove DNS Records**
   - Dashboard → DNS → Delete CNAME records for root domain

4. **Verify**
   - Check domain no longer resolves
   - Verify project removed from Pages list

---

### For Cloudflare Workers (API Proxy)

1. **Delete Worker**
   - Dashboard → Workers → Worker → Settings → Delete Worker

2. **Remove DNS Records**
   - Dashboard → DNS → Delete CNAME records for subdomains (app, api, etc.)

3. **Remove Routes** (if any)
   - Routes are automatically removed when worker is deleted

4. **Verify**
   - Check worker no longer appears in list
   - Verify subdomains no longer resolve

---

## ⚠️ Important Considerations

### Before Deleting

1. **Backup Configuration**
   - Save `wrangler.toml` file
   - Document environment variables
   - Note custom domains

2. **Check Dependencies**
   - Other services pointing to this?
   - Webhooks configured?
   - API clients using this?

3. **DNS Impact**
   - DNS records may need manual cleanup
   - Subdomains will stop working
   - Root domain may need new records

4. **Data Loss**
   - Pages: Static files are lost (but can redeploy)
   - Workers: Code is lost (but can redeploy from Git)

---

## 🔄 Restart After Bringing Down

### Cloudflare Pages

**Resume builds:**
1. Dashboard → Pages → Project → Settings
2. Toggle **"Pause builds"** to **OFF**
3. Click **"Save"**

**Redeploy:**
1. Push to GitHub (if auto-deploy enabled)
2. Or manually trigger deploy from dashboard

### Cloudflare Workers

**Redeploy:**
```bash
wrangler deploy
```

Or redeploy from dashboard:
1. Dashboard → Workers → Create Worker
2. Upload code or connect to Git

---

## 🎯 Quick Reference

### Cloudflare Pages
- **Pause:** Dashboard → Pages → Project → Settings → Pause builds
- **Delete:** Dashboard → Pages → Project → Settings → Delete project
- **Resume:** Dashboard → Pages → Project → Settings → Unpause builds

### Cloudflare Workers
- **Delete:** Dashboard → Workers → Worker → Settings → Delete Worker
- **CLI:** `wrangler delete <worker-name>`
- **Redeploy:** `wrangler deploy`

### DNS Cleanup
- **Remove Records:** Dashboard → DNS → Records → Delete
- **Common:** Remove CNAME records for `@`, `www`, `app`, `api`

---

## 📊 Checklist

Before bringing down:
- [ ] Backup `wrangler.toml` (if using Workers)
- [ ] Save environment variables
- [ ] Document custom domains
- [ ] Check dependent services
- [ ] Note DNS record configurations

After bringing down:
- [ ] Verify project/worker removed
- [ ] Clean up DNS records
- [ ] Verify domains no longer resolve
- [ ] Update documentation
- [ ] Notify users (if production)

---

## 🔍 Troubleshooting

### "Cannot delete project"
- Check if custom domain is still attached
- Remove custom domain first
- Then delete project

### "DNS records still active"
- DNS records are separate from Pages/Workers
- Must be manually deleted
- Go to DNS → Records → Delete

### "Want to keep site but stop builds"
- Use **"Pause builds"** instead of delete
- Site stays live
- No new deployments

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
