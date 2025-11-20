#!/bin/bash
# Setup script for Massive.com API key configuration in REDLINE

set -e

echo "=========================================="
echo "Massive.com API Key Setup for REDLINE"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if API key is already set
if [ -n "$MASSIVE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  MASSIVE_API_KEY is already set in environment${NC}"
    echo "Current value: ${MASSIVE_API_KEY:0:10}..."
    read -p "Do you want to update it? (y/n): " update_env
    if [ "$update_env" != "y" ]; then
        echo "Keeping existing environment variable."
    fi
fi

# Get API key from user
echo ""
echo "Enter your Massive.com API key:"
echo "(You can get it from https://massive.com)"
read -s api_key

if [ -z "$api_key" ]; then
    echo -e "${RED}❌ API key cannot be empty${NC}"
    exit 1
fi

echo ""
echo "Choose configuration method:"
echo "1. Save to REDLINE config file (recommended for web UI)"
echo "2. Set as environment variable (for command-line use)"
echo "3. Both (recommended)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        method="config"
        ;;
    2)
        method="env"
        ;;
    3)
        method="both"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

# Save to config file
if [ "$method" == "config" ] || [ "$method" == "both" ]; then
    echo ""
    echo "📝 Saving API key to REDLINE config file..."
    
    # Find config directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    CONFIG_DIR="$HOME/.redline"
    API_KEYS_FILE="$CONFIG_DIR/api_keys.json"
    
    # Create config directory if it doesn't exist
    mkdir -p "$CONFIG_DIR"
    
    # Load existing keys or create new structure
    if [ -f "$API_KEYS_FILE" ]; then
        # Use Python to safely update JSON
        python3 << EOF
import json
import os

api_keys_file = "$API_KEYS_FILE"
api_key = "$api_key"

# Load existing keys
try:
    with open(api_keys_file, 'r') as f:
        keys = json.load(f)
except:
    keys = {}

# Update with Massive.com key
keys['massive'] = api_key

# Save back
with open(api_keys_file, 'w') as f:
    json.dump(keys, f, indent=2)

# Set secure permissions
os.chmod(api_keys_file, 0o600)

print("✅ API key saved to config file")
EOF
    else
        # Create new file
        python3 << EOF
import json
import os

api_keys_file = "$API_KEYS_FILE"
api_key = "$api_key"

keys = {'massive': api_key}

with open(api_keys_file, 'w') as f:
    json.dump(keys, f, indent=2)

os.chmod(api_keys_file, 0o600)

print("✅ API key saved to config file")
EOF
    fi
    
    echo -e "${GREEN}✅ API key saved to: $API_KEYS_FILE${NC}"
    echo "   (This will be used by the REDLINE web UI)"
fi

# Set environment variable
if [ "$method" == "env" ] || [ "$method" == "both" ]; then
    echo ""
    echo "📝 Setting environment variable..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    if [ "$SHELL_NAME" == "zsh" ]; then
        RC_FILE="$HOME/.zshrc"
    elif [ "$SHELL_NAME" == "bash" ]; then
        RC_FILE="$HOME/.bashrc"
    else
        RC_FILE="$HOME/.profile"
    fi
    
    # Check if already exists
    if grep -q "MASSIVE_API_KEY" "$RC_FILE" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  MASSIVE_API_KEY already exists in $RC_FILE${NC}"
        read -p "Do you want to update it? (y/n): " update_rc
        if [ "$update_rc" == "y" ]; then
            # Remove old entry
            sed -i.bak "/MASSIVE_API_KEY/d" "$RC_FILE"
            echo "" >> "$RC_FILE"
            echo "# Massive.com API Key for REDLINE" >> "$RC_FILE"
            echo "export MASSIVE_API_KEY=\"$api_key\"" >> "$RC_FILE"
            echo -e "${GREEN}✅ Updated $RC_FILE${NC}"
        fi
    else
        echo "" >> "$RC_FILE"
        echo "# Massive.com API Key for REDLINE" >> "$RC_FILE"
        echo "export MASSIVE_API_KEY=\"$api_key\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added to $RC_FILE${NC}"
    fi
    
    # Export for current session
    export MASSIVE_API_KEY="$api_key"
    echo -e "${GREEN}✅ Environment variable set for current session${NC}"
    echo ""
    echo -e "${YELLOW}💡 Note: Run 'source $RC_FILE' or restart your terminal to use in new sessions${NC}"
fi

# Test the API key
echo ""
echo "🧪 Testing API key..."
echo ""

# Check if Python test script exists
if [ -f "$SCRIPT_DIR/test_massive_integration.py" ]; then
    export MASSIVE_API_KEY="$api_key"
    python3 "$SCRIPT_DIR/test_massive_integration.py" 2>&1 | head -20
else
    echo "Test script not found. Skipping test."
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If you saved to config file: Use Massive.com in REDLINE web UI"
echo "2. If you set environment variable: Restart terminal or run 'source $RC_FILE'"
echo "3. Test the integration: python3 test_massive_integration.py"
echo ""
echo "To use in REDLINE:"
echo "  - Go to Settings → API Keys"
echo "  - Find 'Massive.com' in the list"
echo "  - Your API key should already be saved"
echo "  - Or enter it manually if needed"
echo ""
echo "To use in Download tab:"
echo "  - Select 'Massive.com' as the data source"
echo "  - Enter ticker and date range"
echo "  - Click Download"
echo ""

