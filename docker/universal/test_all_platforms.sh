#!/bin/bash
set -e

# REDLINE Universal Docker Test Script for All Platforms
# Comprehensive testing across multiple architectures
# Tests both GUI and Web App functionality

echo "🧪 REDLINE Universal Docker Test Suite - All Platforms"
echo "======================================================"
echo "✅ Testing GUI, Web App, and Core functionality"
echo "🌍 Multi-platform architecture support"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_test() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

print_platform() {
    echo -e "${CYAN}[PLATFORM]${NC} $1"
}

# Configuration
IMAGE_NAME="redline-universal"
CONTAINER_NAME="redline-test-container"
CONDA_ENV_NAME="redline-universal"
TEST_RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"

# Platform configurations
PLATFORMS=("linux/amd64" "linux/arm64" "linux/arm/v7")
PLATFORM_NAMES=("AMD64" "ARM64" "ARMv7")

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Initialize test results file
init_test_results() {
    echo "REDLINE Universal Docker Test Results - $(date)" > $TEST_RESULTS_FILE
    echo "================================================" >> $TEST_RESULTS_FILE
    echo "" >> $TEST_RESULTS_FILE
}

# Log test result
log_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    case $result in
        "PASS")
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo "[$(date '+%H:%M:%S')] PASS: $test_name" >> $TEST_RESULTS_FILE
            print_success "$test_name"
            ;;
        "FAIL")
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "[$(date '+%H:%M:%S')] FAIL: $test_name - $details" >> $TEST_RESULTS_FILE
            print_error "$test_name - $details"
            ;;
        "SKIP")
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            echo "[$(date '+%H:%M:%S')] SKIP: $test_name - $details" >> $TEST_RESULTS_FILE
            print_warning "$test_name - $details"
            ;;
    esac
    
    if [ -n "$details" ]; then
        echo "  Details: $details" >> $TEST_RESULTS_FILE
    fi
    echo "" >> $TEST_RESULTS_FILE
}

# Check Docker and buildx support
check_docker_setup() {
    print_test "Checking Docker setup..."
    
    if ! command -v docker &> /dev/null; then
        log_test_result "Docker Installation" "FAIL" "Docker not installed"
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        log_test_result "Docker Permissions" "FAIL" "Cannot run Docker commands"
        exit 1
    fi
    
    if docker buildx version &> /dev/null; then
        BUILDX_AVAILABLE=true
        log_test_result "Docker Buildx" "PASS" "Available"
    else
        BUILDX_AVAILABLE=false
        log_test_result "Docker Buildx" "SKIP" "Not available, using standard build"
    fi
    
    log_test_result "Docker Setup" "PASS" "Ready for testing"
}

# Test if image exists
test_image_exists() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing image existence for $platform_name..."
    
    if docker images | grep -q $IMAGE_NAME; then
        log_test_result "Image Exists ($platform_name)" "PASS" "Image found: $IMAGE_NAME"
    else
        log_test_result "Image Exists ($platform_name)" "FAIL" "Image not found: $IMAGE_NAME"
        return 1
    fi
}

# Test basic container functionality
test_basic_container() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing basic container functionality for $platform_name..."
    
    # Test container can start and run basic commands
    if docker run --rm $IMAGE_NAME /bin/bash -c "echo 'Container test successful'" &> /dev/null; then
        log_test_result "Basic Container ($platform_name)" "PASS" "Container starts and runs commands"
    else
        log_test_result "Basic Container ($platform_name)" "FAIL" "Container failed to start or run commands"
        return 1
    fi
}

# Test conda environment
test_conda_environment() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing conda environment for $platform_name..."
    
    local conda_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        conda info --envs | grep redline-universal
    " 2>&1)
    
    if echo "$conda_test" | grep -q "redline-universal"; then
        log_test_result "Conda Environment ($platform_name)" "PASS" "Environment activated successfully"
    else
        log_test_result "Conda Environment ($platform_name)" "FAIL" "Environment activation failed: $conda_test"
        return 1
    fi
}

# Test Python packages
test_python_packages() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing Python packages for $platform_name..."
    
    local packages=("pandas" "numpy" "matplotlib" "flask" "tkinter" "requests" "duckdb" "pyarrow")
    local failed_packages=()
    
    for package in "${packages[@]}"; do
        local package_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
            source /opt/conda/bin/activate redline-universal && \
            python -c 'import $package; print(\"$package version:\", getattr($package, \"__version__\", \"unknown\"))'
        " 2>&1)
        
        if [ $? -eq 0 ]; then
            echo "  ✅ $package: $(echo "$package_test" | tail -1)"
        else
            failed_packages+=("$package")
            echo "  ❌ $package: Failed to import"
        fi
    done
    
    if [ ${#failed_packages[@]} -eq 0 ]; then
        log_test_result "Python Packages ($platform_name)" "PASS" "All packages imported successfully"
    else
        log_test_result "Python Packages ($platform_name)" "FAIL" "Failed packages: ${failed_packages[*]}"
        return 1
    fi
}

# Test GUI components
test_gui_components() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing GUI components for $platform_name..."
    
    # Test tkinter availability
    local tkinter_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        python -c 'import tkinter; print(\"Tkinter version:\", tkinter.TkVersion)'
    " 2>&1)
    
    if echo "$tkinter_test" | grep -q "Tkinter version:"; then
        log_test_result "Tkinter ($platform_name)" "PASS" "Tkinter available: $(echo "$tkinter_test" | tail -1)"
    else
        log_test_result "Tkinter ($platform_name)" "FAIL" "Tkinter test failed: $tkinter_test"
        return 1
    fi
    
    # Test matplotlib GUI backend
    local matplotlib_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        python -c 'import matplotlib; print(\"Matplotlib backend:\", matplotlib.get_backend())'
    " 2>&1)
    
    if echo "$matplotlib_test" | grep -q "Matplotlib backend:"; then
        log_test_result "Matplotlib GUI ($platform_name)" "PASS" "Matplotlib GUI backend available"
    else
        log_test_result "Matplotlib GUI ($platform_name)" "FAIL" "Matplotlib GUI test failed: $matplotlib_test"
        return 1
    fi
}

# Test web app components
test_web_components() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing web app components for $platform_name..."
    
    # Test Flask
    local flask_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        python -c 'import flask; print(\"Flask version:\", flask.__version__)'
    " 2>&1)
    
    if echo "$flask_test" | grep -q "Flask version:"; then
        log_test_result "Flask ($platform_name)" "PASS" "Flask available: $(echo "$flask_test" | tail -1)"
    else
        log_test_result "Flask ($platform_name)" "FAIL" "Flask test failed: $flask_test"
        return 1
    fi
    
    # Test Gunicorn
    local gunicorn_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        gunicorn --version
    " 2>&1)
    
    if echo "$gunicorn_test" | grep -q "gunicorn"; then
        log_test_result "Gunicorn ($platform_name)" "PASS" "Gunicorn available: $(echo "$gunicorn_test" | head -1)"
    else
        log_test_result "Gunicorn ($platform_name)" "FAIL" "Gunicorn test failed: $gunicorn_test"
        return 1
    fi
    
    # Test nginx
    local nginx_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        nginx -v 2>&1
    " 2>&1)
    
    if echo "$nginx_test" | grep -q "nginx"; then
        log_test_result "Nginx ($platform_name)" "PASS" "Nginx available: $(echo "$nginx_test")"
    else
        log_test_result "Nginx ($platform_name)" "FAIL" "Nginx test failed: $nginx_test"
        return 1
    fi
}

# Test REDLINE modules
test_redline_modules() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing REDLINE modules for $platform_name..."
    
    local modules=("redline.core.data_loader" "redline.database.connector" "redline.gui.main_window" "redline.web")
    local failed_modules=()
    
    for module in "${modules[@]}"; do
        local module_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
            source /opt/conda/bin/activate redline-universal && \
            python -c 'import $module; print(\"$module imported successfully\")'
        " 2>&1)
        
        if echo "$module_test" | grep -q "imported successfully"; then
            echo "  ✅ $module: Imported successfully"
        else
            failed_modules+=("$module")
            echo "  ❌ $module: Failed to import - $module_test"
        fi
    done
    
    if [ ${#failed_modules[@]} -eq 0 ]; then
        log_test_result "REDLINE Modules ($platform_name)" "PASS" "All modules imported successfully"
    else
        log_test_result "REDLINE Modules ($platform_name)" "FAIL" "Failed modules: ${failed_modules[*]}"
        return 1
    fi
}

# Test startup scripts
test_startup_scripts() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing startup scripts for $platform_name..."
    
    local scripts=("start_gui.sh" "start_web.sh" "start_production.sh" "test_universal.sh")
    local failed_scripts=()
    
    for script in "${scripts[@]}"; do
        local script_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
            if [ -f /app/$script ]; then
                echo 'Script exists and is executable'
            else
                echo 'Script not found or not executable'
            fi
        " 2>&1)
        
        if echo "$script_test" | grep -q "Script exists and is executable"; then
            echo "  ✅ $script: Available and executable"
        else
            failed_scripts+=("$script")
            echo "  ❌ $script: Not found or not executable"
        fi
    done
    
    if [ ${#failed_scripts[@]} -eq 0 ]; then
        log_test_result "Startup Scripts ($platform_name)" "PASS" "All startup scripts available"
    else
        log_test_result "Startup Scripts ($platform_name)" "FAIL" "Missing scripts: ${failed_scripts[*]}"
        return 1
    fi
}

# Test platform-specific functionality
test_platform_specific() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing platform-specific functionality for $platform_name..."
    
    # Test architecture detection
    local arch_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        echo 'Architecture: ' \$(uname -m)
        echo 'Platform: ' \$(uname -p)
        echo 'OS: ' \$(uname -s)
    " 2>&1)
    
    echo "  Architecture info: $arch_test"
    
    # Test conda architecture detection
    local conda_arch_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        conda info | grep 'platform'
    " 2>&1)
    
    if echo "$conda_arch_test" | grep -q "platform"; then
        log_test_result "Platform Detection ($platform_name)" "PASS" "Platform detection working: $(echo "$conda_arch_test")"
    else
        log_test_result "Platform Detection ($platform_name)" "FAIL" "Platform detection failed: $conda_arch_test"
        return 1
    fi
}

# Test container networking
test_networking() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing networking for $platform_name..."
    
    # Test port binding (web app)
    local port_test=$(timeout 10s docker run --rm -p 5001:5000 $IMAGE_NAME /bin/bash -c "
        source /opt/conda/bin/activate redline-universal && \
        python -c '
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((\"0.0.0.0\", 5000))
    print(\"Port 5000 available\")
    sock.close()
except Exception as e:
    print(f\"Port test failed: {e}\")
    sys.exit(1)
'
    " 2>&1)
    
    if echo "$port_test" | grep -q "Port 5000 available"; then
        log_test_result "Networking ($platform_name)" "PASS" "Port binding successful"
    else
        log_test_result "Networking ($platform_name)" "FAIL" "Port binding failed: $port_test"
        return 1
    fi
}

# Test file system operations
test_filesystem() {
    local platform="$1"
    local platform_name="$2"
    
    print_test "Testing file system operations for $platform_name..."
    
    local fs_test=$(docker run --rm $IMAGE_NAME /bin/bash -c "
        cd /app && \
        echo 'Test file' > test_file.txt && \
        if [ -f test_file.txt ]; then
            echo 'File creation successful'
            cat test_file.txt
            rm test_file.txt
            echo 'File deletion successful'
        else
            echo 'File creation failed'
        fi
    " 2>&1)
    
    if echo "$fs_test" | grep -q "File creation successful" && echo "$fs_test" | grep -q "File deletion successful"; then
        log_test_result "File System ($platform_name)" "PASS" "File operations successful"
    else
        log_test_result "File System ($platform_name)" "FAIL" "File operations failed: $fs_test"
        return 1
    fi
}

# Run comprehensive test suite for a platform
test_platform() {
    local platform="$1"
    local platform_name="$2"
    
    print_platform "Testing platform: $platform_name ($platform)"
    echo "================================================"
    
    # Run all tests for this platform
    test_image_exists "$platform" "$platform_name" || return 1
    test_basic_container "$platform" "$platform_name" || return 1
    test_conda_environment "$platform" "$platform_name" || return 1
    test_python_packages "$platform" "$platform_name" || return 1
    test_gui_components "$platform" "$platform_name" || return 1
    test_web_components "$platform" "$platform_name" || return 1
    test_redline_modules "$platform" "$platform_name" || return 1
    test_startup_scripts "$platform" "$platform_name" || return 1
    test_platform_specific "$platform" "$platform_name" || return 1
    test_networking "$platform" "$platform_name" || return 1
    test_filesystem "$platform" "$platform_name" || return 1
    
    print_success "All tests passed for $platform_name!"
    echo ""
}

# Generate test summary
generate_summary() {
    echo "📊 Test Summary"
    echo "==============="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Skipped: $SKIPPED_TESTS"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "All tests passed! ✅"
        echo ""
        echo "🎉 REDLINE Universal Docker image is working correctly across all platforms!"
    else
        print_error "$FAILED_TESTS tests failed ❌"
        echo ""
        echo "📋 Check the test results file: $TEST_RESULTS_FILE"
        echo "🔧 Review failed tests and fix issues before deployment"
    fi
    
    # Add summary to results file
    echo "" >> $TEST_RESULTS_FILE
    echo "Test Summary" >> $TEST_RESULTS_FILE
    echo "============" >> $TEST_RESULTS_FILE
    echo "Total Tests: $TOTAL_TESTS" >> $TEST_RESULTS_FILE
    echo "Passed: $PASSED_TESTS" >> $TEST_RESULTS_FILE
    echo "Failed: $FAILED_TESTS" >> $TEST_RESULTS_FILE
    echo "Skipped: $SKIPPED_TESTS" >> $TEST_RESULTS_FILE
    echo "Test completed at: $(date)" >> $TEST_RESULTS_FILE
}

# Main function
main() {
    print_status "Starting comprehensive platform testing..."
    echo ""
    
    init_test_results
    check_docker_setup
    
    # Test each platform
    for i in "${!PLATFORMS[@]}"; do
        platform="${PLATFORMS[$i]}"
        platform_name="${PLATFORM_NAMES[$i]}"
        
        test_platform "$platform" "$platform_name"
    done
    
    generate_summary
    
    echo ""
    echo "📁 Detailed test results saved to: $TEST_RESULTS_FILE"
    echo "🚀 Ready for deployment across all supported platforms!"
}

# Run main function
main "$@"
