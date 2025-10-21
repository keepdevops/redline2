#!/bin/bash
# REDLINE Web GUI Shutdown Script
# Graceful shutdown with cleanup and logging

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="REDLINE Web GUI"
APP_DIR="/opt/redline"
LOG_DIR="/var/log/redline"
PID_DIR="/var/run/redline"
DATA_DIR="/opt/redline/data"
CONFIG_DIR="/opt/redline/config"
SHUTDOWN_TIMEOUT=30
FORCE_SHUTDOWN_TIMEOUT=60

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Function to log shutdown event
log_shutdown() {
    local reason="${1:-Manual shutdown}"
    local log_file="${LOG_DIR}/app/shutdown.log"
    
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) - Shutdown initiated: $reason" >> "$log_file"
    print_status "Shutdown logged: $reason"
}

# Function to check if process is running
is_process_running() {
    local process_name="$1"
    pgrep -f "$process_name" >/dev/null 2>&1
}

# Function to get process PID
get_process_pid() {
    local process_name="$1"
    pgrep -f "$process_name" 2>/dev/null || echo ""
}

# Function to gracefully stop process
graceful_stop() {
    local process_name="$1"
    local timeout="${2:-$SHUTDOWN_TIMEOUT}"
    
    if ! is_process_running "$process_name"; then
        print_status "$process_name is not running"
        return 0
    fi
    
    local pid=$(get_process_pid "$process_name")
    print_status "Stopping $process_name (PID: $pid)..."
    
    # Send TERM signal
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while is_process_running "$process_name" && [[ $count -lt $timeout ]]; do
        sleep 1
        ((count++))
        if [[ $((count % 5)) -eq 0 ]]; then
            print_status "Waiting for $process_name to stop... (${count}s)"
        fi
    done
    
    if is_process_running "$process_name"; then
        print_warning "$process_name did not stop gracefully within ${timeout}s"
        return 1
    else
        print_success "$process_name stopped gracefully"
        return 0
    fi
}

# Function to force stop process
force_stop() {
    local process_name="$1"
    
    if ! is_process_running "$process_name"; then
        return 0
    fi
    
    local pid=$(get_process_pid "$process_name")
    print_warning "Force stopping $process_name (PID: $pid)..."
    
    # Send KILL signal
    kill -KILL "$pid" 2>/dev/null || true
    
    # Wait a moment
    sleep 2
    
    if is_process_running "$process_name"; then
        print_error "Failed to force stop $process_name"
        return 1
    else
        print_success "$process_name force stopped"
        return 0
    fi
}

# Function to stop Flask application
stop_flask_app() {
    print_status "Stopping Flask application..."
    
    local processes=("web_app.py" "gunicorn" "flask")
    
    for process in "${processes[@]}"; do
        if is_process_running "$process"; then
            if ! graceful_stop "$process" "$SHUTDOWN_TIMEOUT"; then
                force_stop "$process"
            fi
        fi
    done
    
    print_success "Flask application stopped"
}

# Function to stop Nginx
stop_nginx() {
    print_status "Stopping Nginx..."
    
    if command -v systemctl >/dev/null 2>&1; then
        # Use systemctl if available
        if systemctl is-active nginx >/dev/null 2>&1; then
            systemctl stop nginx
            print_success "Nginx stopped via systemctl"
        else
            print_status "Nginx is not running (systemctl)"
        fi
    else
        # Fallback to direct process management
        if is_process_running "nginx"; then
            if ! graceful_stop "nginx" "$SHUTDOWN_TIMEOUT"; then
                force_stop "nginx"
            fi
        else
            print_status "Nginx is not running"
        fi
    fi
}

# Function to stop supervisor
stop_supervisor() {
    print_status "Stopping Supervisor..."
    
    if is_process_running "supervisord"; then
        if ! graceful_stop "supervisord" "$SHUTDOWN_TIMEOUT"; then
            force_stop "supervisord"
        fi
    else
        print_status "Supervisor is not running"
    fi
    
    print_success "Supervisor stopped"
}

# Function to cleanup temporary files
cleanup_temp_files() {
    print_status "Cleaning up temporary files..."
    
    local temp_dirs=(
        "/tmp/redline*"
        "${APP_DIR}/temp"
        "${APP_DIR}/__pycache__"
        "${APP_DIR}/**/__pycache__"
    )
    
    for pattern in "${temp_dirs[@]}"; do
        if ls $pattern >/dev/null 2>&1; then
            rm -rf $pattern
            print_status "Cleaned: $pattern"
        fi
    done
    
    print_success "Temporary files cleaned"
}

# Function to cleanup log files
cleanup_logs() {
    print_status "Cleaning up log files..."
    
    local log_files=(
        "${LOG_DIR}/app/*.log"
        "${LOG_DIR}/nginx/*.log"
        "${LOG_DIR}/supervisor/*.log"
    )
    
    # Keep only last 7 days of logs
    find "${LOG_DIR}" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Compress old logs
    find "${LOG_DIR}" -name "*.log" -type f -mtime +1 -exec gzip {} \; 2>/dev/null || true
    
    print_success "Log files cleaned"
}

# Function to save application state
save_state() {
    print_status "Saving application state..."
    
    local state_file="${CONFIG_DIR}/shutdown_state.json"
    
    cat > "$state_file" << EOF
{
    "shutdown_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "uptime": "$(uptime -p 2>/dev/null || echo 'unknown')",
    "memory_usage": "$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}' 2>/dev/null || echo 'unknown')",
    "disk_usage": "$(df -h "${APP_DIR}" | awk 'NR==2 {print $5}' 2>/dev/null || echo 'unknown')",
    "process_count": "$(ps aux | wc -l 2>/dev/null || echo 'unknown')"
}
EOF
    
    print_success "Application state saved to $state_file"
}

# Function to check for running processes
check_running_processes() {
    print_status "Checking for remaining processes..."
    
    local processes=("web_app.py" "gunicorn" "flask" "nginx" "supervisord")
    local running_processes=()
    
    for process in "${processes[@]}"; do
        if is_process_running "$process"; then
            running_processes+=("$process")
        fi
    done
    
    if [[ ${#running_processes[@]} -gt 0 ]]; then
        print_warning "The following processes are still running:"
        for process in "${running_processes[@]}"; do
            local pid=$(get_process_pid "$process")
            print_warning "  - $process (PID: $pid)"
        done
        return 1
    else
        print_success "All processes stopped successfully"
        return 0
    fi
}

# Function to show shutdown summary
show_shutdown_summary() {
    print_success "${APP_NAME} shutdown completed!"
    print_status "Shutdown time: $(date)"
    print_status "Total shutdown duration: ${SECONDS}s"
    print_status "Application directory: ${APP_DIR}"
    print_status "Log directory: ${LOG_DIR}"
    print_status "Data directory: ${DATA_DIR}"
    print_status "Configuration directory: ${CONFIG_DIR}"
    
    # Show final process check
    if check_running_processes; then
        print_success "All processes stopped cleanly"
    else
        print_warning "Some processes may still be running"
    fi
}

# Function to handle emergency shutdown
emergency_shutdown() {
    print_error "Emergency shutdown initiated!"
    
    # Force stop all processes
    pkill -KILL -f "web_app.py" 2>/dev/null || true
    pkill -KILL -f "gunicorn" 2>/dev/null || true
    pkill -KILL -f "flask" 2>/dev/null || true
    pkill -KILL -f "nginx" 2>/dev/null || true
    pkill -KILL -f "supervisord" 2>/dev/null || true
    
    # Stop systemd services
    if command -v systemctl >/dev/null 2>&1; then
        systemctl stop nginx 2>/dev/null || true
        systemctl stop redline 2>/dev/null || true
    fi
    
    print_warning "Emergency shutdown completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -f, --force         Force shutdown without graceful stop"
    echo "  -e, --emergency     Emergency shutdown (kill all processes)"
    echo "  -c, --cleanup       Clean up temporary files and logs"
    echo "  -s, --save-state    Save application state before shutdown"
    echo "  -t, --timeout SEC   Set graceful shutdown timeout (default: 30)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Normal graceful shutdown"
    echo "  $0 -f               # Force shutdown"
    echo "  $0 -e               # Emergency shutdown"
    echo "  $0 -c -s            # Shutdown with cleanup and state save"
}

# Main function
main() {
    local force_shutdown=false
    local emergency_shutdown_flag=false
    local cleanup_files=false
    local save_state_flag=false
    local timeout="$SHUTDOWN_TIMEOUT"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -f|--force)
                force_shutdown=true
                shift
                ;;
            -e|--emergency)
                emergency_shutdown_flag=true
                shift
                ;;
            -c|--cleanup)
                cleanup_files=true
                shift
                ;;
            -s|--save-state)
                save_state_flag=true
                shift
                ;;
            -t|--timeout)
                timeout="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Record start time
    SECONDS=0
    
    print_status "Starting ${APP_NAME} shutdown process..."
    
    # Log shutdown reason
    if [[ "$emergency_shutdown_flag" == true ]]; then
        log_shutdown "Emergency shutdown"
    elif [[ "$force_shutdown" == true ]]; then
        log_shutdown "Force shutdown"
    else
        log_shutdown "Graceful shutdown"
    fi
    
    # Handle emergency shutdown
    if [[ "$emergency_shutdown_flag" == true ]]; then
        emergency_shutdown
        exit 0
    fi
    
    # Save state if requested
    if [[ "$save_state_flag" == true ]]; then
        save_state
    fi
    
    # Stop services
    if [[ "$force_shutdown" == true ]]; then
        print_warning "Force shutdown mode - skipping graceful stops"
        stop_flask_app
        stop_nginx
        stop_supervisor
    else
        stop_flask_app
        stop_nginx
        stop_supervisor
    fi
    
    # Cleanup if requested
    if [[ "$cleanup_files" == true ]]; then
        cleanup_temp_files
        cleanup_logs
    fi
    
    # Show summary
    show_shutdown_summary
    
    print_success "Shutdown process completed successfully"
}

# Run main function
main "$@"
