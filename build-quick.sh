#!/bin/bash

# =============================================================================
# VarioSync Quick Build Script
# Simple wrapper for common build scenarios
# Usage: ./build-quick.sh <image-name> [target] [--push|--load]
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default registry
REGISTRY="${VARIOSYNC_REGISTRY:-keepdevops}"

# Get image name from argument or prompt
IMAGE_NAME="${1:-}"
TARGET="${2:-}"
BUILD_ACTION="${3:---push}"

if [[ -z "${IMAGE_NAME}" ]]; then
    echo -e "${CYAN}VarioSync Quick Build${NC}"
    echo ""
    read -p "Enter image name: " IMAGE_NAME
    if [[ -z "${IMAGE_NAME}" ]]; then
        echo "Image name is required"
        exit 1
    fi
fi

# Determine target flags
TARGET_FLAG=""
if [[ -n "${TARGET}" && "${TARGET}" != "--push" && "${TARGET}" != "--load" ]]; then
    TARGET_FLAG="-t ${TARGET}"
    BUILD_ACTION="${3:---push}"
else
    # Target might be the action flag
    if [[ "${TARGET}" == "--push" || "${TARGET}" == "--load" ]]; then
        BUILD_ACTION="${TARGET}"
        TARGET_FLAG=""
    fi
fi

echo ""
echo -e "${GREEN}Building: ${REGISTRY}/${IMAGE_NAME}${NC}"
echo -e "${CYAN}Target: ${TARGET:-default}${NC}"
echo -e "${CYAN}Action: ${BUILD_ACTION}${NC}"
echo ""

# Execute the main build script
./build-bytecode-variosync.sh \
    -n "${IMAGE_NAME}" \
    -r "${REGISTRY}" \
    ${TARGET_FLAG} \
    ${BUILD_ACTION}
