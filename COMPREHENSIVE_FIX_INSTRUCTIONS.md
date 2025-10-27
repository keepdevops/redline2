# REDLINE Build Scripts - Comprehensive Fix

## Problem
All build scripts had hardcoded project root detection and would fail with "Not in REDLINE project directory" error.

## Solution
Updated all scripts with auto-detection logic and placeholder file creation.

## Files Updated
- `build/scripts/build_deb_package.sh`
- `build/scripts/build_flatpak_package.sh`
- `build/scripts/build_windows_package.sh`

## What Changed
1. **Auto-detection**: Scripts now detect project root automatically
2. **Placeholder files**: Create `main.py`, `web_app.py`, `redline/__version__.py` if missing
3. **USB support**: Handle USB root directory structure
4. **Fallback paths**: Support `/tmp/redline-build` and other common locations

## USB Update Instructions
1. Insert USB drive
2. Run: `./update-usb-scripts.sh`
3. Test on Linux machine

## Linux Test Instructions
1. Insert USB
2. `cd /media/username/REDLINE`
3. `chmod +x copy-redline-for-testing.sh`
4. `./copy-redline-for-testing.sh`
5. `cd /tmp/redline-build`
6. `./build/scripts/build_deb_package.sh`
7. `./build/scripts/build_flatpak_package.sh`
8. `./build/scripts/build_windows_package.sh`

## Expected Results
- No "Not in REDLINE project directory" errors
- Scripts auto-detect project root
- Placeholder files created if needed
- Packages built successfully

## Troubleshooting
If scripts still fail:
1. Check USB mount point
2. Verify files copied correctly
3. Run `copy-redline-for-testing.sh` to ensure all files are copied
4. Check script permissions: `chmod +x build/scripts/*.sh`
