# Python Files Over 200 LOC

## Summary

**Total files over 200 LOC**: 75 files  
**Largest file**: `data_module_shared.py` (3,776 LOC)  
**Target**: All files ≤200 LOC per code quality requirement

## Files Over 200 LOC (Sorted by Size)

### Critical (>1000 LOC) - Priority 1

| LOC  | File | Status |
|------|------|--------|
| 3776 | `./data_module_shared.py` | ❌ **CRITICAL** - Needs major refactoring |
| 1441 | `./redline/web/routes/data.py` | ❌ **CRITICAL** - Needs refactoring |
| 952  | `./redline/web/routes/api.py` | ❌ **HIGH** - Needs refactoring |

### High Priority (500-1000 LOC) - Priority 2

| LOC  | File | Status |
|------|------|--------|
| 881  | `./redline/gui/converter_tab.py` | ❌ Needs refactoring |
| 850  | `./comprehensive_financial_downloader.py` | ⚠️ Standalone script |
| 830  | `./redline/gui/widgets/filter_dialog.py` | ❌ Needs refactoring |
| 813  | `./redline/web/routes/data_routes.py` | ❌ Needs refactoring |
| 766  | `./redline/gui/main_window.py` | ❌ Needs refactoring |
| 757  | `./redline/gui/download_tab.py` | ❌ Needs refactoring |
| 687  | `./redline/web/routes/converter.py` | ❌ Needs refactoring |
| 626  | `./financial_data_formats_guide.py` | ⚠️ Standalone script |
| 605  | `./redline/web/routes/download.py` | ❌ Needs refactoring |
| 563  | `./redline/database/optimized_connector.py` | ⚠️ Database core - acceptable |
| 540  | `./universal_gui_downloader.py` | ⚠️ Standalone script |
| 519  | `./stooq_historical_data_downloader.py` | ⚠️ Standalone script |
| 513  | `./multi_source_downloader.py` | ⚠️ Standalone script |
| 491  | `./web_app.py` | ⚠️ Main app entry - acceptable |
| 484  | `./redline/web/routes/analysis.py` | ❌ Needs refactoring |
| 463  | `./redline/core/format_converter.py` | ⚠️ Core functionality - acceptable |
| 454  | `./redline/web/routes/payments.py` | ⚠️ Payment routes - acceptable |
| 433  | `./redline/background/tasks.py` | ⚠️ Background tasks - acceptable |
| 430  | `./licensing/server/license_server.py` | ⚠️ License server - acceptable |
| 428  | `./redline/storage/user_storage.py` | ⚠️ Storage module - acceptable |
| 427  | `./redline/web/routes/api_keys.py` | ⚠️ API routes - acceptable |
| 425  | `./redline/web/routes/settings.py` | ⚠️ Settings routes - acceptable |
| 423  | `./redline/gui/utils/file_operations.py` | ⚠️ File utils - acceptable |
| 420  | `./stooq_historical_downloader.py` | ⚠️ Standalone script |
| 394  | `./bulk_stock_downloader.py` | ⚠️ Standalone script |
| 392  | `./redline/utils/file_ops.py` | ⚠️ Utils - acceptable |
| 383  | `./stooq_gui_downloader.py` | ⚠️ Standalone script |
| 372  | `./redline/database/connector.py` | ⚠️ Database core - acceptable |
| 369  | `./redline/web/utils/file_loading.py` | ⚠️ Web utils - acceptable |
| 363  | `./redline/cli/analyze.py` | ⚠️ CLI tool - acceptable |
| 356  | `./redline/core/data_validator.py` | ⚠️ Core functionality - acceptable |
| 356  | `./chartoasis_stooq_downloader.py` | ⚠️ Standalone script |
| 352  | `./redline/core/data_loading_service.py` | ⚠️ Core service - acceptable |
| 343  | `./redline/database/usage_storage.py` | ⚠️ Database module - acceptable |
| 335  | `./redline/downloaders/csv_downloader.py` | ⚠️ Downloader - acceptable |
| 334  | `./redline/downloaders/base_downloader.py` | ⚠️ Base class - acceptable |
| 326  | `./redline/background/task_manager.py` | ⚠️ Background tasks - acceptable |
| 324  | `./redline/database/operations.py` | ⚠️ Database ops - acceptable |
| 323  | `./redline/web/routes/tasks.py` | ⚠️ Task routes - acceptable |
| 320  | `./redline/utils/config.py` | ⚠️ Config - acceptable |
| 313  | `./redline/updates/update_checker.py` | ⚠️ Update system - acceptable |
| 311  | `./redline/database/query_builder.py` | ⚠️ Database - acceptable |
| 308  | `./data_module_grid.py` | ⚠️ Standalone script |
| 299  | `./redline/downloaders/multi_source.py` | ⚠️ Downloader - acceptable |
| 295  | `./redline/gui/widgets/data_source.py` | ⚠️ GUI widget - acceptable |
| 294  | `./redline/downloaders/format_handlers/stooq_format.py` | ⚠️ Format handler - acceptable |
| 292  | `./redline/core/data_loader.py` | ⚠️ Core loader - acceptable |
| 289  | `./redline/downloaders/stooq_downloader.py` | ⚠️ Downloader - acceptable |
| 282  | `./redline/gui/settings_tab.py` | ⚠️ GUI tab - acceptable |
| 280  | `./redline/gui/utils/conversion_ui.py` | ⚠️ GUI utils - acceptable |
| 273  | `./redline/core/data_cleaner.py` | ⚠️ Core functionality - acceptable |
| 271  | `./redline/gui/analysis_tab.py` | ⚠️ GUI tab - acceptable |
| 270  | `./redline/downloaders/bulk_downloader.py` | ⚠️ Downloader - acceptable |
| 269  | `./redline/downloaders/yahoo_downloader.py` | ⚠️ Downloader - acceptable |
| 263  | `./redline/utils/logging_config.py` | ⚠️ Utils - acceptable |
| 263  | `./redline/gui/widgets/progress_tracker.py` | ⚠️ GUI widget - acceptable |
| 254  | `./redline/tests/test_downloaders.py` | ⚠️ Test file |
| 250  | `./redline/gui/widgets/virtual_treeview.py` | ⚠️ GUI widget - acceptable |
| 250  | `./redline/downloaders/finnhub_downloader.py` | ⚠️ Downloader - acceptable |
| 247  | `./redline/downloaders/alpha_vantage_downloader.py` | ⚠️ Downloader - acceptable |
| 237  | `./licensing/client/license_validator.py` | ⚠️ License client - acceptable |
| 231  | `./redline/gui/data_tab.py` | ⚠️ GUI tab - acceptable |
| 228  | `./redline/utils/error_handling.py` | ⚠️ Utils - acceptable |
| 226  | `./redline/gui/utils/file_browser.py` | ⚠️ GUI utils - acceptable |
| 225  | `./redline/web/routes/main.py` | ⚠️ Main routes - acceptable |
| 223  | `./redline/utils/security_validator.py` | ⚠️ Utils - acceptable |
| 211  | `./redline/updates/update_installer.py` | ⚠️ Update system - acceptable |
| 209  | `./redline/gui/utils/conversion_logic.py` | ⚠️ GUI utils - acceptable |
| 202  | `./redline/core/data_loader.py` | ⚠️ Core loader - acceptable |

## Refactoring Priority

### Priority 1: Critical Files (>1000 LOC)

1. **`data_module_shared.py`** (3,776 LOC)
   - **Action**: Split into multiple utility modules
   - **Target**: 5-10 files of ~200-300 LOC each

2. **`redline/web/routes/data.py`** (1,441 LOC)
   - **Action**: Split into focused route modules
   - **Target**: 4-6 files of ~200-300 LOC each

3. **`redline/web/routes/api.py`** (952 LOC)
   - **Action**: Split into API endpoint modules
   - **Target**: 3-4 files of ~200-300 LOC each

### Priority 2: High Priority (500-1000 LOC)

4. **`redline/gui/converter_tab.py`** (881 LOC)
5. **`redline/gui/widgets/filter_dialog.py`** (830 LOC)
6. **`redline/web/routes/data_routes.py`** (813 LOC)
7. **`redline/gui/main_window.py`** (766 LOC)
8. **`redline/gui/download_tab.py`** (757 LOC)
9. **`redline/web/routes/converter.py`** (687 LOC)
10. **`redline/web/routes/download.py`** (605 LOC)
11. **`redline/web/routes/analysis.py`** (484 LOC)

### Priority 3: Medium Priority (200-500 LOC)

Files in this range are generally acceptable but could be optimized:
- Core modules (database, storage, background tasks) - acceptable
- Route files - could be split if they grow
- GUI components - acceptable for UI complexity
- Standalone scripts - not part of main codebase

## Notes

- **Standalone scripts** (root directory) are not part of the main codebase
- **Test files** are excluded from refactoring priority
- **Core modules** (database, storage) may be acceptable at current size
- **GUI components** may require more LOC due to UI complexity

## Code Quality Target

**Goal**: All production code files ≤200 LOC  
**Current**: 75 files exceed 200 LOC  
**Progress**: Need to refactor 11 critical/high-priority files

