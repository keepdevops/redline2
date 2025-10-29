#!/usr/bin/env bash

# Remove ARM64 images NOT in the verified working list of 5

echo "🗑️ ARM64 Non-Working Images Cleanup"
echo "===================================="
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
remove_non_working_image() {
    local image=$1
    local reason=$2
    
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        echo ""
        echo "Removing non-working image: $image"
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

echo "🎯 Target: Keep only the 5 verified working images"
echo ""

# The 5 verified working images (DO NOT REMOVE)
working_images=(
    "keepdevops/redline:v1.0.0-arm64-optimized"
    "redline-webgui-ultra-slim:latest-arm64"
    "redline-webgui-ultra-slim:latest"
    "redline-webgui-ultra-slim:v1.0.0-multiplatform"
    "redline-webgui-compiled-optimized:arm64"
)

echo "✅ PROTECTED (Working Images):"
for img in "${working_images[@]}"; do
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
        echo "  🛡️ $img"
    fi
done

echo ""

# Get initial space usage
echo "📊 Before cleanup:"
docker system df | head -2
echo ""

log_info "Starting non-working ARM64/multiplatform image removal..."

# Remove non-working development images
echo "🔥 Removing non-working ARM64/multiplatform images:"

remove_non_working_image "redline-webgui-optimized:latest" "Not in working list (failed testing)"
remove_non_working_image "redline-webgui-optimized:v1.0.0-multiplatform" "Not in working list (failed testing)"
remove_non_working_image "redline-webgui-ultra-slim-final:arm64" "Not in working list (development artifact)"
remove_non_working_image "redline-webgui-ultra-slim-fixed:arm64" "Not in working list (development artifact)"
remove_non_working_image "redline-webgui-ultra-slim:arm64" "Not in working list (failed testing)"
remove_non_working_image "keepdevops/redline:v1.0.0-arm64-standard" "Not in working list (failed testing)"
remove_non_working_image "redline-webgui-compiled:arm64" "Not in working list (failed testing)"
remove_non_working_image "redline-webgui-compiled:arm64-v1.0.0" "Not in working list (failed testing)"
remove_non_working_image "redline-webgui:latest" "Not in working list (failed testing)"

echo ""
echo "✅ FINAL WORKING IMAGES:"
echo "========================"

remaining_count=0
total_size=0

for img in "${working_images[@]}"; do
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
        size=$(docker images "$img" --format "{{.Size}}")
        echo "  ✅ $img ($size)"
        ((remaining_count++))
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
echo "🎉 ARM64 Cleanup Complete!"
echo "=========================="
echo ""
echo "Working images remaining: $remaining_count"
echo "Non-working images removed: All development artifacts"
echo ""
echo "💡 You now have only the 5 verified working REDLINE images!"
echo "🎯 Perfect for production use with minimal disk footprint!"
