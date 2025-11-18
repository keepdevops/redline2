# Critical Files Refactoring Plan (>1000 LOC)

## Overview

Three files exceed 1000 LOC and need immediate refactoring to meet the 200 LOC requirement.

---

## File 1: `data_module_shared.py` - 3,776 LOC ❌ CRITICAL

### Current Structure

**Location**: Root directory  
**Size**: 3,776 lines  
**Purpose**: Monolithic utility module with data loading, validation, cleaning, and GUI operations

### What It Contains

Based on analysis, this file likely contains:
- Data loading functions
- Data validation logic
- Data cleaning operations
- Format conversion utilities
- File operations
- GUI-related data operations
- Date/time utilities
- Parsers for different formats

### Refactoring Plan

**Split into 5-10 focused modules:**

1. **`redline/utils/file_helpers.py`** (~300 LOC)
   - File operations
   - File format detection
   - File path utilities
   - File validation

2. **`redline/utils/data_validation.py`** (~400 LOC)
   - Data schema validation
   - Column validation
   - Data type checking
   - Data integrity checks

3. **`redline/utils/data_cleaning.py`** (~500 LOC)
   - Data cleaning functions
   - Missing value handling
   - Outlier detection
   - Data normalization

4. **`redline/utils/date_utils.py`** (~200 LOC)
   - Date parsing
   - Date formatting
   - Date range utilities
   - Timezone handling

5. **`redline/utils/parsers.py`** (~400 LOC)
   - CSV parsing
   - JSON parsing
   - Format-specific parsers
   - Data extraction

6. **`redline/utils/formatters.py`** (~300 LOC)
   - Data formatting
   - Output formatting
   - Display formatting
   - Export formatting

7. **`redline/utils/gui_data_ops.py`** (~400 LOC)
   - GUI-specific data operations
   - Tkinter integration
   - UI data binding

8. **`redline/utils/config_utils.py`** (~200 LOC)
   - Configuration loading
   - Config validation
   - Config management

**Estimated Result**: 8 files of ~200-500 LOC each

---

## File 2: `redline/web/routes/data.py` - 1,441 LOC ❌ CRITICAL

### Current Structure

**Location**: `redline/web/routes/data.py`  
**Size**: 1,441 lines  
**Purpose**: Data tab routes for web GUI - handles viewing, filtering, loading, and management

### What It Contains

**Routes identified:**
- `/` - Main data tab
- `/browser` - File browser
- `/stooq` - Stooq downloader
- `/multi` - Multi-file data tab
- `/load-multiple` - Load multiple files
- `/load` - Load single file
- `/filter` - Filter file data
- `/export` - Export file data
- `/debug` - Debug view
- `/simple` - Simple view

**Helper functions:**
- `clean_dataframe_columns()` - Clean CSV headers
- `_detect_format_from_path()` - Format detection
- `_load_single_file_parallel()` - Parallel file loading
- `_load_files_parallel()` - Batch file loading
- `_load_file_by_format()` - Format-specific loading
- `_save_file_by_format()` - Format-specific saving
- `_apply_filters()` - Data filtering
- `_load_large_file_chunked()` - Chunked loading for large files

### Refactoring Plan

**Split into 4-6 focused route modules:**

1. **`redline/web/routes/data_tab.py`** (~300 LOC)
   - Main data tab route (`/`)
   - Tab rendering
   - Basic data display

2. **`redline/web/routes/data_file_loading.py`** (~400 LOC)
   - `/load` - Single file loading
   - `/load-multiple` - Multiple file loading
   - `_load_single_file_parallel()`
   - `_load_files_parallel()`
   - `_load_file_by_format()`
   - `_load_large_file_chunked()`

3. **`redline/web/routes/data_filtering.py`** (~300 LOC)
   - `/filter` - Filter operations
   - `_apply_filters()`
   - Filter logic
   - Filter validation

4. **`redline/web/routes/data_browsing.py`** (~200 LOC)
   - `/browser` - File browser
   - File listing
   - File metadata

5. **`redline/web/routes/data_export.py`** (~200 LOC)
   - `/export` - Export operations
   - `_save_file_by_format()`
   - Export formatting

6. **`redline/web/utils/data_helpers.py`** (~200 LOC)
   - `clean_dataframe_columns()`
   - `_detect_format_from_path()`
   - Shared utilities

**Estimated Result**: 6 files of ~200-400 LOC each

---

## File 3: `redline/web/routes/api.py` - 952 LOC ❌ HIGH

### Current Structure

**Location**: `redline/web/routes/api.py`  
**Size**: 952 lines  
**Purpose**: REST API endpoints for data operations

### What It Contains

**Routes identified:**
- `/status` - Application status
- `/database/indexes` - Index management
- `/files` - List files
- `/files/<filename>` - Delete file
- `/upload` - Upload file
- `/formats` - Supported formats
- `/convert` - Convert file
- `/download/<ticker>` - Download data
- `/data/quick/<filename>` - Quick stats
- `/data/<filename>` - Data preview
- `/themes` - Get themes
- `/theme` - Set/get theme

**Helper functions:**
- `rate_limit()` - Rate limiting decorator
- `allowed_file()` - File validation
- `paginate_data()` - Data pagination

### Refactoring Plan

**Split into 3-4 focused API modules:**

1. **`redline/web/routes/api_files.py`** (~350 LOC)
   - `/files` - List files
   - `/files/<filename>` - Delete file
   - `/upload` - Upload file
   - File operations
   - `allowed_file()` helper

2. **`redline/web/routes/api_data.py`** (~300 LOC)
   - `/data/<filename>` - Data preview
   - `/data/quick/<filename>` - Quick stats
   - `/download/<ticker>` - Download data
   - Data retrieval operations

3. **`redline/web/routes/api_metadata.py`** (~200 LOC)
   - `/status` - Application status
   - `/formats` - Supported formats
   - `/themes` - Get themes
   - `/theme` - Set/get theme
   - Metadata endpoints

4. **`redline/web/routes/api_database.py`** (~200 LOC)
   - `/database/indexes` - Index management
   - Database operations
   - Index utilities

5. **`redline/web/routes/api_convert.py`** (~200 LOC)
   - `/convert` - Convert file
   - Conversion operations
   - Format conversion logic

**Estimated Result**: 5 files of ~200-350 LOC each

---

## Refactoring Strategy

### Phase 1: Extract Utilities (Low Risk)

1. Extract helper functions to utility modules
2. Create shared utility files
3. Update imports in main files
4. Test to ensure nothing breaks

### Phase 2: Split Routes (Medium Risk)

1. Create new route modules
2. Move route handlers to new modules
3. Update Blueprint registration
4. Test each route individually

### Phase 3: Clean Up (Low Risk)

1. Remove old code
2. Update documentation
3. Verify all tests pass
4. Check file sizes meet 200 LOC

---

## Implementation Steps

### For Each File:

1. **Analyze Dependencies**
   ```bash
   # Find all imports and function calls
   grep -E "^import |^from |def |class " <file>
   ```

2. **Identify Logical Groups**
   - Group related functions
   - Identify shared utilities
   - Find route patterns

3. **Create New Modules**
   - Create new files
   - Move functions to appropriate modules
   - Update imports

4. **Update Imports**
   - Update all files that import from old module
   - Test imports work correctly

5. **Test Thoroughly**
   - Run all tests
   - Test each route/function
   - Verify no regressions

---

## Risk Assessment

| File | Risk Level | Complexity | Estimated Time |
|------|------------|------------|---------------|
| `data_module_shared.py` | **HIGH** | Very High | 2-3 days |
| `redline/web/routes/data.py` | **MEDIUM** | High | 1-2 days |
| `redline/web/routes/api.py` | **MEDIUM** | Medium | 1 day |

**Total Estimated Time**: 4-6 days

---

## Benefits After Refactoring

1. **Better Maintainability**: Smaller files are easier to understand
2. **Easier Testing**: Focused modules enable targeted tests
3. **Better Code Reviews**: Smaller files are easier to review
4. **Reduced Cognitive Load**: Developers can focus on specific functionality
5. **Improved Reusability**: Smaller components can be reused
6. **Meets Code Quality Standard**: All files ≤200 LOC

---

## Quick Start

### Start with Lowest Risk: `api.py`

1. Extract utilities first (`rate_limit`, `allowed_file`, `paginate_data`)
2. Split into route modules
3. Test each module
4. Move to next file

### Then Medium Risk: `data.py`

1. Extract file loading utilities
2. Split route handlers
3. Test routes
4. Verify functionality

### Finally High Risk: `data_module_shared.py`

1. Extract utilities first
2. Split by functionality
3. Test thoroughly
4. Update all imports

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Start with one file** - Begin refactoring
3. **Test incrementally** - Verify after each change
4. **Document changes** - Update documentation

Would you like me to start refactoring one of these files?

