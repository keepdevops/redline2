# Clarification: "Legacy" Modules

## The Confusion

You're right to question the "legacy" naming! Here's what's actually happening:

## What "Legacy" Actually Means

**"Legacy" = Extracted from the old monolithic `data_module_shared.py` file**

The `*_legacy.py` modules are:
- ✅ **NEW refactored code** (better organized, ≤200 LOC each)
- ✅ **Extracted from** the old `data_module_shared.py` (3,776 LOC)
- ❌ **NOT deprecated/old code**
- ❌ **NOT currently used** in Dockerfile or main app

## Current State

### What's Actually Being Used

**Dockerfile (`Dockerfile.webgui.bytecode`):**
- Uses: `web_app.py` (web version)
- Does NOT use: `data_module_shared.py`
- Does NOT use: `*_legacy.py` modules

**`main.py` (Tkinter GUI):**
- Uses: `redline.core.data_loader` (NEW module, already exists)
- Uses: `redline.database.connector` (NEW module, already exists)
- Does NOT use: `data_module_shared.py`
- Does NOT use: `*_legacy.py` modules

**`data_module_shared.py`:**
- OLD monolithic file (3,776 LOC)
- Still exists in codebase
- Only used by: `simple_feather_test.py` (test file)
- Should be replaced/removed

## The Problem

1. **Confusing naming**: "legacy" suggests old/deprecated code
2. **Two sets of modules exist**:
   - `redline.core.data_loader` (already in use, 292 LOC)
   - `redline.core.data_loader_legacy` (extracted from old file, 133 LOC)
3. **Different purposes**:
   - Existing modules: Used by main app
   - Legacy modules: Refactored from old monolithic file (not yet integrated)

## Recommendation

### Option 1: Rename "Legacy" to "Shared"
Rename to indicate they came from the "shared" module:
- `data_loader_legacy.py` → `data_loader_shared.py`
- `legacy_connector.py` → `connector_shared.py`

### Option 2: Keep for Reference Only
- Keep `*_legacy.py` modules as reference
- Don't use them in production
- Use existing `redline.core.data_loader` instead

### Option 3: Merge Best Parts
- Compare existing vs legacy modules
- Merge the best parts
- Keep one unified set

## Answer to Your Question

**Q: Are these "legacy" files what we're using in Dockerfile?**

**A: NO** - The Dockerfile uses:
- `web_app.py` (which uses `redline.core.data_loader`, NOT the legacy modules)
- The `*_legacy.py` modules are refactored code extracted from the old monolithic file
- They're not yet integrated into the main application

## Next Steps

1. **Decide on naming**: Rename "legacy" to something clearer?
2. **Check if needed**: Do we need these modules, or should we use existing ones?
3. **Integration**: If we want to use them, integrate them into the app
4. **Cleanup**: Remove `data_module_shared.py` once refactoring is complete

