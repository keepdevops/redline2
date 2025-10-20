#!/bin/bash
set -e

# REDLINE Dependency Checker Script
# Checks if all required packages are installed and working

echo "🔍 REDLINE Dependency Checker"
echo "============================="

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
MISSING_DEPS=()
OPTIONAL_MISSING=()

# Function to check if REDLINE directory exists
check_redline_directory() {
    if [[ ! -d "$REDLINE_DIR" ]]; then
        print_error "REDLINE directory not found: $REDLINE_DIR"
        print_status "Please run the universal installer first:"
        print_status "./install/install_universal.sh"
        exit 1
    fi
    
    cd "$REDLINE_DIR"
    print_success "Found REDLINE directory: $REDLINE_DIR"
}

# Function to activate virtual environment
activate_venv() {
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        exit 1
    fi
    
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to check a package
check_package() {
    local package_name=$1
    local import_name=$2
    local is_required=${3:-true}
    
    print_status "Checking $package_name..."
    
    if python3 -c "import $import_name; print('✅ $package_name:', $import_name.__version__)" 2>/dev/null; then
        print_success "$package_name is installed and working"
        return 0
    else
        if [[ "$is_required" == "true" ]]; then
            print_error "$package_name is missing or not working"
            MISSING_DEPS+=("$package_name")
            return 1
        else
            print_warning "$package_name is missing (optional)"
            OPTIONAL_MISSING+=("$package_name")
            return 1
        fi
    fi
}

# Function to check all required dependencies
check_required_dependencies() {
    print_status "Checking required dependencies..."
    
    # Core data processing
    check_package "pandas" "pandas" true
    check_package "numpy" "numpy" true
    check_package "configparser" "configparser" true
    
    # Data storage and processing
    check_package "pyarrow" "pyarrow" true
    check_package "polars" "polars" true
    check_package "duckdb" "duckdb" true
    
    # Financial data
    check_package "yfinance" "yfinance" true
    
    # Web framework
    check_package "flask" "flask" true
    check_package "flask-socketio" "flask_socketio" true
    check_package "flask-compress" "flask_compress" true
    
    # Utilities
    check_package "requests" "requests" true
    check_package "urllib3" "urllib3" true
    check_package "python-dateutil" "dateutil" true
    check_package "pytz" "pytz" true
}

# Function to check optional dependencies
check_optional_dependencies() {
    print_status "Checking optional dependencies..."
    
    # Scientific computing
    check_package "matplotlib" "matplotlib" false
    check_package "seaborn" "seaborn" false
    check_package "scipy" "scipy" false
    check_package "scikit-learn" "sklearn" false
    
    # File I/O
    check_package "openpyxl" "openpyxl" false
    check_package "xlsxwriter" "xlsxwriter" false
    
    # System monitoring
    check_package "psutil" "psutil" false
    
    # GUI
    check_package "tkinter" "tkinter" false
}

# Function to check REDLINE module imports
check_redline_modules() {
    print_status "Checking REDLINE module imports..."
    
    # Test basic REDLINE imports
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    import redline
    print('✅ REDLINE module imported')
except ImportError as e:
    print(f'❌ REDLINE module import failed: {e}')
    exit(1)

try:
    from redline.core.data_loader import DataLoader
    print('✅ DataLoader imported')
except ImportError as e:
    print(f'❌ DataLoader import failed: {e}')
    exit(1)

try:
    from redline.database.connector import DatabaseConnector
    print('✅ DatabaseConnector imported')
except ImportError as e:
    print(f'❌ DatabaseConnector import failed: {e}')
    exit(1)

try:
    from redline.gui.main_window import StockAnalyzerGUI
    print('✅ StockAnalyzerGUI imported')
except ImportError as e:
    print(f'❌ StockAnalyzerGUI import failed: {e}')
    exit(1)

print('✅ All REDLINE modules imported successfully')
" || {
        print_error "REDLINE module imports failed"
        return 1
    }
    
    print_success "All REDLINE modules imported successfully"
}

# Function to create a comprehensive test script
create_test_script() {
    print_status "Creating comprehensive test script..."
    
    cat > test_all_dependencies.py << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Comprehensive Dependency Test
Tests all packages and REDLINE modules
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_package(package_name, import_name, is_required=True):
    """Test if a package can be imported."""
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError as e:
        if is_required:
            print(f"❌ {package_name}: {e}")
            return False
        else:
            print(f"⚠️  {package_name}: {e} (optional)")
            return False

def main():
    """Run all dependency tests."""
    print("🧪 REDLINE Dependency Test")
    print("=" * 50)
    
    required_passed = 0
    required_failed = 0
    optional_passed = 0
    optional_failed = 0
    
    # Required dependencies
    print("\n📦 Required Dependencies:")
    required_tests = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("configparser", "configparser"),
        ("pyarrow", "pyarrow"),
        ("polars", "polars"),
        ("duckdb", "duckdb"),
        ("yfinance", "yfinance"),
        ("flask", "flask"),
        ("flask-socketio", "flask_socketio"),
        ("flask-compress", "flask_compress"),
        ("requests", "requests"),
        ("urllib3", "urllib3"),
        ("python-dateutil", "dateutil"),
        ("pytz", "pytz"),
    ]
    
    for package, import_name in required_tests:
        if test_package(package, import_name, True):
            required_passed += 1
        else:
            required_failed += 1
    
    # Optional dependencies
    print("\n📦 Optional Dependencies:")
    optional_tests = [
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("scipy", "scipy"),
        ("scikit-learn", "sklearn"),
        ("openpyxl", "openpyxl"),
        ("xlsxwriter", "xlsxwriter"),
        ("psutil", "psutil"),
        ("tkinter", "tkinter"),
    ]
    
    for package, import_name in optional_tests:
        if test_package(package, import_name, False):
            optional_passed += 1
        else:
            optional_failed += 1
    
    # REDLINE modules
    print("\n📦 REDLINE Modules:")
    try:
        import redline
        print("✅ REDLINE module")
        
        from redline.core.data_loader import DataLoader
        print("✅ DataLoader")
        
        from redline.database.connector import DatabaseConnector
        print("✅ DatabaseConnector")
        
        from redline.gui.main_window import StockAnalyzerGUI
        print("✅ StockAnalyzerGUI")
        
        redline_modules_ok = True
    except ImportError as e:
        print(f"❌ REDLINE modules: {e}")
        redline_modules_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Required: {required_passed} passed, {required_failed} failed")
    print(f"   Optional: {optional_passed} passed, {optional_failed} failed")
    print(f"   REDLINE modules: {'✅ OK' if redline_modules_ok else '❌ FAILED'}")
    
    if required_failed == 0 and redline_modules_ok:
        print("\n🎉 All required dependencies are working!")
        return True
    else:
        print("\n❌ Some dependencies are missing or not working")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

    chmod +x test_all_dependencies.py
    print_success "Test script created: test_all_dependencies.py"
}

# Function to run the comprehensive test
run_comprehensive_test() {
    print_status "Running comprehensive dependency test..."
    
    python3 test_all_dependencies.py || {
        print_error "Dependency test failed"
        return 1
    }
    
    print_success "All dependency tests passed"
}

# Function to show summary and recommendations
show_summary() {
    echo ""
    echo "📋 Dependency Check Summary:"
    echo "============================"
    
    if [[ ${#MISSING_DEPS[@]} -eq 0 ]]; then
        print_success "All required dependencies are installed!"
    else
        print_error "Missing required dependencies:"
        for dep in "${MISSING_DEPS[@]}"; do
            echo "   - $dep"
        done
        echo ""
        print_status "To fix missing dependencies, run:"
        print_status "./install/fix_pandas_import.sh"
        print_status "or"
        print_status "./install/install_universal.sh"
    fi
    
    if [[ ${#OPTIONAL_MISSING[@]} -gt 0 ]]; then
        print_warning "Missing optional dependencies:"
        for dep in "${OPTIONAL_MISSING[@]}"; do
            echo "   - $dep"
        done
        echo ""
        print_status "Optional dependencies can be installed later if needed"
    fi
    
    echo ""
    print_status "To run a comprehensive test:"
    print_status "python3 test_all_dependencies.py"
}

# Main function
main() {
    print_status "Starting REDLINE dependency check..."
    
    # Check REDLINE directory
    check_redline_directory
    
    # Activate virtual environment
    activate_venv
    
    # Check required dependencies
    check_required_dependencies
    
    # Check optional dependencies
    check_optional_dependencies
    
    # Check REDLINE modules
    check_redline_modules
    
    # Create test script
    create_test_script
    
    # Run comprehensive test
    run_comprehensive_test
    
    # Show summary
    show_summary
    
    if [[ ${#MISSING_DEPS[@]} -eq 0 ]]; then
        print_success "Dependency check completed successfully!"
    else
        print_error "Dependency check found issues that need to be fixed"
        exit 1
    fi
}

# Run main function
main "$@"
