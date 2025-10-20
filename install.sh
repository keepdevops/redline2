#!/bin/bash
# REDLINE One-Liner Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/redline/redline/main/install.sh | bash
# Or: wget -qO- https://raw.githubusercontent.com/redline/redline/main/install.sh | bash

set -e

echo "🚀 REDLINE Universal Installer"
echo "=============================="

# Download and run the universal installer
if command -v curl &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/redline/redline/main/install/install_universal.sh | bash
elif command -v wget &> /dev/null; then
    wget -qO- https://raw.githubusercontent.com/redline/redline/main/install/install_universal.sh | bash
else
    echo "❌ curl or wget required for installation"
    exit 1
fi
