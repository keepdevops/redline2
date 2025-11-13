# Global Balance Tracker - Test Guide

## ✅ Status: Implemented and Ready for Testing

The global balance tracker has been successfully implemented and is now active on all pages.

## What Was Implemented

1. **Global Balance Tracker Script** (`redline/web/static/js/balance_tracker.js`)
   - Automatically loads on all pages
   - Displays hours remaining in navbar
   - Auto-refreshes every 60 seconds
   - Shows time elapsed since last update

2. **Navbar Integration** (`redline/web/templates/base.html`)
   - Balance display appears in top-right navbar
   - Color-coded status (green/yellow/red)
   - Click to refresh functionality

## Testing Steps

### 1. Basic Functionality Test

1. **Open the application:**
   ```bash
   # Web app should be running at:
   http://localhost:8080
   ```

2. **Open Browser DevTools:**
   - Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Go to **Console** tab

3. **Check for balance tracker:**
   - Look in the navbar (top right) for balance display
   - Should show hours remaining (if license key is set)
   - Should show "Just now" or time elapsed

### 2. License Key Test

1. **If you don't have a license key:**
   - Go to **Register** page
   - Create a new account and get a license key
   - License key will be saved to `localStorage`

2. **If you have a license key:**
   - Enter it on the Payment page
   - Or it should auto-load from `localStorage`
   - Balance should appear in navbar within 1-2 seconds

### 3. Balance Display Test

**Expected behavior:**
- ✅ Balance appears in navbar (top right, before "Online" status)
- ✅ Shows hours remaining (e.g., "1.50 hours")
- ✅ Shows time elapsed (e.g., "5s ago", "1m 30s ago")
- ✅ Color coding:
  - 🟢 Green: 5+ hours remaining
  - 🟡 Yellow: 1-5 hours remaining
  - 🔴 Red: < 1 hour remaining

### 4. Auto-Refresh Test

1. **Wait for refresh:**
   - Balance should auto-refresh every 60 seconds
   - Time elapsed updates every second
   - Watch the "X ago" text update in real-time

2. **Manual refresh:**
   - Click on the balance display in navbar
   - Balance should refresh immediately

### 5. Cross-Page Persistence Test

1. **Navigate between pages:**
   - Dashboard → Data → Analysis → Download → Payment
   - Balance should persist across all pages
   - Should not disappear when navigating

2. **Check console:**
   - Should see balance loading messages
   - No errors related to balance tracker

### 6. Multi-Tab Test

1. **Open multiple tabs:**
   - Open `http://localhost:8080` in 2-3 tabs
   - Enter license key in one tab
   - Other tabs should update automatically (via localStorage events)

### 7. Browser Console Check

**Expected console output:**
```
✅ License key loaded from localStorage: ...
✅ Balance tracker initialized
```

**No errors should appear:**
- ❌ No "balance_tracker.js not found" errors
- ❌ No "loadBalance is not defined" errors
- ❌ No CORS errors

## Troubleshooting

### Balance Not Appearing

1. **Check license key:**
   ```javascript
   // In browser console:
   localStorage.getItem('redline_license_key')
   ```

2. **Check balance endpoint:**
   ```bash
   curl "http://localhost:8080/payments/balance?license_key=YOUR_KEY"
   ```

3. **Check script loading:**
   ```javascript
   // In browser console:
   typeof window.REDLINE_BALANCE
   // Should return "object"
   ```

### Balance Not Refreshing

1. **Check refresh interval:**
   - Should refresh every 60 seconds
   - Check Network tab in DevTools for `/payments/balance` requests

2. **Check console for errors:**
   - Look for fetch errors
   - Check if license server is running

### Balance Disappears on Navigation

1. **Check script is loaded:**
   ```javascript
   // In browser console on any page:
   document.querySelector('script[src*="balance_tracker"]')
   // Should return the script element
   ```

2. **Check balance display element:**
   ```javascript
   // In browser console:
   document.getElementById('globalBalanceDisplay')
   // Should return the balance display element
   ```

## API Functions

The balance tracker exposes these global functions:

```javascript
// Refresh balance manually
window.REDLINE_BALANCE.refresh()

// Get current balance
window.REDLINE_BALANCE.getBalance()

// Load balance (with error display)
window.REDLINE_BALANCE.loadBalance()
```

## Expected Behavior Summary

| Feature | Expected Behavior |
|---------|------------------|
| **Initial Load** | Balance appears within 1-2 seconds if license key exists |
| **Auto-Refresh** | Refreshes every 60 seconds automatically |
| **Time Elapsed** | Updates every second showing "X ago" |
| **Cross-Page** | Persists across all page navigations |
| **Multi-Tab** | Syncs across browser tabs |
| **Click Refresh** | Clicking balance refreshes immediately |
| **Color Coding** | Green/Yellow/Red based on hours remaining |

## Test Checklist

- [ ] Balance appears in navbar when license key is set
- [ ] Balance shows correct hours remaining
- [ ] Time elapsed updates every second
- [ ] Balance auto-refreshes every 60 seconds
- [ ] Balance persists when navigating between pages
- [ ] Balance syncs across browser tabs
- [ ] Click to refresh works
- [ ] Color coding works (green/yellow/red)
- [ ] No console errors
- [ ] Balance disappears when license key is removed

## Next Steps

After testing:
1. Verify all checklist items pass
2. Test with real license keys and payments
3. Monitor for any performance issues
4. Check browser compatibility (Chrome, Firefox, Safari)

