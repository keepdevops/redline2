# Manual Testing Guide

## Quick Start

1. **Open Browser**: Navigate to `http://localhost:8080`
2. **Services**: Ensure both services are running:
   - License Server: `http://localhost:5001`
   - Web App: `http://localhost:8080`

## Test Scenarios

### 1. Registration Flow

**URL**: `http://localhost:8080/register`

**Steps**:
1. Fill out the registration form:
   - Name: Test User
   - Email: test@example.com
   - Company: Test Company
   - License Type: Trial
2. Click "Create License Key"
3. **Expected**: License key displayed, copy button works
4. **Verify**: License key format is `RL-XXXXXXXX-YYYYYYYY-ZZZZZZZZ`

**Test License Key** (if already created):
```
RL-00C5EBEE-67BC4349-0DF71C19
```

### 2. Payment Flow

**URL**: `http://localhost:8080/payments/`

**Steps**:
1. Enter your license key in the input field
2. Click "Check Balance" or wait for auto-load
3. **Expected**: Shows hours remaining (should be 0 if new license)
4. Select a package (e.g., "5 Hours Pack")
5. Click "Purchase"
6. **Expected**: Redirects to Stripe checkout
7. Use test card: `4242 4242 4242 4242`
8. Complete payment
9. **Expected**: Redirects to success page with countdown
10. **Expected**: Auto-redirects to dashboard after 3 seconds

### 3. Dashboard Access

**URL**: `http://localhost:8080/dashboard`

**Steps**:
1. Open dashboard without license key
2. **Expected**: Page loads (public page)
3. Open with license key: `http://localhost:8080/dashboard?license_key=YOUR_KEY`
4. **Expected**: Page loads with license key in URL

### 4. Data Access (API Endpoints)

#### Test 1: Query Parameter
**URL**: `http://localhost:8080/data/files?license_key=YOUR_LICENSE_KEY`

**Expected**: JSON response with list of files

#### Test 2: Browser Console (Header Method)
Open browser console (F12) and run:
```javascript
fetch('http://localhost:8080/data/files', {
  headers: {
    'X-License-Key': 'YOUR_LICENSE_KEY'
  }
})
.then(r => r.json())
.then(data => console.log(data));
```

**Expected**: JSON response with list of files

### 5. Access Control Testing

#### Test 1: No License Key
**URL**: `http://localhost:8080/data/files`

**Expected**: JSON error: `{"error": "License key is required"}`

#### Test 2: Invalid License Key
**URL**: `http://localhost:8080/data/files?license_key=INVALID_KEY`

**Expected**: JSON error: `{"error": "Invalid license"}`

#### Test 3: Valid License Key with Hours
**URL**: `http://localhost:8080/data/files?license_key=YOUR_VALID_KEY`

**Expected**: JSON response with files array

### 6. Payment Success Page

**URL**: `http://localhost:8080/payments/success?session_id=test&license_key=YOUR_KEY`

**Expected**: 
- Shows error page (400 status)
- Displays "Payment verification error" message
- No 500 error

### 7. Web Pages (Public Access)

Test these URLs without license key:

- `http://localhost:8080/dashboard` - Should load
- `http://localhost:8080/register` - Should load
- `http://localhost:8080/payments/` - Should load
- `http://localhost:8080/help` - Should load

**Expected**: All pages load successfully (200 OK)

### 8. API Endpoints (Require License)

Test these with license key:

- `http://localhost:8080/data/files?license_key=YOUR_KEY`
- `http://localhost:8080/user-data/files?license_key=YOUR_KEY`
- `http://localhost:8080/user-data/stats?license_key=YOUR_KEY`

**Expected**: JSON responses with data

## Browser Console Testing

### Test POST Endpoint

```javascript
// Test task submission
fetch('http://localhost:8080/tasks/submit', {
  method: 'POST',
  headers: {
    'X-License-Key': 'YOUR_LICENSE_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_name: 'process_data_conversion',
    args: [],
    kwargs: {}
  })
})
.then(r => r.json())
.then(data => console.log('Task submitted:', data));
```

### Test Payment Balance

```javascript
fetch('http://localhost:8080/payments/balance?license_key=YOUR_LICENSE_KEY')
.then(r => r.json())
.then(data => console.log('Balance:', data));
```

## Test Checklist

### Registration
- [ ] Registration form loads
- [ ] Form validation works
- [ ] License key generated and displayed
- [ ] Copy button works
- [ ] Email sent (if SMTP enabled)

### Payment
- [ ] Payment page loads
- [ ] License key input works
- [ ] Balance displays correctly
- [ ] Packages display correctly
- [ ] Purchase button works
- [ ] Stripe checkout opens
- [ ] Payment completes
- [ ] Success page loads
- [ ] Auto-redirect to dashboard works

### Access Control
- [ ] Web pages accessible without license
- [ ] API endpoints blocked without license
- [ ] API endpoints work with valid license
- [ ] Invalid license keys blocked
- [ ] Expired licenses blocked

### API Endpoints
- [ ] GET with query parameter works
- [ ] GET with header works
- [ ] POST with header works
- [ ] POST with JSON body works
- [ ] File upload works (with header)

## Common Issues

### Issue: 500 Error on Payment Success
**Solution**: Already fixed - should return 400 for invalid sessions

### Issue: License Key Not Recognized
**Solution**: 
- Check license key format
- Ensure license has hours (add hours via license server)
- Try different authentication method (query param vs header)

### Issue: CORS Errors
**Solution**: Use proxy endpoints (e.g., `/api/register` instead of direct license server)

## Test License Key

If you need a test license key, use:
```
RL-00C5EBEE-67BC4349-0DF71C19
```

Hours: 20.0 (add more via license server if needed)

## Quick Commands

### Add Hours to License
```bash
curl -X POST "http://localhost:5001/api/licenses/YOUR_LICENSE_KEY/hours" \
  -H "Content-Type: application/json" \
  -d '{"hours": 20}'
```

### Check License Balance
```bash
curl "http://localhost:5001/api/licenses/YOUR_LICENSE_KEY/hours"
```

### Test API Endpoint
```bash
curl "http://localhost:8080/data/files?license_key=YOUR_LICENSE_KEY"
```

---

**Happy Testing!** 🧪

