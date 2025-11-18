# Refactoring Plan: data_module_shared.py (3,776 LOC → ~19 files of ~200 LOC)

## Current Structure Analysis

**File**: `data_module_shared.py` - 3,776 lines

### Classes Identified:
1. **DataLoader** (line 35-493) - ~458 LOC
2. **DatabaseConnector** (line 494-558) - ~64 LOC  
3. **DataAdapter** (line 559-590) - ~31 LOC
4. **VirtualScrollingTreeview** (line 591-665) - ~74 LOC
5. **AdvancedQueryBuilder** (line 666-729) - ~63 LOC
6. **DataSource** (line 730-792) - ~62 LOC
7. **StockAnalyzerGUI** (line 793-3759) - ~2,966 LOC ⚠️ **HUGE**
8. **run() function** (line 3760-3776) - ~16 LOC

## Refactoring Strategy

### Phase 1: Extract Standalone Classes (Low Risk)

#### 1. DataLoader Class → `redline/core/data_loader_legacy.py` (~400 LOC)
**Extract**: Lines 35-493
- `clean_and_select_columns()` static method
- `__init__()`
- `validate_data()`
- `load_data()`
- `convert_format()`
- `save_to_shared()`
- `_standardize_txt_columns()`
- `load_file_by_type()` static method
- `save_file_by_type()` static method
- `analyze_ticker_distribution()`
- `filter_data_by_date_range()`
- `balance_ticker_data()`

**Note**: This is legacy code - may already exist in `redline/core/data_loader.py`

#### 2. DatabaseConnector Class → `redline/database/legacy_connector.py` (~65 LOC)
**Extract**: Lines 494-558
- `__init__()`
- `create_connection()`
- `read_shared_data()`
- `write_shared_data()`

**Note**: May duplicate existing `redline/database/connector.py`

#### 3. DataAdapter Class → `redline/core/data_adapter.py` (~32 LOC)
**Extract**: Lines 559-590
- `prepare_training_data()`
- `prepare_rl_state()`
- `summarize_preprocessed()`

#### 4. VirtualScrollingTreeview → `redline/gui/widgets/virtual_treeview_legacy.py` (~75 LOC)
**Extract**: Lines 591-665
- All virtual scrolling functionality

**Note**: May duplicate existing `redline/gui/widgets/virtual_treeview.py`

#### 5. AdvancedQueryBuilder → `redline/database/query_builder_legacy.py` (~64 LOC)
**Extract**: Lines 666-729
- Query building logic

**Note**: May duplicate existing `redline/database/query_builder.py`

#### 6. DataSource Class → `redline/gui/widgets/data_source_legacy.py` (~63 LOC)
**Extract**: Lines 730-792
- Data source management

**Note**: May duplicate existing `redline/gui/widgets/data_source.py`

### Phase 2: Split StockAnalyzerGUI (High Risk - 2,966 LOC)

This is the largest component. Split into:

#### 7. GUI Main Window → `redline/gui/legacy/main_window.py` (~300 LOC)
- Window initialization
- Notebook setup
- Main layout

#### 8. GUI Data Loader Tab → `redline/gui/legacy/loader_tab.py` (~400 LOC)
- File selection
- Format selection
- Loading operations
- Progress tracking

#### 9. GUI Data View Tab → `redline/gui/legacy/view_tab.py` (~500 LOC)
- File browser
- Data viewer
- Treeview setup
- Display logic

#### 10. GUI Filtering → `redline/gui/legacy/filtering.py` (~300 LOC)
- Basic filters
- Advanced filters
- Query builder integration
- Filter application

#### 11. GUI Search → `redline/gui/legacy/search.py` (~200 LOC)
- Search functionality
- Search results
- Search UI

#### 12. GUI Export → `redline/gui/legacy/export.py` (~200 LOC)
- Export operations
- Format conversion
- File saving

#### 13. GUI Utilities → `redline/gui/legacy/gui_utils.py` (~200 LOC)
- Error dialogs
- Tooltips
- Keyboard shortcuts
- Clipboard operations

#### 14. GUI Event Handlers → `redline/gui/legacy/event_handlers.py` (~300 LOC)
- Button click handlers
- Selection handlers
- Navigation handlers

#### 15. GUI Data Operations → `redline/gui/legacy/data_ops.py` (~300 LOC)
- Data loading
- Data processing
- Data validation
- Data cleaning

#### 16. GUI Statistics → `redline/gui/legacy/statistics.py` (~200 LOC)
- Statistics display
- Analysis functions
- Reporting

#### 17. GUI Configuration → `redline/gui/legacy/config.py` (~200 LOC)
- Configuration loading
- Settings management
- Preferences

### Phase 3: Extract Utility Functions

#### 18. File Operations → `redline/utils/file_ops_legacy.py` (~200 LOC)
- File loading helpers
- File saving helpers
- Format detection
- Path utilities

#### 19. Data Validation → `redline/utils/data_validation_legacy.py` (~200 LOC)
- Data validation functions
- Schema validation
- Type checking

## Implementation Order

1. **Start with standalone classes** (Phase 1) - Lower risk
2. **Extract utilities** (Phase 3) - Medium risk
3. **Split GUI class** (Phase 2) - Higher risk, do last

## File Size Targets

Each new file should be **≤200 LOC**:
- Some files may be slightly over (up to 250 LOC acceptable)
- Split further if needed
- Combine small related pieces if under 150 LOC

## Next Steps

1. Create new module files
2. Extract code sections
3. Update imports
4. Test functionality
5. Remove old code

Would you like me to start with Phase 1 (extracting standalone classes)?

