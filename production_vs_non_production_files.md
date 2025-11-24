# Production vs Non-Production Files Analysis

## Production Files (Used in Web Application)

### Core Application Files
- `web_app.py` - Main Flask application entry point
- `gunicorn.conf.py` - Gunicorn configuration for production
- `entrypoint_web.sh` - Docker entrypoint script
- `entrypoint.sh` - Main Docker entrypoint

### Web Application Routes (`redline/web/routes/`)
All files in `redline/web/routes/` are used in production:
- `main.py`, `main_index.py`, `main_auth.py` - Main routes
- `api.py`, `api_*.py` - API endpoints
- `data_*.py` - Data management routes
- `analysis_*.py` - Analysis routes
- `converter_*.py` - File conversion routes
- `download_*.py` - Download routes
- `settings_*.py` - Settings routes
- `tasks_*.py` - Background tasks
- `payments_*.py` - Payment processing
- `api_keys_*.py` - API key management
- `user_data.py` - User data storage
- `ml.py`, `ml_tab.py` - ML features

### Web Application Utilities (`redline/web/utils/`)
- `api_helpers.py`
- `converter_helpers.py`
- `data_helpers.py`
- `download_helpers.py`
- `file_loading.py`
- `security_helpers.py`
- `analysis_helpers.py`

### Web Templates (`redline/web/templates/`)
- All `.html` files in `redline/web/templates/`

### Web Static Files (`redline/web/static/`)
- All `.js`, `.css` files in `redline/web/static/`

### Core Modules Used by Web App
- `redline/core/format_converter.py` - Format conversion
- `redline/core/data_loader.py` - Data loading
- `redline/core/data_validator.py` - Data validation
- `redline/core/data_cleaner.py` - Data cleaning
- `redline/core/data_standardizer.py` - Data standardization
- `redline/core/data_loading_service.py` - Data loading service
- `redline/core/schema.py` - Data schema definitions

### Database Modules Used by Web App
- `redline/database/connector.py` - Database connector
- `redline/database/operations.py` - Database operations
- `redline/database/query_builder.py` - Query builder
- `redline/database/usage_storage.py` - Usage tracking

### Downloaders Used by Web App
- `redline/downloaders/base_downloader.py` - Base class
- `redline/downloaders/yahoo_downloader.py`
- `redline/downloaders/stooq_downloader.py`
- `redline/downloaders/alpha_vantage_downloader.py`
- `redline/downloaders/finnhub_downloader.py`
- `redline/downloaders/massive_downloader.py`
- `redline/downloaders/multi_source.py`
- `redline/downloaders/generic_api_downloader.py`
- `redline/downloaders/csv_downloader.py`
- `redline/downloaders/bulk_downloader.py`

### Authentication & Payment
- `redline/auth/access_control.py`
- `redline/auth/usage_tracker.py`
- `redline/payment/config.py`
- `redline/storage/user_storage.py`

### Background Tasks
- `redline/background/task_manager.py`
- `redline/background/tasks.py`

### Utilities Used by Web App
- `redline/utils/config.py`
- `redline/utils/error_handling.py`
- `redline/utils/logging_mixin.py`
- `redline/utils/logging_config.py`
- `redline/utils/security_validator.py`
- `redline/utils/file_ops.py`
- `redline/utils/config_paths.py`

### Updates
- `redline/updates/update_checker.py`
- `redline/updates/update_installer.py`

### Licensing
- `licensing/client/license_validator.py`
- `licensing/server/license_server.py`

---

## Non-Production Files (NOT Used in Web Application)

### Legacy/Old Files (`old/` directory)
- `old/analysis.py.original`
- `old/api.py.original`
- `old/api.py.refactored`
- `old/data_module_shared.py.original`
- `old/data.py.old`
- `old/data.py.old_monolithic`
- `old/comprehensive_financial_downloader.py`
- `old/multi_source_downloader.py`
- `old/stooq_historical_data_downloader.py`
- `old/universal_gui_downloader.py`
- `old/financial_data_formats_guide.py`

### Standalone Scripts (Root Level)
- `main.py` - GUI application (not web)
- `bulk_stock_downloader.py` - Standalone script
- `chartoasis_stooq_downloader.py` - Standalone script
- `comprehensive_financial_downloader.py` - Standalone script
- `multi_source_downloader.py` - Standalone script
- `stooq_data_downloader.py` - Standalone script
- `stooq_gui_downloader.py` - Standalone script
- `stooq_historical_data_downloader.py` - Standalone script
- `stooq_historical_downloader.py` - Standalone script
- `stooq_manual_downloader.py` - Standalone script
- `universal_gui_downloader.py` - Standalone script
- `yahoo_data_downloader.py` - Standalone script

### GUI Application Files (Not Web)
- `redline/gui/*.py` - All GUI application files (Tkinter-based)
  - `main_window.py`
  - `data_tab.py`
  - `analysis_tab.py`
  - `converter_tab.py`
  - `download_tab.py`
  - `settings_tab.py`
  - All files in `redline/gui/` directory

### CLI Tools (Not Web)
- `redline/cli/*.py` - Command-line interface tools

### Test Files
- `test/*.py` - Test files
- `tests/*.py` - Test files
- `redline/tests/*.py` - Test files
- `test_*.py` - Test scripts in root
- `run_gui_tests.py`

### Legacy Shared Modules (May be used by GUI, not web)
- `redline/core/data_format_converter_shared.py` - Legacy version
- `redline/core/data_loader_shared.py` - Legacy version
- `redline/core/data_adapter_shared.py` - Legacy version
- `redline/core/data_processing_shared.py` - Legacy version
- `redline/core/data_standardizer_shared.py` - Legacy version
- `redline/database/connector_shared.py` - Legacy version
- `redline/database/query_builder_shared.py` - Legacy version
- `redline/gui/widgets/virtual_treeview_shared.py` - Legacy version
- `redline/gui/widgets/data_source_shared.py` - Legacy version

### Development/Utility Scripts
- `analyze_help_docs.py`
- `cleanup_conversion_files.py`
- `convert_to_stooq_format.py`
- `cost_calculator.py`
- `create_test_license.py`
- `enhanced_database_status.py`
- `log_viewer_route.py`
- `move_stooq_from_downloads.py`
- `open_stooq_manual.py`
- `setup_massive_api_key.py`
- `use_converted_data.py`
- `test_batch_merge.py`
- `test_column_editor.py`
- `test_conversion_merge.py`
- `test_financial_analysis.py`
- `test_form_labels.py`
- `test_massive_integration.py`
- `test_redline_app.py`

### Build/Install Scripts
- `build_*.bash`, `build_*.bat`
- `run_*.bash`
- `save_*.bash`
- `load_to_ubuntu.bash`
- `setup.py` - Package setup (used for installation, not runtime)
- `pyproject.toml` - Package configuration
- `MANIFEST.in` - Package manifest

### Configuration Templates
- `docker.env.template`
- `env.template`
- `data_config.ini.backup`

### Documentation Files
- All `.md` files (documentation)
- `API_DOCUMENTATION.md`
- `REDLINE_DEVELOPER_GUIDE.md`
- etc.

### Archive Files
- `archive/` directory - Old Dockerfiles and archived code
- `build/` directory - Build artifacts
- `dist/` directory - Distribution files
- `redline2/` directory - Old version

### Debug/Test HTML Files
- `debug_*.html` files
- `simple_data_tab.html`
- `standalone_test.html`

### Other Non-Production
- `web_app_safe.py` - Alternative web app (not used)
- `data_module_grid.py` - Legacy file
- `cloudflare-worker.js` - Cloudflare worker (separate service)
- `fly.toml`, `wrangler.toml` - Deployment configs (not runtime code)
- `CUSTOM_API_EXAMPLE.py` - Example file
- `CUSTOM_API_FORM_EXAMPLE.html` - Example file
- `DUPLICATION_CONSOLIDATION_DEMO.py` - Demo file

---

## Summary

### Production Files Count
- **Web Routes**: ~76 Python files
- **Web Utils**: ~7 Python files
- **Core Modules**: ~12 files
- **Database Modules**: ~8 files
- **Downloaders**: ~14 files
- **Templates**: ~27 HTML files
- **Static Files**: ~12 JS/CSS files
- **Total Production**: ~150+ files

### Non-Production Files Count
- **Legacy/Old**: ~11 files in `old/`
- **Standalone Scripts**: ~12 files
- **GUI Application**: ~27 files
- **Test Files**: ~10+ files
- **Development Scripts**: ~15 files
- **Build/Install Scripts**: ~20 files
- **Documentation**: ~100+ .md files
- **Total Non-Production**: ~200+ files

---

## Key Distinction

**Production (Web App)**:
- Entry point: `web_app.py`
- Runs via: Gunicorn or Flask dev server
- Serves: Web interface at port 8080
- Uses: Files in `redline/web/` and core modules

**Non-Production**:
- GUI application: `main.py` (Tkinter-based)
- Standalone scripts: Various downloader scripts
- Legacy code: Files in `old/` directory
- Test/Dev: Test files and development utilities

