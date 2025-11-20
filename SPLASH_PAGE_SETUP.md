# Setting Up a Splash Page for redfindat.com
**Guide:** Create a landing page for root domain, keep app on subdomain

---

## 🎯 Overview

Set up a splash/landing page for `redfindat.com` while keeping the main application at `app.redfindat.com`.

**Architecture:**
```
redfindat.com        → Splash/Landing Page (Cloudflare Pages)
app.redfindat.com   → REDLINE Application (Render)
```

---

## 🚀 Option 1: Cloudflare Pages (Recommended - Easiest)

**Best for:** Simple static splash page, free hosting

### Step 1: Create Splash Page HTML

The splash page HTML is already created at `splash/index.html`. It includes:
- Modern gradient design
- Video support (MPEG4/MP4)
- Responsive layout
- "Launch Application" button

**To add your video:**
1. Place your MPEG4 video file in the `splash/` directory
2. Name it `video.mp4` or `video.mpeg4`
3. The video will automatically display on the splash page

**Video file location:**
```
splash/
├── index.html
└── video.mp4  (or video.mpeg4)
```

Create a simple HTML file for your splash page:

**File: `splash/index.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REDFINDAT YOU SAY</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            text-align: center;
            max-width: 800px;
            padding: 2rem;
        }
        
        h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .tagline {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .description {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            line-height: 1.6;
            opacity: 0.8;
        }
        
        .cta-button {
            display: inline-block;
            padding: 1rem 2.5rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 4rem;
        }
        
        .feature {
            padding: 1.5rem;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .feature h3 {
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }
        
        .feature p {
            opacity: 0.8;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>REDFINDAT</h1><
        <p class="tagline">REDFINDAT</p>
        <p class="description">
            Transform, analyze, and manage financial data with ease. 
            Multi-format support, advanced processing, and powerful analytics.
        </p>
        <a href="https://app.redfindat.com" class="cta-button">Launch Application</a>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 Fast</h3>
                <p>Lightning-fast data processing and conversion</p>
            </div>
            <div class="feature">
                <h3>📊 Multi-Format</h3>
                <p>Support for CSV, JSON, Parquet, Feather, and more</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure</h3>
                <p>Enterprise-grade security and data privacy</p>
            </div>
        </div>
    </div>
</body>
</html>
```

---

### Step 2: Deploy to Cloudflare Pages

1. **Create GitHub Repository** (or use existing)
   - Create a new repo: `redfindat-splash`
   - Or add `splash/` folder to existing repo

2. **Add Video File**
   - Place your MPEG4 video in the `splash/` directory
   - Name it `video.mp4` or `video.mpeg4`
   - Recommended: Compress video for web (keep file size reasonable)

3. **Push Files to GitHub**
   ```bash
   # If splash directory doesn't exist
   mkdir splash
   
   # Add HTML and video
   git add splash/
   git commit -m "Add splash page with video"
   git push
   ```
   
   **Files to include:**
   - `splash/index.html` (already created)
   - `splash/video.mp4` (your video file)

3. **Deploy to Cloudflare Pages**
   - Go to: https://dash.cloudflare.com
   - Click **"Workers & Pages"** → **"Pages"**
   - Click **"Create a project"**
   - Connect GitHub repository
   - Select repository: `redfindat-splash` (or your repo)
   - **Build settings:**
     - Framework preset: None
     - Build command: (leave empty)
     - Build output directory: `splash` (or root if index.html is in root)
   - Click **"Save and Deploy"**
   
   **Note:** Cloudflare Pages will serve your video file automatically. Make sure `video.mp4` is in the `splash/` directory.

4. **Get Pages URL**
   - After deployment, you'll get a URL like: `redfindat-splash.pages.dev`
   - Note this URL

---

### Step 3: Configure DNS for Splash Page

1. **Go to Cloudflare DNS**
   - Cloudflare Dashboard → `redfindat.com` → DNS → Records

2. **Add CNAME for Root Domain**
   - Click **"Add record"**
   - **Type**: CNAME
   - **Name**: `@` (root domain)
   - **Target**: `redfindat-splash.pages.dev` (your Pages URL)
   - **Proxy**: ✅ Proxied (orange cloud)
   - **TTL**: Auto
   - Click **"Save"**

3. **Keep App Subdomain**
   - Ensure `app` CNAME still points to Render:
   - **Type**: CNAME
   - **Name**: `app`
   - **Target**: `redline-xxxx.onrender.com`
   - **Proxy**: ✅ Proxied

**Result:**
- `redfindat.com` → Splash page (Cloudflare Pages)
- `app.redfindat.com` → REDLINE app (Render)

---

### Step 4: Add Custom Domain to Pages

1. **In Cloudflare Pages**
   - Go to your Pages project
   - Click **"Custom domains"**
   - Click **"Set up a custom domain"**
   - Enter: `redfindat.com`
   - Cloudflare automatically configures DNS

2. **Verify SSL**
   - SSL certificate automatically provisioned
   - Wait 5-15 minutes

---

## 🎨 Option 2: Simple HTML File on Render (Alternative)

If you prefer to host splash page on Render:

### Step 1: Create Static HTML Service

1. **Create New Render Service**
   - Render Dashboard → New → Static Site
   - Connect GitHub repo with `splash/index.html`
   - **Build command**: (leave empty)
   - **Publish directory**: `splash`

2. **Get Render URL**
   - URL: `redfindat-splash.onrender.com`

3. **Update DNS**
   - CNAME `@` → `redfindat-splash.onrender.com`

---

## 🎯 Option 3: Cloudflare Workers (Advanced)

For dynamic splash page with serverless functions:

1. **Create Worker**
   ```javascript
   export default {
     async fetch(request) {
       const html = `
       <!DOCTYPE html>
       <html>
       <head>
         <title>REDLINE</title>
         <style>/* Your CSS */</style>
       </head>
       <body>
         <h1>REDLINE</h1>
         <a href="https://app.redfindat.com">Launch App</a>
       </body>
       </html>
       `;
       
       return new Response(html, {
         headers: { 'Content-Type': 'text/html' }
       });
     }
   };
   ```

2. **Deploy Worker**
   ```bash
   wrangler deploy
   ```

3. **Route to Domain**
   - Cloudflare Dashboard → Workers & Pages → Routes
   - Add route: `redfindat.com/*` → Your worker

---

## 📋 Complete DNS Setup with Splash Page

### DNS Records

```
Type    Name    Target                          Proxy   Purpose
CNAME   @       redfindat-splash.pages.dev      ✅      Splash page (root)
CNAME   app     redline-xxxx.onrender.com       ✅      Main application
CNAME   www     redfindat.com                   ✅      WWW redirect
```

### Result URLs

- `https://redfindat.com` → Splash/Landing page
- `https://www.redfindat.com` → Redirects to root
- `https://app.redfindat.com` → REDLINE application

---

## 🎨 Splash Page Design Ideas

### Minimal Design
- Clean, simple layout
- Logo + tagline
- Single CTA button
- Link to app

### Feature Showcase
- Key features listed
- Screenshots/demos
- Pricing information
- Testimonials

### Marketing Page
- Hero section
- Benefits
- Use cases
- Call-to-action

---

## ✅ Setup Checklist

### Pre-Setup
- [ ] Decide on splash page design
- [ ] Create HTML file
- [ ] Choose hosting (Pages recommended)

### Cloudflare Pages Setup
- [ ] Create GitHub repo (or use existing)
- [ ] Push HTML file
- [ ] Deploy to Cloudflare Pages
- [ ] Get Pages URL

### DNS Configuration
- [ ] Add CNAME for root domain (`@`) → Pages URL
- [ ] Verify `app` CNAME still points to Render
- [ ] Add custom domain to Pages project
- [ ] Wait for SSL certificate

### Testing
- [ ] Visit `https://redfindat.com` - shows splash page
- [ ] Visit `https://app.redfindat.com` - shows REDLINE app
- [ ] Test "Launch Application" button
- [ ] Verify SSL certificates

---

## 🔗 Quick Links

- **Cloudflare Pages**: https://dash.cloudflare.com → Workers & Pages → Pages
- **DNS Records**: https://dash.cloudflare.com → Select domain → DNS → Records
- **Render Dashboard**: https://dashboard.render.com

---

## 📝 Summary

**Recommended Approach:** Cloudflare Pages

1. ✅ Create simple HTML splash page
2. ✅ Deploy to Cloudflare Pages (free)
3. ✅ Point root domain (`@`) to Pages URL
4. ✅ Keep `app` subdomain pointing to Render

**Result:**
- `redfindat.com` → Beautiful splash page
- `app.redfindat.com` → REDLINE application

**Time Required:** 15-30 minutes

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
