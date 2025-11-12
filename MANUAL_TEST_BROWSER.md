# Manual Browser Test: Expired License Protection

## Quick Test Script

Run this to set up a test:
```bash
./manual_test_expired_license.sh
```

This will:
1. Create a license with hours
2. Expire it
3. Restart license server
4. Test the endpoints
5. Give you a license key to test in browser

## Browser Test Steps

### Step 1: Get an Expired License Key

Run the test script or manually:
```bash
# Create license
python3 create_test_license.py --hours 10

# Note the license key (e.g., RL-XXXXXXXX-XXXXXXXX-XXXXXXXX)

# Expire it
python3 -c "
import json
from datetime import datetime, timedelta
license_file = 'licenses.json'
license_key = 'YOUR_LICENSE_KEY_HERE'
with open(license_file, 'r') as f:
    licenses = json.load(f)
if license_key in licenses:
    licenses[license_key]['expires'] = (datetime.now() - timedelta(days=1)).isoformat()
    with open(license_file, 'w') as f:
        json.dump(licenses, f, indent=2)
    print('License expired')
"

# Restart license server
pkill -f license_server.py
python3 licensing/server/license_server.py &
```

### Step 2: Open Payment Tab

1. Open browser: http://localhost:8080/payments/
2. You should see the Payment & Access Time page

### Step 3: Enter Expired License Key

1. In the "License Key" field, enter your expired license key
2. The page should automatically try to load balance

**Expected Result**: 
- ❌ Balance should NOT load
- ⚠️ Error message should appear: "License has expired"

### Step 4: Try to Purchase Hours

1. Click on any hour package (e.g., "5 Hours Pack")
2. Or enter custom hours and click "Purchase"

**Expected Result**:
- ❌ Checkout should NOT be created
- ⚠️ Error message: "License has expired. Please contact support to renew your license."
- ❌ Should NOT redirect to Stripe checkout

### Step 5: Verify Error Messages

You should see error messages like:
- "License has expired"
- "License has expired. Please contact support to renew your license."

## What to Look For

✅ **Correct Behavior:**
- Expired license shows error when checking balance
- Expired license cannot create checkout sessions
- Clear error messages displayed
- No redirect to Stripe checkout

❌ **Incorrect Behavior:**
- Balance loads successfully
- Checkout session created
- Redirects to Stripe checkout
- No error messages

## Test Different Scenarios

### Scenario 1: Valid License with 0 Hours
- Should be able to purchase hours
- Balance shows 0 hours but allows purchase

### Scenario 2: Valid License with Hours
- Should be able to purchase more hours
- Balance shows remaining hours

### Scenario 3: Expired License
- Should NOT be able to purchase hours
- Should show expiration error

### Scenario 4: Invalid License Key
- Should show "Invalid license key" error

## Browser Console Check

Open browser developer tools (F12) and check Console tab:

1. **When entering expired license:**
   - Look for API calls to `/payments/balance`
   - Should see 403 status code
   - Error response in console

2. **When trying to purchase:**
   - Look for API calls to `/payments/create-checkout`
   - Should see 403 status code
   - Error response in console

## Quick Test Commands

```bash
# Test expired license via curl
LICENSE_KEY="YOUR_EXPIRED_LICENSE_KEY"

# Check balance (should fail)
curl "http://localhost:8080/payments/balance?license_key=$LICENSE_KEY"

# Try checkout (should fail)
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d "{\"license_key\": \"$LICENSE_KEY\", \"hours\": 10}"
```

Both should return 403 Forbidden with expiration error.

