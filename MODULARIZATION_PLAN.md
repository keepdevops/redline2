# REDLINE Code Modularization Plan

## 🎯 Target: Files under 400 LOC (ideally under 300)

### Current Issue: 13 files over 400 LOC

## 🔴 Critical (Over 500 LOC)

### 1. `data_module_shared.py` - 3,776 lines ❌ MASSIVE
**Problem:** Monolithic utility file
**Solution:** Split into separate modules:
- `redline/utils/file_helpers.py` - File operations
- `redline/utils/data_validation.py` - Data validation
- `redline/utils/date_utils.py` - Date formatting
- `redline/utils/parsers.py` - Format parsers

### 2. `redline/web/routes/data.py` - 1,382 lines ❌ VERY LARGE
**Problem:** Too many responsibilities
**Solution:** Split into:
- `redline/web/routes/data_tab.py` - Main tab route
- `redline/web/routes/data_file_loading.py` - File loading logic
- `redline/web/routes/data_filtering.py` - Filtering operations
- `redline/web/routes/data_browsing.py` - File browser

### 3. `redline/gui/converter_tab.py` - 871 lines ❌
**Solution:** Extract:
- `redline/gui/widgets/format_selector.py` - Format selection UI
- `redline/gui/utils/conversion_logic.py` - Conversion logic

### 4-10. GUI Files (750-830 lines each)
**Pattern:** Each has similar issues
**Solution:** Extract widgets and logic:
- Extract filter dialogs to `redline/gui/widgets/filters/`
- Extract data loading to `redline/gui/utils/`
- Extract view components to `redline/gui/components/`

## 📊 Recommended Module Size

| File Type | Ideal LOC | Max LOC | Target LOC |
|-----------|-----------|---------|------------|
| Routes    | 200-300   | 400     | 250        |
| GUI Tabs  | 300-400   | 500     | 350        |
| Tasks     | 200-300   | 400     | 250        |
| Database  | 400-500   | 600     | 450        |
| Utils     | 100-200   | 300     | 150        |

## 🎯 Priority Order

1. **data_module_shared.py** - Most critical (3,776 lines)
2. **redline/web/routes/data.py** - High priority (1,382 lines)
3. GUI files - Medium priority (6 files, 750-870 lines)
4. API routes - Low priority (695 lines, acceptable if organized)

## ✅ Files Already Well-Sized

- `redline/background/tasks.py` - 433 lines ✓
- `redline/web/routes/converter.py` - 460 lines ✓
- `redline/database/optimized_connector.py` - 563 lines (acceptable for database)

