# User Access Guide - Complete Flow

## Overview
This guide explains the complete user journey from registration to accessing the paid REDLINE application.

## Complete User Flow

### Step 1: Registration ✅
1. **Go to Registration Page**: http://localhost:8080/register
2. **Fill Out Form**:
   - Full Name
   - Email Address
   - Company/Organization
   - License Type (Trial, Standard, or Professional)
3. **Click "Create License Key"**
4. **Save Your License Key**: Copy and save it securely
5. **Email Confirmation**: License key is sent to your email (if SMTP configured)

**Result**: You now have a license key with **0 hours** (cannot access application yet)

### Step 2: Purchase Hours ✅
1. **Go to Payment Tab**: http://localhost:8080/payments/
2. **Enter Your License Key** in the input field
3. **Choose a Package** or **Enter Custom Hours**:
   - 5 Hours Pack: $25
   - 10 Hours Pack: $45
   - 20 Hours Pack: $80
   - 50 Hours Pack: $180
   - Custom: Any number of hours
4. **Click "Purchase"**
5. **Complete Payment** on Stripe checkout page:
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any CVC
6. **Payment Success**: You'll be redirected back with hours added

**Result**: Hours are automatically added to your license key

### Step 3: Access Application ✅
After purchasing hours, you can now access the REDLINE application!

#### How to Use Your License Key

**Option 1: Web Interface**
- All web pages automatically check your license
- Enter license key in payment tab to view balance
- Access is granted automatically when hours > 0

**Option 2: API Access**
Include your license key in API requests:

```bash
# Using Header (Recommended)
curl -H "X-License-Key: YOUR_LICENSE_KEY" \
     http://localhost:8080/data/files

# Using Query Parameter
curl "http://localhost:8080/data/files?license_key=YOUR_LICENSE_KEY"

# Using JSON Body
curl -X POST http://localhost:8080/api/endpoint \
     -H "Content-Type: application/json" \
     -d '{"license_key": "YOUR_LICENSE_KEY", ...}'
```

**Option 3: Browser Session**
- License key is saved in browser localStorage
- Automatically used for API calls
- Can be entered in payment tab

## Protected Endpoints

These endpoints **require** a valid license key with hours > 0:

- `/api/*` - All API endpoints
- `/data/*` - Data management endpoints
- `/analysis/*` - Analysis endpoints
- `/download/*` - Download endpoints
- `/converter/*` - File conversion endpoints

## Public Endpoints

These endpoints are accessible without a license:

- `/` - Home page
- `/register` - Registration page
- `/payments/` - Payment page (to purchase hours)
- `/payments/packages` - View available packages
- `/health` - Health check
- `/static/*` - Static files

## Access Control

### ✅ Access Granted When:
- Valid license key provided
- License is not expired
- License status is "active"
- Hours remaining > 0

### ❌ Access Denied When:
- No license key provided → **401 Unauthorized**
- Invalid license key → **403 Forbidden**
- License expired → **403 Forbidden**
- License inactive → **403 Forbidden**
- Hours = 0 → **403 Forbidden** ("No hours remaining")

## Using the Application

### 1. View Your Balance
```bash
curl "http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY"
```

### 2. Upload Data
```bash
curl -X POST http://localhost:8080/api/upload \
     -H "X-License-Key: YOUR_LICENSE_KEY" \
     -F "file=@data.csv"
```

### 3. Download Data
```bash
curl -H "X-License-Key: YOUR_LICENSE_KEY" \
     http://localhost:8080/download/download?file=data.csv
```

### 4. Analyze Data
```bash
curl -X POST http://localhost:8080/analysis/analyze \
     -H "X-License-Key: YOUR_LICENSE_KEY" \
     -H "Content-Type: application/json" \
     -d '{"data": [...], "analysis_type": "summary"}'
```

## Hours Usage

Hours are deducted automatically as you use the application:
- **API calls**: Hours deducted based on usage time
- **Data processing**: Hours deducted for processing time
- **File operations**: Hours deducted for file operations

### Check Remaining Hours
```bash
curl "http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY"
```

### Purchase More Hours
When hours run low, purchase more:
1. Go to Payment tab
2. Enter license key
3. Purchase additional hours
4. Hours are added immediately

## Troubleshooting

### "No hours remaining"
- **Solution**: Purchase hours on the Payment tab
- **Check**: Verify payment was successful
- **Verify**: Check balance endpoint

### "Invalid license key"
- **Solution**: Double-check license key spelling
- **Check**: License key format: `RL-XXXXXXXX-YYYYYYYY-ZZZZZZZZ`
- **Verify**: License hasn't expired

### "License expired"
- **Solution**: Contact support to renew license
- **Check**: License expiration date
- **Note**: Expired licenses cannot purchase hours

### Payment Completed But No Access
1. **Check Balance**: Verify hours were added
2. **Check Webhook**: Ensure Stripe webhook is configured
3. **Wait**: Sometimes takes a few seconds
4. **Contact Support**: If issue persists

## Quick Start Checklist

- [ ] Register and get license key
- [ ] Save license key securely
- [ ] Purchase hours via Payment tab
- [ ] Verify balance shows hours > 0
- [ ] Access application with license key
- [ ] Use API endpoints with license key header
- [ ] Monitor remaining hours
- [ ] Purchase more hours when needed

## Support

If you encounter issues:
1. Check this guide
2. Verify license key is correct
3. Check hours balance
4. Review error messages
5. Contact support with:
   - License key (first 8 characters)
   - Error message
   - Steps to reproduce

## Example: Complete Flow

```bash
# 1. Register (via web UI or API)
curl -X POST http://localhost:8080/api/register \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "company": "Acme Corp", "type": "trial", "duration_days": 365, "hours": 0}'

# Response: {"success": true, "license": {"key": "RL-..."}}

# 2. Purchase hours (via web UI - Stripe checkout)
# Or simulate: Add hours directly
curl -X POST http://localhost:5001/api/licenses/RL-.../hours \
     -H "Content-Type: application/json" \
     -d '{"hours": 10}'

# 3. Access application
curl -H "X-License-Key: RL-..." \
     http://localhost:8080/data/files

# 4. Check balance
curl "http://localhost:8080/payments/balance?license_key=RL-..."
```

## Next Steps After Purchase

1. **Save License Key**: Store it securely
2. **Test Access**: Try accessing a protected endpoint
3. **Explore Features**: Use data upload, analysis, conversion
4. **Monitor Usage**: Check balance regularly
5. **Purchase More**: Buy additional hours as needed

---

**Remember**: Your license key is your access credential. Keep it secure and use it with all API requests!

