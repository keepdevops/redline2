# Fixing Cloudflare Pages Splash Page Crash
**Troubleshooting guide for deployment issues**

---

## 🔍 Common Causes

### 1. Build Configuration Issues

**Problem:** Cloudflare Pages doesn't know how to build/deploy

**Solution:**
- Set build command to empty (or `echo "No build needed"`)
- Set output directory to `splash` (or root if index.html is in root)
- Framework preset: None

### 2. Missing Video File

**Problem:** Video file not in repository or too large

**Solution:**
- Ensure `redfindat-movie.mp4` is committed to Git
- Check file size (Cloudflare Pages has limits)
- Verify file is in `splash/` directory

### 3. HTML Errors

**Problem:** Syntax errors in HTML

**Solution:**
- Validate HTML
- Check for unclosed tags
- Verify all paths are relative

### 4. Path Issues

**Problem:** Incorrect file paths

**Solution:**
- Use relative paths: `redfindat-movie.mp4` not `/redfindat-movie.mp4`
- Ensure files are in same directory

---

## 🛠️ Step-by-Step Fix

### Step 1: Check Cloudflare Pages Logs

1. Go to Cloudflare Dashboard
2. Workers & Pages → Pages
3. Click your project
4. Go to "Deployments" tab
5. Click on failed deployment
6. Check "Build logs" for errors

**Common errors:**
- "File not found"
- "Build failed"
- "Path error"

### Step 2: Verify File Structure

**Required structure:**
```
splash/
├── index.html
└── redfindat-movie.mp4
```

**Check in GitHub:**
```bash
git ls-files splash/
```

### Step 3: Fix Build Configuration

**In Cloudflare Pages Settings:**

1. **Build settings:**
   - Framework preset: **None**
   - Build command: **(leave empty)**
   - Build output directory: **splash** (or `/` if root)

2. **Root directory:**
   - If files are in `splash/` subdirectory, set root to `splash`
   - Or set output directory to `splash`

### Step 4: Check HTML for Errors

**Common issues:**
- Unclosed tags
- Invalid characters
- Missing quotes

**Validate:**
```bash
# Check HTML syntax
python3 -m html.parser splash/index.html
```

---

## 🔧 Quick Fixes

### Fix 1: Update Build Configuration

**In Cloudflare Pages Dashboard:**

1. Settings → Builds & deployments
2. Set:
   - **Framework preset:** None
   - **Build command:** (empty)
   - **Build output directory:** `splash`
   - **Root directory:** `/` (or `splash` if needed)

### Fix 2: Ensure Files Are Committed

```bash
# Check what's committed
git ls-files splash/

# If video is missing, add it
git add splash/redfindat-movie.mp4
git commit -m "Add video file"
git push
```

### Fix 3: Simplify HTML (Temporary)

If video is causing issues, temporarily remove it:

```html
<!-- Comment out video temporarily -->
<!--
<video ...>
  <source src="redfindat-movie.mp4" type="video/mp4">
</video>
-->
```

### Fix 4: Check File Size

**Cloudflare Pages limits:**
- Individual files: 25 MB
- Total deployment: 500 MB

**If video is too large:**
```bash
# Check size
ls -lh splash/redfindat-movie.mp4

# Compress if needed
ffmpeg -i splash/redfindat-movie.mp4 -vcodec h264 -crf 28 splash/redfindat-movie-compressed.mp4
```

---

## 📋 Debugging Checklist

- [ ] Check Cloudflare Pages build logs
- [ ] Verify files are in GitHub repository
- [ ] Check build configuration (framework, command, output)
- [ ] Validate HTML syntax
- [ ] Verify video file size (< 25 MB)
- [ ] Check file paths are relative
- [ ] Ensure video file is committed
- [ ] Test HTML locally first

---

## 🎯 Specific Error Messages

### "Build failed"
- Check build command (should be empty)
- Verify framework preset is "None"
- Check output directory

### "File not found"
- Verify files are in Git repository
- Check file paths in HTML
- Ensure files are in correct directory

### "Deployment error"
- Check Cloudflare Pages logs
- Verify repository connection
- Check branch name

### "Video not loading"
- Verify video file is committed
- Check file size
- Verify path in HTML is correct
- Check browser console for 404 errors

---

## 🔄 Redeploy Steps

1. **Fix the issue** (based on logs)
2. **Commit changes:**
   ```bash
   git add splash/
   git commit -m "Fix Cloudflare Pages deployment"
   git push
   ```
3. **Trigger redeploy:**
   - Cloudflare Pages auto-deploys on push
   - Or manually trigger from dashboard

---

## 🆘 Still Crashing?

### Option 1: Deploy Without Video First

1. Temporarily remove video from HTML
2. Deploy and verify page works
3. Add video back once page is working

### Option 2: Use Different Hosting

- **Netlify:** Similar to Cloudflare Pages
- **Vercel:** Good for static sites
- **GitHub Pages:** Simple static hosting

### Option 3: Check Cloudflare Status

- Visit: https://www.cloudflarestatus.com
- Check for service issues

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
