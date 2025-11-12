# Expired License Protection

## Status: ✅ **IMPLEMENTED**

Expired licenses are now blocked from purchasing hours.

## What Was Added

### 1. Payment Endpoint Validation (`/payments/create-checkout`)
- Validates license before creating Stripe checkout
- Blocks expired licenses (403 Forbidden)
- Blocks inactive licenses (403 Forbidden)
- Allows purchases when hours = 0 (user buying more)

### 2. Balance Endpoint Validation (`/payments/balance`)
- Validates license before showing balance
- Returns 403 if license is expired
- Returns 403 if license is inactive

### 3. Webhook Validation (`/payments/webhook`)
- Validates license before adding hours
- Prevents hours from being added to expired licenses
- Logs error if payment completes but license is expired

## How It Works

1. **User tries to purchase hours** → `/payments/create-checkout` validates license
2. **If expired** → Returns 403: "License has expired. Please contact support to renew your license."
3. **If inactive** → Returns 403: "License is inactive. Please contact support."
4. **If valid** → Creates Stripe checkout session
5. **Payment completes** → Webhook validates license again before adding hours

## Testing

### Manual Test

```bash
# 1. Create license
python3 create_test_license.py --hours 5

# 2. Manually expire it
python3 -c "
import json
from datetime import datetime, timedelta
license_file = 'licenses.json'
license_key = 'YOUR_LICENSE_KEY'
with open(license_file, 'r') as f:
    licenses = json.load(f)
if license_key in licenses:
    licenses[license_key]['expires'] = (datetime.now() - timedelta(days=1)).isoformat()
    with open(license_file, 'w') as f:
        json.dump(licenses, f, indent=2)
"

# 3. Restart license server to reload licenses
pkill -f license_server.py
python3 licensing/server/license_server.py &

# 4. Try to purchase (should be blocked)
curl -X POST http://localhost:8080/payments/create-checkout \
  -H "Content-Type: application/json" \
  -d '{"license_key": "YOUR_LICENSE_KEY", "hours": 10}'

# Expected: {"error": "License has expired. Please contact support to renew your license."} (403)
```

### Automated Test

```bash
python3 test_expired_license.py
```

## Important Notes

1. **License Server Caching**: The license server loads licenses into memory on startup. After manually editing `licenses.json`, restart the license server to pick up changes.

2. **Hours = 0 vs Expired**: 
   - Licenses with 0 hours CAN purchase more (expected behavior)
   - Expired licenses CANNOT purchase more (security feature)

3. **Validation Order**:
   - Expiration checked first
   - Status checked second  
   - Hours checked last (only if not expired)

## Security

✅ **Expired licenses cannot:**
- Create checkout sessions
- Check balance
- Receive hours via webhook

✅ **Expired licenses are blocked at:**
- Payment endpoint
- Balance endpoint
- Webhook processing

This prevents users from purchasing hours on expired licenses, ensuring they must renew their license first.

