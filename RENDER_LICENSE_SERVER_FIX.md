# Fix: "Could not connect to license server" Error on Render

## Problem

The error "Could not connect to license server. Please try again later. Status: 503" occurs because:

1. **License server URL is set to `localhost`** - This won't work on Render
2. **License server is not deployed** - It needs to be running separately
3. **Connection timeout** - Render can't reach `http://localhost:5001`

## Solution Options

### Option 1: Deploy License Server Separately (Recommended for Production)

Deploy the license server as a separate service on Render:

1. **Create New Web Service on Render**
   - Go to Render Dashboard → New + → Web Service
   - Connect your GitHub repository
   - **Root Directory**: `licensing/server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python license_server.py`
   - **Plan**: Starter ($7/month)

2. **Get License Server URL**
   - After deployment, Render gives you a URL like: `https://license-server-xxxx.onrender.com`
   - Copy this URL

3. **Update Main Service Environment Variable**
   - Go to your main REDLINE service on Render
   - Environment tab → Add/Edit:
   - **Key**: `LICENSE_SERVER_URL`
   - **Value**: `https://license-server-xxxx.onrender.com` (your license server URL)
   - Save changes

### Option 2: Disable License Server Requirement (Quick Fix for Testing)

If you don't need license validation immediately:

1. **Set Environment Variable in Render**
   - Go to your service → Environment tab
   - Add:
   - **Key**: `REQUIRE_LICENSE_SERVER`
   - **Value**: `false`
   - Save changes

2. **Update LICENSE_SERVER_URL**
   - Even if disabled, set it to avoid connection errors:
   - **Key**: `LICENSE_SERVER_URL`
   - **Value**: `http://localhost:5001` (or any placeholder - won't be used if disabled)

**Note**: This will allow the app to work, but license validation won't function.

### Option 3: Use External License Server

If you have a license server hosted elsewhere:

1. **Set LICENSE_SERVER_URL** to your external server:
   - **Key**: `LICENSE_SERVER_URL`
   - **Value**: `https://your-license-server.com` (your actual server URL)

## Quick Fix (Immediate)

**For immediate testing, add this to Render environment:**

```
LICENSE_SERVER_URL=http://localhost:5001
REQUIRE_LICENSE_SERVER=false
```

This will:
- Allow the app to continue even if license server is unavailable
- Prevent the 503 error
- Let you test other features

**Note**: License validation won't work, but payments and other features will.

## Verify Fix

After adding environment variables:

1. **Check Render Logs**
   - Go to Logs tab
   - Look for "Could not connect to license server" - should be warnings, not errors
   - App should continue working

2. **Test Application**
   - Try accessing payment features
   - Should work without 503 errors

## Production Setup

For production, you need:

1. **License Server Deployed** (separate Render service)
2. **LICENSE_SERVER_URL** pointing to deployed server
3. **REQUIRE_LICENSE_SERVER=true** (if you want strict validation)

## License Server Deployment Steps

### 1. Check License Server Code

The license server should be in: `licensing/server/license_server.py`

### 2. Create requirements.txt for License Server

Create `licensing/server/requirements.txt`:
```
flask
flask-cors
```

### 3. Deploy to Render

1. New Web Service
2. Connect repository
3. Root Directory: `licensing/server`
4. Build: `pip install -r requirements.txt`
5. Start: `python license_server.py` or `gunicorn license_server:app`
6. Get URL and update main service

## Environment Variables Summary

**Minimum (to stop 503 errors):**
```
LICENSE_SERVER_URL=http://localhost:5001
REQUIRE_LICENSE_SERVER=false
```

**Production (with license server):**
```
LICENSE_SERVER_URL=https://your-license-server.onrender.com
REQUIRE_LICENSE_SERVER=true
```

## Troubleshooting

### Still Getting 503 Error?

1. **Check Environment Variables** are saved in Render
2. **Wait 2-3 minutes** after adding variables (auto-redeploy)
3. **Check Logs** for specific connection errors
4. **Verify License Server** is running (if using separate service)

### License Server Not Responding?

1. **Check License Server Logs** (if deployed separately)
2. **Verify URL** is correct (no typos)
3. **Test License Server** directly:
   ```bash
   curl https://your-license-server.onrender.com/health
   ```

