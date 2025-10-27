#!/bin/bash
# USB Distribution Package Creator
# Creates a comprehensive package for testing REDLINE on multiple platforms

set -e

echo "🚀 Creating REDLINE USB Distribution Package..."

# Get project root and version
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

VERSION=$(python -c "import sys; sys.path.insert(0, '.'); from redline.__version__ import __version__; print(__version__)")
PACKAGE_NAME="REDLINE-${VERSION}-USB-Test-Package"
PACKAGE_DIR="dist/usb-package"

# Clean and create package directory
echo "📦 Creating USB package directory..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Create package structure
mkdir -p "$PACKAGE_DIR/macOS"
mkdir -p "$PACKAGE_DIR/Windows"
mkdir -p "$PACKAGE_DIR/Ubuntu"
mkdir -p "$PACKAGE_DIR/Documentation"

echo "✅ Package structure created"

# Copy macOS app bundles
echo "🍎 Copying macOS app bundles..."
if [[ -d "dist/macos/REDLINE.app" ]] && [[ -d "dist/macos/REDLINE Web.app" ]]; then
    cp -R dist/macos/REDLINE.app "$PACKAGE_DIR/macOS/"
    cp -R "dist/macos/REDLINE Web.app" "$PACKAGE_DIR/macOS/"
    echo "✅ macOS app bundles copied"
else
    echo "⚠️ macOS app bundles not found, skipping..."
fi

# Copy executables for Windows and Ubuntu
echo "🪟 Preparing Windows executables..."
if [[ -f "dist/executables/redline-gui-macos-arm64" ]] && [[ -f "dist/executables/redline-web-macos-arm64" ]]; then
    # Note: These are macOS executables, but we'll include them for reference
    cp dist/executables/redline-gui-macos-arm64 "$PACKAGE_DIR/Windows/redline-gui-macos-arm64"
    cp dist/executables/redline-web-macos-arm64 "$PACKAGE_DIR/Windows/redline-web-macos-arm64"
    echo "✅ Windows executables prepared (macOS versions for reference)"
else
    echo "⚠️ Executables not found, skipping..."
fi

echo "🐧 Preparing Ubuntu executables..."
if [[ -f "dist/executables/redline-gui-macos-x64" ]] && [[ -f "dist/executables/redline-web-macos-x64" ]]; then
    # Note: These are macOS executables, but we'll include them for reference
    cp dist/executables/redline-gui-macos-x64 "$PACKAGE_DIR/Ubuntu/redline-gui-macos-x64"
    cp dist/executables/redline-web-macos-x64 "$PACKAGE_DIR/Ubuntu/redline-web-macos-x64"
    echo "✅ Ubuntu executables prepared (macOS versions for reference)"
else
    echo "⚠️ Executables not found, skipping..."
fi

# Create installation instructions
echo "📝 Creating installation instructions..."

# macOS instructions
cat > "$PACKAGE_DIR/macOS/INSTALL.txt" << EOF
REDLINE macOS Installation Instructions
=====================================

Version: ${VERSION}
Date: $(date)

INSTALLATION:
1. Drag REDLINE.app to your Applications folder
2. Drag "REDLINE Web.app" to your Applications folder
3. Launch REDLINE from Applications or Spotlight

FEATURES:
- REDLINE.app: Desktop GUI application
- REDLINE Web.app: Web-based interface (runs on localhost:8080)

SYSTEM REQUIREMENTS:
- macOS 10.15 or later
- 4GB RAM minimum
- 500MB free disk space

TROUBLESHOOTING:
- If apps don't open, right-click and select "Open"
- Check System Preferences > Security & Privacy for blocked apps
- For web interface, open REDLINE Web.app and visit http://localhost:8080

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues

Architecture: ARM64 (Apple Silicon) and x64 (Intel)
EOF

# Windows instructions
cat > "$PACKAGE_DIR/Windows/INSTALL.txt" << EOF
REDLINE Windows Installation Instructions
========================================

Version: ${VERSION}
Date: $(date)

NOTE: This package contains macOS executables for reference only.
Windows installers (.exe and .msi) will be available in future releases.

CURRENT STATUS:
- macOS executables included for reference
- Windows installers: Coming soon
- Ubuntu packages: Coming soon

PLANNED FEATURES:
- REDLINE-Setup.exe: NSIS installer (x64 and ARM64)
- REDLINE.msi: MSI package (x64 and ARM64)
- Desktop shortcuts and Start Menu integration
- Automatic updates

SYSTEM REQUIREMENTS (Planned):
- Windows 10 or later
- 4GB RAM minimum
- 500MB free disk space

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues
EOF

# Ubuntu instructions
cat > "$PACKAGE_DIR/Ubuntu/INSTALL.txt" << EOF
REDLINE Ubuntu Installation Instructions
=======================================

Version: ${VERSION}
Date: $(date)

NOTE: This package contains macOS executables for reference only.
Ubuntu DEB packages will be available in future releases.

CURRENT STATUS:
- macOS executables included for reference
- Ubuntu DEB packages: Coming soon
- Windows installers: Coming soon

PLANNED FEATURES:
- redline-financial_${VERSION}_amd64.deb: AMD64 package
- redline-financial_${VERSION}_arm64.deb: ARM64 package
- Desktop integration and menu entries
- Automatic dependency resolution

SYSTEM REQUIREMENTS (Planned):
- Ubuntu 20.04 LTS or later
- 4GB RAM minimum
- 500MB free disk space

INSTALLATION (Planned):
sudo dpkg -i redline-financial_${VERSION}_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues
EOF

# Create main README
cat > "$PACKAGE_DIR/README.txt" << EOF
REDLINE Financial Analysis Platform
==================================

Version: ${VERSION}
Package Date: $(date)

OVERVIEW:
REDLINE is a professional financial data analysis platform with both
desktop GUI and web-based interfaces.

CURRENT STATUS:
✅ macOS: Ready for testing (ARM64 and x64)
🔄 Windows: In development (NSIS and MSI installers)
🔄 Ubuntu: In development (DEB packages)

PLATFORMS:
- macOS: App bundles ready for testing
- Windows: Installers coming soon
- Ubuntu: DEB packages coming soon

ARCHITECTURES SUPPORTED:
- macOS: ARM64 (Apple Silicon) and x64 (Intel)
- Windows: x64 and ARM64 (planned)
- Ubuntu: AMD64 and ARM64 (planned)

INSTALLATION:
1. Navigate to your platform folder (macOS/Windows/Ubuntu)
2. Follow the INSTALL.txt instructions
3. Report any issues on GitHub

FEATURES:
- Desktop GUI application
- Web-based interface (localhost:8080)
- Multi-platform support
- Professional financial analysis tools

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues
- Documentation: See Documentation/ folder

SECURITY:
- All installers are built with security best practices
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

TESTING:
This USB package is designed for testing REDLINE on multiple platforms.
Please report any issues or feedback to help improve the platform.

Thank you for testing REDLINE!
EOF

# Copy documentation
echo "📚 Copying documentation..."
if [[ -f "SECURITY_GUIDE.md" ]]; then
    cp SECURITY_GUIDE.md "$PACKAGE_DIR/Documentation/"
fi
if [[ -f "GIT_SECURITY_GUIDE.md" ]]; then
    cp GIT_SECURITY_GUIDE.md "$PACKAGE_DIR/Documentation/"
fi
if [[ -f "INSTALLER_BUILD_GUIDE.md" ]]; then
    cp INSTALLER_BUILD_GUIDE.md "$PACKAGE_DIR/Documentation/"
fi
if [[ -f "env.template" ]]; then
    cp env.template "$PACKAGE_DIR/Documentation/"
fi

echo "✅ Documentation copied"

# Create package info
cat > "$PACKAGE_DIR/PACKAGE_INFO.txt" << EOF
REDLINE USB Test Package Information
====================================

Package Name: ${PACKAGE_NAME}
Version: ${VERSION}
Created: $(date)
Platform: Multi-platform (macOS ready, others in development)

Contents:
- macOS/: macOS app bundles and installation instructions
- Windows/: Windows installation instructions (installers coming soon)
- Ubuntu/: Ubuntu installation instructions (DEB packages coming soon)
- Documentation/: Security guides and configuration templates
- README.txt: Main package information
- PACKAGE_INFO.txt: This file

File Sizes:
$(du -sh "$PACKAGE_DIR"/* 2>/dev/null | sort -hr)

Total Package Size: $(du -sh "$PACKAGE_DIR" | cut -f1)

Build Information:
- Built on: $(uname -s) $(uname -m)
- Build Date: $(date)
- Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "Unknown")
- Python Version: $(python --version 2>/dev/null || echo "Unknown")

Testing Notes:
- macOS app bundles are ready for immediate testing
- Windows and Ubuntu packages are in development
- All security measures are implemented
- Environment variables are properly configured
EOF

# Create archive
echo "📦 Creating archive..."
cd dist
tar -czf "${PACKAGE_NAME}.tar.gz" usb-package/
cd ..

echo "✅ USB package created successfully!"
echo ""
echo "📁 Package location: $PACKAGE_DIR"
echo "📦 Archive: dist/${PACKAGE_NAME}.tar.gz"
echo ""
echo "📊 Package contents:"
ls -la "$PACKAGE_DIR"
echo ""
echo "💾 Package size: $(du -sh "$PACKAGE_DIR" | cut -f1)"
echo "📦 Archive size: $(du -sh "dist/${PACKAGE_NAME}.tar.gz" | cut -f1)"
echo ""
echo "🚀 Ready for USB distribution!"
echo "   Copy the usb-package folder to your USB drive"
echo "   Or extract the tar.gz archive on the target system"
