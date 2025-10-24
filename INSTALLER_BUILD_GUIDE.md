# Multi-Platform Installer Build Guide

This guide explains how to build native installers for REDLINE across all major platforms using GitHub Actions.

## Overview

REDLINE now supports native installers for:
- **macOS**: DMG installer with app bundles (x64 and ARM64)
- **Windows**: NSIS installer and MSI package (x64 and ARM64)
- **Ubuntu**: DEB package with desktop integration (AMD64 and ARM64)

All installers are built automatically via GitHub Actions - no local setup required!

## Quick Start

### 1. Trigger a Build

**Option A: Create a Release Tag**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Option B: Manual Trigger**
1. Go to GitHub Actions tab
2. Select "Multi-Platform Installer Build"
3. Click "Run workflow"
4. Enter version number (e.g., 1.0.0)

### 2. Download Installers

After the build completes (15-20 minutes):
1. Go to GitHub Releases
2. Download installers for your platform and architecture:
   - `REDLINE-1.0.0-macOS.dmg` (macOS - Universal binary)
   - `REDLINE-1.0.0-Setup.exe` (Windows - Auto-detects architecture)
   - `REDLINE-1.0.0.msi` (Windows MSI - Auto-detects architecture)
   - `redline-financial_1.0.0_amd64.deb` (Ubuntu AMD64)
   - `redline-financial_1.0.0_arm64.deb` (Ubuntu ARM64)

## Platform-Specific Details

### macOS DMG Installer

**Features:**
- Drag-and-drop installation
- REDLINE.app and REDLINE Web.app bundles
- Applications folder integration
- Code signing support (optional)

**Installation:**
1. Download `REDLINE-1.0.0-macOS.dmg`
2. Double-click to mount
3. Drag apps to Applications folder
4. Launch from Applications or Spotlight

**Code Signing:**
- Requires Apple Developer account
- Set `MACOS_CERT_ID` secret in GitHub
- Enables Gatekeeper compatibility

### Windows Installers

**NSIS Installer (`REDLINE-1.0.0-Setup.exe`):**
- Professional installation wizard
- Start Menu shortcuts
- Desktop shortcuts (optional)
- PATH configuration
- Uninstaller in Control Panel

**MSI Package (`REDLINE-1.0.0.msi`):**
- Enterprise deployment ready
- Group Policy compatible
- Silent installation support
- Same features as NSIS installer

**Installation:**
1. Download installer
2. Run as Administrator
3. Follow installation wizard
4. Launch from Start Menu or Desktop

**Code Signing:**
- Requires Windows code signing certificate
- Set `WINDOWS_CERT_BASE64` and `WINDOWS_CERT_PASSWORD` secrets
- Eliminates Windows security warnings

### Ubuntu DEB Package

**Features:**
- Native package management
- Desktop application entries
- Command-line integration
- Automatic PATH setup
- Multi-user support

**Installation:**
```bash
# Download DEB package
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0/redline-financial_1.0.0_amd64.deb

# Install package
sudo dpkg -i redline-financial_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Start REDLINE
cd ~
redline-web
```

**Important Notes:**
- Always run `cd ~` before starting REDLINE
- Data is stored in `~/redline-data/`
- Web interface runs on `localhost:8080`

**Code Signing:**
- Uses GPG (free)
- Set `GPG_PRIVATE_KEY` and `GPG_KEY_ID` secrets
- Enables APT repository integration

## GitHub Actions Secrets

### Required for Code Signing (Optional)

**macOS:**
- `MACOS_CERT_ID`: Apple Developer certificate ID

**Windows:**
- `WINDOWS_CERT_BASE64`: Base64-encoded certificate (.pfx file)
- `WINDOWS_CERT_PASSWORD`: Certificate password

**Ubuntu:**
- `GPG_PRIVATE_KEY`: GPG private key
- `GPG_KEY_ID`: GPG key ID

### Setting Up Secrets

1. Go to repository Settings
2. Navigate to Secrets and Variables > Actions
3. Click "New repository secret"
4. Add each secret with appropriate values

## Build Process

### Automated Build Steps

1. **Checkout Code**: Get latest source
2. **Setup Python**: Install Python 3.11
3. **Install Dependencies**: Install requirements and PyInstaller
4. **Build Executables**: Create platform-specific executables
5. **Create Installers**: Build native installers
6. **Code Signing**: Sign installers (if certificates available)
7. **Upload Artifacts**: Make installers available for download
8. **Create Release**: Publish to GitHub Releases

### Build Times

- **macOS DMG**: ~8 minutes
- **Windows Installers**: ~10 minutes
- **Ubuntu DEB**: ~6 minutes
- **Total**: ~15 minutes (parallel builds)

## Testing Installers

### macOS Testing
- [ ] Download DMG from GitHub Releases
- [ ] Mount DMG and verify contents
- [ ] Drag apps to Applications folder
- [ ] Launch REDLINE.app
- [ ] Launch REDLINE Web.app
- [ ] Test web interface at localhost:8080
- [ ] Verify data directory creation

### Windows Testing
- [ ] Download installer from GitHub Releases
- [ ] Run installer as Administrator
- [ ] Accept security warning (if unsigned)
- [ ] Verify installation to Program Files
- [ ] Check Start Menu shortcuts
- [ ] Test `redline-web` from Command Prompt
- [ ] Verify web interface at localhost:8080
- [ ] Test uninstaller

### Ubuntu Testing
- [ ] Download DEB from GitHub Releases
- [ ] Install: `sudo dpkg -i redline-financial_1.0.0_amd64.deb`
- [ ] Fix dependencies: `sudo apt-get install -f`
- [ ] Check symlinks: `which redline-web`
- [ ] Verify desktop entries in Applications menu
- [ ] Test: `cd ~ && redline-web`
- [ ] Verify data directory: `ls ~/redline-data`
- [ ] Test web interface at localhost:8080
- [ ] Uninstall: `sudo apt-get remove redline-financial`

## Troubleshooting

### Common Issues

**macOS:**
- "App is damaged" error: Disable Gatekeeper or use signed DMG
- Apps won't launch: Check System Preferences > Security & Privacy

**Windows:**
- "Windows protected your PC" warning: Normal for unsigned installers
- PATH not updated: Restart Command Prompt or reboot
- Permission denied: Run installer as Administrator

**Ubuntu:**
- "cd ~" requirement: Always run from home directory
- Permission errors: Check file ownership in ~/redline-data
- Desktop entries missing: Run `update-desktop-database`

### Getting Help

- Check GitHub Issues for known problems
- Review build logs in GitHub Actions
- Test with unsigned installers first
- Verify Python 3.11+ compatibility

## Advanced Configuration

### Custom Build Scripts

All installer scripts are in `build/installers/`:
- `macos/build_dmg.sh`: DMG creation
- `macos/create_app_bundle.sh`: App bundle creation
- `windows/redline.nsi`: NSIS installer script
- `ubuntu/build_deb.sh`: DEB package creation

### Modifying Installers

1. Edit appropriate script in `build/installers/`
2. Test locally if possible
3. Push changes to trigger new build
4. Download and test new installer

### Adding Code Signing

1. Obtain appropriate certificates
2. Add secrets to GitHub repository
3. Push changes to trigger signed build
4. Verify signatures on downloaded installers

## Future Enhancements

- **macOS**: App Store distribution
- **Windows**: Microsoft Store package
- **Ubuntu**: PPA repository
- **Cross-platform**: Universal installer script
- **Enterprise**: Silent installation options

---

For more information, visit the [REDLINE GitHub repository](https://github.com/keepdevops/redline2).


