# Production Files List - REDLINE Web Application

**Generated:** 2025-01-XX  
**Status:** Current production codebase

---

## 📦 Main Application Files

- `web_app.py` - Flask application entry point
- `gunicorn.conf.py` - Gunicorn configuration for production
- `entrypoint_web.sh` - Docker entrypoint script
- `entrypoint.sh` - Main Docker entrypoint

---

## 🌐 Web Routes (`redline/web/routes/`)

### Main Routes
- `main.py` - Main routes
- `main_index.py` - Index/dashboard routes
- `main_auth.py` - Authentication routes

### API Routes
- `api.py` - Main API blueprint
- `api_convert.py` - Format conversion API
- `api_data.py` - Data API endpoints
- `api_database.py` - Database API
- `api_files.py` - File operations API
- `api_files_list.py` - File listing API
- `api_files_operations.py` - File operations
- `api_font_colors.py` - Font/color customization API
- `api_keys.py` - API keys management
- `api_keys_management.py` - API keys CRUD
- `api_keys_sources.py` - API key sources
- `api_keys_testing.py` - API key testing
- `api_metadata.py` - Metadata API
- `api_themes.py` - Theme management API

### Data Routes
- `data_routes.py` - Main data routes
- `data_tab.py` - Data tab routes
- `data_browsing.py` - File browsing
- `data_filtering.py` - Data filtering
- `data_filtering_clean.py` - Data cleaning
- `data_filtering_filter.py` - Filter operations
- `data_loading.py` - Data loading
- `data_loading_single.py` - Single file loading
- `data_loading_multiple.py` - Multiple file loading

### Analysis Routes
- `analysis.py` - Main analysis routes
- `analysis_tab.py` - Analysis tab routes
- `analysis_basic.py` - Basic analysis
- `analysis_charts.py` - Chart generation
- `analysis_correlation.py` - Correlation analysis
- `analysis_export.py` - Export analysis
- `analysis_financial.py` - Financial analysis
- `analysis_ml.py` - ML analysis
- `analysis_sklearn.py` - Scikit-learn operations
- `analysis_statistical.py` - Statistical analysis
- `analysis_visualization.py` - Visualization

### ML Routes
- `ml.py` - ML blueprint
- `ml_tab.py` - ML tab routes

### Download Routes
- `download.py` - Main download routes
- `download_tab.py` - Download tab routes
- `download_single.py` - Single downloads
- `download_batch.py` - Batch downloads
- `download_history.py` - Download history
- `download_sources.py` - Download sources

### Converter Routes
- `converter.py` - Main converter routes
- `converter_tab.py` - Converter tab routes
- `converter_single.py` - Single file conversion
- `converter_batch.py` - Batch conversion
- `converter_browsing.py` - Converter browsing
- `converter_browsing_browse.py` - Browse files
- `converter_browsing_list.py` - List files
- `converter_cleanup.py` - Cleanup operations
- `converter_merge.py` - File merging

### Settings Routes
- `settings.py` - Main settings routes
- `settings_config.py` - Configuration settings
- `settings_database.py` - Database settings
- `settings_system.py` - System settings

### Tasks Routes
- `tasks.py` - Main tasks routes
- `tasks_status.py` - Task status
- `tasks_submit.py` - Task submission

### Payments Routes
- `payments.py` - Main payments routes
- `payments_tab.py` - Payments tab routes
- `payments_balance.py` - Balance management
- `payments_checkout.py` - Checkout processing
- `payments_webhook.py` - Stripe webhooks

### User Data Routes
- `user_data.py` - User data storage

**Total Routes:** 76 files

---

## 🛠️ Web Utilities (`redline/web/utils/`)

- `analysis_helpers.py` - Analysis helper functions
- `api_helpers.py` - API helper functions
- `converter_helpers.py` - Format conversion helpers
- `data_helpers.py` - Data manipulation helpers
- `download_helpers.py` - Download helpers
- `file_loading.py` - File loading utilities
- `security_helpers.py` - Security utilities

**Total Utilities:** 7 files

---

## ⚙️ Core Modules (`redline/core/`)

- `format_converter.py` - Format conversion engine
- `data_loader.py` - Data loading service
- `data_validator.py` - Data validation
- `data_cleaner.py` - Data cleaning
- `data_loading_service.py` - Data loading service
- `schema.py` - Data schema definitions

**Total Core Modules:** 6 files

---

## 💾 Database Modules (`redline/database/`)

- `connector.py` - Database connector
- `operations.py` - Database operations
- `optimized_connector.py` - Optimized connector
- `query_builder.py` - Query builder
- `usage_storage.py` - Usage tracking storage

**Total Database Modules:** 5 files

---

## ⬇️ Downloaders (`redline/downloaders/`)

- `base_downloader.py` - Base downloader class
- `alpha_vantage_downloader.py` - Alpha Vantage API
- `yahoo_downloader.py` - Yahoo Finance API
- `finnhub_downloader.py` - Finnhub API
- `stooq_downloader.py` - Stooq data
- `massive_downloader.py` - Massive.com API
- `massive_websocket.py` - Massive.com WebSocket
- `csv_downloader.py` - CSV downloader
- `bulk_downloader.py` - Bulk downloads
- `generic_api_downloader.py` - Generic API downloader
- `multi_source.py` - Multi-source downloader

**Total Downloaders:** 11 files

---

## 📄 Templates (`redline/web/templates/`)

- `base.html` - Base template
- `index.html` - Home page
- `dashboard.html` - Dashboard
- `data_tab.html` - Data tab
- `analysis_tab.html` - Analysis tab
- `ml_tab.html` - ML tab
- `download_tab.html` - Download tab
- `converter_tab.html` - Converter tab
- `settings_tab.html` - Settings tab
- `tasks_tab.html` - Tasks tab
- `payment_tab.html` - Payment tab
- `api_keys_page.html` - API keys page
- `file_browser.html` - File browser
- `help.html` - Help page
- `register.html` - Registration
- `payment_success.html` - Payment success
- `404.html` - Not found error
- `500.html` - Server error

**Total Templates:** 18 files

---

## 🎨 Static Files (`redline/web/static/`)

### CSS Files
- `css/main.css` / `css/main.min.css`
- `css/themes.css` / `css/themes.min.css`
- `css/color-customizer.css` / `css/color-customizer.min.css`
- `css/virtual-scroll.css` / `css/virtual-scroll.min.css`

### JavaScript Files
- `js/main.js` / `js/main.min.js`
- `js/payments.js`
- `js/balance_tracker.js`
- `js/color-customizer.js` / `js/color-customizer.min.js`
- `js/date-formatter.js`
- `js/virtual-scroll.js` / `js/virtual-scroll.min.js`

### JavaScript Modules (`js/modules/`)
- `button-handler.js`
- `data-display.js`
- `data-loader.js`
- `data-tab-controller.js`
- `file-loader.js`
- `file-selector.js`

**Total Static Files:** ~20 files

---

## 🔧 Supporting Modules

- `redline/auth/access_control.py` - Access control
- `redline/auth/usage_tracker.py` - Usage tracking
- `redline/background/task_manager.py` - Background tasks
- `redline/payment/config.py` - Payment configuration
- `redline/storage/user_storage.py` - User storage
- `redline/utils/json_utils.py` - JSON utilities
- `redline/utils/config_paths.py` - Config path utilities
- `redline/__version__.py` - Version information

**Total Supporting Modules:** 8 files

---

## 📊 Summary

| Category | Count |
|----------|-------|
| Main Application Files | 4 |
| Web Routes | 76 |
| Web Utilities | 7 |
| Core Modules | 6 |
| Database Modules | 5 |
| Downloaders | 11 |
| Templates | 18 |
| Supporting Modules | 8 |
| Static Files (CSS/JS) | ~20 |
| **TOTAL** | **~155 Python files + ~20 static files** |

---

## ✅ Notes

- All files listed are actively used in production
- Files in `old/` directory are NOT production files
- Test files (`test_*.py`) are NOT production files
- GUI application files (`redline/gui/`) are NOT used by web app
- Standalone scripts are NOT production files
- Documentation files (`.md`) are NOT production code

## 🔄 Latest Consolidation Changes (2025-01)

### Consolidation 1: `clean_dataframe_columns()`
- **Consolidated to:** `redline/web/utils/data_helpers.py`
- **Removed from:** `redline/web/utils/analysis_helpers.py`
- **Updated imports in:** 6 route files
- **Lines saved:** ~28 lines

### Consolidation 2: Rate Limiting
- **Consolidated to:** `redline/downloaders/base_downloader.py`
- **Removed from:** 4 child downloader classes
- **Lines saved:** ~26 lines

### Consolidation 3: `_load_data_file()`
- **Consolidated to:** `redline/web/utils/analysis_helpers.py`
- **Removed from:** `analysis_sklearn.py` and `analysis_visualization.py`
- **Lines saved:** ~97 lines

**Total consolidation savings:** ~151 lines of duplicate code removed

---

## 🔍 Verification

To verify production files, check:
1. `web_app.py` - Lists all imported blueprints
2. Blueprint files - Import utilities and core modules
3. Import chains - Trace dependencies from entry point

---

**Last Updated:** 2025-01-XX  
**Status:** Current and verified

