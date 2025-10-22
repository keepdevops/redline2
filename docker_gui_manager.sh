#!/bin/bash

# REDLINE Tkinter GUI Docker Manager Script
# Complete management script for Docker operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SCRIPT="$SCRIPT_DIR/build_docker_gui.sh"
RUN_SCRIPT="$SCRIPT_DIR/run_docker_gui.sh"
STOP_SCRIPT="$SCRIPT_DIR/stop_docker_gui.sh"

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}[MANAGER]${NC} $1"
}

# Function to check if scripts exist
check_scripts() {
    local scripts=("$BUILD_SCRIPT" "$RUN_SCRIPT" "$STOP_SCRIPT")
    
    for script in "${scripts[@]}"; do
        if [ ! -f "$script" ]; then
            print_error "Script not found: $script"
            exit 1
        fi
        if [ ! -x "$script" ]; then
            print_warning "Making script executable: $script"
            chmod +x "$script"
        fi
    done
    
    print_success "All scripts found and executable"
}

# Function to detect current platform
detect_platform() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        *)
            print_error "Unsupported architecture: $arch"
            exit 1
            ;;
    esac
}

# Function to build and run
build_and_run() {
    local platform=$1
    
    print_header "Build and Run for $platform"
    
    # Build the image
    print_status "Building image..."
    "$BUILD_SCRIPT" "build-$platform"
    
    # Run the container
    print_status "Running container..."
    "$RUN_SCRIPT" "run-$platform"
}

# Function to quick start
quick_start() {
    local platform=$(detect_platform)
    
    print_header "Quick Start for $platform"
    
    # Check if image exists
    if docker images "redline-gui:latest-$platform" --format "{{.Repository}}:{{.Tag}}" | grep -q "redline-gui:latest-$platform"; then
        print_status "Image exists, running directly..."
        "$RUN_SCRIPT" "run-$platform"
    else
        print_status "Image not found, building first..."
        build_and_run "$platform"
    fi
}

# Function to restart
restart() {
    print_header "Restarting REDLINE GUI"
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    "$STOP_SCRIPT" "stop-all"
    
    # Wait a moment
    sleep 2
    
    # Start again
    local platform=$(detect_platform)
    print_status "Starting GUI for $platform..."
    "$RUN_SCRIPT" "run-$platform"
}

# Function to show status
show_status() {
    print_header "REDLINE GUI Status"
    
    # Show Docker status
    "$STOP_SCRIPT" "status"
    
    # Show running processes
    print_status "Running processes:"
    ps aux | grep -E "(redline|docker)" | grep -v grep || print_warning "No REDLINE processes found"
}

# Function to show logs
show_logs() {
    print_header "REDLINE GUI Logs"
    "$RUN_SCRIPT" "logs"
}

# Function to test GUI
test_gui() {
    local platform=$(detect_platform)
    
    print_header "Testing GUI Components for $platform"
    "$BUILD_SCRIPT" "test-$platform"
}

# Function to clean up
cleanup() {
    print_header "Cleaning up REDLINE resources"
    "$STOP_SCRIPT" "cleanup"
}

# Function to show help
show_help() {
    echo "REDLINE Tkinter GUI Docker Manager"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build-amd64      Build for AMD64 architecture"
    echo "  build-arm64      Build for ARM64 architecture"
    echo "  build-multi      Build multi-platform image"
    echo "  run-amd64        Run GUI for AMD64 architecture"
    echo "  run-arm64        Run GUI for ARM64 architecture"
    echo "  run-auto         Run GUI for current platform"
    echo "  build-and-run    Build and run for current platform"
    echo "  quick-start      Quick start (build if needed, then run)"
    echo "  restart          Restart GUI (stop and start)"
    echo "  stop             Stop GUI containers"
    echo "  stop-all         Stop all REDLINE containers"
    echo "  status           Show current status"
    echo "  logs             Show container logs"
    echo "  test             Test GUI components"
    echo "  cleanup          Clean up all resources"
    echo "  help             Show this help message"
    echo ""
    echo "Options:"
    echo "  --verbose        Verbose output"
    echo "  --force          Force operations"
    echo ""
    echo "Examples:"
    echo "  $0 quick-start"
    echo "  $0 build-and-run"
    echo "  $0 restart"
    echo "  $0 status"
    echo ""
}

# Function to show menu
show_menu() {
    echo "REDLINE Tkinter GUI Docker Manager"
    echo "=================================="
    echo ""
    echo "Select an option:"
    echo "1) Quick Start (recommended)"
    echo "2) Build and Run"
    echo "3) Run GUI"
    echo "4) Stop GUI"
    echo "5) Show Status"
    echo "6) Show Logs"
    echo "7) Test GUI"
    echo "8) Cleanup"
    echo "9) Help"
    echo "0) Exit"
    echo ""
    read -p "Enter your choice [0-9]: " choice
    
    case $choice in
        1)
            quick_start
            ;;
        2)
            local platform=$(detect_platform)
            build_and_run "$platform"
            ;;
        3)
            local platform=$(detect_platform)
            "$RUN_SCRIPT" "run-$platform"
            ;;
        4)
            "$STOP_SCRIPT" "stop"
            ;;
        5)
            show_status
            ;;
        6)
            show_logs
            ;;
        7)
            test_gui
            ;;
        8)
            cleanup
            ;;
        9)
            show_help
            ;;
        0)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            show_menu
            ;;
    esac
}

# Main script logic
main() {
    # Check if scripts exist
    check_scripts
    
    # Parse arguments
    local verbose=""
    local force=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                verbose="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    case "${1:-menu}" in
        build-amd64)
            "$BUILD_SCRIPT" "build-amd64"
            ;;
        build-arm64)
            "$BUILD_SCRIPT" "build-arm64"
            ;;
        build-multi)
            "$BUILD_SCRIPT" "build-multi"
            ;;
        run-amd64)
            "$RUN_SCRIPT" "run-amd64"
            ;;
        run-arm64)
            "$RUN_SCRIPT" "run-arm64"
            ;;
        run-auto)
            "$RUN_SCRIPT" "run-auto"
            ;;
        build-and-run)
            local platform=$(detect_platform)
            build_and_run "$platform"
            ;;
        quick-start)
            quick_start
            ;;
        restart)
            restart
            ;;
        stop)
            "$STOP_SCRIPT" "stop"
            ;;
        stop-all)
            "$STOP_SCRIPT" "stop-all"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        test)
            test_gui
            ;;
        cleanup)
            cleanup
            ;;
        menu)
            show_menu
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
