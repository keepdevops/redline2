# License Key Debugging Guide

## Issue
Buttons were showing "no license" errors even when a valid license key exists.

## Fix Applied
Enhanced the jQuery `$.ajax()` override in `base.html` to:
1. Handle all jQuery call patterns (`$.ajax(url, options)` and `$.ajax(options)`)
2. Add comprehensive logging to track license key inclusion
3. Add diagnostic functions for debugging

## How to Test

### 1. Check License Key in Browser Console
Open browser console (F12) and run:
```javascript
checkLicenseKey()
```

This will show:
- Whether license key exists in localStorage
- Whether license key exists in window.REDLINE_LICENSE_KEY
- The current license key (first 20 chars)

### 2. Verify License Key is Saved
```javascript
localStorage.getItem('redline_license_key')
```

Should return your license key string.

### 3. Test API Call with License Key
```javascript
$.ajax({
    url: '/data/files',
    method: 'GET',
    success: function(data) {
        console.log('✅ Success:', data);
    },
    error: function(xhr) {
        console.error('❌ Error:', xhr.responseText);
    }
});
```

You should see console logs like:
- `✅ Added license key to headers for: /data/files`
- `✅ jQuery license key override installed`

### 4. Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click any button that makes an API call
4. Click on the request
5. Check "Headers" tab
6. Look for `X-License-Key` header

## Common Issues

### Issue: License key not in localStorage
**Solution**: 
- Go to `/register` and create a new license key
- Or go to `/payments` and enter your license key (it should auto-save)
- Or manually set: `localStorage.setItem('redline_license_key', 'YOUR-KEY-HERE')`

### Issue: License key exists but not being sent
**Solution**:
- Check browser console for warnings: `⚠️ No license key found in localStorage`
- Verify jQuery override is installed: Look for `✅ jQuery license key override installed`
- Check if request URL starts with `/` (override only works for same-origin requests)

### Issue: License key invalid or expired
**Solution**:
- Verify license key is valid: `curl http://localhost:5001/api/licenses/YOUR-KEY/validate`
- Check license hours: `curl http://localhost:5001/api/licenses/YOUR-KEY/hours`
- Purchase more hours if needed

## Manual License Key Entry

If license key is not auto-loading, you can manually set it:

```javascript
// Set license key
localStorage.setItem('redline_license_key', 'YOUR-LICENSE-KEY-HERE');

// Reload page or refresh
location.reload();
```

## Debugging Steps

1. **Open browser console** (F12)
2. **Check license key**: `checkLicenseKey()`
3. **Try an API call**: Use the test code above
4. **Check console logs**: Look for `✅` or `⚠️` messages
5. **Check Network tab**: Verify `X-License-Key` header is present
6. **Check server logs**: Look for license validation errors

## Expected Console Output

When working correctly, you should see:
```
License key loaded from localStorage: RL-12345678-1234...
✅ jQuery license key override installed
✅ Added license key to headers for: /data/files
```

If you see warnings instead:
```
⚠️ No license key found in localStorage for request: /data/files
```

This means the license key is not saved in localStorage.

