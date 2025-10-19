#!/bin/bash

# Test script for REDLINE Docker setup
# Verifies that all components are properly configured

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

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log "Testing: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_success "$test_name - PASSED"
        ((TESTS_PASSED++))
        return 0
    else
        log_error "$test_name - FAILED"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main test execution
main() {
    log "REDLINE Docker Setup Test"
    log "========================"
    
    # Test 1: Check if Docker is installed
    run_test "Docker installation" "docker --version"
    
    # Test 2: Check if Docker is running
    run_test "Docker daemon running" "docker info"
    
    # Test 3: Check if Docker Compose is available
    run_test "Docker Compose available" "docker compose version"
    
    # Test 4: Check if required files exist
    run_test "Dockerfile exists" "[ -f Dockerfile ]"
    run_test "entrypoint.sh exists" "[ -f entrypoint.sh ]"
    run_test "docker-compose.yml exists" "[ -f docker-compose.yml ]"
    run_test "requirements_docker.txt exists" "[ -f requirements_docker.txt ]"
    
    # Test 5: Check if scripts exist and are executable
    run_test "X11 script exists and executable" "[ -x scripts/run_docker_x11.sh ]"
    run_test "VNC script exists and executable" "[ -x scripts/run_docker_vnc.sh ]"
    run_test "Headless script exists and executable" "[ -x scripts/run_docker_headless.sh ]"
    
    # Test 6: Check if entrypoint is executable
    run_test "Entrypoint script executable" "[ -x entrypoint.sh ]"
    
    # Test 7: Validate Dockerfile syntax (basic check)
    run_test "Dockerfile syntax check" "grep -q 'FROM ubuntu:24.04' Dockerfile"
    
    # Test 8: Check if data directory exists
    run_test "Data directory exists" "[ -d data ]"
    
    # Test 9: Check if main.py exists
    run_test "Main application file exists" "[ -f main.py ]"
    
    # Test 10: Check if redline module exists
    run_test "REDLINE module exists" "[ -d redline ]"
    
    # Optional tests (warnings only)
    log "Running optional tests..."
    
    # Test X11 availability (optional)
    if [ -n "$DISPLAY" ] && command -v xset >/dev/null 2>&1; then
        if xset q >/dev/null 2>&1; then
            log_success "X11 display available - X11 mode will work"
        else
            log_warning "X11 display not accessible - use VNC mode instead"
        fi
    else
        log_warning "X11 not available - use VNC or headless mode"
    fi
    
    # Test VNC client availability (optional)
    if command -v vncviewer >/dev/null 2>&1; then
        log_success "VNC client available - can connect to VNC mode"
    else
        log_warning "VNC client not installed - install with: sudo apt-get install tigervnc-viewer"
    fi
    
    # Summary
    echo ""
    log "Test Summary"
    log "============"
    log_success "Tests Passed: $TESTS_PASSED"
    if [ $TESTS_FAILED -gt 0 ]; then
        log_error "Tests Failed: $TESTS_FAILED"
    else
        log_success "Tests Failed: $TESTS_FAILED"
    fi
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "All tests passed! Docker setup is ready."
        echo ""
        log "Quick Start Commands:"
        log "  X11 Mode:     ./scripts/run_docker_x11.sh"
        log "  VNC Mode:     ./scripts/run_docker_vnc.sh"
        log "  Headless:     ./scripts/run_docker_headless.sh"
        log "  Docker Compose: docker-compose --profile vnc up"
        return 0
    else
        log_error "Some tests failed. Please fix the issues before proceeding."
        return 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verbose      Show detailed output"
        echo ""
        echo "This script tests the REDLINE Docker setup to ensure"
        echo "all components are properly configured."
        exit 0
        ;;
    --verbose)
        # Remove the >/dev/null 2>&1 redirection for verbose output
        set +e
        main "$@"
        ;;
    *)
        main "$@"
        ;;
esac
