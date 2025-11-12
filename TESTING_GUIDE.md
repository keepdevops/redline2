# REDLINE Payment Integration Testing Guide

## Quick Test

Run the comprehensive test suite:

```bash
python3 test_payment_integration.py
```

## Prerequisites

### 1. Install Dependencies
```bash
pip3 install stripe requests
```

### 2. Set Up Environment Variables (Optional)
```bash
# For full testing, create .env file:
cp env.template .env
# Edit .env and add your Stripe test keys (optional for basic tests)
```

### 3. Start Services

**Option A: Test Without Running Services**
- Tests will check module imports and configuration
- Some tests will fail (expected) if services aren't running

**Option B: Full Integration Test**

Start License Server:
```bash
python3 licensing/server/license_server.py
# Runs on http://localhost:5001
```

Start Web App:
```bash
python3 web_app.py
# Runs on http://localhost:8080
```

## Test Results Interpretation

### ✅ Expected Passes (Even Without Services)
- Module imports (except Stripe if not installed)
- Payment configuration
- Usage tracker initialization
- User storage initialization
- Usage storage database

### ⚠️ Expected Warnings (Normal)
- Stripe keys not set (if testing without Stripe)
- License server not running (if not started)
- Web app not running (if not started)

### ❌ Fixes Needed
- Install Stripe: `pip3 install stripe`
- Fix SQL syntax errors (if any)
- Start services for full integration test

## Manual Testing

### 1. Test Payment Configuration
```python
from redline.payment.config import PaymentConfig

# Check packages
packages = PaymentConfig.HOUR_PACKAGES
print(packages)

# Test calculations
hours = PaymentConfig.calculate_hours_from_price(25)
print(f"$25 = {hours} hours")
```

### 2. Test Usage Tracker
```python
from redline.auth.usage_tracker import usage_tracker

# Create session
session_id = usage_tracker.start_session("TEST-LICENSE-KEY")
print(f"Session: {session_id}")

# Update session
usage_tracker.update_session(session_id)

# End session
usage_tracker.end_session(session_id)
```

### 3. Test User Storage
```python
from redline.storage.user_storage import user_storage

# Initialize storage
user_storage.initialize_user_storage("TEST-LICENSE-KEY")

# List files
files = user_storage.list_files("TEST-LICENSE-KEY")
print(f"Files: {len(files)}")

# Get stats
stats = user_storage.get_storage_stats("TEST-LICENSE-KEY")
print(stats)
```

### 4. Test Payment Routes (Requires Running Web App)
```bash
# Get packages
curl http://localhost:8080/payments/packages

# Check balance (requires license key)
curl "http://localhost:8080/payments/balance?license_key=YOUR-KEY"
```

## Test Checklist

- [ ] Install Stripe: `pip3 install stripe`
- [ ] Run test suite: `python3 test_payment_integration.py`
- [ ] Check module imports pass
- [ ] Check payment configuration loads
- [ ] Check usage tracker works
- [ ] Check user storage works
- [ ] (Optional) Start license server and test integration
- [ ] (Optional) Start web app and test API endpoints

## Common Issues

### Stripe Not Installed
```bash
pip3 install stripe
```

### License Server Not Running
```bash
python3 licensing/server/license_server.py
```

### Web App Not Running
```bash
python3 web_app.py
```

### SQL Syntax Errors
- DuckDB uses `INTERVAL ? DAYS` not `INTERVAL ? DAY`
- Fixed in latest code

## Next Steps After Testing

1. **Set up Stripe account** (for production)
2. **Configure environment variables**
3. **Test with real Stripe test keys**
4. **Deploy to staging environment**
5. **Test end-to-end payment flow**

