#!/bin/bash
# REDLINE Web GUI Docker Deployment Script
# Complete deployment automation with modern Ubuntu 24.04 LTS features

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="redline-web"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
CONFIG_DIR="config"
DATA_DIR="data"
LOGS_DIR="logs"
SSL_DIR="ssl"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  REDLINE Web GUI Deployment${NC}"
    echo -e "${PURPLE}================================${NC}"
}

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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check available resources
    local mem_total=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local disk_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ $mem_total -lt 2048 ]]; then
        print_warning "Low memory available (${mem_total}MB). Recommended: 2GB+"
    fi
    
    if [[ $disk_space -lt 5 ]]; then
        print_warning "Low disk space available (${disk_space}GB). Recommended: 5GB+"
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create directory structure
create_directories() {
    print_step "Creating directory structure..."
    
    local dirs=(
        "$CONFIG_DIR"
        "$DATA_DIR"
        "$LOGS_DIR"
        "$SSL_DIR"
        "$DATA_DIR/uploads"
        "$DATA_DIR/downloads"
        "$DATA_DIR/converted"
        "$LOGS_DIR/app"
        "$LOGS_DIR/nginx"
        "$LOGS_DIR/redis"
        "$LOGS_DIR/prometheus"
        "$LOGS_DIR/fluentd"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
    
    print_success "Directory structure created"
}

# Function to create environment file
create_env_file() {
    print_step "Creating environment configuration..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        cat > "$ENV_FILE" << EOF
# REDLINE Web GUI Environment Configuration
# Generated on $(date)

# Security
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "redline-secret-key-$(date +%s)")
REDIS_PASSWORD=$(openssl rand -base64 16 2>/dev/null || echo "redline-redis-password")

# Database
DB_PATH=/opt/redline/data/redline_data.duckdb

# Application
FLASK_ENV=production
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=8080
WEB_PORT=8080

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/redline/app.log

# Performance
WORKERS=4
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
TIMEOUT=30

# Timezone
TZ=UTC

# Python
PYTHONPATH=/opt/redline
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
EOF
        print_success "Environment file created: $ENV_FILE"
    else
        print_status "Environment file already exists: $ENV_FILE"
    fi
}

# Function to create configuration files
create_config_files() {
    print_step "Creating configuration files..."
    
    # Nginx configuration
    cat > "$CONFIG_DIR/nginx.conf" << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    include /etc/nginx/conf.d/*.conf;
}
EOF

    # Nginx site configuration
    cat > "$CONFIG_DIR/nginx-site.conf" << 'EOF'
upstream redline_backend {
    server redline-web:8080;
}

server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://redline_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    location /health {
        access_log off;
        proxy_pass http://redline_backend/health;
    }
    
    location /static {
        proxy_pass http://redline_backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # Redis configuration
    cat > "$CONFIG_DIR/redis.conf" << 'EOF'
# Redis configuration for REDLINE
bind 0.0.0.0
port 6379
timeout 0
keepalive 300

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis.log

# Security
requirepass redline-redis-password

# Performance
tcp-keepalive 300
tcp-backlog 511
EOF

    # Prometheus configuration
    cat > "$CONFIG_DIR/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'redline-web'
    static_configs:
      - targets: ['redline-web:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-proxy:80']
    metrics_path: '/nginx_status'
    scrape_interval: 30s
EOF

    # Fluentd configuration
    cat > "$CONFIG_DIR/fluentd.conf" << 'EOF'
<source>
  @type tail
  path /var/log/redline/*.log
  pos_file /var/log/fluentd/redline.log.pos
  tag redline.*
  format none
</source>

<match redline.**>
  @type stdout
</match>
EOF

    print_success "Configuration files created"
}

# Function to build Docker images
build_images() {
    print_step "Building Docker images..."
    
    # Build with BuildKit for better performance
    export DOCKER_BUILDKIT=1
    
    docker-compose build --no-cache --parallel
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Function to start services
start_services() {
    print_step "Starting services..."
    
    # Start services in background
    docker-compose up -d
    
    if [[ $? -eq 0 ]]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Function to wait for services
wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    local services=("redline-web" "redis" "nginx-proxy")
    local max_wait=300
    local wait_time=0
    
    for service in "${services[@]}"; do
        print_status "Waiting for $service..."
        
        while [[ $wait_time -lt $max_wait ]]; do
            if docker-compose ps "$service" | grep -q "Up"; then
                print_success "$service is ready"
                break
            fi
            
            sleep 5
            ((wait_time += 5))
            
            if [[ $((wait_time % 30)) -eq 0 ]]; then
                print_status "Still waiting for $service... (${wait_time}s)"
            fi
        done
        
        if [[ $wait_time -ge $max_wait ]]; then
            print_error "$service failed to start within ${max_wait}s"
            docker-compose logs "$service"
            exit 1
        fi
        
        wait_time=0
    done
}

# Function to run health checks
run_health_checks() {
    print_step "Running health checks..."
    
    # Check REDLINE web service
    local max_attempts=10
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f http://localhost:8080/health >/dev/null 2>&1; then
            print_success "REDLINE web service is healthy"
            break
        fi
        
        ((attempt++))
        print_status "Health check attempt $attempt/$max_attempts..."
        sleep 10
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_error "REDLINE web service health check failed"
        docker-compose logs redline-web
        exit 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
        exit 1
    fi
    
    # Check Nginx
    if curl -f http://localhost:8081/health >/dev/null 2>&1; then
        print_success "Nginx proxy is healthy"
    else
        print_warning "Nginx proxy health check failed (this may be expected)"
    fi
}

# Function to show deployment information
show_deployment_info() {
    print_step "Deployment Information"
    
    echo -e "${CYAN}Service URLs:${NC}"
    echo "  • REDLINE Web GUI: http://localhost:8080"
    echo "  • Nginx Proxy: http://localhost:8081"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Redis: localhost:6379"
    
    echo -e "\n${CYAN}Management Commands:${NC}"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Scale services: docker-compose up -d --scale redline-web=2"
    
    echo -e "\n${CYAN}Container Status:${NC}"
    docker-compose ps
    
    echo -e "\n${CYAN}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    echo -e "\n${CYAN}Log Files:${NC}"
    echo "  • Application logs: $LOGS_DIR/app/"
    echo "  • Nginx logs: $LOGS_DIR/nginx/"
    echo "  • Redis logs: $LOGS_DIR/redis/"
    
    print_success "Deployment completed successfully!"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -b, --build-only    Only build images, don't start services"
    echo "  -s, --start-only    Only start services (assumes images are built)"
    echo "  -c, --clean         Clean up before deployment"
    echo "  -f, --force         Force rebuild without cache"
    echo "  --no-health-check   Skip health checks"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full deployment"
    echo "  $0 -b               # Build only"
    echo "  $0 -s               # Start only"
    echo "  $0 -c -f            # Clean deployment with force rebuild"
}

# Function to clean up
cleanup() {
    print_step "Cleaning up..."
    
    # Stop and remove containers
    docker-compose down -v --remove-orphans
    
    # Remove images
    docker rmi $(docker images -q "$PROJECT_NAME*") 2>/dev/null || true
    
    # Clean up volumes
    docker volume prune -f
    
    # Clean up networks
    docker network prune -f
    
    print_success "Cleanup completed"
}

# Main function
main() {
    local build_only=false
    local start_only=false
    local cleanup_flag=false
    local force_rebuild=false
    local skip_health_check=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -b|--build-only)
                build_only=true
                shift
                ;;
            -s|--start-only)
                start_only=true
                shift
                ;;
            -c|--clean)
                cleanup_flag=true
                shift
                ;;
            -f|--force)
                force_rebuild=true
                shift
                ;;
            --no-health-check)
                skip_health_check=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Pre-deployment checks
    check_prerequisites
    
    # Cleanup if requested
    if [[ "$cleanup_flag" == true ]]; then
        cleanup
    fi
    
    # Setup
    create_directories
    create_env_file
    create_config_files
    
    # Build images
    if [[ "$start_only" == false ]]; then
        build_images
    fi
    
    # Start services
    if [[ "$build_only" == false ]]; then
        start_services
        wait_for_services
        
        if [[ "$skip_health_check" == false ]]; then
            run_health_checks
        fi
        
        show_deployment_info
    fi
    
    print_success "Deployment process completed!"
}

# Run main function
main "$@"
