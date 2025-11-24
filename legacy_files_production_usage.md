# Legacy Files Used in Production

## Summary

**Total Legacy Files (`*_shared.py`)**: 9 files

**Used in Production (Web App)**: **1 file** (11.1%)
**Not Used in Production**: **8 files** (88.9%)

---

## Legacy Files Used in Production

### ✅ `redline/core/data_adapter_shared.py`
- **Used by**: `redline/web/routes/analysis_ml.py`
- **Usage**: Imports `DataAdapter` class
- **Location**: Line 30 in `analysis_ml.py`
- **Status**: **ACTIVELY USED** in production

---

## Legacy Files NOT Used in Production

### ❌ `redline/core/data_format_converter_shared.py`
- **Not imported** by any production code
- Only imports `data_loader_shared` (which is also unused)
- **Can be removed** after verification

### ❌ `redline/core/data_loader_shared.py`
- **Not directly imported** by production code
- Only imported by other unused legacy files:
  - `data_format_converter_shared.py` (unused)
  - `connector_shared.py` (unused)
- **Can be removed** after verification

### ❌ `redline/core/data_processing_shared.py`
- **Not imported** by any production code
- **Can be removed**

### ❌ `redline/core/data_standardizer_shared.py`
- **Not imported** by any production code
- **Can be removed**

### ❌ `redline/database/connector_shared.py`
- **Not imported** by any production code
- Only imports `data_loader_shared` (which is also unused)
- **Can be removed**

### ❌ `redline/database/query_builder_shared.py`
- **Not imported** by any production code
- **Can be removed**

### ❌ `redline/gui/widgets/data_source_shared.py`
- **Not imported** by production code (GUI only)
- **Can be removed** (GUI files are not production)

### ❌ `redline/gui/widgets/virtual_treeview_shared.py`
- **Not imported** by production code (GUI only)
- **Can be removed** (GUI files are not production)

---

## Detailed Analysis

### Production Usage

**Only 1 legacy file is directly used in production**:
- `redline/core/data_adapter_shared.py` → Used by `analysis_ml.py` route

### Indirect Dependencies

The following legacy files form a dependency chain but are **NOT used in production**:
1. `data_format_converter_shared.py` imports `data_loader_shared.py`
2. `connector_shared.py` imports `data_loader_shared.py`
3. Both are unused in production

---

## Migration Path

### Immediate Action (Safe to Remove)
These 7 files can be removed immediately:
1. `redline/core/data_format_converter_shared.py`
2. `redline/core/data_loader_shared.py`
3. `redline/core/data_processing_shared.py`
4. `redline/core/data_standardizer_shared.py`
5. `redline/database/connector_shared.py`
6. `redline/database/query_builder_shared.py`
7. `redline/gui/widgets/data_source_shared.py`
8. `redline/gui/widgets/virtual_treeview_shared.py`

### Requires Migration
1. **`redline/core/data_adapter_shared.py`**
   - Used by: `redline/web/routes/analysis_ml.py`
   - Action: Replace with main `DataAdapter` implementation or migrate `analysis_ml.py` to use main classes

---

## Impact Assessment

### Files That Can Be Removed: 8 files
- **Risk**: Low - Not used in production
- **Benefit**: Reduces codebase size, eliminates confusion

### Files Requiring Migration: 1 file
- **Risk**: Medium - Used in production route
- **Action**: Update `analysis_ml.py` to use main implementation
- **Benefit**: Consolidates code, removes legacy dependency

---

## Recommendation

1. **Phase 1**: Remove 8 unused legacy files (immediate)
2. **Phase 2**: Migrate `analysis_ml.py` to use main `DataAdapter` or equivalent
3. **Phase 3**: Remove `data_adapter_shared.py` after migration

This will eliminate all 9 legacy files from the codebase.

