# Linux Test Computer - Quick Reference Guide

## 🚀 Approach 1: Complete Fix Script

### Step 1: Insert USB Drive
- Insert USB drive into Linux computer
- USB will usually auto-mount at `/media/username/REDLINE`

### Step 2: Navigate to USB Drive
```bash
cd /media/username/REDLINE
```

### Step 3: Run the Fix Script
```bash
chmod +x fix-usb-permissions.sh
./fix-usb-permissions.sh
```

## 📋 What the Fix Script Does

### ✅ Automatic Detection
- Finds USB drive automatically
- Checks common mount points
- Verifies USB drive contents

### ✅ Prerequisites Installation
- Installs Python 3, pip3, dpkg-dev
- Installs flatpak, flatpak-builder
- Installs PyInstaller
- Sets up Flatpak runtime

### ✅ Permission Fixing
- Tries to fix USB permissions
- If USB is read-only, copies to `/tmp/redline-build/`
- Makes all scripts executable
- Creates project structure

### ✅ Ready to Use
- All automation scripts ready
- Project structure created
- Prerequisites installed

## 🎯 After Running the Fix Script

### Run DEB Package Automation
```bash
cd /tmp/redline-build
./scripts/build_deb_package.sh
```

### Run Flatpak Package Automation
```bash
cd /tmp/redline-build
./scripts/build_flatpak_package.sh
```

### Run Windows Package Automation
```bash
cd /tmp/redline-build
./scripts/build_windows_package.sh
```

## 📦 Expected Results

### DEB Packages
- `dist/deb-package/repository/redline-financial_1.0.0_amd64.deb`
- `dist/deb-package/repository/redline-financial_1.0.0_arm64.deb`

### Flatpak Packages
- `dist/flatpak-package/com.redline.financial-1.0.0.flatpak`

### Windows Packages
- `dist/windows-package/` with all Windows files

## 🔧 Troubleshooting

### If USB Drive Not Found
```bash
# Check mount points
ls /media/
ls /mnt/
ls /run/media/

# Check mount status
mount | grep REDLINE
```

### If Script Fails
```bash
# Manual copy
cp -r /media/username/REDLINE/build/ /tmp/redline-build/
chmod +x /tmp/redline-build/scripts/*.sh
cd /tmp/redline-build
./scripts/build_deb_package.sh
```

### If Prerequisites Missing
```bash
# Install manually
sudo apt update
sudo apt install python3 python3-pip dpkg-dev flatpak flatpak-builder
pip3 install pyinstaller
```

## 🎉 Success Indicators

- ✅ Script runs without errors
- ✅ Prerequisites installed
- ✅ Scripts copied to `/tmp/redline-build/`
- ✅ All scripts executable
- ✅ Project structure created
- ✅ Ready to run automation

---

**The fix script handles everything automatically!** 🚀
