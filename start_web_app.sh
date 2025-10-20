#!/bin/bash

# REDLINE Flask Web Application Startup Script
# This script handles the complete startup process for the REDLINE web application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_PORT=8082
DEFAULT_HOST="0.0.0.0"
DEFAULT_DEBUG="false"

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
    echo -e "${BLUE}  REDLINE Flask Web Application Startup${NC}"
    echo -e "${BLUE}==============================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        print_warning "Killing existing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to check Python dependencies
check_dependencies() {
    print_status "Checking Python dependencies..."
    
    # Check if Python 3 is available
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if pip is available
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "pip is not installed or not in PATH"
        exit 1
    fi
    
    # Check for required Python packages
    local required_packages=("flask" "flask-socketio" "flask-compress")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -ne 0 ]; then
        print_warning "Missing Python packages: ${missing_packages[*]}"
        print_status "Installing missing packages..."
        
        # Install missing packages
        if command_exists pip3; then
            pip3 install "${missing_packages[@]}"
        else
            pip install "${missing_packages[@]}"
        fi
        
        print_status "Dependencies installed successfully"
    else
        print_status "All Python dependencies are available"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    local directories=(
        "data"
        "data/uploads"
        "data/converted"
        "logs"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to set environment variables
set_environment() {
    local port=${1:-$DEFAULT_PORT}
    local host=${2:-$DEFAULT_HOST}
    local debug=${3:-$DEFAULT_DEBUG}
    
    export WEB_PORT=$port
    export HOST=$host
    export DEBUG=$debug
    export FLASK_APP=web_app.py
    export FLASK_ENV=${debug,,}
    
    print_status "Environment variables set:"
    print_status "  WEB_PORT=$port"
    print_status "  HOST=$host"
    print_status "  DEBUG=$debug"
    print_status "  FLASK_APP=web_app.py"
}

# Function to start the Flask application
start_flask_app() {
    local port=$1
    local host=$2
    local debug=$3
    
    print_status "Starting Flask application..."
    print_status "Access the application at: http://$host:$port"
    
    # Start the Flask app
    if [ "$debug" = "true" ]; then
        print_status "Starting in DEBUG mode..."
        python3 web_app.py
    else
        print_status "Starting in PRODUCTION mode..."
        python3 web_app.py
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT      Set the port number (default: $DEFAULT_PORT)"
    echo "  -h, --host HOST      Set the host address (default: $DEFAULT_HOST)"
    echo "  -d, --debug          Enable debug mode"
    echo "  -k, --kill           Kill any existing process on the specified port"
    echo "  --check-deps         Only check dependencies and exit"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Start with default settings"
    echo "  $0 -p 8080                   # Start on port 8080"
    echo "  $0 -p 8080 -d                # Start on port 8080 in debug mode"
    echo "  $0 -k -p 8082                # Kill existing process and start on port 8082"
    echo "  $0 --check-deps              # Check dependencies only"
}

# Function to check application health
check_health() {
    local port=$1
    local host=$2
    
    print_status "Checking application health..."
    
    # Wait for the application to start
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$host:$port/health" >/dev/null 2>&1; then
            print_status "Application is healthy and running!"
            return 0
        fi
        
        print_status "Waiting for application to start... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Application failed to start or is not responding"
    return 1
}

# Main function
main() {
    local port=$DEFAULT_PORT
    local host=$DEFAULT_HOST
    local debug=$DEFAULT_DEBUG
    local kill_existing=false
    local check_deps_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                port="$2"
                shift 2
                ;;
            -h|--host)
                host="$2"
                shift 2
                ;;
            -d|--debug)
                debug="true"
                shift
                ;;
            -k|--kill)
                kill_existing=true
                shift
                ;;
            --check-deps)
                check_deps_only=true
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
    
    # Check if web_app.py exists
    if [ ! -f "web_app.py" ]; then
        print_error "web_app.py not found in current directory"
        print_error "Please run this script from the REDLINE project root directory"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    if [ "$check_deps_only" = true ]; then
        print_status "Dependency check completed successfully"
        exit 0
    fi
    
    # Kill existing process if requested
    if [ "$kill_existing" = true ]; then
        kill_port $port
    fi
    
    # Check if port is already in use
    if check_port $port; then
        print_warning "Port $port is already in use"
        if [ "$kill_existing" = false ]; then
            print_error "Use -k/--kill flag to kill existing process, or choose a different port"
            exit 1
        fi
    fi
    
    # Create necessary directories
    create_directories
    
    # Set environment variables
    set_environment $port $host $debug
    
    # Start the Flask application
    print_status "Starting REDLINE Flask Web Application..."
    print_status "Press Ctrl+C to stop the application"
    echo ""
    
    # Start the app in the background and check health
    start_flask_app $port $host $debug &
    local flask_pid=$!
    
    # Give the app a moment to start
    sleep 3
    
    # Check if the process is still running
    if ! kill -0 $flask_pid 2>/dev/null; then
        print_error "Flask application failed to start"
        exit 1
    fi
    
    # Check application health
    if check_health $port $host; then
        echo ""
        print_status "🎉 REDLINE Flask Web Application is running successfully!"
        print_status "📱 Access your application at: http://$host:$port"
        print_status "🎨 Look for the floating palette button (🎨) to customize font colors!"
        print_status "📊 All features are available: Data Analysis, Downloads, Conversion, and more!"
        echo ""
        print_status "Press Ctrl+C to stop the application"
        
        # Wait for the Flask process
        wait $flask_pid
    else
        print_error "Application health check failed"
        kill $flask_pid 2>/dev/null || true
        exit 1
    fi
}

# Trap Ctrl+C to clean up
trap 'echo ""; print_status "Shutting down REDLINE Flask Web Application..."; exit 0' INT

# Run main function with all arguments
main "$@"
