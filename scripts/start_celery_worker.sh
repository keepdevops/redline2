#!/bin/bash
# REDLINE Celery Worker Startup Script
# Starts Celery workers for background task processing

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
CELERY_APP="redline"
CELERY_WORKER_NAME="redline-worker"
CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-4}
CELERY_LOGLEVEL=${CELERY_LOGLEVEL:-info}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-"redis://localhost:6379/0"}
CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-"redis://localhost:6379/0"}

print_status "Starting Celery worker for REDLINE"
print_status "App: $CELERY_APP"
print_status "Broker: $CELERY_BROKER_URL"
print_status "Concurrency: $CELERY_CONCURRENCY"

# Check if Celery is installed
if ! command -v celery &> /dev/null; then
    print_error "Celery is not installed"
    print_status "Install with: pip install celery"
    exit 1
fi

# Check if Redis is available
if ! python3 -c "import redis; r = redis.from_url('$CELERY_BROKER_URL'); r.ping()" 2>/dev/null; then
    print_warning "Redis is not available at $CELERY_BROKER_URL"
    print_warning "Celery worker will start but tasks may fail"
else
    print_status "Redis connection successful"
fi

# Start Celery worker
celery -A ${CELERY_APP} worker \
    --concurrency=${CELERY_CONCURRENCY} \
    --loglevel=${CELERY_LOGLEVEL} \
    --hostname=${CELERY_WORKER_NAME}@%h \
    --queues=redline_tasks \
    --time-limit=1800 \
    --soft-time-limit=1500 \
    --max-tasks-per-child=1000 \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    --logfile=logs/celery_worker.log \
    --pidfile=logs/celery_worker.pid

print_status "Celery worker stopped"

