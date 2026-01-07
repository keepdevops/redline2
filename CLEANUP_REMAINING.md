# Remaining License Key Cleanup

This document lists files that still contain license key references and need cleanup.

**Status**: Updated 2026-01-07

---

## ✅ COMPLETED

### Templates
- ✅ `redline/web/templates/base.html` - Removed license key code, added JWT auth
- ✅ `redline/web/templates/register.html` - Redirects to `/auth/signup`
- ✅ `redline/web/templates/login.html` - NEW: JWT login page
- ✅ `redline/web/templates/signup.html` - NEW: JWT signup page

### JavaScript
- ✅ `redline/web/static/js/main.js` - Updated to JWT authentication
- ✅ `redline/web/static/js/payments.js` - Updated to Stripe subscriptions
- ✅ `redline/web/static/js/balance_tracker.js` - Updated to subscription tracker

### Python Routes
- ✅ `redline/web/routes/payments_*.py` - All payment routes updated for Stripe
- ✅ `redline/web/routes/main_auth.py` - Updated for Supabase signup
- ✅ `redline/web/routes/data_loading_*.py` - All use `g.user_id` now

---

## ⚠️ NEEDS CLEANUP

### Priority 1: User-Facing Templates (Update or Delete)

#### `redline/web/templates/payment_tab.html`
- **Issue**: Old hour balance UI
- **Action**: Update to show subscription status instead
- **Priority**: HIGH

#### `redline/web/templates/payment_success.html`
- **Issue**: Old payment success page (hour purchases)
- **Action**: Redirect to `/payments/subscription-success` or update for subscriptions
- **Priority**: HIGH

#### `redline/web/templates/dashboard.html`
- **Issue**: May display license key or hour balance
- **Action**: Update to show subscription status and user info
- **Priority**: MEDIUM

### Priority 2: Data Display Templates (Check & Update if needed)

#### `redline/web/templates/data_tab.html`
- **Issue**: May reference license key in header/forms
- **Action**: Check and remove if present
- **Priority**: MEDIUM

#### `redline/web/templates/download_tab.html`
- **Issue**: May require license key input
- **Action**: Remove license key fields
- **Priority**: MEDIUM

#### `redline/web/templates/converter_tab.html`
- **Issue**: May require license key input
- **Action**: Remove license key fields
- **Priority**: MEDIUM

#### `redline/web/templates/analysis_tab.html`
- **Issue**: May reference license key
- **Action**: Check and remove if present
- **Priority**: LOW

#### `redline/web/templates/ml_tab.html`
- **Issue**: May reference license key
- **Action**: Check and remove if present
- **Priority**: LOW

#### `redline/web/templates/tasks_tab.html`
- **Issue**: May reference license key
- **Action**: Check and remove if present
- **Priority**: LOW

### Priority 3: Multi-File Data Templates (Likely Duplicates - Can Delete)

#### `redline/web/templates/data_tab_multi_file.html`
- **Action**: Likely old version, check if still used, then delete
- **Priority**: LOW

#### `redline/web/templates/data_tab_tkinter_style.html`
- **Action**: Old version, can probably delete
- **Priority**: LOW

### Priority 4: Utility Templates

#### `redline/web/templates/help.html`
- **Issue**: May reference license key registration
- **Action**: Update help text to reference JWT signup
- **Priority**: LOW

#### `redline/web/templates/api_keys_page.html`
- **Issue**: May confuse API keys with license keys
- **Action**: Clarify that these are API keys for integrations, not license keys
- **Priority**: LOW

---

## 🗑️ CAN DELETE (Test Files)

### Test/Debug Files
- ✅ **DELETE**: `redline/web/static/test_browser_license_key.html` - Old test file
- ✅ **DELETE**: `redline/web/static/test_button_clicks.html` - Old test file

---

## 🔍 NEEDS INVESTIGATION

### JavaScript Modules

#### `redline/web/static/js/modules/file-loader.js`
- **Issue**: May use `X-License-Key` header
- **Action**: Update to use `Authorization: Bearer {token}`
- **Priority**: HIGH (if actively used)

#### `redline/web/static/js/modules/data-loader.js`
- **Issue**: May use `X-License-Key` header
- **Action**: Update to use `Authorization: Bearer {token}`
- **Priority**: HIGH (if actively used)

#### `redline/web/static/js/virtual-scroll.js`
- **Issue**: Unknown if it uses license keys
- **Action**: Check and update if needed
- **Priority**: LOW

### Python Backend (Old Auth System - CAN DELETE)

#### `redline/auth/access_control.py`
- **Action**: Old license validation - DELETE or mark deprecated
- **Priority**: MEDIUM

#### `redline/auth/hour_deduction.py`
- **Action**: Old hour tracking - DELETE (replaced by Stripe metered billing)
- **Priority**: MEDIUM

#### `redline/auth/usage_tracker.py`
- **Action**: Old usage tracking - DELETE (now handled by Stripe)
- **Priority**: MEDIUM

#### `redline/database/usage_storage.py`
- **Action**: Old usage database - DELETE if only for license system
- **Priority**: LOW

#### `redline/storage/user_storage.py`
- **Action**: Check if used for JWT users or just license keys
- **Priority**: LOW

#### `redline/web/utils/download_helpers.py`
- **Action**: Check if uses license validation
- **Priority**: MEDIUM

### Licensing Server (ENTIRE DIRECTORY CAN DELETE)

#### `licensing/client/license_validator.py`
- **Action**: DELETE - Old license validation client
- **Priority**: LOW (not in active code path)

#### `licensing/server/license_server.py`
- **Action**: DELETE - Old license server
- **Priority**: LOW (separate service, not needed)

### Configuration

#### `cloudflare-worker.js`
- **Issue**: May use license keys for edge validation
- **Action**: Update to use JWT validation or disable
- **Priority**: LOW (if not deployed)

---

## 📝 RECOMMENDED CLEANUP ORDER

1. **High Priority (User-Facing)**:
   - Update `payment_tab.html` to subscription UI
   - Update `payment_success.html` for subscriptions
   - Update `file-loader.js` and `data-loader.js` for JWT

2. **Medium Priority (Backend)**:
   - Delete old auth modules: `access_control.py`, `hour_deduction.py`, `usage_tracker.py`
   - Check and update `dashboard.html`
   - Check data templates: `data_tab.html`, `download_tab.html`, `converter_tab.html`

3. **Low Priority (Cleanup)**:
   - Delete test files
   - Delete old `licensing/` directory
   - Update help documentation
   - Delete duplicate data templates

---

## 🎯 QUICK WINS (Do These Now)

```bash
# Delete test files
rm redline/web/static/test_browser_license_key.html
rm redline/web/static/test_button_clicks.html

# Delete old licensing directory
rm -rf licensing/

# Delete old duplicate templates (after verifying not used)
# rm redline/web/templates/data_tab_multi_file.html
# rm redline/web/templates/data_tab_tkinter_style.html
```

---

**Next Steps**: Focus on Priority 1 items to ensure user-facing pages work correctly with new JWT authentication.
