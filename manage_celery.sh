#!/bin/bash
# REDLINE Celery Management Script
# Comprehensive script for managing Celery workers, Redis, and background tasks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
# Celery app is defined in redline.background.tasks
CELERY_APP="redline.background.tasks"
CELERY_WORKER_NAME="redline-worker"
CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-2}
CELERY_LOGLEVEL=${CELERY_LOGLEVEL:-info}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-${REDIS_URL:-"redis://localhost:6379/0"}}
CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-${REDIS_URL:-"redis://localhost:6379/0"}}
CELERY_QUEUE=${CELERY_QUEUE:-"redline_tasks"}
LOG_DIR="${LOG_DIR:-./logs}"
PID_FILE="${LOG_DIR}/celery_worker.pid"
LOG_FILE="${LOG_DIR}/celery_worker.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Helper functions
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

# Check if Celery is installed
check_celery() {
    if ! python3 -c "import celery" 2>/dev/null; then
        print_error "Celery is not installed"
        print_status "Install with: pip install celery redis"
        return 1
    fi
    return 0
}

# Check if Redis is available
check_redis() {
    print_status "Checking Redis connection at $CELERY_BROKER_URL..."
    
    # Try to connect to Redis
    if python3 -c "
import redis
try:
    r = redis.from_url('$CELERY_BROKER_URL')
    r.ping()
    print('OK')
except Exception as e:
    print('FAILED:', str(e))
    exit(1)
" 2>/dev/null | grep -q "OK"; then
        print_success "Redis connection successful"
        return 0
    else
        print_warning "Redis is not available at $CELERY_BROKER_URL"
        print_warning "Start Redis with: docker-compose --profile full up -d redis"
        print_warning "Or manually: docker run -d --name redline-redis -p 6379:6379 redis:7-alpine"
        return 1
    fi
}

# Start Redis container
start_redis() {
    print_status "Starting Redis container..."
    
    # Check if Redis container exists
    if docker ps -a --format "{{.Names}}" | grep -q "^redline-redis$"; then
        if docker ps --format "{{.Names}}" | grep -q "^redline-redis$"; then
            print_warning "Redis container already running"
            return 0
        else
            print_status "Starting existing Redis container..."
            docker start redline-redis
        fi
    else
        print_status "Creating new Redis container..."
        docker run -d \
            --name redline-redis \
            -p 6379:6379 \
            -v redline-redis-data:/data \
            --restart unless-stopped \
            redis:7-alpine \
            redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    fi
    
    sleep 2
    
    if check_redis; then
        print_success "Redis container started"
        return 0
    else
        print_error "Failed to start Redis container"
        return 1
    fi
}

# Start Celery worker
start_worker() {
    print_status "Starting Celery worker for REDLINE..."
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Celery worker already running (PID: $PID)"
            return 0
        else
            print_status "Removing stale PID file..."
            rm -f "$PID_FILE"
        fi
    fi
    
    # Check prerequisites
    if ! check_celery; then
        return 1
    fi
    
    # Check Redis (but don't fail if not available - worker can start and wait)
    check_redis || print_warning "Redis not available, worker will start but tasks may fail"
    
    print_status "Configuration:"
    echo "  App: $CELERY_APP"
    echo "  Broker: $CELERY_BROKER_URL"
    echo "  Result Backend: $CELERY_RESULT_BACKEND"
    echo "  Queue: $CELERY_QUEUE"
    echo "  Concurrency: $CELERY_CONCURRENCY"
    echo "  Log Level: $CELERY_LOGLEVEL"
    echo "  Log File: $LOG_FILE"
    echo "  PID File: $PID_FILE"
    echo ""
    
    # Start Celery worker in background
    print_status "Starting Celery worker..."
    
    nohup celery -A "$CELERY_APP" worker \
        --concurrency="$CELERY_CONCURRENCY" \
        --loglevel="$CELERY_LOGLEVEL" \
        --hostname="${CELERY_WORKER_NAME}@%h" \
        --queues="$CELERY_QUEUE" \
        --time-limit=1800 \
        --soft-time-limit=1500 \
        --max-tasks-per-child=1000 \
        --logfile="$LOG_FILE" \
        --pidfile="$PID_FILE" \
        > "$LOG_DIR/celery_startup.log" 2>&1 &
    
    WORKER_PID=$!
    
    sleep 3
    
    # Check if worker started
    if [ -f "$PID_FILE" ]; then
        ACTUAL_PID=$(cat "$PID_FILE" 2>/dev/null)
        if ps -p "$ACTUAL_PID" > /dev/null 2>&1; then
            print_success "Celery worker started (PID: $ACTUAL_PID)"
            return 0
        fi
    fi
    
    print_error "Celery worker failed to start"
    print_status "Check logs: tail -20 $LOG_FILE"
    if [ -f "$LOG_DIR/celery_startup.log" ]; then
        tail -20 "$LOG_DIR/celery_startup.log"
    fi
    return 1
}

# Stop Celery worker
stop_worker() {
    print_status "Stopping Celery worker..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "PID file not found, searching for running workers..."
        PIDS=$(pgrep -f "celery.*worker.*$CELERY_APP" || true)
        if [ -z "$PIDS" ]; then
            print_warning "No Celery workers found running"
            return 0
        fi
    else
        PIDS=$(cat "$PID_FILE" 2>/dev/null)
    fi
    
    for PID in $PIDS; do
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "Stopping worker (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Force killing worker (PID: $PID)..."
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
    done
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    print_success "Celery worker stopped"
}

# Restart Celery worker
restart_worker() {
    print_status "Restarting Celery worker..."
    stop_worker
    sleep 2
    start_worker
}

# Show worker status
show_status() {
    print_status "Celery Worker Status"
    echo "========================"
    echo ""
    
    # Check if worker is running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if ps -p "$PID" > /dev/null 2>&1; then
            print_success "Worker is running (PID: $PID)"
            echo ""
            echo "Process info:"
            ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem
        else
            print_warning "PID file exists but process not running"
            rm -f "$PID_FILE"
        fi
    else
        # Check for any celery workers
        PIDS=$(pgrep -f "celery.*worker" || true)
        if [ -n "$PIDS" ]; then
            print_warning "Found Celery workers but no PID file:"
            for PID in $PIDS; do
                ps -p "$PID" -o pid,cmd
            done
        else
            print_warning "No Celery workers running"
        fi
    fi
    
    echo ""
    print_status "Redis Status:"
    if check_redis; then
        print_success "Redis is available"
    else
        print_warning "Redis is not available"
    fi
    
    echo ""
    print_status "Configuration:"
    echo "  Broker URL: $CELERY_BROKER_URL"
    echo "  Result Backend: $CELERY_RESULT_BACKEND"
    echo "  Queue: $CELERY_QUEUE"
    echo "  Concurrency: $CELERY_CONCURRENCY"
    echo "  Log File: $LOG_FILE"
}

# Show worker logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing last 50 lines of Celery worker log:"
        echo ""
        tail -50 "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
}

# Monitor worker (follow logs)
monitor() {
    print_status "Monitoring Celery worker (Ctrl+C to stop)..."
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
        print_status "Waiting for log file to be created..."
        sleep 2
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            print_error "Log file still not found. Is the worker running?"
        fi
    fi
}

# Inspect active tasks
inspect_tasks() {
    print_status "Inspecting Celery workers..."
    
    if ! check_celery; then
        return 1
    fi
    
    # Use celery inspect command
    celery -A "$CELERY_APP" inspect active 2>/dev/null || {
        print_warning "Could not inspect active tasks. Is the worker running?"
    }
    
    echo ""
    print_status "Registered tasks:"
    celery -A "$CELERY_APP" inspect registered 2>/dev/null || {
        print_warning "Could not inspect registered tasks"
    }
    
    echo ""
    print_status "Worker stats:"
    celery -A "$CELERY_APP" inspect stats 2>/dev/null || {
        print_warning "Could not get worker stats"
    }
}

# Show help
show_help() {
    cat << EOF
REDLINE Celery Management Script

Usage: $0 <command> [options]

Commands:
  start           Start Celery worker
  stop            Stop Celery worker
  restart         Restart Celery worker
  status          Show worker status
  logs            Show worker logs
  monitor         Follow worker logs (real-time)
  inspect         Inspect active tasks and workers
  redis-start     Start Redis container
  redis-status    Check Redis status
  help            Show this help message

Environment Variables:
  CELERY_BROKER_URL       Redis broker URL (default: redis://localhost:6379/0)
  CELERY_RESULT_BACKEND   Result backend URL (default: redis://localhost:6379/0)
  CELERY_CONCURRENCY      Worker concurrency (default: 2)
  CELERY_LOGLEVEL         Log level (default: info)
  CELERY_QUEUE            Queue name (default: redline_tasks)
  LOG_DIR                 Log directory (default: ./logs)

Examples:
  $0 start                # Start Celery worker
  $0 start redis-start    # Start Redis and Celery worker
  $0 status               # Check worker status
  $0 logs                 # View logs
  $0 monitor              # Follow logs in real-time
  $0 inspect              # Inspect active tasks
  $0 stop                 # Stop worker

EOF
}

# Main command handler
main() {
    case "${1:-help}" in
        start)
            if [ "$2" = "redis-start" ] || [ "$2" = "redis" ]; then
                start_redis
            fi
            start_worker
            ;;
        stop)
            stop_worker
            ;;
        restart)
            restart_worker
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        monitor)
            monitor
            ;;
        inspect)
            inspect_tasks
            ;;
        redis-start)
            start_redis
            ;;
        redis-status)
            check_redis
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

