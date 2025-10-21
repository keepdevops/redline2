#!/bin/bash

# REDLINE Docker Build Test Script
# Helps debug pip installation issues

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Test 1: Check if requirements file exists and is readable
test_requirements_file() {
    log "Testing requirements file..."
    
    if [ ! -f "requirements-simple.txt" ]; then
        log_error "requirements-simple.txt not found"
        return 1
    fi
    
    log "File exists, checking content..."
    cat requirements-simple.txt
    echo ""
    
    log_success "Requirements file is readable"
}

# Test 2: Test pip installation locally
test_local_pip() {
    log "Testing pip installation locally..."
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 not found locally"
        return 1
    fi
    
    log "pip3 version: $(pip3 --version)"
    
    # Test installing just Flask
    log "Testing Flask installation..."
    pip3 install --dry-run flask==2.3.3 || log_warning "Dry run failed"
    
    log_success "Local pip test completed"
}

# Test 3: Build with ultra-simple Dockerfile
test_ultra_simple_build() {
    log "Testing ultra-simple Docker build..."
    
    # Copy ultra-minimal requirements
    cp requirements-ultra-minimal.txt requirements-simple.txt
    
    # Build with ultra-simple Dockerfile
    docker build \
        --file dockerfiles/Dockerfile.ultra-simple \
        --tag redline-test-ultra \
        .
    
    log_success "Ultra-simple build completed"
}

# Test 4: Build with debug output
test_debug_build() {
    log "Testing debug Docker build..."
    
    # Restore original requirements
    git checkout requirements-simple.txt
    
    # Build with debug Dockerfile
    docker build \
        --file dockerfiles/Dockerfile.debug \
        --tag redline-test-debug \
        .
    
    log_success "Debug build completed"
}

# Main function
main() {
    log "REDLINE Docker Build Test"
    log "========================"
    
    # Find project root
    PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
    cd "$PROJECT_ROOT"
    
    log "Project root: $PROJECT_ROOT"
    
    # Run tests
    test_requirements_file
    test_local_pip
    test_ultra_simple_build
    test_debug_build
    
    log_success "All tests completed!"
}

# Run main function
main "$@"
