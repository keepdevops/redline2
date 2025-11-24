# Duplicate Classes Analysis

## Critical Duplicates (Active Code)

### 1. **FormatConverter** - DUPLICATE
- **Location 1**: `redline/core/format_converter.py` (570 lines)
  - Full-featured implementation
  - Used by: `redline/core/data_loader.py`
  - Has `convert_format()`, `get_supported_formats()`, file I/O methods
  
- **Location 2**: `redline/core/data_format_converter_shared.py` (214 lines)
  - Legacy/shared module version
  - Static methods, simpler implementation
  - Comment says "extracted from data_module_shared.py (shared module)"

**Impact**: HIGH - Both are in active codebase, could cause import conflicts
**Recommendation**: Remove `data_format_converter_shared.py` and update imports

---

### 2. **DataLoader** - DUPLICATE
- **Location 1**: `redline/core/data_loader.py` (293 lines)
  - Main implementation
  - Uses `FormatConverter` from `format_converter.py`
  - Full-featured with config support
  
- **Location 2**: `redline/core/data_loader_shared.py` (134 lines)
  - Legacy version
  - Comment says "extracted from data_module_shared.py (shared module)"
  - Simpler implementation

**Impact**: HIGH - Both are in active codebase
**Recommendation**: Remove `data_loader_shared.py` and update imports

---

### 3. **DatabaseConnector** - DUPLICATE
- **Location 1**: `redline/database/connector.py` (373 lines)
  - Main implementation
  - Full-featured with connection pooling
  - Uses local path: `redline_data.duckdb`
  
- **Location 2**: `redline/database/connector_shared.py` (114 lines)
  - Legacy version
  - Comment says "extracted from data_module_shared.py (shared module)"
  - Uses Docker path: `/app/redline_data.duckdb`

**Impact**: HIGH - Different default paths could cause issues
**Recommendation**: Remove `connector_shared.py` and update imports

---

### 4. **VirtualScrollingTreeview** - DUPLICATE
- **Location 1**: `redline/gui/widgets/virtual_treeview.py`
- **Location 2**: `redline/gui/widgets/virtual_treeview_shared.py`

**Impact**: MEDIUM - Widget duplication
**Recommendation**: Consolidate into one implementation

---

### 5. **AdvancedQueryBuilder** - DUPLICATE
- **Location 1**: `redline/database/query_builder.py`
- **Location 2**: `redline/database/query_builder_shared.py`

**Impact**: MEDIUM - Query builder duplication
**Recommendation**: Consolidate into one implementation

---

### 6. **DataSource** - DUPLICATE
- **Location 1**: `redline/gui/widgets/data_source.py`
- **Location 2**: `redline/gui/widgets/data_source_shared.py`

**Impact**: MEDIUM - Widget duplication
**Recommendation**: Consolidate into one implementation

---

## Legacy/Old Code Duplicates (Lower Priority)

### 7. **MultiSourceDownloader** - Multiple Versions
- **Active**: `redline/downloaders/multi_source.py`
- **Legacy**: `old/multi_source_downloader.py`
- **Root**: `multi_source_downloader.py` (likely unused)

**Impact**: LOW - Old files in `old/` directory
**Recommendation**: Keep active version, remove old files

---

### 8. **StooqHistoricalDownloader** - Multiple Versions
- `old/stooq_historical_data_downloader.py`
- `stooq_historical_downloader.py`
- `stooq_historical_data_downloader.py`
- `stooq_gui_downloader.py`
- `stooq_data_downloader.py`
- `stooq_manual_downloader.py`
- `chartoasis_stooq_downloader.py`

**Impact**: LOW - Multiple standalone scripts
**Recommendation**: Consolidate if possible, or document which to use

---

## Import Analysis

### Files Importing FormatConverter:
- `redline/core/data_loader.py` → imports from `format_converter.py` ✅
- `redline/core/data_format_converter_shared.py` → standalone ❌

### Files Importing DataLoader:
- Multiple files import from `data_loader.py` ✅
- `redline/core/data_loader_shared.py` → standalone ❌

### Files Importing DatabaseConnector:
- Multiple files import from `connector.py` ✅
- `redline/database/connector_shared.py` → standalone ❌

---

## Summary

### High Priority (Active Duplicates):
1. ✅ **FormatConverter** - 2 active versions
2. ✅ **DataLoader** - 2 active versions
3. ✅ **DatabaseConnector** - 2 active versions

### Medium Priority (Widget Duplicates):
4. **VirtualScrollingTreeview** - 2 versions
5. **AdvancedQueryBuilder** - 2 versions
6. **DataSource** - 2 versions

### Low Priority (Legacy/Old):
7. **MultiSourceDownloader** - Multiple old versions
8. **StooqHistoricalDownloader** - Multiple standalone scripts

---

## Recommendations

1. **Remove `*_shared.py` files** - These appear to be legacy extracts
2. **Update all imports** to use the main implementations
3. **Test thoroughly** after removal to ensure no breakage
4. **Document** which classes are the canonical versions

---

## Files to Remove (After Import Updates):
- `redline/core/data_format_converter_shared.py`
- `redline/core/data_loader_shared.py`
- `redline/database/connector_shared.py`
- `redline/gui/widgets/virtual_treeview_shared.py`
- `redline/database/query_builder_shared.py`
- `redline/gui/widgets/data_source_shared.py`

