#!/bin/bash
# Simple DMG Creator for REDLINE
# Creates a DMG installer without complex mounting operations

set -e

echo "🍎 Creating simple REDLINE DMG installer..."

# Get project root and version
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

VERSION=$(python -c "import sys; sys.path.insert(0, '.'); from redline.__version__ import __version__; print(__version__)")
DMG_NAME="REDLINE-${VERSION}-macOS"
DMG_FILE="${DMG_NAME}.dmg"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/installers/*.dmg
mkdir -p dist/installers

# Check if app bundles exist
if [[ ! -d "dist/macos/REDLINE.app" ]] || [[ ! -d "dist/macos/REDLINE Web.app" ]]; then
    echo "❌ App bundles not found! Please run create_app_bundle.sh first"
    exit 1
fi

# Create DMG contents directory
echo "📦 Preparing DMG contents..."
DMG_CONTENTS="dmg_contents"
rm -rf "$DMG_CONTENTS"
mkdir -p "$DMG_CONTENTS"

# Copy app bundles
echo "📱 Copying app bundles..."
cp -R dist/macos/REDLINE.app "$DMG_CONTENTS/"
cp -R "dist/macos/REDLINE Web.app" "$DMG_CONTENTS/"

# Create Applications folder alias
echo "🔗 Creating Applications alias..."
ln -s /Applications "$DMG_CONTENTS/Applications"

# Add README
echo "📝 Adding README..."
cat > "$DMG_CONTENTS/README.txt" << EOF
REDLINE Financial Analysis Platform
===================================

Version: ${VERSION}
Build Date: $(date)

INSTALLATION INSTRUCTIONS:
1. Drag REDLINE.app to the Applications folder
2. Drag "REDLINE Web.app" to the Applications folder
3. Launch REDLINE from Applications or Spotlight

FEATURES:
- REDLINE.app: Desktop GUI application
- REDLINE Web.app: Web-based interface (runs on localhost:8080)

SYSTEM REQUIREMENTS:
- macOS 10.15 or later
- 4GB RAM minimum
- 500MB free disk space

ARCHITECTURE SUPPORT:
- ARM64 (Apple Silicon) - Primary
- x64 (Intel) - Fallback

TROUBLESHOOTING:
- If apps don't open, right-click and select "Open"
- Check System Preferences > Security & Privacy for blocked apps
- For web interface, open REDLINE Web.app and visit http://localhost:8080

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues

SECURITY:
- All security vulnerabilities have been fixed
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

Thank you for using REDLINE!
EOF

# Create simple DMG using hdiutil
echo "💿 Creating DMG installer..."
echo "   This may take a few minutes..."

# Calculate size needed (app bundles + overhead)
APP_SIZE=$(du -sk "$DMG_CONTENTS" | cut -f1)
DMG_SIZE_MB=$((APP_SIZE / 1024 + 100))  # Add 100MB overhead

echo "   App bundles size: ${APP_SIZE}KB"
echo "   DMG size: ${DMG_SIZE_MB}MB"

# Create DMG directly from folder
hdiutil create -srcfolder "$DMG_CONTENTS" \
    -volname "REDLINE ${VERSION}" \
    -fs HFS+ \
    -format UDZO \
    -imagekey zlib-level=9 \
    -size ${DMG_SIZE_MB}m \
    "dist/installers/${DMG_FILE}"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$DMG_CONTENTS"

# Verify DMG
if [[ -f "dist/installers/${DMG_FILE}" ]]; then
    DMG_SIZE=$(du -sh "dist/installers/${DMG_FILE}" | cut -f1)
    echo ""
    echo "✅ DMG installer created successfully!"
    echo "📁 Location: dist/installers/${DMG_FILE}"
    echo "💾 Size: ${DMG_SIZE}"
    echo ""
    echo "🚀 Ready for distribution!"
    echo "   The DMG can be mounted by double-clicking"
    echo "   Users can drag apps to Applications folder"
else
    echo "❌ DMG creation failed!"
    exit 1
fi

# Show DMG info
echo "📊 DMG Information:"
ls -lh "dist/installers/${DMG_FILE}"
echo ""
echo "🔍 DMG contents preview:"
hdiutil attach "dist/installers/${DMG_FILE}" -readonly -nobrowse -mountpoint /tmp/redline_dmg_preview 2>/dev/null || true
if [[ -d "/tmp/redline_dmg_preview" ]]; then
    ls -la /tmp/redline_dmg_preview/
    hdiutil detach /tmp/redline_dmg_preview 2>/dev/null || true
fi
