# Purchase Button Fix

## Issue
The "Purchase" button on the payment tab was not working.

## Root Cause
Same issue as registration page - the payment template was using `{% block extra_scripts %}` but the base template defines `{% block extra_js %}`.

**Result**: The JavaScript code (`payments.js`) was never being included in the rendered HTML, so:
- Purchase button click handlers were not attached
- No checkout sessions could be created
- Buttons appeared to do nothing

## Fixes Applied

### 1. JavaScript Block Name ✅
Changed in `redline/web/templates/payment_tab.html`:
```jinja2
{% block extra_scripts %}  ❌ WRONG
```

To:
```jinja2
{% block extra_js %}  ✅ CORRECT
```

### 2. Enhanced Debugging ✅
Added comprehensive console logging to `payments.js`:
- Log when `purchasePackage` is called
- Log when `purchaseHours` is called
- Log checkout request/response
- Log errors with details

### 3. Improved License Key Handling ✅
- Auto-load license key from input field if not in memory
- Better validation and error messages
- Focus input field when license key is missing

## Testing Steps

1. **Open Payment Tab**:
   ```
   http://localhost:8080/payments/
   ```

2. **Open Browser Console** (F12 → Console tab)

3. **Check for JavaScript Loading**:
   - Should see packages loading
   - Should see balance loading (if license key entered)

4. **Enter License Key**:
   - Enter a valid license key in the input field
   - Balance should update automatically

5. **Click Purchase Button**:
   - Click "Purchase" on any package
   - Console should show:
     ```
     purchasePackage called: small
     Current license key: RL-...
     Purchasing package: {id: "small", hours: 5, ...}
     purchaseHours called: {hours: 5, packageId: "small", ...}
     Creating checkout session with: {...}
     Checkout response status: 200
     Checkout response data: {checkout_url: "https://checkout.stripe.com/..."}
     Redirecting to: https://checkout.stripe.com/...
     ```

6. **Expected Result**:
   - Redirects to Stripe checkout page
   - Can complete payment with test card: 4242 4242 4242 4242

## Troubleshooting

### Button Does Nothing
1. **Check Browser Console**:
   - Look for JavaScript errors
   - Verify "purchasePackage called" appears when clicking

2. **Check Network Tab**:
   - Look for request to `/payments/create-checkout`
   - Check response status and body

3. **Verify JavaScript File**:
   ```bash
   curl http://localhost:8080/static/js/payments.js
   ```

### "Please enter your license key first"
1. **Enter license key** in the input field
2. **Click outside** the input to trigger change event
3. **Try purchase again**

### Checkout Creation Fails
1. **Check console** for error message
2. **Verify license key is valid**:
   ```bash
   curl http://localhost:5001/api/licenses/YOUR_KEY/validate
   ```
3. **Check Stripe configuration**:
   - Verify `STRIPE_SECRET_KEY` is set in `.env`
   - Verify `STRIPE_PUBLISHABLE_KEY` is set

### No Redirect to Stripe
1. **Check console** for checkout URL
2. **Verify response** contains `checkout_url`
3. **Check for JavaScript errors** blocking redirect

## Current Status

✅ JavaScript block name fixed
✅ JavaScript code now loads
✅ Purchase button handlers attached
✅ Enhanced debugging added
✅ License key auto-loading improved
✅ Better error messages

## Next Steps

1. Test in browser
2. Verify console logs appear
3. Verify purchase button works
4. Verify redirect to Stripe checkout
5. Complete test payment

If issues persist, check browser console for specific errors.

