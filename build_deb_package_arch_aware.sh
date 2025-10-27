#!/bin/bash
# build_deb_package_arch_aware.sh
# Architecture-aware DEB package builder for REDLINE

set -e

echo "📦 REDLINE DEB Package Builder (Architecture-Aware)"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        ARCH_SUFFIX="amd64"
        ;;
    aarch64|arm64)
        ARCH_SUFFIX="arm64"
        ;;
    *)
        ARCH_SUFFIX="amd64"
        print_warning "Unknown architecture $ARCH, defaulting to amd64"
        ;;
esac

print_info "Detected architecture: $ARCH_SUFFIX"

# Find project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/../../main.py" ] || [ -f "$SCRIPT_DIR/../../web_app.py" ]; then
    PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
elif [ -f "$SCRIPT_DIR/../main.py" ] || [ -f "$SCRIPT_DIR/../web_app.py" ]; then
    PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
else
    print_error "Cannot find project root"
    exit 1
fi

print_info "Project root: $PROJECT_ROOT"

# Configuration
VERSION="1.0.0"
PACKAGE_NAME="redline-financial"
OUTPUT_DIR="$PROJECT_ROOT/dist/deb-package"
DEB_DIR="$OUTPUT_DIR/deb/$ARCH_SUFFIX"

# Create output directory
print_info "Creating output directory..."
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/redline"
mkdir -p "$DEB_DIR/usr/local/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_DIR/usr/share/doc/$PACKAGE_NAME"

# Create control file
print_info "Creating control file..."
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH_SUFFIX
Maintainer: REDLINE Development Team <support@redline.example.com>
Depends: libc6 (>= 2.17), libgcc-s1 (>= 3.0), libstdc++6 (>= 4.8.1), python3 (>= 3.9)
Description: Professional financial data analysis platform
 REDLINE is a comprehensive financial data analysis platform that provides
 both desktop GUI and web-based interfaces for market research, data
 visualization, and algorithmic trading.
 .
 This package contains the $ARCH_SUFFIX version of REDLINE.
EOF

# Copy executables if they exist
print_info "Looking for executables..."
if [ -f "$PROJECT_ROOT/dist/executables/redline-gui-linux-$ARCH_SUFFIX" ]; then
    cp "$PROJECT_ROOT/dist/executables/redline-gui-linux-$ARCH_SUFFIX" "$DEB_DIR/opt/redline/redline-gui"
    chmod +x "$DEB_DIR/opt/redline/redline-gui"
    print_status "GUI executable copied"
else
    print_warning "GUI executable not found, creating placeholder"
    cat > "$DEB_DIR/opt/redline/redline-gui" << 'EOF'
#!/bin/bash
echo "REDLINE Financial Platform - GUI Application"
echo "Version: 1.0.0"
echo "Architecture: $(uname -m)"
EOF
    chmod +x "$DEB_DIR/opt/redline/redline-gui"
fi

if [ -f "$PROJECT_ROOT/dist/executables/redline-web-linux-$ARCH_SUFFIX" ]; then
    cp "$PROJECT_ROOT/dist/executables/redline-web-linux-$ARCH_SUFFIX" "$DEB_DIR/opt/redline/redline-web"
    chmod +x "$DEB_DIR/opt/redline/redline-web"
    print_status "Web executable copied"
else
    print_warning "Web executable not found, creating placeholder"
    cat > "$DEB_DIR/opt/redline/redline-web" << 'EOF'
#!/bin/bash
echo "REDLINE Financial Platform - Web Application"
echo "Version: 1.0.0"
echo "Architecture: $(uname -m)"
EOF
    chmod +x "$DEB_DIR/opt/redline/redline-web"
fi

# Create symlinks
print_info "Creating symlinks..."
ln -sf /opt/redline/redline-gui "$DEB_DIR/usr/local/bin/redline-gui"
ln -sf /opt/redline/redline-web "$DEB_DIR/usr/local/bin/redline-web"

# Create desktop entries
print_info "Creating desktop entries..."
cat > "$DEB_DIR/usr/share/applications/redline-financial-gui.desktop" << EOF
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

cat > "$DEB_DIR/usr/share/applications/redline-financial-web.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Web Interface
Comment=Web-based interface for REDLINE Financial Analysis Platform
Exec=/opt/redline/redline-web
Icon=redline-financial
Terminal=false
Categories=Office;Finance;Network;
Keywords=finance;analysis;data;trading;web;
EOF

# Create postinst script
print_info "Creating postinst script..."
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
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

echo "REDLINE Financial Analysis Platform installed successfully!"
echo "Run 'redline-gui' for desktop interface or 'redline-web' for web interface"
echo "Web interface will be available at http://localhost:8080"

exit 0
EOF
chmod +x "$DEB_DIR/DEBIAN/postinst"

# Create prerm script
print_info "Creating prerm script..."
cat > "$DEB_DIR/DEBIAN/prerm" << 'EOF'
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
chmod +x "$DEB_DIR/DEBIAN/prerm"

# Build DEB package
print_info "Building DEB package..."
mkdir -p "$OUTPUT_DIR/repository"
dpkg-deb --build "$DEB_DIR" "$OUTPUT_DIR/repository/${PACKAGE_NAME}_${VERSION}_${ARCH_SUFFIX}.deb"

print_status "DEB package built successfully!"
echo ""
echo "📦 Package created: $OUTPUT_DIR/repository/${PACKAGE_NAME}_${VERSION}_${ARCH_SUFFIX}.deb"
echo ""
echo "🚀 To install:"
echo "sudo dpkg -i $OUTPUT_DIR/repository/${PACKAGE_NAME}_${VERSION}_${ARCH_SUFFIX}.deb"
echo "sudo apt-get install -f  # To resolve any missing dependencies"
echo ""
print_status "Architecture-aware DEB package creation complete!"
