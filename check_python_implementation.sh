#!/usr/bin/env bash

# Check Python implementation in working Docker images

echo "🐍 Checking Python Implementation in Working Docker Images"
echo "========================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Cleanup function
cleanup() {
    docker stop python-check-container 2>/dev/null || true
    docker rm python-check-container 2>/dev/null || true
}
trap cleanup EXIT

# Check Python implementation in image
check_python_impl() {
    local image=$1
    local container_name="python-check-container"
    
    echo ""
    echo "=================================================="
    log_info "Checking: $image"
    echo "=================================================="
    
    # Start container
    if ! docker run -d --name "$container_name" "$image" >/dev/null 2>&1; then
        log_warning "Could not start container"
        return 1
    fi
    
    # Wait a moment for container to be ready
    sleep 3
    
    # Check Python implementation
    echo "🔍 Python Implementation Check:"
    echo "-------------------------------"
    
    # Get Python version and implementation
    python_info=$(docker exec "$container_name" python3 -c "
import sys
import platform
print(f'Implementation: {sys.implementation.name}')
print(f'Version: {sys.version.split()[0]}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.machine()}')
print(f'Compiler: {platform.python_compiler()}')
" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "$python_info"
        
        # Check if it's CPython
        if echo "$python_info" | grep -q "Implementation: cpython"; then
            log_success "✅ CPython detected!"
            
            # Check for compiled bytecode
            echo ""
            echo "🔍 Bytecode Compilation Check:"
            echo "------------------------------"
            
            compiled_check=$(docker exec "$container_name" find /app -name "*.pyc" | wc -l 2>/dev/null)
            if [ "$compiled_check" -gt 0 ]; then
                log_success "📦 Has compiled bytecode ($compiled_check .pyc files)"
            else
                log_info "📝 No pre-compiled bytecode found"
            fi
            
            # Check optimization level
            echo ""  
            echo "🔍 Python Optimization Check:"
            echo "-----------------------------"
            
            opt_check=$(docker exec "$container_name" python3 -c "
import sys
if sys.flags.optimize == 0:
    print('Standard Python (no optimization)')
elif sys.flags.optimize == 1:
    print('Optimized Python (-O flag)')  
elif sys.flags.optimize == 2:
    print('Highly optimized Python (-OO flag)')
else:
    print(f'Custom optimization level: {sys.flags.optimize}')
" 2>/dev/null)
            
            echo "$opt_check"
            
            return 0
        else
            log_warning "❌ Not CPython - using different implementation"
            return 1
        fi
    else
        log_warning "Could not check Python implementation"
        return 1
    fi
    
    # Stop container
    docker stop "$container_name" >/dev/null 2>&1
    docker rm "$container_name" >/dev/null 2>&1
}

# Working images to check
working_images=(
    "keepdevops/redline:v1.0.0-arm64-optimized"
    "redline-webgui-ultra-slim:latest-arm64"
    "redline-webgui-ultra-slim:latest"
    "redline-webgui-ultra-slim:v1.0.0-multiplatform"
    "redline-webgui-compiled-optimized:arm64"
)

cpython_images=()
other_images=()

for image in "${working_images[@]}"; do
    if check_python_impl "$image"; then
        cpython_images+=("$image")
    else
        other_images+=("$image")
    fi
    
    # Cleanup between tests
    docker stop python-check-container 2>/dev/null || true
    docker rm python-check-container 2>/dev/null || true
done

echo ""
echo "🎯 PYTHON IMPLEMENTATION SUMMARY"
echo "================================"
echo ""

if [ ${#cpython_images[@]} -gt 0 ]; then
    echo "✅ CPYTHON IMAGES (${#cpython_images[@]} found):"
    for img in "${cpython_images[@]}"; do
        echo "  • $img"
    done
else
    echo "❌ No CPython images found"
fi

if [ ${#other_images[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  NON-CPYTHON IMAGES (${#other_images[@]} found):"
    for img in "${other_images[@]}"; do
        echo "  • $img"
    done
fi

echo ""
echo "💡 RECOMMENDATION:"
if [ ${#cpython_images[@]} -gt 0 ]; then
    echo "Use CPython images for:"
    echo "  • Maximum compatibility with Python packages"
    echo "  • Standard Python behavior and debugging"
    echo "  • Best ecosystem support"
else
    echo "All working images use alternative Python implementations"
fi

echo ""
