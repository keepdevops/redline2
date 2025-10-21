#!/bin/bash

# REDLINE Web GUI Master Startup Script
# Builds and starts the REDLINE Web GUI in one command

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

# Default values
BUILD_CLEAN="false"
RUN_MODE="detached"
WEB_PORT="8080"
SKIP_BUILD="false"

# Show banner
show_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    REDLINE Web GUI                          ║"
    echo "║                Master Startup Script                         ║"
    echo "║                                                              ║"
    echo "║  This script will build and start the REDLINE Web GUI       ║"
    echo "║  Access at: http://localhost:$WEB_PORT                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
    
    # Check if scripts exist
    if [ ! -f "./build/build_web_gui.sh" ]; then
        log_error "Build script not found: ./build/build_web_gui.sh"
        exit 1
    fi
    
    if [ ! -f "./build/run_web_gui.sh" ]; then
        log_error "Run script not found: ./build/run_web_gui.sh"
        exit 1
    fi
    
    log_success "All scripts found"
}

# Build the application
build_app() {
    if [ "$SKIP_BUILD" = "false" ]; then
        log "Building REDLINE Web GUI..."
        
        if [ "$BUILD_CLEAN" = "true" ]; then
            ./build/build_web_gui.sh --clean
        else
            ./build/build_web_gui.sh
        fi
        
        log_success "Build completed"
    else
        log_warning "Skipping build (--skip-build specified)"
    fi
}

# Run the application
run_app() {
    log "Starting REDLINE Web GUI..."
    
    if [ "$RUN_MODE" = "foreground" ]; then
        ./build/run_web_gui.sh --foreground --port "$WEB_PORT"
    else
        ./build/run_web_gui.sh --detached --port "$WEB_PORT"
    fi
    
    log_success "Application started"
}

# Show final information
show_final_info() {
    log_success "REDLINE Web GUI is ready!"
    echo ""
    echo "Application Information:"
    echo "======================="
    echo "Status: Running"
    echo "URL: http://localhost:$WEB_PORT"
    echo "Mode: $RUN_MODE"
    echo ""
    echo "Management Commands:"
    echo "==================="
    echo "View logs:    docker logs redline-web-gui"
    echo "Stop:         ./build/shutdown_web_gui.sh"
    echo "Restart:      docker restart redline-web-gui"
    echo "Shell access: docker exec -it redline-web-gui /bin/bash"
    echo ""
    echo "To access from another machine:"
    echo "  Replace 'localhost' with this machine's IP address"
    echo ""
    echo "Firefox: Open http://localhost:$WEB_PORT"
    echo "Chrome:  Open http://localhost:$WEB_PORT"
    echo "Edge:    Open http://localhost:$WEB_PORT"
}

# Main function
main() {
    show_banner
    check_prerequisites
    build_app
    run_app
    show_final_info
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            BUILD_CLEAN="true"
            shift
            ;;
        --skip-build)
            SKIP_BUILD="true"
            shift
            ;;
        --foreground|-f)
            RUN_MODE="foreground"
            shift
            ;;
        --detached|-d)
            RUN_MODE="detached"
            shift
            ;;
        --port)
            WEB_PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --clean             Clean build (remove old images)"
            echo "  --skip-build        Skip building, just run existing image"
            echo "  --foreground, -f    Run in foreground (see logs)"
            echo "  --detached, -d      Run in background (default)"
            echo "  --port PORT         Web port (default: 8080)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Build and run with defaults"
            echo "  $0 --clean                            # Clean build and run"
            echo "  $0 --foreground                       # Run in foreground"
            echo "  $0 --port 8081                        # Use port 8081"
            echo "  $0 --skip-build                       # Just run, don't build"
            echo ""
            echo "This script will:"
            echo "  1. Check prerequisites (Docker, scripts)"
            echo "  2. Build the Docker image (unless --skip-build)"
            echo "  3. Start the web application"
            echo "  4. Show access information"
            echo ""
            echo "Prerequisites:"
            echo "  - Docker must be running"
            echo "  - Scripts must be in ./build/ directory"
            echo "  - Dockerfile must be in current directory"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
