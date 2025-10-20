#!/bin/bash
set -e

# REDLINE Installation Verification Script
# Quick verification of REDLINE installation

echo "🔍 REDLINE Installation Verification"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Configuration
REDLINE_DIR="$HOME/redline"
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test a package
test_package() {
    local package_name=$1
    local import_name=$2
    local is_required=${3:-true}
    
    if python3 -c "import $import_name; print('✅ $package_name')" 2>/dev/null; then
        print_success "$package_name is working"
        ((TESTS_PASSED++))
        return 0
    else
        if [[ "$is_required" == "true" ]]; then
            print_error "$package_name is missing or not working"
            ((TESTS_FAILED++))
            return 1
        else
            print_warning "$package_name is missing (optional)"
            return 1
        fi
    fi
}

# Function to test REDLINE modules
test_redline_modules() {
    print_status "Testing REDLINE modules..."
    
    if python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    import redline
    from redline.core.data_loader import DataLoader
    from redline.database.connector import DatabaseConnector
    from redline.gui.main_window import StockAnalyzerGUI
    print('✅ All REDLINE modules imported successfully')
except ImportError as e:
    print(f'❌ REDLINE module import failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "REDLINE modules are working"
        ((TESTS_PASSED++))
        return 0
    else
        print_error "REDLINE modules are not working"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main verification function
main() {
    # Check if REDLINE directory exists
    if [[ ! -d "$REDLINE_DIR" ]]; then
        print_error "REDLINE directory not found: $REDLINE_DIR"
        print_status "Please run the installation script first: ./install.sh"
        exit 1
    fi
    
    cd "$REDLINE_DIR"
    
    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        print_status "Please run the installation script first: ./install.sh"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    print_status "Starting verification tests..."
    
    # Test required packages
    print_status "Testing required packages..."
    test_package "pandas" "pandas" true
    test_package "numpy" "numpy" true
    test_package "flask" "flask" true
    test_package "duckdb" "duckdb" true
    test_package "pyarrow" "pyarrow" true
    test_package "polars" "polars" true
    test_package "yfinance" "yfinance" true
    
    # Test optional packages
    print_status "Testing optional packages..."
    test_package "matplotlib" "matplotlib" false
    test_package "tkinter" "tkinter" false
    
    # Test REDLINE modules
    test_redline_modules
    
    # Show results
    echo ""
    echo "📊 Verification Results:"
    echo "======================="
    echo "• Tests passed: $TESTS_PASSED"
    echo "• Tests failed: $TESTS_FAILED"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        print_success "All verification tests passed! REDLINE is ready to use."
        echo ""
        echo "🚀 How to start REDLINE:"
        echo "========================"
        echo "• Web interface: ./start_web.sh"
        echo "• GUI interface: ./start_gui.sh"
        echo "• Docker services: ./start_docker.sh"
        echo ""
        echo "🌐 Web interface will be available at: http://localhost:8080"
        exit 0
    else
        print_error "Some verification tests failed. REDLINE may not work properly."
        echo ""
        echo "🛠️  Troubleshooting:"
        echo "==================="
        echo "• Run: ./install/archive/fix_pandas_import.sh"
        echo "• Run: ./install/archive/fix_import_issues.sh"
        echo "• Run: ./install.sh --mode minimal"
        exit 1
    fi
}

# Run main function
main "$@"
