# Fixing Balance Error
**Troubleshooting and fixing balance display errors**

---

## 🔍 Common Balance Errors

### Error 1: "purchased_hours is undefined"

**Symptoms:**
- Frontend shows "Error" or "NaN"
- Console shows: `Cannot read property 'purchased_hours' of undefined`

**Cause:**
- API response missing `purchased_hours` field
- Response format inconsistent

**Fix:**
- Backend should always return `purchased_hours` (already fixed)
- Frontend should handle missing fields (already has fallback)

---

### Error 2: "Failed to load balance"

**Symptoms:**
- Balance shows "Error" in UI
- Network request fails

**Possible Causes:**
1. License server unavailable
2. Invalid license key
3. Rate limit exceeded
4. Network error

**Fix:**
- Check license server is running
- Verify license key is correct
- Check rate limits
- Review network connectivity

---

### Error 3: "time balance for purchased subscription"

**Symptoms:**
- Error message mentions "time balance"
- Balance not displaying correctly

**Possible Causes:**
- Missing `purchased_hours` in response
- Frontend trying to calculate balance incorrectly
- License server response format issue

---

## 🔧 Quick Fixes

### Fix 1: Ensure purchased_hours Always Present

The backend already ensures this, but let's verify all paths:

**File:** `redline/web/routes/payments_balance.py`

All response paths should include:
```python
result['purchased_hours'] = result.get('purchased_hours', 0.0)
```

### Fix 2: Improve Frontend Error Handling

**File:** `redline/web/static/js/balance_tracker.js`

Ensure all balance access uses fallbacks:
```javascript
const purchasedHours = balance?.purchased_hours || 0;
const hoursRemaining = balance?.hours_remaining || 0;
const usedHours = balance?.used_hours || 0;
```

### Fix 3: Better Error Messages

Add more descriptive error messages in frontend.

---

## 🚨 Debugging Steps

### Step 1: Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for balance-related errors
4. Check Network tab for `/payments/balance` requests

### Step 2: Check API Response

```bash
# Test balance endpoint directly
curl "https://your-service.onrender.com/payments/balance?license_key=YOUR_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "hours_remaining": 0.0,
  "used_hours": 0.0,
  "purchased_hours": 0.0
}
```

### Step 3: Check Render Logs

1. Render Dashboard → Your Service → Logs
2. Look for balance-related errors
3. Check for "purchased_hours" mentions

---

## ✅ Verification Checklist

- [ ] API response includes `purchased_hours` field
- [ ] API response includes `success: true` (or `hours_remaining` exists)
- [ ] Frontend handles missing fields gracefully
- [ ] No JavaScript errors in console
- [ ] Network requests return 200 status
- [ ] License server is accessible

---

**Next:** Check browser console for specific error message

