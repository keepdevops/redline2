#!/bin/bash

# REDLINE Docker Entrypoint Script
# Supports multiple deployment modes: x11, vnc, headless, web

set -e

# Default values
MODE=${MODE:-auto}
VNC_PORT=${VNC_PORT:-5900}
WEB_PORT=${WEB_PORT:-8080}
DISPLAY=${DISPLAY:-:99}
VNC_PASSWORD=${VNC_PASSWORD:-redline123}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Function to detect available mode
detect_mode() {
    log "Detecting available display mode..."
    
    # Check if DISPLAY is set and accessible
    if [ -n "$DISPLAY" ] && xset q >/dev/null 2>&1; then
        log_success "X11 display detected: $DISPLAY"
        echo "x11"
        return
    fi
    
    # Check if we're in a container without X11
    if [ -f /.dockerenv ] || [ -n "$CONTAINER" ]; then
        log "Container environment detected, using VNC mode"
        echo "vnc"
        return
    fi
    
    # Default to headless
    log "No display detected, using headless mode"
    echo "headless"
}

# Function to setup X11 forwarding mode
setup_x11() {
    log "Setting up X11 forwarding mode..."
    
    # Check if DISPLAY is set
    if [ -z "$DISPLAY" ]; then
        log_error "DISPLAY environment variable not set"
        return 1
    fi
    
    # Check if X server is accessible
    if ! xset q >/dev/null 2>&1; then
        log_error "Cannot connect to X server at $DISPLAY"
        log "Make sure X11 forwarding is enabled and DISPLAY is set correctly"
        return 1
    fi
    
    log_success "X11 forwarding setup complete"
    return 0
}

# Function to setup VNC mode
setup_vnc() {
    log "Setting up VNC server mode..."
    
    # Set display for virtual framebuffer
    export DISPLAY=:99
    
    # Start Xvfb (virtual framebuffer)
    log "Starting virtual framebuffer (Xvfb)..."
    Xvfb $DISPLAY -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    XVFB_PID=$!
    
    # Wait for Xvfb to start
    sleep 2
    
    # Start window manager
    log "Starting window manager (fluxbox)..."
    fluxbox &
    WM_PID=$!
    
    # Start VNC server
    log "Starting VNC server on port $VNC_PORT..."
    x11vnc -display $DISPLAY -rfbport $VNC_PORT -forever -usepw -quiet &
    VNC_PID=$!
    
    # Wait for VNC to start
    sleep 2
    
    log_success "VNC server setup complete"
    log "Connect to: localhost:$VNC_PORT"
    log "Password: $VNC_PASSWORD"
    
    # Store PIDs for cleanup
    echo $XVFB_PID > /tmp/xvfb.pid
    echo $WM_PID > /tmp/wm.pid
    echo $VNC_PID > /tmp/vnc.pid
}

# Function to setup headless mode
setup_headless() {
    log "Setting up headless mode..."
    
    # Set display for virtual framebuffer
    export DISPLAY=:99
    
    # Start Xvfb for GUI applications that need a display
    log "Starting virtual framebuffer (Xvfb)..."
    Xvfb $DISPLAY -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    XVFB_PID=$!
    
    # Wait for Xvfb to start
    sleep 2
    
    log_success "Headless mode setup complete"
    
    # Store PID for cleanup
    echo $XVFB_PID > /tmp/xvfb.pid
}

# Function to setup web mode
setup_web() {
    log "Setting up web interface mode..."
    
    # Start web server
    log "Starting web server on port $WEB_PORT..."
    python3 -m flask run --host=0.0.0.0 --port=$WEB_PORT &
    WEB_PID=$!
    
    log_success "Web interface setup complete"
    log "Access at: http://localhost:$WEB_PORT"
    
    # Store PID for cleanup
    echo $WEB_PID > /tmp/web.pid
}

# Function to cleanup processes
cleanup() {
    log "Cleaning up processes..."
    
    # Kill Xvfb if running
    if [ -f /tmp/xvfb.pid ]; then
        kill $(cat /tmp/xvfb.pid) 2>/dev/null || true
        rm -f /tmp/xvfb.pid
    fi
    
    # Kill window manager if running
    if [ -f /tmp/wm.pid ]; then
        kill $(cat /tmp/wm.pid) 2>/dev/null || true
        rm -f /tmp/wm.pid
    fi
    
    # Kill VNC server if running
    if [ -f /tmp/vnc.pid ]; then
        kill $(cat /tmp/vnc.pid) 2>/dev/null || true
        rm -f /tmp/vnc.pid
    fi
    
    # Kill web server if running
    if [ -f /tmp/web.pid ]; then
        kill $(cat /tmp/web.pid) 2>/dev/null || true
        rm -f /tmp/web.pid
    fi
    
    log_success "Cleanup complete"
}

# Function to start REDLINE application
start_redline() {
    log "Starting REDLINE application..."
    
    # Check if GUI mode is requested
    if [ "$1" = "--task=gui" ] || [ "$1" = "gui" ]; then
        log "Starting REDLINE GUI..."
        python3 main.py --task=gui
    else
        log "Starting REDLINE CLI..."
        python3 main.py "$@"
    fi
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    log "REDLINE Docker Container Starting..."
    log "Mode: $MODE"
    log "User: $(whoami)"
    log "Working Directory: $(pwd)"
    
    # Parse command line arguments
    ARGS=()
    GUI_MODE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode=*)
                MODE="${1#*=}"
                shift
                ;;
            --task=gui|gui)
                GUI_MODE=true
                ARGS+=("$1")
                shift
                ;;
            *)
                ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    # Auto-detect mode if not specified
    if [ "$MODE" = "auto" ]; then
        MODE=$(detect_mode)
    fi
    
    log "Using mode: $MODE"
    
    # Setup based on mode
    case $MODE in
        x11)
            if setup_x11; then
                log_success "X11 mode ready"
            else
                log_warning "X11 setup failed, falling back to VNC mode"
                MODE="vnc"
                setup_vnc
            fi
            ;;
        vnc)
            setup_vnc
            ;;
        headless)
            setup_headless
            ;;
        web)
            setup_web
            ;;
        *)
            log_error "Unknown mode: $MODE"
            log "Available modes: x11, vnc, headless, web, auto"
            exit 1
            ;;
    esac
    
    # Start REDLINE application
    if [ "$GUI_MODE" = true ] || [ "$MODE" != "web" ]; then
        start_redline "${ARGS[@]}"
    else
        log "Web mode: Starting web interface..."
        # Start web application
        python3 web_app.py
    fi
}

# Run main function
main "$@"
