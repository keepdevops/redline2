#!/bin/bash
echo "🔍 Architecture Detection Test"
echo "==============================="
echo ""

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
        ;;
esac

echo "📋 System Information:"
echo "• Architecture: $ARCH"
echo "• Package suffix: $ARCH_SUFFIX"
echo "• OS: $(uname -s)"
echo "• Kernel: $(uname -r)"
echo ""

if [ "$ARCH_SUFFIX" = "amd64" ]; then
    echo "✅ This is an AMD64/x86_64 system"
    echo "📦 Will build: redline-financial_1.0.0_amd64.deb"
elif [ "$ARCH_SUFFIX" = "arm64" ]; then
    echo "✅ This is an ARM64/aarch64 system"
    echo "📦 Will build: redline-financial_1.0.0_arm64.deb"
fi

echo ""
echo "🎯 Ready to build DEB package for $ARCH_SUFFIX architecture!"
