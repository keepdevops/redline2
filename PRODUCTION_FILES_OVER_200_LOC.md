# Production Files Over 200 LOC

## Files Used in Production (`web_app.py`)

These files are actively used in production and imported by `web_app.py`:

---

### 1. `redline/web/routes/api.py` - 952 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: `web_app.py` line 399
```python
from redline.web.routes.api import api_bp
```

**Blueprint**: `api_bp` (registered at `/api`)

**Routes**:
- `/api/status` - Application status
- `/api/database/indexes` - Index management
- `/api/files` - File operations
- `/api/upload` - File upload
- `/api/convert` - Format conversion
- `/api/data/<filename>` - Data preview
- `/api/themes` - Theme management

**Refactoring Priority**: **HIGH** (952 LOC, needs to be split)

---

### 2. `redline/web/routes/data_routes.py` - 813 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: `web_app.py` line 400
```python
from redline.web.routes.data_routes import data_bp
```

**Blueprint**: `data_bp` (registered at `/data`)

**Routes**:
- `/data/` - Main data tab
- `/data/browser` - File browser
- `/data/load` - Load files
- `/data/filter` - Filter data
- `/data/export` - Export data

**Refactoring Priority**: **HIGH** (813 LOC, needs to be split)

---

### 3. `redline/web/routes/converter.py` - 687 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: `web_app.py` line 403
```python
from redline.web.routes.converter import converter_bp
```

**Blueprint**: `converter_bp` (registered at `/converter`)

**Routes**:
- Format conversion operations
- File conversion endpoints

**Refactoring Priority**: **MEDIUM** (687 LOC)

---

### 4. `redline/web/routes/download.py` - 605 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: `web_app.py` line 402
```python
from redline.web.routes.download import download_bp
```

**Blueprint**: `download_bp` (registered at `/download`)

**Routes**:
- Data download operations
- Download endpoints

**Refactoring Priority**: **MEDIUM** (605 LOC)

---

### 5. `redline/database/optimized_connector.py` - 563 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: Used by route files
- `redline/web/routes/data.py` (line 18)
- `redline/web/routes/data_routes.py` (line 12)

**Purpose**: Optimized database connector with connection pooling

**Refactoring Priority**: **MEDIUM** (563 LOC)

---

### 6. `redline/web/routes/analysis.py` - 484 LOC ⚠️

**Status**: ✅ **USED IN PRODUCTION**

**Import Location**: `web_app.py` line 401
```python
from redline.web.routes.analysis import analysis_bp
```

**Blueprint**: `analysis_bp` (registered at `/analysis`)

**Routes**:
- Analysis operations
- Statistical analysis endpoints

**Refactoring Priority**: **MEDIUM** (484 LOC)

---

### 7. `web_app.py` - 491 LOC ⚠️ **CRITICAL**

**Status**: ✅ **CRITICAL PRODUCTION FILE**

**Usage**: 
- **Main entry point** for production
- Used by Dockerfile: `gunicorn ... web_app:create_app()`
- Flask application factory

**Refactoring Priority**: **LOW** (Critical entry point - handle with extreme care)

---

## Summary Table

| File | LOC | Blueprint | Priority | Status |
|------|-----|-----------|----------|--------|
| `redline/web/routes/api.py` | 952 | `api_bp` | **HIGH** | ⚠️ Refactor |
| `redline/web/routes/data_routes.py` | 813 | `data_bp` | **HIGH** | ⚠️ Refactor |
| `redline/web/routes/converter.py` | 687 | `converter_bp` | MEDIUM | ⚠️ Refactor |
| `redline/web/routes/download.py` | 605 | `download_bp` | MEDIUM | ⚠️ Refactor |
| `redline/database/optimized_connector.py` | 563 | N/A | MEDIUM | ⚠️ Refactor |
| `redline/web/routes/analysis.py` | 484 | `analysis_bp` | MEDIUM | ⚠️ Refactor |
| `web_app.py` | 491 | N/A | **LOW** | ⚠️ Critical |

**Total**: 7 files, ~4,595 LOC

---

## Refactoring Recommendations

### High Priority (2 files, ~1,765 LOC)

1. **`redline/web/routes/api.py`** (952 LOC)
   - Split into: `api_files.py`, `api_data.py`, `api_metadata.py`, `api_database.py`, `api_convert.py`
   - Target: 5 files of ~200 LOC each

2. **`redline/web/routes/data_routes.py`** (813 LOC)
   - Already has helper functions in `redline/web/utils/file_loading.py`
   - Split routes into: `data_tab.py`, `data_loading.py`, `data_filtering.py`, `data_export.py`
   - Target: 4 files of ~200 LOC each

### Medium Priority (4 files, ~2,339 LOC)

3. **`redline/web/routes/converter.py`** (687 LOC)
4. **`redline/web/routes/download.py`** (605 LOC)
5. **`redline/database/optimized_connector.py`** (563 LOC)
6. **`redline/web/routes/analysis.py`** (484 LOC)

### Low Priority (1 file, 491 LOC)

7. **`web_app.py`** (491 LOC)
   - Critical entry point
   - Refactor only if absolutely necessary
   - Keep as single file for clarity

---

## Next Steps

1. **Start with high priority files** (api.py, data_routes.py)
2. **Test thoroughly** after each refactoring
3. **Update imports** incrementally
4. **Maintain backward compatibility**

