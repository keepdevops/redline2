#!/bin/bash
# REDLINE Web GUI Startup Script
# Modern Ubuntu 24.04 LTS startup with systemd and supervisor

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

# Environment variables
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
export FLASK_APP="web_app.py"
export FLASK_ENV="${FLASK_ENV:-production}"
export FLASK_DEBUG="${FLASK_DEBUG:-false}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8080}"
export WEB_PORT="${WEB_PORT:-8080}"
export SECRET_KEY="${SECRET_KEY:-redline-secret-key-$(date +%s)}"

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

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Consider using a non-root user for security."
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    local dirs=(
        "${LOG_DIR}"
        "${PID_DIR}"
        "${DATA_DIR}"
        "${CONFIG_DIR}"
        "${DATA_DIR}/uploads"
        "${DATA_DIR}/downloads"
        "${DATA_DIR}/converted"
        "${LOG_DIR}/app"
        "${LOG_DIR}/nginx"
        "${LOG_DIR}/supervisor"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
    
    print_success "Directory structure created"
}

# Function to set proper permissions
set_permissions() {
    print_status "Setting proper permissions..."
    
    # Set ownership
    if [[ $EUID -eq 0 ]]; then
        chown -R redline:redline "${APP_DIR}" 2>/dev/null || true
        chown -R redline:redline "${LOG_DIR}" 2>/dev/null || true
        chown -R redline:redline "${PID_DIR}" 2>/dev/null || true
    fi
    
    # Set permissions
    chmod 755 "${APP_DIR}"
    chmod 755 "${LOG_DIR}"
    chmod 755 "${PID_DIR}"
    chmod 755 "${DATA_DIR}"
    chmod 755 "${CONFIG_DIR}"
    
    print_success "Permissions set"
}

# Function to check Python environment
check_python() {
    print_status "Checking Python environment..."
    
    # Check Python version (multi-platform)
    python3 --version
    
    # Check pip
    pip3 --version
    
    # Check virtual environment
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        print_status "Virtual environment: ${VIRTUAL_ENV}"
    else
        print_warning "No virtual environment detected"
    fi
    
    # Check required packages
    local required_packages=(
        "flask"
        "flask-socketio"
        "pandas"
        "numpy"
        "duckdb"
    )
    
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "✓ $package is available"
        else
            print_error "✗ $package is not available"
            exit 1
        fi
    done
    
    print_success "Python environment check passed"
}

# Function to check system resources
check_resources() {
    print_status "Checking system resources..."
    
    # Check memory
    local mem_total=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local mem_available=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    
    print_status "Total memory: ${mem_total}MB"
    print_status "Available memory: ${mem_available}MB"
    
    if [[ $mem_available -lt 512 ]]; then
        print_warning "Low memory available (${mem_available}MB). Consider increasing memory."
    fi
    
    # Check disk space
    local disk_usage=$(df -h "${APP_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
    print_status "Disk usage: ${disk_usage}%"
    
    if [[ $disk_usage -gt 90 ]]; then
        print_warning "High disk usage (${disk_usage}%). Consider cleaning up."
    fi
    
    # Check CPU
    local cpu_count=$(nproc)
    print_status "CPU cores: ${cpu_count}"
    
    print_success "Resource check completed"
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    local db_path="${DATA_DIR}/redline_data.duckdb"
    
    if [[ ! -f "$db_path" ]]; then
        print_status "Creating new database: $db_path"
        python3 -c "
import duckdb
conn = duckdb.connect('$db_path')
conn.execute('CREATE TABLE IF NOT EXISTS metadata (key VARCHAR, value VARCHAR)')
conn.execute('INSERT INTO metadata VALUES (?, ?)', ('created_at', '$(date -u +%Y-%m-%dT%H:%M:%SZ)'))
conn.execute('INSERT INTO metadata VALUES (?, ?)', ('version', '1.0.0'))
conn.close()
print('Database initialized successfully')
"
    else
        print_status "Database already exists: $db_path"
    fi
    
    print_success "Database initialization completed"
}

# Function to start nginx
start_nginx() {
    print_status "Starting Nginx..."
    
    # Test nginx configuration
    if nginx -t 2>/dev/null; then
        print_status "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
    
    # Start nginx
    if command -v systemctl >/dev/null 2>&1; then
        systemctl start nginx 2>/dev/null || true
    else
        nginx 2>/dev/null || true
    fi
    
    print_success "Nginx started"
}

# Function to start the Flask application
start_flask_app() {
    print_status "Starting ${APP_NAME}..."
    
    # Change to application directory
    cd "${APP_DIR}"
    
    # Start the Flask application
    print_status "Starting Flask application on ${HOST}:${PORT}"
    
    # Use gunicorn for production, flask for development
    if [[ "${FLASK_ENV}" == "production" ]]; then
        print_status "Starting with Gunicorn (production mode)"
        exec gunicorn \
            --bind "${HOST}:${PORT}" \
            --workers 4 \
            --worker-class gevent \
            --worker-connections 1000 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --timeout 30 \
            --keep-alive 2 \
            --access-logfile "${LOG_DIR}/app/access.log" \
            --error-logfile "${LOG_DIR}/app/error.log" \
            --log-level info \
            --capture-output \
            --enable-stdio-inheritance \
            web_app:app
    else
        print_status "Starting with Flask (development mode)"
        exec python3 web_app.py
    fi
}

# Function to setup signal handlers
setup_signals() {
    print_status "Setting up signal handlers..."
    
    # Function to handle shutdown
    shutdown_handler() {
        print_status "Received shutdown signal. Gracefully shutting down..."
        
        # Stop nginx
        if command -v systemctl >/dev/null 2>&1; then
            systemctl stop nginx 2>/dev/null || true
        else
            pkill nginx 2>/dev/null || true
        fi
        
        # Stop Flask app
        pkill -TERM -f "web_app.py" 2>/dev/null || true
        pkill -TERM -f "gunicorn" 2>/dev/null || true
        
        # Wait for processes to finish
        sleep 2
        
        # Force kill if still running
        pkill -KILL -f "web_app.py" 2>/dev/null || true
        pkill -KILL -f "gunicorn" 2>/dev/null || true
        
        print_success "Shutdown completed"
        exit 0
    }
    
    # Set up signal handlers
    trap shutdown_handler SIGTERM SIGINT SIGQUIT
    
    print_success "Signal handlers set up"
}

# Function to show startup information
show_startup_info() {
    print_success "${APP_NAME} startup completed!"
    print_status "Application directory: ${APP_DIR}"
    print_status "Log directory: ${LOG_DIR}"
    print_status "Data directory: ${DATA_DIR}"
    print_status "Configuration directory: ${CONFIG_DIR}"
    print_status "Host: ${HOST}"
    print_status "Port: ${PORT}"
    print_status "Environment: ${FLASK_ENV}"
    print_status "Debug mode: ${FLASK_DEBUG}"
    print_status "Python path: ${PYTHONPATH}"
    print_status "Process ID: $$"
    print_status "User: $(whoami)"
    print_status "Working directory: $(pwd)"
    print_status "Logs: tail -f ${LOG_DIR}/app/access.log"
    print_status "Health check: curl http://${HOST}:${PORT}/health"
}

# Main function
main() {
    print_status "Starting ${APP_NAME} initialization..."
    
    # Pre-startup checks and setup
    check_root
    create_directories
    set_permissions
    check_python
    check_resources
    init_database
    setup_signals
    
    # Start services
    start_nginx
    
    # Show startup information
    show_startup_info
    
    # Start the main application
    start_flask_app
}

# Run main function
main "$@"
