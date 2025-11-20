# Fix "Launch Application" Button Not Reaching App
**Troubleshooting guide for splash page button**

---

## 🔍 Problem

The "Launch Application" button on the splash page points to a URL that's not reachable.

**Current URL in splash/index.html:**
```html
<a href="https://app.redfindat.com" class="cta-button">Launch Application</a>
```

---

## 🛠️ Solutions

### Solution 1: Update to Correct Render URL

If your app is deployed on Render, update the button to point to your Render service URL:

```html
<a href="https://your-service.onrender.com" class="cta-button">Launch Application</a>
```

**Steps:**
1. Find your Render service URL
2. Update splash/index.html
3. Commit and push
4. Cloudflare Pages will redeploy

### Solution 2: Use Cloudflare DNS Subdomain

If you've set up DNS for `app.redfindat.com`:

1. **Check DNS Record:**
   - Cloudflare Dashboard → DNS → Records
   - Verify `app` CNAME points to Render service

2. **Check SSL/TLS:**
   - Cloudflare Dashboard → SSL/TLS
   - Set to "Full (strict)" if using Render

3. **Verify Render Service:**
   - Ensure Render service is running
   - Check service URL is correct

### Solution 3: Use Direct Render URL (Temporary)

Until DNS is configured, use the Render URL directly:

```html
<a href="https://redline-xxxx.onrender.com" class="cta-button">Launch Application</a>
```

Replace `redline-xxxx` with your actual Render service name.

---

## 📋 Quick Fix Steps

### Step 1: Find Your App URL

**Render:**
- Dashboard → Your Service → URL
- Format: `https://service-name.onrender.com`

**Other platforms:**
- Check your deployment platform dashboard
- Find the public URL

### Step 2: Update splash/index.html

```html
<!-- Replace this line: -->
<a href="https://app.redfindat.com" class="cta-button">Launch Application</a>

<!-- With your actual URL: -->
<a href="https://your-actual-url.com" class="cta-button">Launch Application</a>
```

### Step 3: Commit and Deploy

```bash
git add splash/index.html
git commit -m "Fix Launch Application button URL"
git push
```

---

## 🔍 Troubleshooting

### Button Doesn't Work

**Check:**
1. Is the URL correct?
2. Is the app service running?
3. Is DNS configured (if using custom domain)?
4. Is SSL/TLS configured?

### DNS Not Working

**For app.redfindat.com:**
1. Cloudflare Dashboard → DNS
2. Add CNAME record:
   - Name: `app`
   - Target: `your-service.onrender.com`
   - Proxy: Enabled (orange cloud)
3. Wait for DNS propagation (few minutes)

### Render Service Down

**Check:**
1. Render Dashboard → Your Service
2. Verify service is "Live"
3. Check service logs for errors
4. Restart service if needed

---

## 🎯 Common URLs

**Render:**
- Format: `https://service-name.onrender.com`
- Example: `https://redline-web.onrender.com`

**Railway:**
- Format: `https://service-name.up.railway.app`
- Example: `https://redline.up.railway.app`

**Custom Domain:**
- Format: `https://app.yourdomain.com`
- Example: `https://app.redfindat.com`

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
