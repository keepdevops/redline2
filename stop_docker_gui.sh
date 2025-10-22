#!/bin/bash

# REDLINE Tkinter GUI Docker Stop Script
# Stops and removes Docker containers and cleans up resources

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
IMAGE_NAME="redline-gui"
CONTAINER_NAME="redline-gui-container"
NETWORK_NAME="redline-network"
VOLUME_NAME="redline-gui-temp"

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
    echo -e "${PURPLE}[STOP]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to stop specific container
stop_container() {
    local container_name=$1
    
    if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        print_status "Stopping container: $container_name"
        docker stop "$container_name"
        print_success "Container stopped: $container_name"
    else
        print_warning "Container not running: $container_name"
    fi
}

# Function to remove specific container
remove_container() {
    local container_name=$1
    
    if docker ps -a --format "{{.Names}}" | grep -q "^${container_name}$"; then
        print_status "Removing container: $container_name"
        docker rm "$container_name"
        print_success "Container removed: $container_name"
    else
        print_warning "Container not found: $container_name"
    fi
}

# Function to stop and remove main container
stop_main_container() {
    print_header "Stopping main container"
    stop_container "$CONTAINER_NAME"
    remove_container "$CONTAINER_NAME"
}

# Function to stop all redline containers
stop_all_containers() {
    print_header "Stopping all REDLINE containers"
    
    # Find all containers with redline in the name
    local containers=$(docker ps -a --format "{{.Names}}" | grep -i redline || true)
    
    if [ -z "$containers" ]; then
        print_warning "No REDLINE containers found"
        return
    fi
    
    print_status "Found containers:"
    echo "$containers"
    
    # Stop and remove each container
    while IFS= read -r container; do
        if [ -n "$container" ]; then
            stop_container "$container"
            remove_container "$container"
        fi
    done <<< "$containers"
}

# Function to remove images
remove_images() {
    local force=${1:-false}
    
    print_header "Removing REDLINE images"
    
    # Find all redline images
    local images=$(docker images "${IMAGE_NAME}" --format "{{.Repository}}:{{.Tag}}" || true)
    
    if [ -z "$images" ]; then
        print_warning "No REDLINE images found"
        return
    fi
    
    print_status "Found images:"
    echo "$images"
    
    if [ "$force" = "true" ]; then
        echo "$images" | xargs docker rmi -f
        print_success "Images removed forcefully"
    else
        echo "$images" | xargs docker rmi
        print_success "Images removed"
    fi
}

# Function to remove volumes
remove_volumes() {
    print_header "Removing REDLINE volumes"
    
    # Find all redline volumes
    local volumes=$(docker volume ls --format "{{.Name}}" | grep -i redline || true)
    
    if [ -z "$volumes" ]; then
        print_warning "No REDLINE volumes found"
        return
    fi
    
    print_status "Found volumes:"
    echo "$volumes"
    
    echo "$volumes" | xargs docker volume rm
    print_success "Volumes removed"
}

# Function to remove networks
remove_networks() {
    print_header "Removing REDLINE networks"
    
    # Find all redline networks
    local networks=$(docker network ls --format "{{.Name}}" | grep -i redline || true)
    
    if [ -z "$networks" ]; then
        print_warning "No REDLINE networks found"
        return
    fi
    
    print_status "Found networks:"
    echo "$networks"
    
    echo "$networks" | xargs docker network rm
    print_success "Networks removed"
}

# Function to clean up everything
cleanup_all() {
    print_header "Complete cleanup"
    
    stop_all_containers
    remove_images "true"
    remove_volumes
    remove_networks
    
    print_success "Complete cleanup finished"
}

# Function to show status
show_status() {
    print_header "Current Status"
    
    print_status "Containers:"
    docker ps -a --filter "name=redline" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" || true
    
    print_status "Images:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" || true
    
    print_status "Volumes:"
    docker volume ls --filter "name=redline" --format "table {{.Name}}\t{{.Driver}}" || true
    
    print_status "Networks:"
    docker network ls --filter "name=redline" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" || true
}

# Function to show help
show_help() {
    echo "REDLINE Tkinter GUI Docker Stop Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  stop             Stop main container"
    echo "  stop-all         Stop all REDLINE containers"
    echo "  remove-images    Remove REDLINE images"
    echo "  remove-volumes   Remove REDLINE volumes"
    echo "  remove-networks  Remove REDLINE networks"
    echo "  cleanup          Complete cleanup (containers, images, volumes, networks)"
    echo "  status           Show current status"
    echo "  help             Show this help message"
    echo ""
    echo "Options:"
    echo "  --force          Force removal (for images)"
    echo "  --verbose        Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 stop"
    echo "  $0 cleanup"
    echo "  $0 status"
    echo ""
}

# Main script logic
main() {
    # Parse arguments
    local force=""
    local verbose=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force="true"
                shift
                ;;
            --verbose)
                verbose="true"
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    case "${1:-help}" in
        stop)
            check_docker
            stop_main_container
            ;;
        stop-all)
            check_docker
            stop_all_containers
            ;;
        remove-images)
            check_docker
            remove_images "$force"
            ;;
        remove-volumes)
            check_docker
            remove_volumes
            ;;
        remove-networks)
            check_docker
            remove_networks
            ;;
        cleanup)
            check_docker
            cleanup_all
            ;;
        status)
            check_docker
            show_status
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
