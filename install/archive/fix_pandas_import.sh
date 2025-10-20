#!/bin/bash
set -e

# Fix Pandas Import Issue Script
# Quickly installs pandas and other required dependencies

echo "🔧 Fixing Pandas Import Issue"
echo "============================"

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

# Function to check and activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to install pandas and dependencies
install_pandas_and_deps() {
    print_status "Installing pandas and required dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install core scientific computing packages
    print_status "Installing pandas..."
    pip install pandas
    
    print_status "Installing numpy..."
    pip install numpy
    
    print_status "Installing matplotlib..."
    pip install matplotlib
    
    print_status "Installing seaborn..."
    pip install seaborn
    
    print_status "Installing scipy..."
    pip install scipy
    
    print_status "Installing scikit-learn..."
    pip install scikit-learn
    
    print_status "Installing Flask..."
    pip install flask
    
    print_status "Installing requests..."
    pip install requests
    
    # Install optional dependencies
    print_status "Installing optional dependencies..."
    pip install duckdb pyarrow || print_warning "Some optional dependencies failed to install"
    
    # Install GUI dependencies
    pip install tk || print_warning "Tkinter installation failed"
    
    print_success "All dependencies installed"
}

# Function to test pandas import
test_pandas_import() {
    print_status "Testing pandas import..."
    
    python3 -c "import pandas as pd; print('✅ Pandas version:', pd.__version__)" || {
        print_error "Pandas import failed"
        return 1
    }
    
    print_success "Pandas import successful"
}

# Function to test all REDLINE imports
test_redline_imports() {
    print_status "Testing REDLINE imports..."
    
    # Test basic imports
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    import pandas as pd
    print('✅ Pandas:', pd.__version__)
except ImportError as e:
    print('❌ Pandas:', e)

try:
    import numpy as np
    print('✅ NumPy:', np.__version__)
except ImportError as e:
    print('❌ NumPy:', e)

try:
    import flask
    print('✅ Flask:', flask.__version__)
except ImportError as e:
    print('❌ Flask:', e)

try:
    import redline
    print('✅ REDLINE module')
except ImportError as e:
    print('❌ REDLINE:', e)
" || {
        print_error "Import tests failed"
        return 1
    }
    
    print_success "Import tests completed"
}

# Function to create a simple test script
create_test_script() {
    print_status "Creating test script..."
    
    cat > test_pandas.py << 'EOF'
#!/usr/bin/env python3
"""
Quick Pandas Import Test
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pandas():
    """Test pandas import and basic functionality."""
    try:
        import pandas as pd
        print(f"✅ Pandas imported successfully: {pd.__version__}")
        
        # Test basic pandas functionality
        df = pd.DataFrame({'test': [1, 2, 3]})
        print(f"✅ Pandas DataFrame created: {len(df)} rows")
        
        return True
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Pandas test failed: {e}")
        return False

def test_redline_imports():
    """Test REDLINE module imports."""
    try:
        from redline.core.data_loader import DataLoader
        print("✅ DataLoader imported")
        
        from redline.database.connector import DatabaseConnector
        print("✅ DatabaseConnector imported")
        
        from redline.gui.main_window import StockAnalyzerGUI
        print("✅ StockAnalyzerGUI imported")
        
        return True
    except ImportError as e:
        print(f"❌ REDLINE import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Pandas and REDLINE imports...")
    print("=" * 50)
    
    pandas_ok = test_pandas()
    redline_ok = test_redline_imports()
    
    print("=" * 50)
    if pandas_ok and redline_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
EOF

    chmod +x test_pandas.py
    print_success "Test script created: test_pandas.py"
}

# Function to run the test
run_test() {
    print_status "Running pandas test..."
    
    python3 test_pandas.py || {
        print_error "Pandas test failed"
        print_status "Check the output above for specific errors"
        return 1
    }
    
    print_success "Pandas test passed"
}

# Function to show next steps
show_next_steps() {
    echo ""
    print_success "Pandas import fix completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo ""
    echo "1. Test pandas import:"
    echo "   python3 test_pandas.py"
    echo ""
    echo "2. Try running REDLINE:"
    echo "   python3 main.py --task=gui"
    echo ""
    echo "3. Or start the web interface:"
    echo "   python3 web_app.py"
    echo ""
    echo "4. If you still have issues, run the full fix:"
    echo "   ./install/fix_import_issues.sh"
    echo ""
}

# Main function
main() {
    print_status "Starting pandas import fix..."
    
    # Check REDLINE directory
    check_redline_directory
    
    # Activate virtual environment
    activate_venv
    
    # Install pandas and dependencies
    install_pandas_and_deps
    
    # Test pandas import
    test_pandas_import
    
    # Test all imports
    test_redline_imports
    
    # Create test script
    create_test_script
    
    # Run test
    run_test
    
    # Show next steps
    show_next_steps
    
    print_success "Pandas import fix completed!"
}

# Run main function
main "$@"
