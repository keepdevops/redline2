# Old/Unused Files Directory

## Purpose

This directory contains files that are:
- **NOT used in production** (`web_app.py`, Dockerfile)
- **NOT used in testing** (test files)
- **NOT imported** by any active code

## Files Moved

### Standalone Scripts (5 files)

1. `comprehensive_financial_downloader.py` (850 LOC)
   - Standalone downloader script
   - Not imported by production or test code

2. `financial_data_formats_guide.py` (626 LOC)
   - Standalone guide/documentation script
   - Not imported by production or test code

3. `universal_gui_downloader.py` (540 LOC)
   - Standalone GUI downloader script
   - Not imported by production or test code

4. `stooq_historical_data_downloader.py` (519 LOC)
   - Standalone Stooq downloader script
   - Not imported by production or test code

5. `multi_source_downloader.py` (513 LOC)
   - Standalone multi-source downloader script
   - Not imported by production or test code

### Old Version Files

6. `data.py.old` (1,441 LOC)
   - Old version of `redline/web/routes/data.py`
   - Replaced by `redline/web/routes/data_routes.py` in production
   - Only used by `web_app_safe.py` (backup version)

## Total

- **6 files** moved to `old/` directory
- **~4,500 LOC** of unused code archived

## Notes

- These files are kept for reference
- Can be safely deleted if not needed
- Original files remain in codebase (copied, not moved)
- Production code is unaffected

## Date

Moved: 2024-11-17

