# Production Files Refactoring Status

## ⚠️ Files Over 200 LOC That Need Refactoring

### HIGH PRIORITY (Critical Production Routes)

1. **`redline/web/routes/analysis.py`** - **669 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 401)
   - **Blueprint**: `analysis_bp`
   - **Routes**: Statistical analysis, correlation analysis, financial analysis
   - **Action**: Split into `analysis_basic.py`, `analysis_statistical.py`, `analysis_correlation.py`, `analysis_financial.py`
   - **Target**: 4 files of ~167 LOC each

2. **`redline/web/routes/payments.py`** - **600 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 407)
   - **Blueprint**: `payments_bp`
   - **Routes**: Stripe payments, balance, history, webhooks
   - **Action**: Split into `payments_stripe.py`, `payments_balance.py`, `payments_history.py`, `payments_webhooks.py`
   - **Target**: 4 files of ~150 LOC each

### MEDIUM PRIORITY

3. **`redline/database/optimized_connector.py`** - **563 LOC** ⚠️
   - **Status**: Used by production routes
   - **Purpose**: Database connector with connection pooling
   - **Action**: Split into `connector_core.py`, `connector_pool.py`, `connector_cache.py`
   - **Target**: 3 files of ~188 LOC each

4. **`redline/web/routes/api_keys.py`** - **427 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 406)
   - **Blueprint**: `api_keys_bp`
   - **Routes**: API key management, custom API configuration
   - **Action**: Split into `api_keys_management.py`, `api_keys_custom.py`
   - **Target**: 2 files of ~214 LOC each

5. **`redline/web/routes/settings.py`** - **425 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 404)
   - **Blueprint**: `settings_bp`
   - **Routes**: Settings management, log viewing
   - **Action**: Split into `settings_management.py`, `settings_logs.py`
   - **Target**: 2 files of ~213 LOC each

6. **`redline/web/routes/tasks.py`** - **323 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 405)
   - **Blueprint**: `tasks_bp`
   - **Routes**: Background task management
   - **Action**: Split into `tasks_list.py`, `tasks_management.py`
   - **Target**: 2 files of ~162 LOC each

7. **`redline/web/routes/main.py`** - **268 LOC** ⚠️
   - **Status**: Used in production (`web_app.py` line 398)
   - **Blueprint**: `main_bp`
   - **Routes**: Main routes, registration, dashboard
   - **Action**: Split into `main_routes.py`, `main_registration.py`
   - **Target**: 2 files of ~134 LOC each

### LOW PRIORITY (Critical Entry Point)

8. **`web_app.py`** - **491 LOC** ⚠️
   - **Status**: **CRITICAL** - Main entry point
   - **Usage**: Dockerfile uses `gunicorn ... web_app:create_app()`
   - **Action**: **DO NOT REFACTOR** - Critical entry point, keep as single file
   - **Note**: This is the Flask application factory - refactoring could break deployment

---

## ✅ Sub-Modules Over 200 LOC (Lower Priority)

These are sub-modules used by registry files. They're close to 200 LOC but could be split further:

1. **`redline/web/routes/data_loading.py`** - **351 LOC** ⚠️
   - Used by: `data_routes.py`
   - **Action**: Split into `data_loading_single.py`, `data_loading_multiple.py`, `data_loading_upload.py`
   - **Target**: 3 files of ~117 LOC each

2. **`redline/web/routes/api_files.py`** - **280 LOC** ⚠️
   - Used by: `api.py`
   - **Action**: Split into `api_files_list.py`, `api_files_upload.py`, `api_files_delete.py`
   - **Target**: 3 files of ~93 LOC each

3. **`redline/web/routes/data_filtering.py`** - **269 LOC** ⚠️
   - Used by: `data_routes.py`
   - **Action**: Split into `data_filtering_filter.py`, `data_filtering_export.py`, `data_filtering_clean.py`
   - **Target**: 3 files of ~90 LOC each

4. **`redline/web/routes/converter_browsing.py`** - **235 LOC** ⚠️
   - Used by: `converter.py`
   - **Action**: Split into `converter_browsing_list.py`, `converter_browsing_preview.py`
   - **Target**: 2 files of ~118 LOC each

5. **`redline/web/routes/download_batch.py`** - **231 LOC** ⚠️
   - Used by: `download.py`
   - **Action**: Split into `download_batch_core.py`, `download_batch_helpers.py`
   - **Target**: 2 files of ~116 LOC each

6. **`redline/web/routes/api_data.py`** - **210 LOC** ⚠️
   - Used by: `api.py`
   - **Action**: Minor refactoring - extract helper functions
   - **Target**: 1 file of ~180 LOC + helpers

---

## 📊 Summary

### Production Files Needing Refactoring:
- **HIGH Priority**: 2 files (1,269 LOC)
- **MEDIUM Priority**: 5 files (2,006 LOC)
- **LOW Priority**: 1 file (491 LOC) - **DO NOT REFACTOR**
- **Sub-Modules**: 6 files (1,576 LOC)

### Total LOC to Refactor: ~4,851 LOC

### Recommended Order:
1. ✅ `analysis.py` (669 LOC) - Most critical route
2. ✅ `payments.py` (600 LOC) - Payment processing
3. ✅ `optimized_connector.py` (563 LOC) - Database layer
4. ✅ `api_keys.py` (427 LOC) - API management
5. ✅ `settings.py` (425 LOC) - Settings management
6. ✅ `tasks.py` (323 LOC) - Task management
7. ✅ `main.py` (268 LOC) - Main routes
8. ⚠️ Sub-modules (as needed)

---

## ✅ Already Refactored (Registry Files)

These files are now registries (< 30 LOC each):
- ✅ `api.py` - 27 LOC (registry)
- ✅ `data_routes.py` - 25 LOC (registry)
- ✅ `converter.py` - 27 LOC (registry)
- ✅ `download.py` - 22 LOC (registry)

