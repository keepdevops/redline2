# License Validation Fix

## Problem
License validation is failing because it's trying to connect to an external license server (`http://localhost:5001`) that doesn't exist.

## Solution
I've updated the system to use Supabase for license validation instead of the external license server.

## Quick Fix Options

### Option 1: Use Supabase (Recommended - Production Ready)

1. **Set up Supabase** (if not done already):
   ```bash
   # Set environment variables
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your-anon-or-service-key"
   ```

2. **Use user ID or email as license key**:
   - License keys can now be:
     - Supabase user UUIDs (e.g., `550e8400-e29b-41d4-a716-446655440000`)
     - Email addresses (e.g., `user@example.com`)

3. **The system will automatically**:
   - Look up the user in Supabase
   - Check their remaining hours from `user_subscriptions` table
   - Allow/deny access based on hours

### Option 2: Development Mode (Quick Fix)

For local development without Supabase:

```bash
# Allow access without license validation
export REQUIRE_LICENSE_VALIDATION=false
export REQUIRE_SUPABASE=false
export ENFORCE_PAYMENT=false
```

This will allow all requests through (fail-open mode).

### Option 3: Disable License Server Requirement

```bash
# Don't require the license server to be running
export REQUIRE_LICENSE_SERVER=false
```

This makes the old system fail-open if the license server is unavailable.

## Updated Files

1. **`auth/supabase_access_control.py`** - New Supabase-based access control
2. **`web/utils/license_helpers.py`** - Updated license validation helpers
3. **`web/utils/download_helpers.py`** - Updated to use new validation

## How It Works Now

### License Key Format
- **User UUID**: `550e8400-e29b-41d4-a716-446655440000`
- **Email**: `user@example.com`
- **Custom keys**: Can be added via mapping table (future enhancement)

### Validation Flow
1. Extract license key from request (header, query param, or body)
2. Map license key to Supabase user ID
3. Check `user_subscriptions` table for remaining hours
4. Allow/deny based on hours and `ENFORCE_PAYMENT` setting

### Development Mode
If Supabase is not configured or `REQUIRE_SUPABASE=false`:
- System fails open (allows access)
- Logs warnings
- Returns `development_mode: true` in license info

## Testing

### Test with Supabase
```python
from redline.web.utils.license_helpers import validate_license_key

# Use a Supabase user ID or email
license_key = "user@example.com"  # or UUID
error = validate_license_key(license_key)
if error:
    print(f"Validation failed: {error}")
else:
    print("License valid!")
```

### Test in Development Mode
```bash
# Set environment variables
export REQUIRE_SUPABASE=false
export ENFORCE_PAYMENT=false

# Start your app
# All requests will be allowed
```

## Migration from Old System

If you have existing license keys from the old system:

1. **Map old keys to Supabase users**:
   - Create a mapping table in Supabase (optional)
   - Or migrate users to use their Supabase user IDs/emails

2. **Update client code**:
   - Change license keys to Supabase user IDs or emails
   - Or implement a lookup service

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_URL` | - | Supabase project URL |
| `SUPABASE_KEY` | - | Supabase anon/service key |
| `REQUIRE_SUPABASE` | `false` | Require Supabase (fail-closed if not available) |
| `ENFORCE_PAYMENT` | `true` | Enforce hour checking |
| `REQUIRE_LICENSE_VALIDATION` | `false` | Require license validation (fail-closed) |
| `REQUIRE_LICENSE_SERVER` | `false` | Require old license server (for backward compat) |

## Next Steps

1. ✅ **Immediate**: Set `REQUIRE_SUPABASE=false` for development
2. ⏭️ **Short-term**: Set up Supabase and use user IDs/emails as license keys
3. ⏭️ **Long-term**: Migrate all users to Supabase-based authentication

## Troubleshooting

### "License validation unavailable"
- **Cause**: Supabase not configured and `REQUIRE_SUPABASE=true`
- **Fix**: Set `REQUIRE_SUPABASE=false` or configure Supabase

### "Invalid license key"
- **Cause**: License key doesn't map to a Supabase user
- **Fix**: Use a valid Supabase user ID or email

### "No hours remaining"
- **Cause**: User has 0 hours in `user_subscriptions` table
- **Fix**: Add hours to user's subscription or set `ENFORCE_PAYMENT=false`

### Connection errors
- **Cause**: Can't connect to Supabase
- **Fix**: Check `SUPABASE_URL` and `SUPABASE_KEY`, verify network access
