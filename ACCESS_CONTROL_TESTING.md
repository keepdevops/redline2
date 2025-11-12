# Access Control Testing Guide

## Overview

This guide explains how to test that customers cannot access the application without payment (i.e., when they have 0 hours remaining).

## Current Implementation

### Access Control Flow

1. **Request arrives** → `check_access()` middleware runs first
2. **License validation** → Checks license server for valid license and hours
3. **Access decision**:
   - ✅ **Allow**: License valid AND hours > 0
   - ❌ **Block**: No license key, invalid license, or hours = 0
4. **Usage tracking** → If allowed, track usage and deduct hours

### Protected Endpoints

These endpoints require a valid license with hours:
- `/api/*` - All API endpoints
- `/data/*` - Data management endpoints
- `/analysis/*` - Analysis endpoints
- `/download/*` - Download endpoints

### Public Endpoints

These endpoints don't require a license:
- `/health` - Health check
- `/register` - User registration
- `/payments/packages` - View packages
- `/payments/create-checkout` - Create checkout (needs license but for payment)
- `/payments/success` - Payment success page
- `/payments/webhook` - Stripe webhook
- `/static/*` - Static files

## Running Tests

### Quick Test

```bash
# Make sure both services are running
python3 licensing/server/license_server.py  # Terminal 1
python3 web_app.py                          # Terminal 2

# Run access control tests
python3 test_access_control.py
```

### Test Scenarios

#### 1. No License Key
**Expected**: API endpoints return `401 Unauthorized`

```bash
curl http://localhost:8080/api/data/list
# Expected: {"error": "License key is required", ...} (401)
```

#### 2. Zero Hours License
**Expected**: API endpoints return `403 Forbidden` with "No hours remaining"

```bash
# Create license with 0 hours
python3 create_test_license.py --hours 0

# Try to access API
curl -H "X-License-Key: YOUR_LICENSE_KEY" http://localhost:8080/api/data/list
# Expected: {"error": "No hours remaining. Please purchase hours to continue.", "code": "INSUFFICIENT_HOURS"} (403)
```

#### 3. Invalid License Key
**Expected**: API endpoints return `403 Forbidden` with "Invalid license"

```bash
curl -H "X-License-Key: RL-INVALID-KEY" http://localhost:8080/api/data/list
# Expected: {"error": "Invalid license key", "code": "INVALID_LICENSE"} (403)
```

#### 4. Valid License With Hours
**Expected**: API endpoints work normally

```bash
# Create license with hours
python3 create_test_license.py --hours 10

# Access API
curl -H "X-License-Key: YOUR_LICENSE_KEY" http://localhost:8080/api/data/list
# Expected: Normal response (200 or appropriate data)
```

#### 5. Public Endpoints
**Expected**: Accessible without license

```bash
curl http://localhost:8080/health
curl http://localhost:8080/register
curl http://localhost:8080/payments/packages
# Expected: All return 200 OK
```

## Manual Testing Steps

### Step 1: Create License with 0 Hours

```bash
python3 create_test_license.py --hours 0
# Save the license key
```

### Step 2: Try to Access Protected Endpoint

```bash
# Using curl
curl -H "X-License-Key: YOUR_LICENSE_KEY" \
     http://localhost:8080/api/data/list

# Using Python
python3 -c "
import requests
response = requests.get(
    'http://localhost:8080/api/data/list',
    headers={'X-License-Key': 'YOUR_LICENSE_KEY'}
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

**Expected Result**: `403 Forbidden` with error message about insufficient hours

### Step 3: Purchase Hours

1. Go to Payment tab: `http://localhost:8080/payments/`
2. Enter license key
3. Purchase hours (use test card: `4242 4242 4242 4242`)
4. Complete payment

### Step 4: Verify Access After Payment

```bash
# Same request as Step 2
curl -H "X-License-Key: YOUR_LICENSE_KEY" \
     http://localhost:8080/api/data/list
```

**Expected Result**: `200 OK` with data (or appropriate response)

## Configuration

### Environment Variables

```bash
# Enable/disable payment enforcement
ENFORCE_PAYMENT=true  # Block access when hours = 0
ENFORCE_PAYMENT=false # Allow access even with 0 hours (for testing)

# License server requirement
REQUIRE_LICENSE_SERVER=false  # Allow access if license server is down
REQUIRE_LICENSE_SERVER=true   # Block access if license server is down
```

### Testing Without Payment Enforcement

To test the application without blocking access (for development):

```bash
# In .env file
ENFORCE_PAYMENT=false
```

This allows you to test functionality without purchasing hours, but still tracks usage.

## Expected Behavior

### With Payment Enforcement Enabled (`ENFORCE_PAYMENT=true`)

| Scenario | License Key | Hours | Expected Response |
|----------|------------|-------|-------------------|
| No key | None | N/A | `401 Unauthorized` |
| Invalid key | Invalid | N/A | `403 Forbidden` |
| Valid, 0 hours | Valid | 0 | `403 Forbidden` - "No hours remaining" |
| Valid, >0 hours | Valid | >0 | `200 OK` (or appropriate response) |
| Expired license | Valid (expired) | N/A | `403 Forbidden` - "License expired" |

### With Payment Enforcement Disabled (`ENFORCE_PAYMENT=false`)

| Scenario | License Key | Hours | Expected Response |
|----------|------------|-------|-------------------|
| No key | None | N/A | `401 Unauthorized` |
| Invalid key | Invalid | N/A | `403 Forbidden` |
| Valid, 0 hours | Valid | 0 | `200 OK` (access allowed) |
| Valid, >0 hours | Valid | >0 | `200 OK` |

## Troubleshooting

### "License server unavailable"

**Problem**: Access controller can't connect to license server

**Solution**:
1. Check license server is running: `curl http://localhost:5001/api/health`
2. Check `LICENSE_SERVER_URL` in `.env`
3. Set `REQUIRE_LICENSE_SERVER=false` for development

### "Access allowed despite 0 hours"

**Problem**: `ENFORCE_PAYMENT` is set to `false`

**Solution**: Set `ENFORCE_PAYMENT=true` in `.env` and restart web app

### "All requests blocked"

**Problem**: License server is down and `REQUIRE_LICENSE_SERVER=true`

**Solution**: Set `REQUIRE_LICENSE_SERVER=false` or fix license server

## Integration with Payment Flow

1. **User registers** → Gets license key with 0 hours
2. **User tries to access** → Blocked (403 - No hours)
3. **User purchases hours** → Hours added via Stripe webhook
4. **User tries again** → Access allowed (hours > 0)
5. **User uses application** → Hours deducted over time
6. **Hours run out** → Access blocked again (403)

This creates a paywall that requires users to purchase hours before accessing the application.

