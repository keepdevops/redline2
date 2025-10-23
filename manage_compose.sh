#!/bin/bash

# REDLINE Docker Compose Management Script
# Complete management for Option 4 Docker Compose setup

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
BACKUP_COMPOSE_FILE="docker-compose-backup.yml"

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
    echo -e "${PURPLE}[REDLINE]${NC} $1"
}

print_title() {
    echo -e "${WHITE}$1${NC}"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose not found!"
        print_status "Please run: ./install_options_redline.sh and choose option 4"
        exit 1
    fi
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon not running!"
        print_status "Please start Docker:"
        print_status "  Linux: sudo systemctl start docker"
        print_status "  macOS: Start Docker Desktop"
        exit 1
    fi
}

# Function to backup current docker-compose.yml
backup_compose_file() {
    if [ -f "$COMPOSE_FILE" ]; then
        cp "$COMPOSE_FILE" "$BACKUP_COMPOSE_FILE"
        print_success "Backed up current docker-compose.yml to $BACKUP_COMPOSE_FILE"
    fi
}

# Function to restore docker-compose.yml
restore_compose_file() {
    if [ -f "$BACKUP_COMPOSE_FILE" ]; then
        cp "$BACKUP_COMPOSE_FILE" "$COMPOSE_FILE"
        print_success "Restored docker-compose.yml from backup"
    else
        print_warning "No backup file found"
    fi
}

# Function to start services
start_services() {
    print_header "Starting REDLINE Services"
    
    check_docker_compose
    check_docker
    
    # Check if docker-compose.yml exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "docker-compose.yml not found!"
        print_status "Please run: ./install_options_redline.sh and choose option 4"
        exit 1
    fi
    
    print_status "Starting REDLINE services..."
    
    # Start services
    docker-compose up -d
    
    # Check if services started successfully
    if [ $? -eq 0 ]; then
        print_success "Services started successfully!"
        echo ""
        print_title "🌐 Service URLs:"
        echo "  • Web App:     http://localhost:8080"
        echo "  • Web GUI:     http://localhost:6080"
        echo "  • VNC Password: redline123"
        echo ""
        print_title "📋 Management Commands:"
        echo "  • View logs:   docker-compose logs -f"
        echo "  • Stop:        docker-compose down"
        echo "  • Restart:     docker-compose restart"
        echo "  • Status:      docker-compose ps"
        echo ""
        
        # Wait a moment and check service status
        sleep 5
        print_status "Checking service status..."
        docker-compose ps
    else
        print_error "Failed to start services!"
        print_status "Check logs: docker-compose logs"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_header "Stopping REDLINE Services"
    
    check_docker_compose
    
    print_status "Stopping REDLINE services..."
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_success "Services stopped successfully!"
    else
        print_error "Failed to stop services!"
        exit 1
    fi
}

# Function to restart services
restart_services() {
    print_header "Restarting REDLINE Services"
    
    check_docker_compose
    check_docker
    
    print_status "Restarting REDLINE services..."
    docker-compose restart
    
    if [ $? -eq 0 ]; then
        print_success "Services restarted successfully!"
        echo ""
        print_title "🌐 Service URLs:"
        echo "  • Web App:     http://localhost:8080"
        echo "  • Web GUI:     http://localhost:6080"
        echo "  • VNC Password: redline123"
    else
        print_error "Failed to restart services!"
        exit 1
    fi
}

# Function to show status
show_status() {
    print_header "REDLINE Service Status"
    
    check_docker_compose
    
    echo ""
    print_title "📊 Container Status:"
    docker-compose ps
    
    echo ""
    print_title "📈 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" $(docker-compose ps -q) 2>/dev/null || print_warning "No containers running"
    
    echo ""
    print_title "🌐 Service URLs:"
    echo "  • Web App:     http://localhost:8080"
    echo "  • Web GUI:     http://localhost:6080"
    echo "  • VNC Password: redline123"
}

# Function to show logs
show_logs() {
    print_header "REDLINE Service Logs"
    
    check_docker_compose
    
    if [ -n "$1" ]; then
        print_status "Showing logs for service: $1"
        docker-compose logs -f "$1"
    else
        print_status "Showing logs for all services"
        docker-compose logs -f
    fi
}

# Function to rebuild services
rebuild_services() {
    print_header "Rebuilding REDLINE Services"
    
    check_docker_compose
    check_docker
    
    print_status "Rebuilding REDLINE services..."
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        print_success "Services rebuilt successfully!"
        print_status "Starting rebuilt services..."
        docker-compose up -d
    else
        print_error "Failed to rebuild services!"
        exit 1
    fi
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up REDLINE Services"
    
    check_docker_compose
    
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing services..."
        docker-compose down -v --remove-orphans
        
        print_status "Removing images..."
        docker rmi redline-webgui:latest 2>/dev/null || true
        
        print_status "Cleaning up unused resources..."
        docker system prune -f
        
        print_success "Cleanup complete!"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show help
show_help() {
    print_title "REDLINE Docker Compose Management"
    echo ""
    print_title "Usage: $0 [COMMAND]"
    echo ""
    print_title "Commands:"
    echo "  start       Start REDLINE services"
    echo "  stop        Stop REDLINE services"
    echo "  restart     Restart REDLINE services"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  rebuild     Rebuild and restart services"
    echo "  cleanup     Remove all containers and data"
    echo "  backup      Backup docker-compose.yml"
    echo "  restore     Restore docker-compose.yml"
    echo "  help        Show this help"
    echo ""
    print_title "Examples:"
    echo "  $0 start                    # Start services"
    echo "  $0 logs redline-webgui      # Show logs for specific service"
    echo "  $0 status                   # Check service status"
    echo ""
    print_title "Service URLs:"
    echo "  • Web App:     http://localhost:8080"
    echo "  • Web GUI:     http://localhost:6080"
    echo "  • VNC Password: redline123"
}

# Main function
main() {
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        rebuild)
            rebuild_services
            ;;
        cleanup)
            cleanup
            ;;
        backup)
            backup_compose_file
            ;;
        restore)
            restore_compose_file
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
