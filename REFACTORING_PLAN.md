# REDLINE Refactoring Plan

## 🎯 Objective: Break down large files into focused, maintainable modules

### Files to Refactor:
1. **data_module_shared.py** - 3,776 lines → Split into 8 focused modules
2. **redline/web/routes/data.py** - 1,382 lines → Split into 5 focused modules

---

## 📦 **Module A: data_module_shared.py Refactoring**

### Current Structure (3,776 lines):
- 7 classes
- 1 standalone function
- 118 methods

### Proposed Split:

#### **1. redline/utils/data_loaders.py** (~400 LOC)
**Purpose:** Core data loading functionality
**Classes:**
- `DataLoader` (core load methods)
- `DataSource` (data source abstraction)

#### **2. redline/utils/data_formatters.py** (~300 LOC)
**Purpose:** Format conversion utilities
**Functions:**
- `load_file_by_type()`
- `save_file_by_type()`
- `convert_format()`

#### **3. redline/utils/data_validators.py** (~200 LOC)
**Purpose:** Data validation
**Functions:**
- `validate_data()`
- `clean_and_select_columns()`
- `_standardize_txt_columns()`

#### **4. redline/utils/data_analyzers.py** (~250 LOC)
**Purpose:** Data analysis utilities
**Functions:**
- `analyze_ticker_distribution()`
- `filter_data_by_date_range()`
- `balance_ticker_data()`

#### **5. redline/gui/widgets/virtual_scroll.py** (~300 LOC)
**Purpose:** Virtual scrolling widget
**Classes:**
- `VirtualScrollingTreeview`

#### **6. redline/gui/widgets/query_builder.py** (~150 LOC)
**Purpose:** Query building utilities
**Classes:**
- `AdvancedQueryBuilder`

#### **7. redline/gui/stock_analyzer_gui.py** (~400 LOC)
**Purpose:** Main GUI components
**Classes:**
- `StockAnalyzerGUI`

#### **8. redline/adapters/data_adapter.py** (~200 LOC)
**Purpose:** Data adapters for ML
**Classes:**
- `DataAdapter`

---

## 🌐 **Module B: redline/web/routes/data.py Refactoring**

### Current Structure (1,382 lines):
- 25+ route handlers
- File loading logic
- Filtering operations
- File browsing logic

### Proposed Split:

#### **1. redline/web/routes/data_tab.py** (~250 LOC)
**Purpose:** Main data tab routes
**Routes:**
- `GET /data/` - Main tab page
- `GET /data/simple` - Simple tab
- `GET /data/browser` - File browser

#### **2. redline/web/utils/file_loaders.py** (~400 LOC)
**Purpose:** File loading utilities
**Functions:**
- `_load_single_file_parallel()`
- `_load_files_parallel()`
- `_load_file_by_format()`
- `_load_large_file_chunked()`
- `_detect_format_from_path()`

#### **3. redline/web/routes/data_filtering.py** (~300 LOC)
**Purpose:** Data filtering operations
**Routes:**
- `POST /data/filter`
- `GET /data/columns/<filename>`
- Filter-specific logic

#### **4. redline/web/routes/data_browsing.py** (~250 LOC)
**Purpose:** File browsing operations
**Routes:**
- `GET /data/browse`
- `POST /data/browse`
- `POST /data/upload`
- Directory navigation

#### **5. redline/web/routes/data_loading.py** (~200 LOC)
**Purpose:** Data loading endpoints
**Routes:**
- `POST /data/load`
- `POST /data/load-from-path`
- `POST /data/load-chunk`
- `GET /data/files`

---

## 📊 **File Size Targets**

| Module | Target LOC | Current |
|--------|-----------|---------|
| data_loaders.py | 400 | 3,776 |
| data_formatters.py | 300 | - |
| data_validators.py | 200 | - |
| data_analyzers.py | 250 | - |
| virtual_scroll.py | 300 | - |
| query_builder.py | 150 | - |
| stock_analyzer_gui.py | 400 | - |
| data_adapter.py | 200 | - |
| data_tab.py | 250 | 1,382 |
| file_loaders.py | 400 | - |
| data_filtering.py | 300 | - |
| data_browsing.py | 250 | - |
| data_loading.py | 200 | - |

---

## 🚀 **Migration Strategy**

### Phase 1: Extract Utilities (Low Risk)
1. Extract validation functions → `data_validators.py`
2. Extract formatters → `data_formatters.py`
3. Extract analyzers → `data_analyzers.py`

### Phase 2: Extract GUI Components (Medium Risk)
1. Extract `VirtualScrollingTreeview` → `virtual_scroll.py`
2. Extract `AdvancedQueryBuilder` → `query_builder.py`
3. Extract `StockAnalyzerGUI` → `stock_analyzer_gui.py`

### Phase 3: Extract Web Routes (Medium Risk)
1. Extract file loading utils → `file_loaders.py`
2. Split routes by functionality → separate route files
3. Update imports and register blueprints

### Phase 4: Integration & Testing
1. Update all imports
2. Run tests
3. Fix any breaking changes

---

## ✅ **Benefits**

1. **Maintainability**: Each file has a single, clear responsibility
2. **Testability**: Easier to test focused modules
3. **Readability**: Developers can find code quickly
4. **Reusability**: Utilities can be imported where needed
5. **Collaboration**: Multiple developers can work on different modules
6. **Onboarding**: New developers can understand codebase faster

---

## ⚠️ **Risks & Mitigation**

1. **Import Errors**: Use find/replace and test after each step
2. **Breaking Changes**: Keep original files as backup
3. **Circular Dependencies**: Carefully manage imports
4. **Testing**: Run full test suite after each phase

---

## 📝 **Next Steps**

1. Create module structure
2. Extract utilities first (lowest risk)
3. Update imports incrementally
4. Test after each extraction
5. Clean up original files once tests pass

