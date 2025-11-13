# License Key Fix - Ensuring Keys Populate All Modules

## Issue
License keys were not being included in API requests from Redline modules (data view, download, etc.), causing "License key is required" errors.

## Root Cause
1. jQuery override might not install before other scripts run
2. License key might not be available when modules initialize
3. Some modules might not be using the override correctly

## Fixes Applied

### 1. Enhanced License Key Loading (`base.html`)
- Made `getLicenseKey()` available immediately (before jQuery loads)
- Added multiple retry attempts to ensure jQuery override installs
- Made license key available via `window.REDLINE.getLicenseKey()` for all modules

### 2. Improved jQuery Override Installation
- Multiple retry attempts (immediate, 100ms, 500ms)
- Checks if jQuery is already loaded
- Handles both DOMContentLoaded and already-loaded states

### 3. Updated `main.js` to Use Global Function
- `getStoredLicenseKey()` now uses global `window.getLicenseKey()` if available
- Falls back to direct localStorage access if global function not available

## Testing

### Check License Key in Browser Console
```javascript
// Check if license key exists
checkLicenseKey()

// Get license key directly
window.getLicenseKey()

// Check via REDLINE object
window.REDLINE.getLicenseKey()
```

### Verify Override is Installed
```javascript
// Check if jQuery override is installed
console.log('jQuery override:', typeof $.ajax === 'function' ? 'Installed' : 'Not installed')

// Test an API call
$.ajax({
    url: '/api/files',
    method: 'GET',
    success: function(data) {
        console.log('✅ API call successful:', data);
    },
    error: function(xhr) {
        console.error('❌ API call failed:', xhr.responseText);
    }
});
```

### Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click any button that makes an API call
4. Click on the request
5. Check "Headers" tab
6. Look for `X-License-Key` header

## Expected Behavior

1. **On Page Load:**
   - Console shows: `✅ License key loaded from localStorage: ...`
   - Console shows: `✅ jQuery license key override installed`

2. **On API Calls:**
   - Console shows: `✅ Added license key to headers for: /api/files`
   - Network tab shows `X-License-Key` header in requests

3. **If License Key Missing:**
   - Console shows: `⚠️ No license key found in localStorage for request: ...`
   - User should register or enter license key

## Manual Fix (If Needed)

If license key still not working, manually set it:

```javascript
// Set license key
localStorage.setItem('redline_license_key', 'YOUR-LICENSE-KEY-HERE');

// Reload page
location.reload();
```

## Next Steps

1. **Refresh browser** to load updated code
2. **Register or enter license key** if not already done
3. **Check browser console** for license key loading messages
4. **Test API calls** (data view, download, etc.)
5. **Verify Network tab** shows `X-License-Key` header

