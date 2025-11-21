# REDFINDAT Splash Page

Landing page for redfindat.com deployed on **Cloudflare Pages** (recommended).

**Architecture:**
- `redfindat.com` → Cloudflare Pages (splash page) ✅
- `app.redfindat.com` → Render (Redline app) ✅

## Files

- `index.html` - Main splash page HTML
- `redfindat-movie.mp4` - Video file (if available)
- `render.yaml` - Render deployment configuration

## Deployment to Cloudflare Pages (Recommended)

Since `redfindat.com` is on Cloudflare, Cloudflare Pages is the best choice:
- ✅ FREE hosting
- ✅ Fast global CDN
- ✅ Automatic SSL
- ✅ Easy custom domain setup
- ✅ Perfect for static sites

### Step 1: Deploy to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **"Workers & Pages"** → **"Pages"**
3. Click **"Create a project"**
4. Connect your GitHub repository
5. Configure:
   - **Project name**: `redfindat-splash`
   - **Production branch**: `main` (or your default branch)
   - **Framework preset**: `None`
   - **Build command**: (leave empty)
   - **Build output directory**: `splash`
6. Click **"Save and Deploy"**
7. Wait for deployment (usually 1-2 minutes)

### Step 2: Add Custom Domain

1. In your Pages project, click **"Custom domains"**
2. Click **"Set up a custom domain"**
3. Enter: `redfindat.com`
4. Cloudflare automatically configures DNS

### Step 3: Verify DNS

Check that DNS records are correct:
- **CNAME `@`** → `redfindat-splash.pages.dev` (splash page)
- **CNAME `app`** → `your-render-service.onrender.com` (app)

---

## Alternative: Deployment to Render

If you prefer Render (not recommended since domain is on Cloudflare):

### Option 1: Using Render Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `redfindat-splash`
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: (leave empty)
   - **Build Command**: (leave empty)
   - **Publish Directory**: `splash`
5. Click **"Create Static Site"**
6. Wait for deployment (usually 1-2 minutes)

### Option 2: Using Render CLI

```bash
# Install Render CLI (if not already installed)
npm install -g render-cli

# Deploy
render deploy
```

### Option 3: Using render.yaml

Render will automatically detect `render.yaml` in the repository root and use it for deployment.

## Custom Domain Setup

After deployment:

1. In Render dashboard, go to your static site
2. Click **"Settings"** → **"Custom Domains"**
3. Add: `redfindat.com`
4. Update DNS in Cloudflare:
   - Type: `CNAME`
   - Name: `@`
   - Target: `redfindat-splash.onrender.com`
   - Proxy: Enabled (orange cloud)

## Features

- ✅ Responsive design (mobile-friendly)
- ✅ Modern gradient background
- ✅ Video support (MPEG4/MP4)
- ✅ Launch Application button
- ✅ Feature showcase
- ✅ Fast loading (static HTML)

## Testing Locally

```bash
# Using Python
cd splash
python3 -m http.server 8000

# Using Node.js
npx serve splash

# Using PHP
php -S localhost:8000 -t splash
```

Then visit: http://localhost:8000

## URL Structure

- **Splash Page**: https://redfindat.com
- **Application**: https://app.redfindat.com

## Notes

- Video file (`redfindat-movie.mp4`) is optional
- If video is not present, the video section will show "Your browser does not support the video tag"
- All assets should be in the `splash/` directory
- Render automatically serves static files from the publish directory

