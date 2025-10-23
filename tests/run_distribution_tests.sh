#!/bin/bash
# REDLINE Comprehensive Test Suite
# Tests all distribution formats, platforms, and functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

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

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_header "REDLINE Comprehensive Test Suite"
print_status "Project root: $PROJECT_ROOT"
print_status "Platform: $(uname -s) $(uname -m)"

# Parse command line arguments
TEST_PYPI=true
TEST_EXECUTABLES=true
TEST_DOCKER=true
TEST_SOURCE=true
TEST_LICENSE=true
TEST_UPDATES=true
TEST_BUILD=true
TEST_WORKFLOWS=true
TEST_WEBSITE=true
CLEAN_BUILD=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-pypi)
            TEST_PYPI=false
            shift
            ;;
        --no-executables)
            TEST_EXECUTABLES=false
            shift
            ;;
        --no-docker)
            TEST_DOCKER=false
            shift
            ;;
        --no-source)
            TEST_SOURCE=false
            shift
            ;;
        --no-license)
            TEST_LICENSE=false
            shift
            ;;
        --no-updates)
            TEST_UPDATES=false
            shift
            ;;
        --no-build)
            TEST_BUILD=false
            shift
            ;;
        --no-workflows)
            TEST_WORKFLOWS=false
            shift
            ;;
        --no-website)
            TEST_WEBSITE=false
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "REDLINE Test Suite"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-pypi         Skip PyPI package tests"
            echo "  --no-executables   Skip executable tests"
            echo "  --no-docker        Skip Docker tests"
            echo "  --no-source        Skip source archive tests"
            echo "  --no-license       Skip license system tests"
            echo "  --no-updates       Skip update system tests"
            echo "  --no-build         Skip build script tests"
            echo "  --no-workflows     Skip GitHub workflow tests"
            echo "  --no-website       Skip distribution website tests"
            echo "  --clean            Clean build artifacts before testing"
            echo "  --verbose          Verbose output"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run all tests"
            echo "  $0 --clean         # Clean build and run all tests"
            echo "  $0 --no-docker     # Run all tests except Docker"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean build artifacts if requested
if [[ "$CLEAN_BUILD" == "true" ]]; then
    print_header "Cleaning Build Artifacts"
    print_status "Removing build artifacts..."
    
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf __pycache__/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Build artifacts cleaned"
fi

# Create test directories
mkdir -p test_results
mkdir -p dist/{packages,executables,releases,website}

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    print_status "Testing: $test_name"
    if [[ -n "$test_description" ]]; then
        print_status "Description: $test_description"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        print_status "Command: $test_command"
    fi
    
    if eval "$test_command"; then
        print_success "$test_name: PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "$test_name: FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Start testing
print_header "Starting Test Execution"

# Test 1: PyPI Package Tests
if [[ "$TEST_PYPI" == "true" ]]; then
    print_header "PyPI Package Tests"
    
    run_test "PyPI Build" \
        "python -m build --outdir dist/packages/" \
        "Build wheel and source distribution"
    
    run_test "PyPI Wheel Check" \
        "python -m twine check dist/packages/*" \
        "Validate PyPI package format"
    
    run_test "PyPI Installation Test" \
        "pip install dist/packages/*.whl --force-reinstall" \
        "Test package installation"
    
    run_test "Console Commands Test" \
        "redline --help && redline-gui --help && redline-web --help" \
        "Test console command availability"
fi

# Test 2: Executable Tests
if [[ "$TEST_EXECUTABLES" == "true" ]]; then
    print_header "Executable Tests"
    
    run_test "Executable Build" \
        "bash build/scripts/build_executables.sh" \
        "Build PyInstaller executables"
    
    run_test "GUI Executable Test" \
        "test -f dist/executables/redline-gui* && dist/executables/redline-gui* --help" \
        "Test GUI executable functionality"
    
    run_test "Web Executable Test" \
        "test -f dist/executables/redline-web* && dist/executables/redline-web* --help" \
        "Test web executable functionality"
fi

# Test 3: Docker Tests
if [[ "$TEST_DOCKER" == "true" ]] && command_exists docker; then
    print_header "Docker Tests"
    
    run_test "Docker Build" \
        "docker build -f Dockerfile.working-insights -t redline-test ." \
        "Build Docker image"
    
    run_test "Docker Run Test" \
        "docker run --rm redline-test --help" \
        "Test Docker container execution"
    
    run_test "Docker Compose Test" \
        "test -f docker-compose-working.yml" \
        "Validate Docker Compose configuration"
else
    print_warning "Docker tests skipped (Docker not available)"
fi

# Test 4: Source Archive Tests
if [[ "$TEST_SOURCE" == "true" ]]; then
    print_header "Source Archive Tests"
    
    run_test "Source Archive Creation" \
        "bash build/scripts/create_release.sh" \
        "Create source archives"
    
    run_test "Tar Archive Test" \
        "test -f dist/releases/*.tar.gz && tar -tzf dist/releases/*.tar.gz | head -5" \
        "Validate tar archive structure"
    
    run_test "Zip Archive Test" \
        "test -f dist/releases/*.zip && unzip -l dist/releases/*.zip | head -5" \
        "Validate zip archive structure"
fi

# Test 5: License System Tests
if [[ "$TEST_LICENSE" == "true" ]]; then
    print_header "License System Tests"
    
    run_test "License Server Test" \
        "python licensing/server/license_server.py --help" \
        "Test license server functionality"
    
    run_test "License Client Test" \
        "python licensing/client/license_validator.py --help" \
        "Test license client functionality"
fi

# Test 6: Update System Tests
if [[ "$TEST_UPDATES" == "true" ]]; then
    print_header "Update System Tests"
    
    run_test "Update Checker Test" \
        "python redline/updates/update_checker.py --help" \
        "Test update checker functionality"
    
    run_test "Update Installer Test" \
        "python redline/updates/update_installer.py --help" \
        "Test update installer functionality"
fi

# Test 7: Build Script Tests
if [[ "$TEST_BUILD" == "true" ]]; then
    print_header "Build Script Tests"
    
    run_test "Build Scripts Exist" \
        "test -f build/scripts/build_all.sh && test -f build/scripts/build_executables.sh && test -f build/scripts/create_release.sh" \
        "Verify build scripts exist"
    
    run_test "Build Scripts Executable" \
        "test -x build/scripts/build_all.sh && test -x build/scripts/build_executables.sh && test -x build/scripts/create_release.sh" \
        "Verify build scripts are executable"
    
    run_test "Version Script Test" \
        "python scripts/update_version.py --help" \
        "Test version management script"
fi

# Test 8: GitHub Workflow Tests
if [[ "$TEST_WORKFLOWS" == "true" ]]; then
    print_header "GitHub Workflow Tests"
    
    run_test "Docker Workflow Test" \
        "test -f .github/workflows/docker-publish.yml" \
        "Verify Docker workflow exists"
    
    run_test "Release Workflow Test" \
        "test -f .github/workflows/release.yml" \
        "Verify release workflow exists"
    
    run_test "Workflow YAML Syntax" \
        "python -c \"import yaml; yaml.safe_load(open('.github/workflows/docker-publish.yml')); yaml.safe_load(open('.github/workflows/release.yml'))\"" \
        "Validate workflow YAML syntax"
fi

# Test 9: Distribution Website Tests
if [[ "$TEST_WEBSITE" == "true" ]]; then
    print_header "Distribution Website Tests"
    
    run_test "Website Exists" \
        "test -f dist/website/index.html" \
        "Verify distribution website exists"
    
    run_test "Website HTML Validation" \
        "grep -q '<html' dist/website/index.html && grep -q '</html>' dist/website/index.html" \
        "Validate website HTML structure"
fi

# Test 10: Integration Tests
print_header "Integration Tests"

run_test "Python Distribution Test" \
    "python tests/test_distribution.py" \
    "Run comprehensive Python distribution tests"

run_test "Package Structure Test" \
    "python -c \"import redline; print('Version:', redline.__version__)\"" \
    "Test package import and version"

# Final Results
print_header "Test Results Summary"
print_status "Total Tests: $TOTAL_TESTS"
print_success "Passed: $PASSED_TESTS"
print_error "Failed: $FAILED_TESTS"

if [[ $FAILED_TESTS -eq 0 ]]; then
    print_success "🎉 All tests passed! REDLINE distribution system is ready for production."
    exit 0
else
    print_error "❌ Some tests failed. Please review the output above."
    exit 1
fi
