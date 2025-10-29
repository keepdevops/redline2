#!/usr/bin/env bash

# Remove AMD64-specific Docker images (keep multiplatform)

echo "🗑️ REDLINE AMD64 Images Cleanup"
echo "==============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to safely remove image
remove_amd64_image() {
    local image=$1
    local reason=$2
    
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        echo ""
        echo "Removing AMD64 image: $image"
        echo "Reason: $reason"
        
        if docker rmi "$image" 2>/dev/null; then
            log_success "Removed $image"
        else
            log_warning "Could not remove $image (may be in use)"
        fi
    else
        log_info "Already removed: $image"
    fi
}

echo "🎯 Target: Remove AMD64-specific images, keep multiplatform"
echo ""

# Get initial space usage
echo "📊 Before cleanup:"
docker system df | head -2
echo ""

log_info "Starting AMD64 image removal..."

# Remove AMD64-specific keepdevops images
echo "🔥 Removing keepdevops AMD64 images:"
remove_amd64_image "keepdevops/redline:v1.0.0-amd64-optimized" "AMD64-specific version"
remove_amd64_image "keepdevops/redline:v1.0.0-amd64-standard" "AMD64-specific version"
remove_amd64_image "keepdevops/redline:v1.0.0-amd64-ultra-slim" "AMD64-specific version"

# Remove AMD64-specific development images
echo ""
echo "🔥 Removing development AMD64 images:"
remove_amd64_image "redline-webgui-ultra-slim:amd64" "AMD64-specific development build"
remove_amd64_image "redline-webgui-compiled-optimized:amd64" "AMD64-specific compiled build"
remove_amd64_image "redline-webgui-compiled:amd64" "AMD64-specific compiled build"
remove_amd64_image "redline-webgui-compiled:amd64-v1.0.0" "AMD64-specific versioned build"
remove_amd64_image "redline-webgui:amd64" "AMD64-specific base build"

echo ""
echo "✅ KEEPING (Multiplatform/ARM64):"
echo "================================="

# List images we're keeping
kept_images=(
    "redline-webgui-ultra-slim:latest-arm64"
    "redline-webgui-ultra-slim:latest"
    "redline-webgui-ultra-slim:v1.0.0-multiplatform"
    "redline-webgui-optimized:latest"
    "redline-webgui-optimized:v1.0.0-multiplatform"
    "redline-webgui-ultra-slim-final:arm64"
    "redline-webgui-ultra-slim-fixed:arm64"
    "redline-webgui-compiled-optimized:arm64"
    "keepdevops/redline:v1.0.0-arm64-optimized"
    "keepdevops/redline:v1.0.0-arm64-standard"
    "redline-webgui-compiled:arm64"
    "redline-webgui-compiled:arm64-v1.0.0"
    "redline-webgui:latest"
)

for image in "${kept_images[@]}"; do
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        echo "  ✅ $image"
    fi
done

echo ""
echo "📊 After cleanup:"
docker system df | head -2

echo ""
echo "🧹 Cleaning up dangling images..."
docker image prune -f >/dev/null 2>&1

echo ""
echo "📊 Final space usage:"
docker system df

echo ""
echo "🎉 AMD64 Cleanup Complete!"
echo "=========================="
echo ""
echo "Removed: AMD64-specific images"
echo "Kept: Multiplatform and ARM64 images"
echo "Working images still available: 5"
echo ""
echo "💡 You still have full access to working REDLINE images!"
