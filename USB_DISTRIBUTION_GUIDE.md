# REDLINE USB Distribution Guide

This guide explains how to create and distribute REDLINE via USB drives for offline installation.

## Overview

The USB distribution system provides:
- **Complete offline installation** - No internet required
- **All platform installers** - Windows, macOS, Ubuntu
- **Professional presentation** - Auto-run capabilities
- **Easy navigation** - Platform-specific folders
- **Source code included** - For developers
- **Comprehensive documentation** - User guides

## Quick Start

### 1. Create USB Distribution
```bash
# Build all installers and create USB package
bash build/usb-distribution/create_usb_distribution.sh
```

### 2. Copy to USB Drive
```bash
# Copy distribution to USB drive
bash build/usb-distribution/copy_to_usb.sh
```

### 3. Distribute USB
- Give USB to users
- Users follow platform-specific instructions
- Complete offline installation

## USB Structure

```
REDLINE-USB/
├── Installers/
│   ├── Windows/
│   │   ├── REDLINE-1.0.0-Setup.exe
│   │   ├── REDLINE-1.0.0.msi
│   │   └── README.txt
│   ├── macOS/
│   │   ├── REDLINE-1.0.0-macOS.dmg
│   │   └── README.txt
│   ├── Ubuntu/
│   │   ├── redline-financial_1.0.0_amd64.deb
│   │   └── README.txt
│   └── Manual/
│       ├── redline-gui-windows-x64.exe
│       ├── redline-web-windows-x64.exe
│       ├── redline-gui-darwin-arm64
│       ├── redline-web-darwin-arm64
│       ├── redline-gui-linux-amd64
│       └── redline-web-linux-amd64
├── Documentation/
│   ├── INSTALLER_BUILD_GUIDE.md
│   ├── INSTALLER_USER_GUIDE.md
│   ├── README.md
│   └── Additional guides
├── Source/
│   ├── redline/
│   ├── licensing/
│   ├── requirements.txt
│   └── Configuration files
├── Scripts/
│   ├── launch_redline_usb.bat (Windows)
│   ├── launch_redline_usb.command (macOS)
│   └── launch_redline_usb.sh (Linux)
├── README.txt (Main instructions)
├── INSTALLATION_SUMMARY.txt
└── autorun.inf (Windows auto-run)
```

## Step-by-Step Process

### 1. Prepare USB Drive

**Format USB Drive:**
- **Windows**: Format as FAT32 or exFAT
- **macOS**: Format as MS-DOS (FAT) or exFAT
- **Linux**: Format as FAT32 or exFAT

**USB Size Requirements:**
- Minimum: 2GB
- Recommended: 4GB+
- Distribution size: ~500MB

### 2. Create Distribution

**Run Distribution Script:**
```bash
bash build/usb-distribution/create_usb_distribution.sh
```

**What This Does:**
- Builds all platform installers
- Creates organized directory structure
- Generates platform-specific documentation
- Creates auto-run scripts
- Packages everything for USB distribution

**Output:**
- `dist/usb-distribution/REDLINE-USB-1.0.0/` - Complete USB package
- `dist/usb-distribution/REDLINE-USB-1.0.0.tar.gz` - Archive version
- `dist/usb-distribution/REDLINE-USB-1.0.0.zip` - Windows-compatible archive

### 3. Copy to USB

**Automatic Copy:**
```bash
bash build/usb-distribution/copy_to_usb.sh
```

**Manual Copy:**
```bash
# Mount USB drive
# Copy distribution folder
cp -r dist/usb-distribution/REDLINE-USB-1.0.0 /media/user/REDLINE-USB
```

### 4. Test USB Distribution

**Windows Testing:**
1. Insert USB drive
2. Auto-run should launch installer
3. Test installation process
4. Verify web interface works

**macOS Testing:**
1. Insert USB drive
2. Double-click `launch_redline_usb.command`
3. Test DMG installation
4. Verify app bundles work

**Ubuntu Testing:**
1. Insert USB drive
2. Run `launch_redline_usb.sh`
3. Test DEB installation
4. Verify `cd ~ && redline-web` works

## Platform-Specific Instructions

### Windows Users

**Installation:**
1. Insert USB drive
2. Auto-run launches installer
3. Run `REDLINE-1.0.0-Setup.exe` as Administrator
4. Follow installation wizard
5. Launch from Start Menu

**Manual Installation:**
1. Navigate to `Installers/Manual/`
2. Copy `redline-web-windows-x64.exe`
3. Run executable directly
4. No installation required

### macOS Users

**Installation:**
1. Insert USB drive
2. Double-click `launch_redline_usb.command`
3. Double-click `REDLINE-1.0.0-macOS.dmg`
4. Drag apps to Applications folder
5. Launch from Applications

**Manual Installation:**
1. Navigate to `Installers/Manual/`
2. Copy `redline-web-darwin-arm64`
3. Make executable: `chmod +x redline-web-darwin-arm64`
4. Run: `./redline-web-darwin-arm64`

### Ubuntu Users

**Installation:**
1. Insert USB drive
2. Run `launch_redline_usb.sh`
3. Install: `sudo dpkg -i redline-financial_1.0.0_amd64.deb`
4. Fix dependencies: `sudo apt-get install -f`
5. Start: `cd ~ && redline-web`

**Manual Installation:**
1. Navigate to `Installers/Manual/`
2. Copy `redline-web-linux-amd64`
3. Make executable: `chmod +x redline-web-linux-amd64`
4. Run: `cd ~ && ./redline-web-linux-amd64`

## Auto-Run Features

### Windows Auto-Run
- `autorun.inf` enables automatic launch
- Runs `launch_redline_usb.bat` on USB insertion
- Opens Windows installer folder
- Provides installation instructions

### macOS Auto-Run
- `launch_redline_usb.command` script
- Double-click to launch
- Opens macOS installer folder
- Provides installation instructions

### Linux Auto-Run
- `launch_redline_usb.sh` script
- Run with `bash launch_redline_usb.sh`
- Opens Ubuntu installer folder
- Provides installation instructions

## USB Distribution Benefits

### For Distributors
- **Complete offline distribution** - No internet required
- **Professional presentation** - Auto-run capabilities
- **All platforms included** - Single USB for all users
- **Easy updates** - Replace USB contents for new versions
- **Cost effective** - Physical distribution method

### For Users
- **No internet required** - Complete offline installation
- **Platform-specific guidance** - Clear instructions per OS
- **Multiple installation methods** - Installer or manual
- **Source code included** - For developers
- **Comprehensive documentation** - All guides included

## Troubleshooting

### USB Not Auto-Running
- **Windows**: Check if autorun is disabled in Group Policy
- **macOS**: Double-click `launch_redline_usb.command` manually
- **Linux**: Run `bash launch_redline_usb.sh` manually

### Installation Issues
- **Windows**: Run installer as Administrator
- **macOS**: Allow apps from anywhere in Security settings
- **Ubuntu**: Always run `cd ~` before starting REDLINE

### USB Space Issues
- **Minimum**: 2GB USB drive required
- **Recommended**: 4GB+ for comfortable operation
- **Distribution**: ~500MB total size

### Permission Issues
- **Linux**: Ensure USB is mounted with proper permissions
- **macOS**: Check USB permissions in Disk Utility
- **Windows**: Run copy script as Administrator if needed

## Advanced Usage

### Custom USB Branding
- Replace `Scripts/redline.ico` with custom icon
- Modify `README.txt` with company information
- Add custom documentation to `Documentation/` folder

### Enterprise Distribution
- Create multiple USB drives for different departments
- Include company-specific configuration files
- Add enterprise installation scripts

### Developer Distribution
- Source code included in `Source/` folder
- Complete development environment
- All dependencies listed in `requirements.txt`

## Maintenance

### Updating USB Distribution
1. Run `create_usb_distribution.sh` with new version
2. Replace USB contents with new distribution
3. Update version numbers in documentation
4. Test on all target platforms

### Version Control
- USB distributions are versioned (e.g., `REDLINE-USB-1.0.0`)
- Keep archives of previous versions
- Document changes between versions

## Security Considerations

### Unsigned Installers
- All installers are unsigned by default
- Users will see security warnings (normal)
- Consider code signing for enterprise distribution

### USB Security
- USB drives can carry malware
- Scan USB before distribution
- Use trusted USB drives only
- Consider encrypted USB drives for sensitive distribution

## Support

### Documentation
- All guides included in `Documentation/` folder
- Platform-specific README files
- Installation summaries and troubleshooting

### Getting Help
- GitHub Issues: https://github.com/keepdevops/redline2/issues
- Email: support@redline.example.com
- Documentation: Included in USB distribution

---

**USB Distribution Complete!** 🎉

REDLINE is now ready for offline distribution via USB drives across all major platforms.




