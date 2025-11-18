# Codebase Duplication Scan Report

**Date**: 2025-11-18  
**Scope**: Production codebase (`redline/` package)

## 🔍 Duplication Patterns Found

### 1. Format Detection Functions (HIGH PRIORITY)

**Issue**: Format detection logic is duplicated across 5+ files

**Locations**:
- `redline/web/utils/file_loading.py` - `detect_format_from_path()`
- `redline/gui/utils/data_management.py` - `_detect_format_from_path()`
- `redline/core/data_loading_service.py` - `detect_format()`
- `redline/cli/analyze.py` - `_detect_format()`
- `redline/core/format_converter.py` - `detect_format_from_extension()`

**Current Implementation** (duplicated):
\`\`\`python
def detect_format_from_path(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_TO_FORMAT.get(ext, 'csv')
\`\`\`

**Recommendation**: 
- Centralize in `redline/core/schema.py` or create `redline/utils/format_utils.py`
- All modules should import from centralized location

---

### 2. Date Formatting JavaScript (MEDIUM PRIORITY)

**Issue**: `formatDateValue()` function duplicated in HTML templates

**Locations**:
- `redline/web/templates/data_tab.html` (lines ~266-355)
- `redline/web/templates/data_tab_tkinter_style.html` (lines ~884-975)

**Status**: Should use `redline/web/static/js/date-formatter.js` (if exists)

**Recommendation**:
- Verify `date-formatter.js` exists and contains the function
- Remove duplicate implementations from HTML templates
- Reference shared JS file via `<script>` tag

---

### 3. JSON NaN Handling (MEDIUM PRIORITY)

**Issue**: `replace_nan_in_dict()` function duplicated in 3 files

**Locations**:
- `redline/core/data_format_converter_shared.py` - `save_file_by_type()` for JSON (lines 127-137)
- `redline/web/utils/file_loading.py` - `save_file_by_format()` for JSON (lines 267-277)
- `redline/core/format_converter.py` - JSON saving (lines 211-224)

**Current Implementation** (duplicated):
\`\`\`python
def replace_nan_in_dict(obj):
    """Recursively replace NaN values with None."""
    if isinstance(obj, dict):
        return {k: replace_nan_in_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_in_dict(item) for item in obj]
    elif isinstance(obj, float) and (pd.isna(obj) or pd.isnull(obj)):
        return None
    elif pd.isna(obj):
        return None
    return obj
\`\`\`

**Recommendation**:
- Centralize in `redline/utils/json_utils.py` or `redline/core/data_utils.py`
- All modules should import from centralized location

---

### 4. Column Cleaning Functions (VERIFY)

**Issue**: Column name cleaning may be duplicated

**Locations to Check**:
- `redline/web/utils/data_helpers.py` - `clean_dataframe_columns()`
- Other locations using similar logic

**Status**: Likely already centralized, verify no duplicates

---

## ✅ Already Consolidated

Based on previous analysis:
- ✅ Logging initialization (via `LoggingMixin`)
- ✅ Error handling patterns (via decorators)
- ✅ API key masking (centralized in `security_helpers.py`)
- ✅ Data cleaning operations (centralized in `DataCleaner`)

---

## 📊 Summary

| Category | Status | Priority | Files Affected |
|----------|--------|----------|----------------|
| Format Detection | ⚠️ Duplicated | HIGH | 5 files |
| Date Formatting JS | ⚠️ Duplicated | MEDIUM | 2 HTML files |
| JSON NaN Handling | ⚠️ Duplicated | MEDIUM | 3 files |
| Column Cleaning | ✅ Centralized | - | 1 file (data_helpers.py) |

---

## 🔧 Recommended Actions

1. **Immediate**: Consolidate format detection functions (5 files)
2. **Short-term**: Remove duplicate `formatDateValue()` from HTML templates (2 files)
3. **Short-term**: Consolidate JSON NaN handling `replace_nan_in_dict()` (3 files)
4. **Verify**: Column cleaning is already centralized ✅

---

## 📝 Detailed Findings

### Format Detection Duplication
All 5 implementations use `EXT_TO_FORMAT` from `schema.py` (good), but duplicate the detection logic:
- Extract to `redline/core/schema.py` as `detect_format_from_path(file_path: str) -> str`
- Update all 5 files to import and use the centralized function

### Date Formatting JavaScript Duplication
The `formatDateValue()` function is ~90 lines duplicated in 2 HTML templates:
- Create `redline/web/static/js/date-formatter.js` with the function
- Remove from HTML templates and reference via `<script src="{{ url_for('static', filename='js/date-formatter.js') }}"></script>`

### JSON NaN Handling Duplication
The `replace_nan_in_dict()` function is duplicated in 3 files:
- Create `redline/utils/json_utils.py` with `replace_nan_in_dict()` and `clean_dataframe_for_json()`
- Update all 3 files to import from centralized location

