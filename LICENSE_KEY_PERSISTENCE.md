# License Key Persistence

## Overview

License keys and purchased hours are stored **permanently** and persist across browser sessions, logouts, and application restarts.

## How It Works

### 1. Permanent Storage

**License Server (`licenses.json`):**
- All license keys stored permanently in `licenses.json`
- Hours purchased are permanently saved with the license
- Data persists across server restarts
- Location: `licenses.json` (in license server directory)

**Example:**
```json
{
  "RL-XXXXXXXX-YYYYYYYY-ZZZZZZZZ": {
    "hours_remaining": 20.0,
    "purchased_hours": 20.0,
    "used_hours": 0.0,
    "status": "active"
  }
}
```

### 2. Browser Storage (localStorage)

**Auto-Save Locations:**
- After registration → Saved to `localStorage.redline_license_key`
- After payment → Saved to `localStorage.redline_license_key`
- After manual entry → Saved when changed

**Auto-Load:**
- All pages automatically load license key from localStorage
- Available globally as `window.REDLINE_LICENSE_KEY`
- Auto-included in API requests via `X-License-Key` header

### 3. Access Flow

```
User Registers
    ↓
License Key Generated
    ↓
Saved to localStorage (browser)
Saved to licenses.json (server)
    ↓
User Purchases Hours
    ↓
Hours Added to License (permanent)
License Key Saved to localStorage
    ↓
User Closes Browser / Logs Out
    ↓
License Key: Still in localStorage ✅
Hours: Still in licenses.json ✅
    ↓
User Returns / Opens Browser
    ↓
License Key Auto-Loaded from localStorage
    ↓
User Accesses Application
    ↓
License Validated → Hours Checked → Access Granted ✅
```

## Testing Persistence

### Test 1: After Purchase
1. Purchase hours with license key
2. Close browser completely
3. Reopen browser
4. Go to `http://localhost:8080/dashboard`
5. **Expected**: License key auto-loaded, access granted

### Test 2: After Logout
1. Use application with license key
2. Clear browser session (but not localStorage)
3. Return to application
4. **Expected**: License key still available, access granted

### Test 3: Cross-Session
1. Register and purchase hours
2. Close browser
3. Restart computer
4. Open browser again
5. **Expected**: License key persists, hours still available

## Browser Console Testing

### Check Stored License Key
```javascript
// Check if license key is stored
localStorage.getItem('redline_license_key');

// Check global variable
window.REDLINE_LICENSE_KEY;
```

### Test API Call with Auto-License Key
```javascript
// Should automatically include license key from localStorage
fetch('/data/files')
  .then(r => r.json())
  .then(data => console.log(data));
```

### Manual License Key Management
```javascript
// Save license key
localStorage.setItem('redline_license_key', 'YOUR_LICENSE_KEY');

// Remove license key (logout)
localStorage.removeItem('redline_license_key');

// Check if stored
localStorage.getItem('redline_license_key');
```

## Important Notes

### ✅ What Persists
- License keys (permanently in `licenses.json`)
- Purchased hours (permanently with license)
- License key in browser localStorage (until cleared)

### ⚠️ What Doesn't Persist
- Flask session data (temporary, cookie-based)
- Active usage sessions (reset on server restart)
- In-memory session tracking (ephemeral)

### 🔒 Security
- License keys stored in browser localStorage (client-side)
- Hours stored on server (server-side)
- License validation happens server-side
- Hours cannot be manipulated client-side

## User Experience

### Current Behavior
1. **First Visit**: User registers → Gets license key → Saved to localStorage
2. **Purchase**: User buys hours → License key persists → Hours added permanently
3. **Return Visit**: License key auto-loaded → Hours still available → Access granted

### Expected Flow
```
Register → License Key Saved
    ↓
Purchase Hours → Hours Added Permanently
    ↓
Close Browser → License Key in localStorage
    ↓
Return Later → License Key Auto-Loaded
    ↓
Access Application → Works Automatically ✅
```

## Troubleshooting

### Issue: License Key Not Persisting
**Solution**: Check browser localStorage:
```javascript
localStorage.getItem('redline_license_key');
```

### Issue: Hours Not Available After Return
**Solution**: Check license server:
```bash
curl "http://localhost:5001/api/licenses/YOUR_LICENSE_KEY/hours"
```

### Issue: Access Denied After Return
**Possible Causes**:
1. License key not in localStorage (cleared)
2. Hours exhausted (check balance)
3. License expired (check expiration date)

## Summary

✅ **YES** - License keys and purchased hours persist permanently
✅ **YES** - Access works after logout and return
✅ **YES** - License key auto-loaded from localStorage
✅ **YES** - Hours stored permanently on server

The application provides persistent access using the same license key after logout and return!

