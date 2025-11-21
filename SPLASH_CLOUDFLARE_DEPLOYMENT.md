# Deploy Splash Page to Cloudflare Pages

**Quick Guide:** Deploy the splash page to Cloudflare Pages since `redfindat.com` is on Cloudflare.

---

## 🎯 Why Cloudflare Pages?

Since your domain `redfindat.com` is already on Cloudflare, Cloudflare Pages is the **best choice**:

- ✅ **FREE** hosting (no cost)
- ✅ **Fast** global CDN
- ✅ **Automatic SSL** certificates
- ✅ **Easy** custom domain setup (already on Cloudflare)
- ✅ **Perfect** for static sites like splash pages
- ✅ **Automatic** deployments from GitHub

---

## 📋 Current Architecture

```
redfindat.com        → Cloudflare Pages (splash page) ✅
app.redfindat.com   → Render (Redline app) ✅
```

---

## 🚀 Deployment Steps

### Step 1: Prepare Files

Ensure your splash page files are in the repository:

```bash
splash/
├── index.html          # Main splash page
└── redfindat-movie.mp4 # Video (optional)
```

### Step 2: Deploy to Cloudflare Pages

1. **Go to Cloudflare Dashboard**
   - https://dash.cloudflare.com
   - Login to your account

2. **Navigate to Pages**
   - Click **"Workers & Pages"** in sidebar
   - Click **"Pages"** tab
   - Click **"Create a project"**

3. **Connect GitHub Repository**
   - Click **"Connect to Git"**
   - Select your repository (the one with `splash/` folder)
   - Authorize Cloudflare to access your repo

4. **Configure Build Settings**
   - **Project name**: `redfindat-splash`
   - **Production branch**: `main` (or your default branch)
   - **Framework preset**: `None` (or `Plain HTML`)
   - **Build command**: (leave empty)
   - **Build output directory**: `splash`

5. **Deploy**
   - Click **"Save and Deploy"**
   - Wait 1-2 minutes for deployment

6. **Get Pages URL**
   - After deployment, you'll get: `https://redfindat-splash.pages.dev`
   - Note this URL

### Step 3: Add Custom Domain

1. **In Cloudflare Pages**
   - Go to your project: `redfindat-splash`
   - Click **"Custom domains"** tab
   - Click **"Set up a custom domain"**

2. **Add Domain**
   - Enter: `redfindat.com`
   - Click **"Continue"**

3. **Cloudflare Auto-Configures**
   - Cloudflare automatically creates DNS record
   - SSL certificate is automatically provisioned
   - Wait 5-15 minutes for SSL

### Step 4: Verify DNS

Check that DNS records are correct:

1. **Go to Cloudflare DNS**
   - Cloudflare Dashboard → `redfindat.com` → **DNS** → **Records**

2. **Verify Records**
   ```
   Type    Name    Target                          Proxy   Purpose
   CNAME   @       redfindat-splash.pages.dev      ✅      Splash page
   CNAME   app     redline-xxxx.onrender.com       ✅      Redline app
   CNAME   www     redfindat.com                   ✅      WWW redirect
   ```

3. **If DNS is wrong, update:**
   - Click on the `@` CNAME record
   - Set **Target** to: `redfindat-splash.pages.dev`
   - Ensure **Proxy** is enabled (orange cloud)
   - Click **"Save"**

---

## ✅ Result

After deployment:

- ✅ `https://redfindat.com` → Splash page (Cloudflare Pages)
- ✅ `https://app.redfindat.com` → Redline app (Render)
- ✅ SSL certificates automatically configured
- ✅ Fast global CDN delivery

---

## 🔧 Troubleshooting

### Issue: Build Fails

**Solution:**
- Check build output directory is set to `splash`
- Ensure `splash/index.html` exists
- Check Cloudflare Pages build logs

### Issue: Video Not Showing

**Solution:**
- Ensure `redfindat-movie.mp4` is in `splash/` directory
- Check file is committed to Git
- Verify file size (Cloudflare Pages has limits)

### Issue: Custom Domain Not Working

**Solution:**
- Wait 5-15 minutes for DNS propagation
- Check DNS records in Cloudflare Dashboard
- Verify SSL certificate is active

### Issue: Wrong Content Showing

**Solution:**
- Check build output directory is `splash`
- Verify `splash/index.html` is correct
- Clear browser cache

---

## 📝 Quick Reference

**Cloudflare Pages Dashboard:**
- https://dash.cloudflare.com → Workers & Pages → Pages

**DNS Records:**
- https://dash.cloudflare.com → Select domain → DNS → Records

**Pages Project URL:**
- `https://redfindat-splash.pages.dev` (before custom domain)

**Custom Domain:**
- `https://redfindat.com` (after setup)

---

## 🎉 Success!

Your splash page is now live on Cloudflare Pages!

**Benefits:**
- ✅ Free hosting
- ✅ Fast CDN
- ✅ Automatic SSL
- ✅ Easy updates (just push to GitHub)

---

**Next Steps:**
- Test the splash page: https://redfindat.com
- Verify "Launch Application" button works
- Check video displays correctly (if added)

