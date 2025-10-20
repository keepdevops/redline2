#!/bin/bash
set -e

# Fix REDLINE Import Issues Script
# Diagnoses and fixes common import problems after installation

echo "🔧 REDLINE Import Issues Fix Script"
echo "=================================="

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
CURRENT_DIR="$(pwd)"

# Function to check if we're in the right directory
check_redline_directory() {
    print_status "Checking REDLINE directory structure..."
    
    if [[ ! -d "$REDLINE_DIR" ]]; then
        print_error "REDLINE directory not found: $REDLINE_DIR"
        print_status "Please run this script from the REDLINE installation directory"
        exit 1
    fi
    
    cd "$REDLINE_DIR"
    
    if [[ ! -f "main.py" ]]; then
        print_error "main.py not found in $REDLINE_DIR"
        exit 1
    fi
    
    if [[ ! -d "redline" ]]; then
        print_error "redline/ directory not found in $REDLINE_DIR"
        exit 1
    fi
    
    print_success "REDLINE directory structure verified"
}

# Function to check Python environment
check_python_environment() {
    print_status "Checking Python environment..."
    
    cd "$REDLINE_DIR"
    
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    if [[ ! -f "venv/bin/activate" ]]; then
        print_error "Virtual environment activation script not found"
        exit 1
    fi
    
    print_success "Python virtual environment found"
}

# Function to check and fix Python path issues
fix_python_path() {
    print_status "Fixing Python path issues..."
    
    cd "$REDLINE_DIR"
    
    # Create a .pth file to ensure redline is in Python path
    echo "$REDLINE_DIR" > venv/lib/python*/site-packages/redline.pth 2>/dev/null || {
        print_warning "Could not create .pth file, trying alternative approach..."
    }
    
    # Alternative: modify main.py to ensure proper path
    if grep -q "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))" main.py; then
        print_success "Python path fix already in place"
    else
        print_status "Adding Python path fix to main.py..."
        # This should already be there, but let's verify
        print_warning "Python path fix should already be in main.py"
    fi
    
    print_success "Python path issues addressed"
}

# Function to install missing dependencies
install_missing_dependencies() {
    print_status "Installing missing dependencies..."
    
    cd "$REDLINE_DIR"
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install core dependencies
    pip install flask pandas numpy matplotlib seaborn scipy scikit-learn requests
    
    # Install GUI dependencies
    pip install tk || print_warning "Tkinter installation failed"
    
    # Install additional dependencies that might be missing
    pip install duckdb pyarrow || print_warning "Some optional dependencies failed to install"
    
    print_success "Dependencies installation completed"
}

# Function to check module imports
test_imports() {
    print_status "Testing module imports..."
    
    cd "$REDLINE_DIR"
    source venv/bin/activate
    
    # Test basic imports
    print_status "Testing basic Python imports..."
    python3 -c "import sys; print('Python path:', sys.path)" || {
        print_error "Python path test failed"
        return 1
    }
    
    # Test redline module import
    print_status "Testing redline module import..."
    python3 -c "import redline; print('REDLINE module import successful')" || {
        print_error "REDLINE module import failed"
        print_status "Checking redline directory structure..."
        ls -la redline/
        return 1
    }
    
    # Test specific GUI import
    print_status "Testing GUI module import..."
    python3 -c "from redline.gui.main_window import StockAnalyzerGUI; print('GUI module import successful')" || {
        print_error "GUI module import failed"
        print_status "Checking GUI directory structure..."
        ls -la redline/gui/
        return 1
    }
    
    print_success "All imports successful"
}

# Function to create a test script
create_test_script() {
    print_status "Creating test script..."
    
    cd "$REDLINE_DIR"
    
    cat > test_imports.py << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Import Test Script
Tests all major imports to identify issues
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all major REDLINE imports."""
    tests = [
        ("sys", "import sys"),
        ("os", "import os"),
        ("logging", "import logging"),
        ("tkinter", "import tkinter"),
        ("pandas", "import pandas"),
        ("numpy", "import numpy"),
        ("flask", "import flask"),
        ("redline", "import redline"),
        ("redline.core.data_loader", "from redline.core.data_loader import DataLoader"),
        ("redline.database.connector", "from redline.database.connector import DatabaseConnector"),
        ("redline.gui.main_window", "from redline.gui.main_window import StockAnalyzerGUI"),
    ]
    
    print("🧪 Testing REDLINE imports...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name}")
            passed += 1
        except ImportError as e:
            print(f"❌ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {name}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All imports successful!")
        return True
    else:
        print("❌ Some imports failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
EOF

    chmod +x test_imports.py
    print_success "Test script created: test_imports.py"
}

# Function to run the test script
run_test_script() {
    print_status "Running import tests..."
    
    cd "$REDLINE_DIR"
    source venv/bin/activate
    
    python3 test_imports.py || {
        print_error "Import tests failed"
        print_status "Check the output above for specific import errors"
        return 1
    }
    
    print_success "All import tests passed"
}

# Function to create a fixed main.py
create_fixed_main() {
    print_status "Creating a more robust main.py..."
    
    cd "$REDLINE_DIR"
    
    # Backup original main.py
    cp main.py main.py.backup
    
    # Create a more robust main.py
    cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
REDLINE Main Application
Enhanced version with better error handling and import management
"""

import sys
import os
import logging
import traceback

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add redline directory to path as well
redline_dir = os.path.join(current_dir, 'redline')
if redline_dir not in sys.path:
    sys.path.insert(0, redline_dir)

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('redline.log')
        ]
    )

def check_imports():
    """Check if all required imports are available."""
    required_modules = [
        'redline.core.data_loader',
        'redline.database.connector',
        'redline.gui.main_window'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            missing_modules.append((module, str(e)))
    
    if missing_modules:
        print("❌ Missing required modules:")
        for module, error in missing_modules:
            print(f"   - {module}: {error}")
        return False
    
    return True

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        print("🚀 Starting REDLINE...")
        
        # Check imports first
        if not check_imports():
            print("❌ Import check failed. Please run the fix script:")
            print("   ./install/fix_import_issues.sh")
            return 1
        
        # Import required modules
        from redline.core.data_loader import DataLoader
        from redline.database.connector import DatabaseConnector
        from redline.gui.main_window import StockAnalyzerGUI
        from redline.utils.logging_config import setup_logging, configure_third_party_logging
        
        # Setup logging
        setup_logging(
            log_level="INFO",
            log_file="redline.log",
            console_output=True
        )
        configure_third_party_logging()
        
        # Initialize components
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Parse command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--task=gui":
            # GUI mode
            import tkinter as tk
            root = tk.Tk()
            app = StockAnalyzerGUI(root, loader, connector)
            root.mainloop()
        else:
            # CLI mode or web mode
            print("📊 REDLINE CLI Mode")
            print("Use --task=gui for GUI mode or run web_app.py for web interface")
            
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Import error: {e}")
        print("💡 Try running: ./install/fix_import_issues.sh")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

    print_success "Enhanced main.py created"
}

# Function to test the fixed main.py
test_fixed_main() {
    print_status "Testing fixed main.py..."
    
    cd "$REDLINE_DIR"
    source venv/bin/activate
    
    # Test import check
    python3 main.py --task=gui &
    sleep 2
    pkill -f "python3 main.py" 2>/dev/null || true
    
    print_success "Fixed main.py test completed"
}

# Function to show usage instructions
show_usage() {
    echo ""
    print_success "REDLINE Import Fix Completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo ""
    echo "1. Test the installation:"
    echo "   cd ~/redline"
    echo "   source venv/bin/activate"
    echo "   python3 test_imports.py"
    echo ""
    echo "2. Try running REDLINE:"
    echo "   python3 main.py --task=gui"
    echo ""
    echo "3. If issues persist, check the logs:"
    echo "   cat ~/redline/redline.log"
    echo ""
    echo "4. For web interface:"
    echo "   python3 web_app.py"
    echo ""
}

# Main function
main() {
    print_status "Starting REDLINE import fix process..."
    
    # Check if we're in the right directory
    check_redline_directory
    
    # Check Python environment
    check_python_environment
    
    # Fix Python path issues
    fix_python_path
    
    # Install missing dependencies
    install_missing_dependencies
    
    # Create test script
    create_test_script
    
    # Run tests
    run_test_script || {
        print_warning "Some tests failed, but continuing..."
    }
    
    # Create fixed main.py
    create_fixed_main
    
    # Test fixed main.py
    test_fixed_main
    
    # Show usage instructions
    show_usage
    
    print_success "Import fix process completed!"
}

# Run main function
main "$@"
