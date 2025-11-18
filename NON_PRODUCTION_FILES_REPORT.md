# Non-Production Files Report

## Summary

This report identifies Python files in the root directory that are **NOT used in production** (`web_app.py`, `main.py`, or Dockerfiles).

## ✅ Files to Remove (Not Used in Production)

### Standalone Scripts (27 files)

These files are standalone scripts/examples that are not imported by production code:

1. **`bulk_stock_downloader.py`** - Standalone bulk downloader script
2. **`chartoasis_stooq_downloader.py`** - Standalone Stooq downloader variant
3. **`cleanup_conversion_files.py`** - Utility script for cleanup
4. **`comprehensive_financial_downloader.py`** - Standalone comprehensive downloader (850 LOC)
5. **`convert_to_stooq_format.py`** - Format conversion utility script
6. **`cost_calculator.py`** - Cost calculation utility (used in docs, not production)
7. **`create_test_license.py`** - Test license generation utility
8. **`CUSTOM_API_EXAMPLE.py`** - Example/demo file for custom API
9. **`data_module_grid.py`** - Data module grid utility
10. **`DUPLICATION_CONSOLIDATION_DEMO.py`** - Demo file for duplication consolidation
11. **`enhanced_database_status.py`** - Database status utility
12. **`financial_data_formats_guide.py`** - Standalone guide/documentation script (626 LOC)
13. **`log_viewer_route.py`** - Log viewer utility (not used in web_app.py)
14. **`move_stooq_from_downloads.py`** - File movement utility
15. **`multi_source_downloader.py`** - Standalone multi-source downloader (513 LOC)
16. **`open_stooq_manual.py`** - Manual Stooq opener utility
17. **`simple_feather_test.py`** - Test file (but user said keep tests, so maybe keep?)
18. **`stooq_data_downloader.py`** - Standalone Stooq downloader
19. **`stooq_gui_downloader.py`** - Standalone Stooq GUI downloader
20. **`stooq_historical_data_downloader.py`** - Standalone historical downloader (519 LOC)
21. **`stooq_historical_downloader.py`** - Another historical downloader variant
22. **`stooq_manual_downloader.py`** - Manual Stooq downloader
23. **`universal_gui_downloader.py`** - Standalone universal GUI downloader (540 LOC)
24. **`use_converted_data.py`** - Utility for using converted data
25. **`web_app_safe.py`** - Backup version of web_app.py (not used in production)
26. **`yahoo_data_downloader.py`** - Standalone Yahoo downloader

### Test Files (Keep per user request)

- **`run_gui_tests.py`** - GUI test runner (KEEP - user said keep tests)
- **`simple_feather_test.py`** - Feather format test (KEEP - user said keep tests)

## 📊 Statistics

- **Total standalone scripts**: 26 files
- **Total LOC (estimated)**: ~5,000+ lines
- **Files already in `old/` directory**: 5 files (already archived)

## 🔍 Verification

### Production Entry Points Checked:
- ✅ `web_app.py` - Does NOT import any of these files
- ✅ `main.py` - Does NOT import any of these files  
- ✅ `Dockerfile.webgui.bytecode` - Does NOT reference any of these files

### Import Search Results:
- ❌ No imports found in `redline/` package
- ❌ No imports found in production routes
- ❌ No references in Dockerfiles

## ✅ Files Already Archived

These files are already in the `old/` directory:
- `old/comprehensive_financial_downloader.py`
- `old/financial_data_formats_guide.py`
- `old/multi_source_downloader.py`
- `old/stooq_historical_data_downloader.py`
- `old/universal_gui_downloader.py`

## 🎯 Recommended Action

**Move to `old/` directory or delete:**
- All 26 standalone scripts listed above
- Keep test files (`run_gui_tests.py`, `simple_feather_test.py`)

## 📝 Notes

- `web_app_safe.py` is a backup version and not used in production
- `cost_calculator.py` is referenced in documentation but not imported by production code
- All Stooq downloader variants are standalone scripts, not part of the production package
- `log_viewer_route.py` appears to be a utility that was replaced by the settings route

