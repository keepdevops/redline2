# REDLINE USB Package Extraction Instructions

## Overview

This guide provides step-by-step instructions for extracting the `REDLINE-1.0.0-USB-Test-Package.tar.gz` archive on different platforms.

## Prerequisites

- USB drive with REDLINE files
- Terminal/Command Prompt access
- Sufficient disk space (~1GB recommended)

---

## 🍎 macOS (macOS 10.12+)

### Method 1: Using Terminal (Recommended)
```bash
# Navigate to USB drive
cd /Volumes/REDLINE

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

### Method 2: Using Finder
1. Navigate to USB drive in Finder
2. Double-click `REDLINE-1.0.0-USB-Test-Package.tar.gz`
3. Archive Utility will automatically extract to `usb-package` folder

### Method 3: Using Archive Utility
1. Open Archive Utility (Applications > Utilities > Archive Utility)
2. Drag `REDLINE-1.0.0-USB-Test-Package.tar.gz` to Archive Utility
3. Extraction will complete automatically

---

## 🪟 Windows (Windows 10/11)

### Method 1: Using PowerShell (Recommended)
```powershell
# Navigate to USB drive (adjust drive letter as needed)
cd E:\

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
dir usb-package
```

### Method 2: Using Command Prompt
```cmd
# Navigate to USB drive (adjust drive letter as needed)
cd /d E:\

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
dir usb-package
```

### Method 3: Using 7-Zip
1. Install 7-Zip from https://www.7-zip.org/
2. Right-click `REDLINE-1.0.0-USB-Test-Package.tar.gz`
3. Select "7-Zip" > "Extract Here"
4. Folder `usb-package` will be created

### Method 4: Using WinRAR
1. Install WinRAR from https://www.win-rar.com/
2. Right-click `REDLINE-1.0.0-USB-Test-Package.tar.gz`
3. Select "Extract Here"
4. Folder `usb-package` will be created

---

## 🐧 Ubuntu/Debian (Ubuntu 18.04+)

### Method 1: Using Terminal (Recommended)
```bash
# Navigate to USB drive (adjust mount point as needed)
cd /media/username/REDLINE

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

### Method 2: Using File Manager
1. Open Files (Nautilus)
2. Navigate to USB drive
3. Right-click `REDLINE-1.0.0-USB-Test-Package.tar.gz`
4. Select "Extract Here"
5. Folder `usb-package` will be created

### Method 3: Using Archive Manager
1. Open Archive Manager
2. File > Open > Select the tar.gz file
3. Click "Extract" button
4. Choose extraction location

---

## 🐧 Other Linux Distributions

### CentOS/RHEL/Fedora
```bash
# Navigate to USB drive
cd /media/username/REDLINE

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

### Arch Linux
```bash
# Navigate to USB drive
cd /run/media/username/REDLINE

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

---

## 📱 Android (Using Termux)

### Prerequisites
- Install Termux from F-Droid or Google Play
- USB OTG adapter for USB drive access

```bash
# Install tar if not available
pkg install tar

# Navigate to USB drive (path may vary)
cd /storage/usbotg

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

---

## 🍎 iOS (Using iSH Terminal)

### Prerequisites
- Install iSH Terminal from App Store
- USB drive accessible through Files app

```bash
# Navigate to USB drive location
cd /mnt/usb

# Extract the archive
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Verify extraction
ls -la usb-package/
```

---

## 🔍 Verification Steps

After extraction, verify the package contents:

### Check Package Structure
```bash
# Navigate to extracted folder
cd usb-package

# List contents
ls -la

# Expected structure:
# macOS/
# Windows/
# Ubuntu/
# Documentation/
# README.txt
# PACKAGE_INFO.txt
```

### Check Platform-Specific Contents
```bash
# macOS contents
ls -la macOS/

# Windows contents  
ls -la Windows/

# Ubuntu contents
ls -la Ubuntu/

# Documentation
ls -la Documentation/
```

---

## 🚨 Troubleshooting

### Common Issues

#### "tar: command not found"
**Solution**: Install tar utility
- **Ubuntu/Debian**: `sudo apt install tar`
- **CentOS/RHEL**: `sudo yum install tar`
- **macOS**: Usually pre-installed
- **Windows**: Use PowerShell or install tar

#### "Permission denied"
**Solution**: Use sudo or check file permissions
```bash
# Linux/macOS
sudo tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz

# Or check permissions
ls -la REDLINE-1.0.0-USB-Test-Package.tar.gz
```

#### "No space left on device"
**Solution**: Free up disk space or extract to different location
```bash
# Extract to different location
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz -C /tmp/
```

#### "Archive format not recognized"
**Solution**: Verify file integrity
```bash
# Check file type
file REDLINE-1.0.0-USB-Test-Package.tar.gz

# Should show: gzip compressed data
```

---

## 📋 Post-Extraction Steps

### 1. Read Documentation
```bash
# Read main instructions
cat usb-package/README.txt

# Read package info
cat usb-package/PACKAGE_INFO.txt
```

### 2. Platform-Specific Installation
- **macOS**: Use files in `macOS/` directory
- **Windows**: Use files in `Windows/` directory  
- **Ubuntu**: Use files in `Ubuntu/` directory

### 3. Security Configuration
- Review `Documentation/SECURITY_GUIDE.md`
- Set up environment variables as needed
- Configure API keys securely

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review platform-specific documentation
3. Verify USB drive is properly mounted
4. Ensure sufficient disk space is available

---

## 🎯 Quick Reference

| Platform | Command | Notes |
|----------|---------|-------|
| macOS | `tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz` | Built-in tar |
| Windows | `tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz` | PowerShell/CMD |
| Ubuntu | `tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz` | Built-in tar |
| Android | `tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz` | Termux required |
| iOS | `tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz` | iSH required |

**Note**: Adjust USB drive path (`/Volumes/REDLINE`, `E:\`, `/media/username/REDLINE`) based on your system's mount point.
