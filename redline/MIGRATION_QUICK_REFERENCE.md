# Migration Quick Reference Guide

## Quick Status Check

```bash
# Run verification script
python3 verify_migration.py
```

**Expected Output**: ✅ No migration issues found

---

## Authentication Changes

### Before (License Key)
```javascript
// Frontend
const licenseKey = localStorage.getItem('variosync_license_key');
headers: { 'X-License-Key': licenseKey }
```

```python
# Backend
license_key = extract_license_key()
error = validate_license_key(license_key)
```

### After (JWT Token)
```javascript
// Frontend
const authToken = localStorage.getItem('variosync_auth_token');
headers: { 'Authorization': `Bearer ${authToken}` }
```

```python
# Backend
@auth_manager.require_auth
def route():
    user_id = g.user_id  # Set by decorator
```

---

## Key Files Modified

### Frontend (9 files)
- `web/templates/payment_success.html`
- `web/templates/tasks_tab.html`
- `web/templates/analysis_tab.html`
- `web/templates/ml_tab.html`
- `web/templates/converter_tab.html`
- `web/templates/data_tab_tkinter_style.html`
- `web/templates/data_tab_multi_file.html`
- `web/templates/api_keys_page.html`

### Backend Routes (15 files)
- `web/routes/download_single.py`
- `web/routes/download_batch.py`
- `web/routes/api_keys_testing.py`
- `web/routes/api_keys_management.py`
- `web/routes/data_loading_single.py`
- `web/routes/data_loading_multiple.py`
- `web/routes/api_files_operations.py`
- `web/routes/analysis_tab.py`
- `web/routes/analysis_sklearn.py`
- `web/routes/analysis_ml.py`
- `web/routes/converter_single.py`
- `web/routes/converter_batch.py`
- `web/routes/converter_merge.py`

### Core Systems (3 files)
- `web/utils/download_helpers.py` - JWT helpers added
- `database/usage_storage.py` - user_id support added
- `storage/user_storage.py` - user_id path hashing

---

## Environment Variables Required

```bash
# Supabase Auth
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SUPABASE_JWT_SECRET=...

# Stripe
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
STRIPE_WEBHOOK_SECRET=...
STRIPE_PRICE_ID_METERED=...

# Storage (optional)
USE_S3_STORAGE=false
S3_BUCKET=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_ENDPOINT_URL=...
```

---

## Common Tasks

### Check Authentication Status
```python
from flask import g
user_id = g.user_id  # Available after @require_auth decorator
```

### Protect a Route
```python
from redline.auth.supabase_auth import auth_manager

@route('/api/endpoint')
@auth_manager.require_auth
def my_route():
    user_id = g.user_id
    # ... use user_id
```

### Use Storage System
```python
from redline.storage.user_storage import user_storage

# Save file
user_storage.save_file(user_id, file_data, filename)

# List files
files = user_storage.list_files(user_id)
```

### Log Usage
```python
from redline.database.usage_storage import usage_storage

# Log session start
usage_storage.log_session_start(session_id, user_id)

# Log hour deduction
usage_storage.log_hour_deduction(user_id, hours)
```

---

## Deprecated Code (Do Not Use)

### ❌ Deprecated Functions
- `extract_license_key()` - Use `extract_jwt_token()` instead
- `validate_license_key()` - Use `verify_jwt_auth()` instead

### ❌ Deprecated Endpoints (Return 410 Gone)
- `/api/register` - Use `/auth/signup` instead
- `/payments/create-checkout` - Use `/payments/create-subscription-checkout` instead
- `/payments/success` - Use `/payments/subscription-success` instead
- `/payments/packages` - No replacement (subscription model)

---

## Troubleshooting

### Authentication Fails
1. Check JWT token in `localStorage`: `variosync_auth_token`
2. Verify token format: `Authorization: Bearer <token>`
3. Check token expiration
4. Verify `SUPABASE_JWT_SECRET` configured

### Storage Issues
1. Verify `user_id` passed to storage methods
2. Check path hashing (should use `user_id`)
3. Verify S3 credentials if using cloud storage

### Database Issues
1. Verify `user_id` columns exist in tables
2. Check indexes on `user_id` columns
3. Verify queries use `user_id` not `license_key`

---

## Migration Verification

### Automated Check
```bash
python3 verify_migration.py
```

### Manual Checks
1. ✅ No `license_key` in routes
2. ✅ All routes use `@require_auth`
3. ✅ Frontend uses `authToken`
4. ✅ Database has `user_id` columns
5. ✅ Storage uses `user_id` for paths

---

## Support

### Documentation
- `TESTING_PLAN.md` - Comprehensive testing guide
- `PHASE6_CLEANUP_PLAN.md` - Cleanup procedures
- `MIGRATION_COMPLETION_REPORT.md` - Full migration report

### Verification
- `verify_migration.py` - Automated verification script

---

**Last Updated**: [Current Date]  
**Migration Status**: ✅ Complete
