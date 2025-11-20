# Adding MPEG4 Video to Splash Page
**Quick guide:** Add your video to the splash page

---

## 🎬 Quick Steps

### Step 1: Add Video File

1. **Place video in splash directory**
   ```bash
   # Copy your video file
   cp /path/to/your/video.mp4 splash/video.mp4
   # or
   cp /path/to/your/video.mpeg4 splash/video.mpeg4
   ```

2. **File location:**
   ```
   splash/
   ├── index.html
   └── video.mp4  (your video file)
   ```

### Step 2: Video File Requirements

**Recommended settings:**
- **Format**: MP4 (MPEG4)
- **Codec**: H.264
- **Max file size**: 10-20 MB (for fast loading)
- **Resolution**: 1280x720 (720p) or 1920x1080 (1080p)
- **Duration**: 30-60 seconds (recommended)

**Compress video for web:**
```bash
# Using ffmpeg (if installed)
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -crf 23 -preset medium output.mp4
```

### Step 3: Deploy to Cloudflare Pages

1. **Push to GitHub**
   ```bash
   git add splash/video.mp4
   git commit -m "Add splash page video"
   git push
   ```

2. **Cloudflare Pages will auto-deploy**
   - Pages automatically serves video files
   - Video will be available at: `https://redfindat.com/video.mp4`

### Step 4: Verify Video Works

1. **Visit splash page**: `https://redfindat.com`
2. **Video should:**
   - Auto-play (muted)
   - Loop continuously
   - Be responsive
   - Have controls

---

## 🎨 Video Customization

### Current Video Settings

The video in `splash/index.html` is configured with:
- ✅ **Autoplay**: Starts automatically
- ✅ **Muted**: Required for autoplay in browsers
- ✅ **Loop**: Repeats continuously
- ✅ **Controls**: User can play/pause
- ✅ **Responsive**: Scales to container width

### Customize Video Behavior

Edit `splash/index.html` to change video settings:

**Remove autoplay:**
```html
<video id="splashVideo" controls loop playsinline>
```

**Remove controls:**
```html
<video id="splashVideo" autoplay muted loop playsinline>
```

**Change video source:**
```html
<source src="your-video.mp4" type="video/mp4">
```

---

## 📊 Video Optimization Tips

### File Size Optimization

1. **Compress video**
   - Use HandBrake, ffmpeg, or online tools
   - Target: 5-15 MB for web

2. **Reduce resolution**
   - 720p (1280x720) is usually sufficient
   - 1080p if you need higher quality

3. **Shorten duration**
   - 15-30 seconds is ideal
   - Longer videos = larger files

### Format Recommendations

**Best for web:**
- MP4 (H.264 codec) ✅
- WebM (alternative)
- Avoid: MOV, AVI (not web-optimized)

---

## 🔧 Troubleshooting

### Video Not Playing

**Issue:** Video doesn't load or play

**Solutions:**
1. Check file path: `splash/video.mp4`
2. Verify file is in GitHub repo
3. Check Cloudflare Pages build logs
4. Verify video format (MP4/H.264)

### Video Too Large

**Issue:** Slow loading, large file size

**Solutions:**
1. Compress video (see optimization tips)
2. Reduce resolution
3. Shorten duration
4. Use video compression tools

### Autoplay Not Working

**Issue:** Video doesn't autoplay

**Solutions:**
1. Ensure `muted` attribute is present (required by browsers)
2. Check browser autoplay policies
3. Some browsers block autoplay with sound

---

## ✅ Checklist

- [ ] Video file added to `splash/` directory
- [ ] Video named `video.mp4` or `video.mpeg4`
- [ ] Video compressed for web (5-15 MB recommended)
- [ ] Video format: MP4 (H.264)
- [ ] Files pushed to GitHub
- [ ] Cloudflare Pages deployed
- [ ] Video displays on splash page
- [ ] Video autoplays (muted)
- [ ] Video loops correctly

---

## 📝 File Structure

```
splash/
├── index.html      (splash page HTML)
└── video.mp4       (your MPEG4 video)
```

**After deployment:**
- `https://redfindat.com` → Shows splash page with video
- `https://redfindat.com/video.mp4` → Direct video URL

---

## 🎯 Quick Reference

**Add video:**
```bash
cp your-video.mp4 splash/video.mp4
git add splash/
git commit -m "Add video"
git push
```

**Video will automatically appear on splash page!** ✅

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
