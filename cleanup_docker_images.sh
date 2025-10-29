#!/bin/bash

# REDLINE Docker Images Cleanup Script
# Removes broken, outdated, and problematic Docker images

set -e

echo "🗑️ REDLINE Docker Images Cleanup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to safely remove image
remove_image() {
    local image=$1
    local reason=$2
    
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        echo "Removing: $image"
        echo "Reason: $reason"
        if docker rmi "$image" 2>/dev/null; then
            log_success "Removed $image"
        else
            log_warning "Could not remove $image (may be in use)"
        fi
    else
        log_info "Already removed: $image"
    fi
    echo ""
}

# Get initial disk usage
echo "📊 Current Docker disk usage:"
docker system df
echo ""

log_info "Starting cleanup of problematic REDLINE Docker images..."
echo ""

# Phase 1: Remove broken/failed images
echo "🔥 PHASE 1: Removing Broken/Failed Images"
echo "========================================"

remove_image "redline-test-simple:latest" "Failed test image - user configuration error"

# Phase 2: Remove images with dependency issues
echo "🔥 PHASE 2: Removing Images with Dependency Issues"
echo "================================================="

remove_image "keepdevops/redline:v1.0.0-arm64-ultra-slim" "Missing werkzeug dependency - crashes on startup"

# Phase 3: Remove outdated images (pre-Custom API)
echo "🔥 PHASE 3: Removing Outdated Images (Pre-Custom API)"
echo "===================================================="

remove_image "keepdevops/redline:v1.0.0-arm64-optimized" "Built before Custom API integration"
remove_image "keepdevops/redline:v1.0.0-amd64-ultra-slim" "Built before Custom API integration"
remove_image "keepdevops/redline:v1.0.0-amd64-optimized" "Built before Custom API integration"
remove_image "keepdevops/redline:v1.0.0-amd64-standard" "Built before Custom API integration"
remove_image "keepdevops/redline:v1.0.0-arm64-standard" "Built before Custom API integration"

# Phase 4: Remove development artifacts
echo "🔥 PHASE 4: Removing Development Artifacts"
echo "=========================================="

remove_image "redline-webgui-ultra-slim:latest-arm64" "Development artifact"
remove_image "redline-webgui-ultra-slim:latest" "Development artifact"
remove_image "redline-webgui-ultra-slim:v1.0.0-multiplatform" "Development artifact"
remove_image "redline-webgui-optimized:latest" "Development artifact"
remove_image "redline-webgui-optimized:v1.0.0-multiplatform" "Development artifact"
remove_image "redline-webgui-ultra-slim-final:arm64" "Development artifact"
remove_image "redline-webgui-ultra-slim-fixed:arm64" "Development artifact"
remove_image "redline-webgui-ultra-slim:amd64" "Development artifact"
remove_image "redline-webgui-ultra-slim:arm64" "Development artifact"
remove_image "redline-webgui-compiled-optimized:arm64" "Development artifact"
remove_image "redline-webgui-compiled-optimized:amd64" "Development artifact"
remove_image "redline-webgui-compiled:arm64" "Development artifact"
remove_image "redline-webgui-compiled:amd64" "Development artifact"
remove_image "redline-webgui-compiled:arm64-v1.0.0" "Development artifact"
remove_image "redline-webgui-compiled:amd64-v1.0.0" "Development artifact"

echo "🧹 CLEANUP: Removing dangling images and build cache..."
docker image prune -f
docker builder prune -f

echo ""
echo "📊 Docker disk usage after cleanup:"
docker system df

echo ""
echo "✅ CLEANUP COMPLETE!"
echo "==================="
echo ""
echo "📋 Summary:"
echo "  • Removed broken/failed images"
echo "  • Removed images with dependency issues" 
echo "  • Removed outdated images (pre-Custom API)"
echo "  • Removed development artifacts"
echo "  • Cleaned up dangling images and build cache"
echo ""
echo "🎯 Next Steps:"
echo "  1. Build fresh Docker images with Custom API integration"
echo "  2. Test new images on ARM64 architecture"
echo "  3. Push clean images to Docker Hub"
echo ""
echo "💡 Remaining useful images:"
docker images | grep redline | head -5
echo ""
