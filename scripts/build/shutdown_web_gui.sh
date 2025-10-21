#!/bin/bash

# REDLINE Web GUI Docker Shutdown Script
# Stops and removes the redline-web-gui container

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
CONTAINER_NAME="redline-web-gui"
FORCE_SHUTDOWN="false"
REMOVE_IMAGE="false"
REMOVE_VOLUMES="false"

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
}

# Stop and remove container
stop_container() {
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        log "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        log_success "Container stopped"
    else
        log_warning "Container $CONTAINER_NAME is not running"
    fi
    
    if docker ps -aq --filter "name=$CONTAINER_NAME" | grep -q .; then
        log "Removing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        log_success "Container removed"
    else
        log_warning "Container $CONTAINER_NAME does not exist"
    fi
}

# Remove image (optional)
remove_image() {
    if [ "$REMOVE_IMAGE" = "true" ]; then
        log "Removing Docker image: redline-web-gui"
        docker rmi redline-web-gui:latest 2>/dev/null || log_warning "Image redline-web-gui:latest not found"
        docker rmi redline-web-gui:$(date +%Y%m%d) 2>/dev/null || log_warning "Dated image not found"
        log_success "Images removed"
    fi
}

# Remove volumes (optional)
remove_volumes() {
    if [ "$REMOVE_VOLUMES" = "true" ]; then
        log "Removing Docker volumes..."
        docker volume prune -f
        log_success "Volumes removed"
    fi
}

# Clean up other redline containers
cleanup_other_containers() {
    log "Cleaning up other REDLINE containers..."
    
    # Stop and remove any containers with 'redline' in the name
    docker ps -aq --filter "name=redline" | while read container_id; do
        if [ ! -z "$container_id" ]; then
            log "Stopping container: $container_id"
            docker stop "$container_id" 2>/dev/null || true
            docker rm "$container_id" 2>/dev/null || true
        fi
    done
    
    log_success "Other REDLINE containers cleaned up"
}

# Show shutdown information
show_shutdown_info() {
    log_success "REDLINE Web GUI shutdown completed!"
    echo ""
    echo "Shutdown Summary:"
    echo "================"
    echo "Container: $CONTAINER_NAME - Stopped and Removed"
    
    if [ "$REMOVE_IMAGE" = "true" ]; then
        echo "Images: Removed"
    else
        echo "Images: Preserved"
    fi
    
    if [ "$REMOVE_VOLUMES" = "true" ]; then
        echo "Volumes: Removed"
    else
        echo "Volumes: Preserved"
    fi
    
    echo ""
    echo "To restart REDLINE Web GUI:"
    echo "  ./build/run_web_gui.sh"
    echo ""
    echo "To rebuild and restart:"
    echo "  ./build/build_web_gui.sh --clean"
    echo "  ./build/run_web_gui.sh"
}

# Main shutdown function
main() {
    log "REDLINE Web GUI Shutdown"
    log "========================"
    
    check_docker
    stop_container
    remove_image
    remove_volumes
    
    if [ "$CLEANUP_ALL" = "true" ]; then
        cleanup_other_containers
    fi
    
    show_shutdown_info
}

# Handle script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --force|-f)
            FORCE_SHUTDOWN="true"
            shift
            ;;
        --remove-image)
            REMOVE_IMAGE="true"
            shift
            ;;
        --remove-volumes)
            REMOVE_VOLUMES="true"
            shift
            ;;
        --cleanup-all)
            CLEANUP_ALL="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --name NAME         Container name (default: redline-web-gui)"
            echo "  --force, -f         Force shutdown (not implemented yet)"
            echo "  --remove-image     Remove Docker images after shutdown"
            echo "  --remove-volumes    Remove Docker volumes after shutdown"
            echo "  --cleanup-all       Clean up all REDLINE containers"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Basic shutdown"
            echo "  $0 --remove-image                     # Remove images too"
            echo "  $0 --cleanup-all                      # Clean everything"
            echo "  $0 --name my-container                # Custom container name"
            echo ""
            echo "This script will:"
            echo "  - Stop the REDLINE Web GUI container"
            echo "  - Remove the container"
            echo "  - Optionally remove images and volumes"
            echo "  - Optionally clean up other REDLINE containers"
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
