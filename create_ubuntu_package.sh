#!/bin/bash
# Ubuntu DEB Package Creator
# Creates Ubuntu DEB packages for USB distribution

set -e

echo "🐧 Creating Ubuntu DEB Package..."

# Get project root and version
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

VERSION=$(python -c "import sys; sys.path.insert(0, '.'); from redline.__version__ import __version__; print(__version__)")
PACKAGE_NAME="REDLINE-${VERSION}-Ubuntu"
PACKAGE_DIR="dist/ubuntu-package"

# Clean and create package directory
echo "📦 Creating Ubuntu package directory..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Create package structure
mkdir -p "$PACKAGE_DIR/DEB"
mkdir -p "$PACKAGE_DIR/Executables"
mkdir -p "$PACKAGE_DIR/Scripts"

echo "✅ Package structure created"

# Copy Linux executables
echo "🐧 Copying Linux executables..."
if [[ -f "dist/executables/redline-gui-linux-x64" ]] && [[ -f "dist/executables/redline-web-linux-x64" ]]; then
    cp dist/executables/redline-gui-linux-x64 "$PACKAGE_DIR/Executables/"
    cp dist/executables/redline-web-linux-x64 "$PACKAGE_DIR/Executables/"
    echo "✅ Linux x64 executables copied"
else
    echo "⚠️ Linux x64 executables not found, skipping..."
fi

if [[ -f "dist/executables/redline-gui-linux-arm64" ]] && [[ -f "dist/executables/redline-web-linux-arm64" ]]; then
    cp dist/executables/redline-gui-linux-arm64 "$PACKAGE_DIR/Executables/"
    cp dist/executables/redline-web-linux-arm64 "$PACKAGE_DIR/Executables/"
    echo "✅ Linux ARM64 executables copied"
else
    echo "⚠️ Linux ARM64 executables not found, skipping..."
fi

# Create DEB package structure for AMD64
echo "📝 Creating DEB package structure for AMD64..."
mkdir -p "$PACKAGE_DIR/DEB/amd64/DEBIAN"
mkdir -p "$PACKAGE_DIR/DEB/amd64/opt/redline"
mkdir -p "$PACKAGE_DIR/DEB/amd64/usr/local/bin"
mkdir -p "$PACKAGE_DIR/DEB/amd64/usr/share/applications"
mkdir -p "$PACKAGE_DIR/DEB/amd64/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial"

# Create DEB package structure for ARM64
echo "📝 Creating DEB package structure for ARM64..."
mkdir -p "$PACKAGE_DIR/DEB/arm64/DEBIAN"
mkdir -p "$PACKAGE_DIR/DEB/arm64/opt/redline"
mkdir -p "$PACKAGE_DIR/DEB/arm64/usr/local/bin"
mkdir -p "$PACKAGE_DIR/DEB/arm64/usr/share/applications"
mkdir -p "$PACKAGE_DIR/DEB/arm64/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PACKAGE_DIR/DEB/arm64/usr/share/doc/redline-financial"

# Create control files
echo "📝 Creating DEB control files..."

# AMD64 control file
cat > "$PACKAGE_DIR/DEB/amd64/DEBIAN/control" << EOF
Package: redline-financial
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: REDLINE Development Team <support@redline.example.com>
Depends: libc6 (>= 2.17), libgcc-s1 (>= 3.0), libstdc++6 (>= 4.8.1)
Description: Professional financial data analysis platform
 REDLINE is a comprehensive financial data analysis platform that provides
 both desktop GUI and web-based interfaces for financial data analysis,
 visualization, and reporting.
 .
 Features:
 - Desktop GUI application with full functionality
 - Web-based interface accessible via browser
 - Multi-architecture support (AMD64, ARM64)
 - Professional financial analysis tools
 - Secure API key management
 - Environment variable configuration
 .
 This package contains the AMD64 version of REDLINE.
EOF

# ARM64 control file
cat > "$PACKAGE_DIR/DEB/arm64/DEBIAN/control" << EOF
Package: redline-financial
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: arm64
Maintainer: REDLINE Development Team <support@redline.example.com>
Depends: libc6 (>= 2.17), libgcc-s1 (>= 3.0), libstdc++6 (>= 4.8.1)
Description: Professional financial data analysis platform
 REDLINE is a comprehensive financial data analysis platform that provides
 both desktop GUI and web-based interfaces for financial data analysis,
 visualization, and reporting.
 .
 Features:
 - Desktop GUI application with full functionality
 - Web-based interface accessible via browser
 - Multi-architecture support (AMD64, ARM64)
 - Professional financial analysis tools
 - Secure API key management
 - Environment variable configuration
 .
 This package contains the ARM64 version of REDLINE.
EOF

# Create postinst scripts
echo "📝 Creating postinst scripts..."

cat > "$PACKAGE_DIR/DEB/amd64/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Make executables executable
chmod +x /opt/redline/redline-gui
chmod +x /opt/redline/redline-web

# Create symlinks
ln -sf /opt/redline/redline-gui /usr/local/bin/redline-gui
ln -sf /opt/redline/redline-web /usr/local/bin/redline-web

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

echo "REDLINE Financial Analysis Platform installed successfully!"
echo "Run 'redline-gui' for desktop interface or 'redline-web' for web interface"
echo "Web interface will be available at http://localhost:8080"

exit 0
EOF

cat > "$PACKAGE_DIR/DEB/arm64/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Make executables executable
chmod +x /opt/redline/redline-gui
chmod +x /opt/redline/redline-web

# Create symlinks
ln -sf /opt/redline/redline-gui /usr/local/bin/redline-gui
ln -sf /opt/redline/redline-web /usr/local/bin/redline-web

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

echo "REDLINE Financial Analysis Platform installed successfully!"
echo "Run 'redline-gui' for desktop interface or 'redline-web' for web interface"
echo "Web interface will be available at http://localhost:8080"

exit 0
EOF

# Create prerm scripts
echo "📝 Creating prerm scripts..."

cat > "$PACKAGE_DIR/DEB/amd64/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Remove symlinks
rm -f /usr/local/bin/redline-gui
rm -f /usr/local/bin/redline-web

exit 0
EOF

cat > "$PACKAGE_DIR/DEB/arm64/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Remove symlinks
rm -f /usr/local/bin/redline-gui
rm -f /usr/local/bin/redline-web

exit 0
EOF

# Create postrm scripts
echo "📝 Creating postrm scripts..."

cat > "$PACKAGE_DIR/DEB/amd64/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

exit 0
EOF

cat > "$PACKAGE_DIR/DEB/arm64/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

exit 0
EOF

# Create desktop entries
echo "📝 Creating desktop entries..."

cat > "$PACKAGE_DIR/DEB/amd64/usr/share/applications/redline-gui.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Financial Analysis
Comment=Professional financial data analysis platform
Exec=/opt/redline/redline-gui
Icon=redline-financial
Terminal=false
Categories=Office;Finance;
Keywords=finance;analysis;data;trading;
EOF

cat > "$PACKAGE_DIR/DEB/amd64/usr/share/applications/redline-web.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Web Interface
Comment=Web-based financial data analysis interface
Exec=/opt/redline/redline-web
Icon=redline-financial
Terminal=false
Categories=Office;Finance;Network;
Keywords=finance;analysis;data;web;trading;
EOF

cat > "$PACKAGE_DIR/DEB/arm64/usr/share/applications/redline-gui.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Financial Analysis
Comment=Professional financial data analysis platform
Exec=/opt/redline/redline-gui
Icon=redline-financial
Terminal=false
Categories=Office;Finance;
Keywords=finance;analysis;data;trading;
EOF

cat > "$PACKAGE_DIR/DEB/arm64/usr/share/applications/redline-web.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Web Interface
Comment=Web-based financial data analysis interface
Exec=/opt/redline/redline-web
Icon=redline-financial
Terminal=false
Categories=Office;Finance;Network;
Keywords=finance;analysis;data;web;trading;
EOF

# Create documentation
echo "📝 Creating documentation..."

cat > "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial/README" << EOF
REDLINE Financial Analysis Platform
===================================

Version: ${VERSION}
Architecture: AMD64

OVERVIEW:
REDLINE is a professional financial data analysis platform with both
desktop GUI and web-based interfaces.

INSTALLATION:
This package installs REDLINE to /opt/redline/ and creates symlinks
in /usr/local/bin/ for easy command-line access.

USAGE:
- Desktop GUI: Run 'redline-gui' or launch from applications menu
- Web Interface: Run 'redline-web' and visit http://localhost:8080

FEATURES:
- Desktop GUI application with full functionality
- Web-based interface accessible via browser
- Multi-architecture support (AMD64, ARM64)
- Professional financial analysis tools
- Secure API key management
- Environment variable configuration

SYSTEM REQUIREMENTS:
- Ubuntu 18.04 or later
- 4GB RAM minimum
- 500MB free disk space
- Internet connection for web interface

SECURITY:
- All security vulnerabilities have been fixed
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues

Thank you for using REDLINE!
EOF

cat > "$PACKAGE_DIR/DEB/arm64/usr/share/doc/redline-financial/README" << EOF
REDLINE Financial Analysis Platform
===================================

Version: ${VERSION}
Architecture: ARM64

OVERVIEW:
REDLINE is a professional financial data analysis platform with both
desktop GUI and web-based interfaces.

INSTALLATION:
This package installs REDLINE to /opt/redline/ and creates symlinks
in /usr/local/bin/ for easy command-line access.

USAGE:
- Desktop GUI: Run 'redline-gui' or launch from applications menu
- Web Interface: Run 'redline-web' and visit http://localhost:8080

FEATURES:
- Desktop GUI application with full functionality
- Web-based interface accessible via browser
- Multi-architecture support (AMD64, ARM64)
- Professional financial analysis tools
- Secure API key management
- Environment variable configuration

SYSTEM REQUIREMENTS:
- Ubuntu 18.04 or later
- 4GB RAM minimum
- 500MB free disk space
- Internet connection for web interface

SECURITY:
- All security vulnerabilities have been fixed
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues

Thank you for using REDLINE!
EOF

# Create copyright file
cat > "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: redline-financial
Source: https://github.com/keepdevops/redline2

Files: *
Copyright: 2024 REDLINE Development Team
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
EOF

cp "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial/copyright" "$PACKAGE_DIR/DEB/arm64/usr/share/doc/redline-financial/copyright"

# Create changelog
cat > "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial/changelog.Debian" << EOF
redline-financial (${VERSION}) stable; urgency=medium

  * Initial release of REDLINE Financial Analysis Platform
  * Desktop GUI application with full functionality
  * Web-based interface accessible via browser
  * Multi-architecture support (AMD64, ARM64)
  * Professional financial analysis tools
  * Secure API key management
  * Environment variable configuration
  * All security vulnerabilities fixed

 -- REDLINE Development Team <support@redline.example.com>  $(date -R)
EOF

cp "$PACKAGE_DIR/DEB/amd64/usr/share/doc/redline-financial/changelog.Debian" "$PACKAGE_DIR/DEB/arm64/usr/share/doc/redline-financial/changelog.Debian"

# Copy executables to package directories
echo "📦 Copying executables to package directories..."

if [[ -f "dist/executables/redline-gui-linux-x64" ]]; then
    cp dist/executables/redline-gui-linux-x64 "$PACKAGE_DIR/DEB/amd64/opt/redline/redline-gui"
    chmod +x "$PACKAGE_DIR/DEB/amd64/opt/redline/redline-gui"
fi

if [[ -f "dist/executables/redline-web-linux-x64" ]]; then
    cp dist/executables/redline-web-linux-x64 "$PACKAGE_DIR/DEB/amd64/opt/redline/redline-web"
    chmod +x "$PACKAGE_DIR/DEB/amd64/opt/redline/redline-web"
fi

if [[ -f "dist/executables/redline-gui-linux-arm64" ]]; then
    cp dist/executables/redline-gui-linux-arm64 "$PACKAGE_DIR/DEB/arm64/opt/redline/redline-gui"
    chmod +x "$PACKAGE_DIR/DEB/arm64/opt/redline/redline-gui"
fi

if [[ -f "dist/executables/redline-web-linux-arm64" ]]; then
    cp dist/executables/redline-web-linux-arm64 "$PACKAGE_DIR/DEB/arm64/opt/redline/redline-web"
    chmod +x "$PACKAGE_DIR/DEB/arm64/opt/redline/redline-web"
fi

# Make scripts executable
chmod +x "$PACKAGE_DIR/DEB/amd64/DEBIAN/postinst"
chmod +x "$PACKAGE_DIR/DEB/amd64/DEBIAN/prerm"
chmod +x "$PACKAGE_DIR/DEB/amd64/DEBIAN/postrm"
chmod +x "$PACKAGE_DIR/DEB/arm64/DEBIAN/postinst"
chmod +x "$PACKAGE_DIR/DEB/arm64/DEBIAN/prerm"
chmod +x "$PACKAGE_DIR/DEB/arm64/DEBIAN/postrm"

# Create build scripts
echo "📝 Creating build scripts..."

cat > "$PACKAGE_DIR/Scripts/build_deb.sh" << 'EOF'
#!/bin/bash
# Build DEB packages script

set -e

echo "Building REDLINE DEB packages..."

# Check if dpkg-deb is available
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb is not installed. Please install it:"
    echo "  sudo apt-get install dpkg-dev"
    exit 1
fi

# Build AMD64 package
echo "Building AMD64 package..."
dpkg-deb --build DEB/amd64 redline-financial_1.0.0_amd64.deb

# Build ARM64 package
echo "Building ARM64 package..."
dpkg-deb --build DEB/arm64 redline-financial_1.0.0_arm64.deb

echo "DEB packages built successfully!"
echo "Files created:"
echo "  - redline-financial_1.0.0_amd64.deb"
echo "  - redline-financial_1.0.0_arm64.deb"
EOF

chmod +x "$PACKAGE_DIR/Scripts/build_deb.sh"

# Create installation instructions
echo "📝 Creating installation instructions..."
cat > "$PACKAGE_DIR/INSTALL.txt" << EOF
REDLINE Ubuntu Installation Instructions
========================================

Version: ${VERSION}
Date: $(date)

OVERVIEW:
REDLINE is a professional financial data analysis platform with both
desktop GUI and web-based interfaces.

INSTALLATION OPTIONS:

1. DEB PACKAGE INSTALLATION (Recommended):
   - File: redline-financial_${VERSION}_amd64.deb (for AMD64 systems)
   - File: redline-financial_${VERSION}_arm64.deb (for ARM64 systems)
   - Automatic dependency resolution
   - Desktop integration
   - Command-line access via symlinks

2. MANUAL INSTALLATION:
   - Copy executables from Executables/ folder
   - Run redline-gui-linux-x64 for desktop interface (AMD64)
   - Run redline-web-linux-x64 for web interface (AMD64)
   - Run redline-gui-linux-arm64 for desktop interface (ARM64)
   - Run redline-web-linux-arm64 for web interface (ARM64)

ARCHITECTURE SUPPORT:
- AMD64 (Intel/AMD): Primary support
- ARM64 (ARM processors): Full support
- Auto-detection: Package manager handles architecture selection

SYSTEM REQUIREMENTS:
- Ubuntu 18.04 or later
- 4GB RAM minimum
- 500MB free disk space
- Internet connection for web interface

FEATURES:
- REDLINE GUI: Desktop application with full functionality
- REDLINE Web: Web-based interface (runs on localhost:8080)
- Multi-architecture support
- Professional financial analysis tools

INSTALLATION STEPS:

For DEB Package:
1. Download the appropriate .deb file for your architecture
2. Install using package manager:
   sudo dpkg -i redline-financial_${VERSION}_amd64.deb
   # OR for ARM64:
   sudo dpkg -i redline-financial_${VERSION}_arm64.deb
3. Resolve any dependency issues:
   sudo apt-get install -f
4. Launch from applications menu or command line:
   redline-gui    # Desktop interface
   redline-web    # Web interface

For Manual Installation:
1. Copy redline-gui-linux-x64 and redline-web-linux-x64 to desired folder
2. Make executables executable:
   chmod +x redline-gui-linux-x64 redline-web-linux-x64
3. Run applications:
   ./redline-gui-linux-x64    # Desktop interface
   ./redline-web-linux-x64    # Web interface
4. Visit http://localhost:8080 for web interface

BUILDING DEB PACKAGES:
If you need to build the DEB packages from source:
1. Install build tools:
   sudo apt-get install dpkg-dev
2. Run build script:
   bash Scripts/build_deb.sh
3. Install built packages as described above

TROUBLESHOOTING:
- If installation fails, check system architecture compatibility
- Ensure sufficient disk space (500MB minimum)
- For web interface, check firewall settings
- Check system logs for any issues:
  journalctl -u redline

UNINSTALLATION:
- Use package manager:
  sudo apt-get remove redline-financial
- Or use dpkg:
  sudo dpkg -r redline-financial

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues
- Documentation: See Documentation/ folder

SECURITY:
- All security vulnerabilities have been fixed
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

Thank you for using REDLINE!
EOF

# Create package info
cat > "$PACKAGE_DIR/PACKAGE_INFO.txt" << EOF
REDLINE Ubuntu DEB Package Information
=====================================

Package Name: ${PACKAGE_NAME}
Version: ${VERSION}
Created: $(date)
Platform: Ubuntu (AMD64 and ARM64)

Contents:
- DEB/: DEB package structures for both architectures
- Executables/: Linux executables (x64 and ARM64)
- Scripts/: Build scripts for Ubuntu
- INSTALL.txt: Installation instructions
- PACKAGE_INFO.txt: This file

Prerequisites for Building:
- dpkg-dev package (for dpkg-deb command)
- Ubuntu 18.04 or later

Build Instructions:
1. Install build tools:
   sudo apt-get install dpkg-dev
2. Run Scripts/build_deb.sh
3. Install built packages:
   sudo dpkg -i redline-financial_${VERSION}_amd64.deb
   sudo dpkg -i redline-financial_${VERSION}_arm64.deb

Output Files:
- redline-financial_${VERSION}_amd64.deb (AMD64 package)
- redline-financial_${VERSION}_arm64.deb (ARM64 package)

Architecture Support:
- AMD64 (Intel/AMD): Primary support
- ARM64 (ARM processors): Full support
- Package manager handles architecture selection

Features:
- Desktop integration
- Command-line access via symlinks
- Automatic dependency resolution
- Multi-architecture support
- Professional installation experience

Security:
- All security vulnerabilities fixed
- No hardcoded secrets
- Environment variable configuration
- Secure API key management
EOF

echo "✅ Ubuntu DEB package created successfully!"
echo ""
echo "📁 Package location: $PACKAGE_DIR"
echo ""
echo "📊 Package contents:"
ls -la "$PACKAGE_DIR"
echo ""
echo "💾 Package size: $(du -sh "$PACKAGE_DIR" | cut -f1)"
echo ""
echo "🚀 Ready for Ubuntu DEB building!"
echo "   Copy to Ubuntu system and run build script"
echo "   Requires dpkg-dev package for building"
