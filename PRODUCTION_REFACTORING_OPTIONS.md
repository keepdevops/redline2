# Production Files Refactoring Options (to 200 LOC)

## Overview

7 production files exceed 200 LOC and need refactoring. This document provides multiple options for each file.

---

## File 1: `redline/web/routes/api.py` - 952 LOC

### Option A: Split by Functionality (Recommended)

**Strategy**: Split into 5 focused modules by endpoint type

**Modules**:
1. `redline/web/routes/api_files.py` (~200 LOC)
   - `/api/files` - List files
   - `/api/files/<filename>` - Delete file
   - `/api/upload` - Upload file
   - `allowed_file()` helper

2. `redline/web/routes/api_data.py` (~200 LOC)
   - `/api/data/<filename>` - Data preview
   - `/api/data/quick/<filename>` - Quick stats
   - `/api/download/<ticker>` - Download data

3. `redline/web/routes/api_metadata.py` (~150 LOC)
   - `/api/status` - Application status
   - `/api/formats` - Supported formats
   - `/api/themes` - Get themes
   - `/api/theme` - Set/get theme

4. `redline/web/routes/api_database.py` (~200 LOC)
   - `/api/database/indexes` - Index management
   - Database operations
   - Index utilities

5. `redline/web/routes/api_convert.py` (~200 LOC)
   - `/api/convert` - Convert file
   - Conversion operations
   - Format conversion logic

**Pros**:
- Clear separation of concerns
- Easy to test each module
- Maintainable

**Cons**:
- More files to manage
- Need to update imports

**Risk**: Low  
**Effort**: 4-6 hours

---

### Option B: Extract Utilities Only

**Strategy**: Keep routes in one file, extract helpers

**Modules**:
1. `redline/web/utils/api_helpers.py` (~200 LOC)
   - `allowed_file()`
   - `paginate_data()`
   - `rate_limit()` decorator
   - File validation utilities

2. `redline/web/routes/api.py` (~750 LOC)
   - All routes remain
   - Uses helpers from utils

**Pros**:
- Minimal changes
- Lower risk
- Quick to implement

**Cons**:
- Still over 200 LOC
- Doesn't fully solve the problem

**Risk**: Very Low  
**Effort**: 1-2 hours

---

### Option C: Hybrid Approach

**Strategy**: Extract utilities + split largest route groups

**Modules**:
1. `redline/web/utils/api_helpers.py` (~200 LOC) - Utilities
2. `redline/web/routes/api_files.py` (~250 LOC) - File operations
3. `redline/web/routes/api_data.py` (~250 LOC) - Data operations
4. `redline/web/routes/api_core.py` (~250 LOC) - Status, metadata, convert

**Pros**:
- Balanced approach
- Reduces file size significantly
- Maintains some grouping

**Cons**:
- Still some files over 200 LOC
- Moderate complexity

**Risk**: Low  
**Effort**: 3-4 hours

---

## File 2: `redline/web/routes/data_routes.py` - 813 LOC

### Option A: Split by Route Groups (Recommended)

**Strategy**: Split into 4 focused route modules

**Modules**:
1. `redline/web/routes/data_tab.py` (~200 LOC)
   - `/data/` - Main data tab
   - Tab rendering
   - Basic display

2. `redline/web/routes/data_loading.py` (~250 LOC)
   - `/data/load` - Load files
   - `/data/load-multiple` - Load multiple
   - File loading logic

3. `redline/web/routes/data_filtering.py` (~200 LOC)
   - `/data/filter` - Filter operations
   - Filter logic
   - Filter validation

4. `redline/web/routes/data_browsing.py` (~200 LOC)
   - `/data/browser` - File browser
   - File listing
   - File metadata

**Note**: Helpers already in `redline/web/utils/file_loading.py`

**Pros**:
- Clear separation
- Uses existing utilities
- Easy to maintain

**Cons**:
- Need to update blueprint registration
- Multiple files

**Risk**: Low  
**Effort**: 3-4 hours

---

### Option B: Extract More Utilities

**Strategy**: Move more logic to utils, keep routes together

**Modules**:
1. `redline/web/utils/data_helpers.py` (~300 LOC)
   - All helper functions
   - Data processing logic
   - Filtering utilities

2. `redline/web/routes/data_routes.py` (~500 LOC)
   - Route handlers only
   - Thin wrappers around utils

**Pros**:
- Single route file
- Reusable utilities
- Lower refactoring risk

**Cons**:
- Still over 200 LOC
- Doesn't fully solve problem

**Risk**: Very Low  
**Effort**: 2-3 hours

---

## File 3: `redline/web/routes/converter.py` - 687 LOC

### Option A: Split Conversion Logic (Recommended)

**Strategy**: Separate conversion logic from routes

**Modules**:
1. `redline/web/utils/conversion_helpers.py` (~300 LOC)
   - Format detection
   - Conversion logic
   - Validation

2. `redline/web/routes/converter.py` (~400 LOC)
   - Route handlers
   - Uses conversion helpers

**Pros**:
- Reusable conversion logic
- Cleaner route file
- Testable utilities

**Cons**:
- Still over 200 LOC in routes
- Need further splitting

**Risk**: Low  
**Effort**: 2-3 hours

---

### Option B: Split by Format Type

**Strategy**: Split by conversion format

**Modules**:
1. `redline/web/routes/converter_core.py` (~200 LOC)
   - Main conversion routes
   - Common logic

2. `redline/web/routes/converter_formats.py` (~250 LOC)
   - Format-specific conversions
   - CSV, JSON, Parquet, etc.

3. `redline/web/utils/conversion_engine.py` (~250 LOC)
   - Core conversion engine
   - Format handlers

**Pros**:
- Format-specific modules
- Clear organization
- All files ≤250 LOC

**Cons**:
- More complex structure
- Higher refactoring effort

**Risk**: Medium  
**Effort**: 4-5 hours

---

## File 4: `redline/web/routes/download.py` - 605 LOC

### Option A: Split by Download Source (Recommended)

**Strategy**: Split by data source

**Modules**:
1. `redline/web/routes/download_core.py` (~200 LOC)
   - Main download routes
   - Common download logic

2. `redline/web/routes/download_sources.py` (~250 LOC)
   - Yahoo Finance downloads
   - Stooq downloads
   - Alpha Vantage downloads

3. `redline/web/utils/download_helpers.py` (~200 LOC)
   - Download utilities
   - Rate limiting
   - Error handling

**Pros**:
- Source-specific modules
- Reusable helpers
- Clear structure

**Cons**:
- Multiple files
- Need to coordinate

**Risk**: Low  
**Effort**: 3-4 hours

---

### Option B: Extract Utilities Only

**Strategy**: Keep routes, extract helpers

**Modules**:
1. `redline/web/utils/download_helpers.py` (~300 LOC)
   - All download utilities
   - Source-specific logic

2. `redline/web/routes/download.py` (~300 LOC)
   - Route handlers only

**Pros**:
- Single route file
- Reusable utilities
- Quick implementation

**Cons**:
- Still over 200 LOC
- Partial solution

**Risk**: Very Low  
**Effort**: 2 hours

---

## File 5: `redline/database/optimized_connector.py` - 563 LOC

### Option A: Split by Functionality (Recommended)

**Strategy**: Split connection management from operations

**Modules**:
1. `redline/database/connection_pool.py` (~200 LOC)
   - Connection pooling
   - Pool management
   - Connection lifecycle

2. `redline/database/query_executor.py` (~200 LOC)
   - Query execution
   - Result handling
   - Transaction management

3. `redline/database/optimized_connector.py` (~200 LOC)
   - Main connector class
   - Public API
   - Uses pool and executor

**Pros**:
- Clear separation
- Testable components
- Better organization

**Cons**:
- More files
- Need to coordinate

**Risk**: Medium  
**Effort**: 4-5 hours

---

### Option B: Extract Caching Logic

**Strategy**: Separate caching from connection logic

**Modules**:
1. `redline/database/query_cache.py` (~200 LOC)
   - Caching logic
   - Cache management
   - TTL handling

2. `redline/database/optimized_connector.py` (~400 LOC)
   - Connection management
   - Query execution
   - Uses cache

**Pros**:
- Reusable cache
- Cleaner connector
- Lower risk

**Cons**:
- Still over 200 LOC
- Partial solution

**Risk**: Low  
**Effort**: 2-3 hours

---

## File 6: `redline/web/routes/analysis.py` - 484 LOC

### Option A: Split by Analysis Type (Recommended)

**Strategy**: Split by analysis category

**Modules**:
1. `redline/web/routes/analysis_core.py` (~200 LOC)
   - Main analysis routes
   - Common analysis logic

2. `redline/web/routes/analysis_statistical.py` (~200 LOC)
   - Statistical analysis
   - Descriptive stats
   - Aggregations

3. `redline/web/utils/analysis_helpers.py` (~150 LOC)
   - Analysis utilities
   - Data processing
   - Result formatting

**Pros**:
- Type-specific modules
   - Reusable utilities
   - Clear organization

**Cons**:
- Multiple files
- Need coordination

**Risk**: Low  
**Effort**: 3-4 hours

---

### Option B: Extract Utilities Only

**Strategy**: Keep routes, extract helpers

**Modules**:
1. `redline/web/utils/analysis_helpers.py` (~300 LOC)
   - All analysis utilities
   - Statistical functions

2. `redline/web/routes/analysis.py` (~200 LOC)
   - Route handlers only

**Pros**:
- Single route file
   - Reusable utilities
   - Quick implementation

**Cons**:
- Large utils file
   - May need further splitting

**Risk**: Very Low  
**Effort**: 2 hours

---

## File 7: `web_app.py` - 491 LOC (CRITICAL)

### Option A: Extract Configuration (Recommended)

**Strategy**: Move config to separate module

**Modules**:
1. `redline/web/config.py` (~200 LOC)
   - Flask configuration
   - Environment setup
   - App initialization helpers

2. `web_app.py` (~300 LOC)
   - Main app factory
   - Blueprint registration
   - Error handlers

**Pros**:
- Separated concerns
   - Reusable config
   - Lower risk

**Cons**:
- Still over 200 LOC
   - Partial solution

**Risk**: Low  
**Effort**: 2-3 hours

---

### Option B: Extract Blueprint Registration

**Strategy**: Move blueprint setup to separate module

**Modules**:
1. `redline/web/blueprints.py` (~200 LOC)
   - All blueprint imports
   - Blueprint registration
   - Route setup

2. `web_app.py` (~300 LOC)
   - App creation
   - Configuration
   - Error handlers

**Pros**:
- Cleaner main file
   - Organized blueprints
   - Lower risk

**Cons**:
- Still over 200 LOC
   - Partial solution

**Risk**: Low  
**Effort**: 2-3 hours

---

### Option C: Keep As-Is (Recommended for Critical File)

**Strategy**: Leave `web_app.py` as single file

**Reasoning**:
- Critical entry point
- Easier to understand
- Lower risk of breaking
- 491 LOC is acceptable for main entry point

**Pros**:
- No risk
   - Single source of truth
   - Easy to debug

**Cons**:
- Still over 200 LOC
   - Doesn't meet target

**Risk**: None  
**Effort**: 0 hours

---

## Recommended Approach

### Phase 1: High Priority (Start Here)

1. **`api.py`** → Option A (Split by Functionality)
   - 5 modules of ~200 LOC each
   - Clear separation
   - High impact

2. **`data_routes.py`** → Option A (Split by Route Groups)
   - 4 modules of ~200 LOC each
   - Uses existing utilities
   - High impact

### Phase 2: Medium Priority

3. **`converter.py`** → Option A (Split Conversion Logic)
4. **`download.py`** → Option A (Split by Download Source)
5. **`optimized_connector.py`** → Option A (Split by Functionality)
6. **`analysis.py`** → Option A (Split by Analysis Type)

### Phase 3: Low Priority

7. **`web_app.py`** → Option C (Keep As-Is)
   - Critical file
   - Acceptable at 491 LOC
   - Too risky to split

---

## Implementation Strategy

### For Each File:

1. **Create new modules** (extract code)
2. **Update imports** in new modules
3. **Update `web_app.py`** to import from new locations
4. **Test thoroughly** (run web app, test all routes)
5. **Remove old code** (after verification)

### Testing Checklist:

- [ ] All routes work
- [ ] All imports resolve
- [ ] No circular dependencies
- [ ] All files ≤200 LOC
- [ ] Production deployment works

---

## Estimated Total Effort

- **Phase 1**: 7-10 hours (2 files)
- **Phase 2**: 12-16 hours (4 files)
- **Phase 3**: 0 hours (keep as-is)

**Total**: 19-26 hours

---

## Risk Assessment

| File | Risk Level | Reason |
|------|------------|--------|
| `api.py` | Low | Well-defined routes |
| `data_routes.py` | Low | Has existing utilities |
| `converter.py` | Low | Clear separation possible |
| `download.py` | Low | Source-based split clear |
| `optimized_connector.py` | Medium | Database operations critical |
| `analysis.py` | Low | Analysis functions isolated |
| `web_app.py` | **High** | Critical entry point |

---

## Next Steps

1. **Choose approach** for each file
2. **Start with Phase 1** (api.py, data_routes.py)
3. **Test incrementally** after each refactoring
4. **Update documentation** as you go

