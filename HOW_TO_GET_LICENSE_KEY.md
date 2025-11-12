# How to Get a License Key

## Current Methods

### Method 1: API Endpoint (For Administrators)

Licenses are created via the license server API:

**Endpoint**: `POST /api/licenses`

**Request**:
```bash
curl -X POST http://localhost:5001/api/licenses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "type": "trial",
    "duration_days": 365,
    "hours": 0
  }'
```

**Response**:
```json
{
  "success": true,
  "license": {
    "key": "RL-12345678-ABCDEFGH-IJKLMNOP",
    "customer": {
      "name": "John Doe",
      "email": "john@example.com",
      "company": "Acme Corp"
    },
    "type": "trial",
    "status": "active",
    "hours_remaining": 0.0,
    "purchased_hours": 0.0,
    "used_hours": 0.0
  }
}
```

### Method 2: Test Script (For Testing)

Use the provided test script:

```bash
python3 create_test_license.py --name "Test User" --hours 0
```

This creates a license with:
- Name: Test User
- Email: test@example.com
- Company: Test Company
- Hours: 0 (to test purchase flow)

### Method 3: Manual License Creation (For Administrators)

If you have access to the license server, you can create licenses programmatically:

```python
from licensing.server.license_server import license_manager

license_data = license_manager.create_license(
    customer_info={
        'name': 'John Doe',
        'email': 'john@example.com',
        'company': 'Acme Corp'
    },
    license_type='standard',
    duration_days=365,
    hours=0  # Start with 0 hours, user purchases via Stripe
)

license_key = license_data['key']
print(f"License Key: {license_key}")
```

## License Types

- **trial**: Basic features, 1 install
- **standard**: Standard features, 3 installs
- **professional**: All features + API access, 10 installs
- **enterprise**: All features + unlimited installs

## After Getting a License Key

1. **Enter license key** in the Payment tab (`/payments/`)
2. **Purchase hours** via Stripe checkout
3. **Use REDLINE** - hours are deducted as you use the system

## Method 4: Web Registration Page (NEW!)

**User-Friendly Registration**: Users can now register directly through the web UI!

1. **Go to Registration Page**: Navigate to `/register` in your browser
2. **Fill out the form**:
   - Full Name
   - Email Address
   - Company/Organization
   - License Type (Trial, Standard, or Professional)
3. **Get License Key**: Your license key is displayed immediately after registration
4. **Purchase Hours**: Click "Purchase Hours Now" to go directly to the Payment tab

**Access**: `http://localhost:8080/register` (or your deployed URL + `/register`)

The registration page:
- ✅ Creates license automatically
- ✅ Shows license key immediately
- ✅ Provides copy button for license key
- ✅ Links directly to payment page
- ✅ Handles errors gracefully

## Recommended: Add User Registration

To make it easier for users to get license keys, you should add:

1. **Registration Page** (`/register`)
   - Form for name, email, company
   - Creates license automatically
   - Shows license key after creation

2. **Email Confirmation** (Optional)
   - Send license key via email
   - Include setup instructions

3. **Trial License Option**
   - Allow users to create trial licenses themselves
   - Limited to 1-2 hours for testing

## Quick Test: Create a License

```bash
# Start license server
python3 licensing/server/license_server.py

# In another terminal, create a test license
python3 create_test_license.py

# Use the license key in the Payment tab
# Then purchase hours via Stripe
```

## License Key Format

License keys follow this format:
```
RL-XXXXXXXX-YYYYYYYY-ZZZZZZZZ
```

Example: `RL-12345678-ABCDEFGH-IJKLMNOP`

The key is generated based on:
- Customer email
- Company name
- Timestamp
- Secret key (HMAC-SHA256)

