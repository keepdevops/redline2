# Legacy Naming Explanation

## The Confusion

The "legacy" naming in the refactored modules is **confusing** and needs clarification.

## What "Legacy" Actually Means

**"Legacy" = Extracted from the old monolithic file**

The modules named `*_legacy.py` are:
- ✅ **NEW refactored code** extracted from `data_module_shared.py`
- ✅ **Better organized** (≤200 LOC each)
- ✅ **Modern structure** (proper modules)
- ❌ **NOT deprecated/old code**

## Current State

### What's Actually Being Used

**`main.py` uses:**
- `redline.core.data_loader` (NEW module - already exists)
- `redline.database.connector` (NEW module - already exists)
- `redline.gui.main_window` (NEW module - already exists)

**`data_module_shared.py` is:**
- The OLD monolithic file (3,776 LOC)
- Still exists but should be replaced
- Contains old code that needs refactoring

**The `*_legacy.py` modules are:**
- Extracted from `data_module_shared.py`
- Refactored versions of the old code
- Ready to replace the old file

## The Problem

1. **Naming is confusing**: "legacy" suggests old/deprecated
2. **Two sets of modules exist**:
   - NEW modules: `redline.core.data_loader` (already in use)
   - LEGACY modules: `redline.core.data_loader_legacy` (extracted from old file)
3. **Need to decide**: Which ones should we use?

## Recommendation

### Option 1: Rename "Legacy" Modules
Rename `*_legacy.py` to something clearer:
- `data_loader_legacy.py` → `data_loader_shared.py` (from shared module)
- Or: `data_loader_legacy.py` → `data_loader_monolithic.py` (from monolithic)

### Option 2: Merge with Existing Modules
- Compare `redline.core.data_loader` vs `redline.core.data_loader_legacy`
- Merge the best parts
- Keep one set of modules

### Option 3: Keep Both (Different Purposes)
- `redline.core.data_loader` = Web app version
- `redline.core.data_loader_legacy` = Tkinter GUI version
- Both serve different purposes

## Next Steps

1. **Check if `data_module_shared.py` is still being used**
2. **Compare new vs legacy modules** to see if they overlap
3. **Decide on naming convention** or merge strategy
4. **Update imports** to use the correct modules

## Current Usage

- **Dockerfile**: Uses `web_app.py` (web version)
- **main.py**: Uses new modules (`redline.core.data_loader`)
- **data_module_shared.py**: Old file, may still be imported somewhere
- **Legacy modules**: Extracted but not yet integrated

