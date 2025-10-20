#!/bin/bash

# REDLINE Flask Web Application - Complete Installation and Startup Script
# This script installs all dependencies and starts the web application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE}  REDLINE Flask Web Application Setup${NC}"
    echo -e "${BLUE}==============================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Core Flask dependencies
    local flask_packages=(
        "flask>=2.3.0"
        "flask-socketio>=5.3.0"
        "flask-compress>=1.13"
        "gunicorn>=21.0.0"
    )
    
    # Data processing dependencies
    local data_packages=(
        "pandas>=1.5.0"
        "numpy>=1.21.0"
        "duckdb>=0.8.0"
        "pyarrow>=10.0.0"
        "openpyxl>=3.0.0"
        "xlrd>=2.0.0"
    )
    
    # Background task processing
    local task_packages=(
        "celery>=5.3.0"
        "redis>=4.5.0"
    )
    
    # Financial data dependencies
    local financial_packages=(
        "yfinance>=0.2.0"
        "requests>=2.28.0"
        "beautifulsoup4>=4.11.0"
        "lxml>=4.9.0"
    )
    
    # Additional utilities
    local utility_packages=(
        "python-dateutil>=2.8.0"
        "pytz>=2022.1"
        "tqdm>=4.64.0"
    )
    
    # Combine all packages
    local all_packages=(
        "${flask_packages[@]}"
        "${data_packages[@]}"
        "${task_packages[@]}"
        "${financial_packages[@]}"
        "${utility_packages[@]}"
    )
    
    # Install packages
    for package in "${all_packages[@]}"; do
        print_status "Installing $package..."
        pip3 install "$package" --quiet
    done
    
    print_status "All dependencies installed successfully!"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    local directories=(
        "data"
        "data/uploads"
        "data/converted"
        "data/converted/csv"
        "data/converted/parquet"
        "data/converted/feather"
        "data/converted/json"
        "data/converted/duckdb"
        "logs"
        "redline/web/static/css"
        "redline/web/static/js"
        "redline/web/templates"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to check if web_app.py exists
check_web_app() {
    if [ ! -f "web_app.py" ]; then
        print_error "web_app.py not found in current directory"
        print_error "Please run this script from the REDLINE project root directory"
        exit 1
    fi
    print_status "web_app.py found"
}

# Function to start the Flask application
start_flask_app() {
    local port=${1:-8082}
    
    print_status "Starting Flask application on port $port..."
    
    # Set environment variables
    export WEB_PORT=$port
    export HOST="0.0.0.0"
    export DEBUG="false"
    export FLASK_APP="web_app.py"
    
    # Kill existing process on port if any
    if lsof -ti :$port >/dev/null 2>&1; then
        print_warning "Killing existing process on port $port..."
        kill -9 $(lsof -ti :$port) 2>/dev/null || true
        sleep 2
    fi
    
    print_status "🚀 REDLINE Flask Web Application is starting..."
    print_status "📱 Access your application at: http://localhost:$port"
    print_status "🎨 Look for the floating palette button (🎨) to customize font colors!"
    print_status "📊 Features available: Data Analysis, Downloads, Conversion, and more!"
    echo ""
    print_status "Press Ctrl+C to stop the application"
    echo ""
    
    # Start the Flask application
    python3 web_app.py
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT      Set the port number (default: 8082)"
    echo "  --install-only       Only install dependencies, don't start the app"
    echo "  --skip-install       Skip dependency installation"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Install dependencies and start on port 8082"
    echo "  $0 -p 8080                   # Install dependencies and start on port 8080"
    echo "  $0 --install-only            # Only install dependencies"
    echo "  $0 --skip-install -p 8080    # Start on port 8080 without installing dependencies"
}

# Main function
main() {
    local port=8082
    local install_only=false
    local skip_install=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                port="$2"
                shift 2
                ;;
            --install-only)
                install_only=true
                shift
                ;;
            --skip-install)
                skip_install=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate port number
    if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        print_error "Invalid port number: $port"
        exit 1
    fi
    
    print_header
    
    # Check if Python 3 is available
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH"
        print_error "Please install Python 3 and try again"
        exit 1
    fi
    
    # Check if pip3 is available
    if ! command_exists pip3; then
        print_error "pip3 is not installed or not in PATH"
        print_error "Please install pip3 and try again"
        exit 1
    fi
    
    # Check if web_app.py exists
    check_web_app
    
    # Install dependencies unless skipped
    if [ "$skip_install" = false ]; then
        install_dependencies
    else
        print_status "Skipping dependency installation"
    fi
    
    # Create directories
    create_directories
    
    # Start the application unless install-only is specified
    if [ "$install_only" = false ]; then
        start_flask_app $port
    else
        print_status "Installation completed successfully!"
        print_status "Run '$0 --skip-install' to start the application"
    fi
}

# Trap Ctrl+C to clean up
trap 'echo ""; print_status "Shutting down..."; exit 0' INT

# Run main function with all arguments
main "$@"
