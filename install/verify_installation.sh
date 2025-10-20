#!/bin/bash
set -e

# REDLINE Installation Verification Script
# Verifies that REDLINE is properly installed and configured

echo "🔍 REDLINE Installation Verification"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
REDLINE_USER="redline"
REDLINE_DIR="/home/$REDLINE_USER/redline"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if service is running
service_running() {
    systemctl is-active --quiet "$1" 2>/dev/null
}

# Function to check if port is open
port_open() {
    netstat -tlnp 2>/dev/null | grep -q ":$1 " || ss -tlnp 2>/dev/null | grep -q ":$1 "
}

# Function to check file exists
file_exists() {
    [[ -f "$1" ]]
}

# Function to check directory exists
dir_exists() {
    [[ -d "$1" ]]
}

# Function to check user exists
user_exists() {
    id "$1" &>/dev/null
}

# Main verification function
main() {
    local errors=0
    local warnings=0
    
    print_status "Starting REDLINE installation verification..."
    echo ""
    
    # Check user exists
    print_status "Checking REDLINE user..."
    if user_exists "$REDLINE_USER"; then
        print_success "User $REDLINE_USER exists"
    else
        print_error "User $REDLINE_USER does not exist"
        ((errors++))
    fi
    
    # Check installation directory
    print_status "Checking installation directory..."
    if dir_exists "$REDLINE_DIR"; then
        print_success "Installation directory exists: $REDLINE_DIR"
    else
        print_error "Installation directory not found: $REDLINE_DIR"
        ((errors++))
    fi
    
    # Check Python installation
    print_status "Checking Python installation..."
    if command_exists python3; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python installed: $python_version"
    else
        print_error "Python3 not installed"
        ((errors++))
    fi
    
    # Check Docker installation
    print_status "Checking Docker installation..."
    if command_exists docker; then
        local docker_version=$(docker --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker installed: $docker_version"
        
        # Check if Docker is running
        if docker info &>/dev/null; then
            print_success "Docker is running"
        else
            print_warning "Docker is not running"
            ((warnings++))
        fi
    else
        print_error "Docker not installed"
        ((errors++))
    fi
    
    # Check Docker Compose installation
    print_status "Checking Docker Compose installation..."
    if command_exists docker-compose; then
        local compose_version=$(docker-compose --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker Compose installed: $compose_version"
    else
        print_error "Docker Compose not installed"
        ((errors++))
    fi
    
    # Check systemd services
    print_status "Checking systemd services..."
    local services=("redline-gui" "redline-web" "redline-docker")
    for service in "${services[@]}"; do
        if systemctl list-unit-files | grep -q "$service.service"; then
            print_success "Service $service is configured"
            
            # Check if service is enabled
            if systemctl is-enabled --quiet "$service" 2>/dev/null; then
                print_success "Service $service is enabled"
            else
                print_warning "Service $service is not enabled"
                ((warnings++))
            fi
        else
            print_error "Service $service is not configured"
            ((errors++))
        fi
    done
    
    # Check startup scripts
    print_status "Checking startup scripts..."
    local scripts=("start_gui.sh" "start_web.sh" "start_docker.sh" "stop_docker.sh")
    for script in "${scripts[@]}"; do
        if file_exists "$REDLINE_DIR/$script"; then
            if [[ -x "$REDLINE_DIR/$script" ]]; then
                print_success "Script $script exists and is executable"
            else
                print_warning "Script $script exists but is not executable"
                ((warnings++))
            fi
        else
            print_error "Script $script not found"
            ((errors++))
        fi
    done
    
    # Check configuration files
    print_status "Checking configuration files..."
    local configs=("docker.env" "redline.conf" "docker-compose.yml")
    for config in "${configs[@]}"; do
        if file_exists "$REDLINE_DIR/$config"; then
            print_success "Configuration file $config exists"
        else
            print_error "Configuration file $config not found"
            ((errors++))
        fi
    done
    
    # Check data directories
    print_status "Checking data directories..."
    local data_dirs=("data" "data/downloaded" "data/converted" "data/stooq_format" "logs")
    for dir in "${data_dirs[@]}"; do
        if dir_exists "$REDLINE_DIR/$dir"; then
            print_success "Data directory $dir exists"
        else
            print_error "Data directory $dir not found"
            ((errors++))
        fi
    done
    
    # Check Docker images
    print_status "Checking Docker images..."
    if docker images | grep -q "redline"; then
        print_success "REDLINE Docker images found"
        docker images | grep "redline" | while read line; do
            print_status "  $line"
        done
    else
        print_warning "REDLINE Docker images not found"
        ((warnings++))
    fi
    
    # Check ports
    print_status "Checking network ports..."
    if port_open 8080; then
        print_warning "Port 8080 is already in use"
        ((warnings++))
    else
        print_success "Port 8080 is available"
    fi
    
    if port_open 5900; then
        print_warning "Port 5900 is already in use"
        ((warnings++))
    else
        print_success "Port 5900 is available"
    fi
    
    # Check desktop shortcuts
    print_status "Checking desktop shortcuts..."
    local shortcuts=("REDLINE-GUI.desktop" "REDLINE-Web.desktop" "REDLINE-Docker.desktop")
    for shortcut in "${shortcuts[@]}"; do
        if file_exists "/home/$REDLINE_USER/Desktop/$shortcut"; then
            print_success "Desktop shortcut $shortcut exists"
        else
            print_warning "Desktop shortcut $shortcut not found"
            ((warnings++))
        fi
    done
    
    # Summary
    echo ""
    print_status "Verification Summary:"
    echo "========================"
    
    if [[ $errors -eq 0 ]]; then
        print_success "Installation verification completed successfully!"
        if [[ $warnings -gt 0 ]]; then
            print_warning "Found $warnings warnings (non-critical issues)"
        fi
    else
        print_error "Installation verification failed with $errors errors"
        if [[ $warnings -gt 0 ]]; then
            print_warning "Also found $warnings warnings"
        fi
    fi
    
    echo ""
    print_status "Next steps:"
    echo "============"
    
    if [[ $errors -eq 0 ]]; then
        echo "1. Start REDLINE services:"
        echo "   sudo systemctl start redline-web"
        echo "   sudo systemctl start redline-gui"
        echo "   sudo systemctl start redline-docker"
        echo ""
        echo "2. Access REDLINE:"
        echo "   Web Interface: http://localhost:8080"
        echo "   VNC Access: localhost:5900 (password: redline123)"
        echo ""
        echo "3. Check logs:"
        echo "   sudo journalctl -u redline-web -f"
        echo "   sudo journalctl -u redline-gui -f"
    else
        echo "1. Fix the errors listed above"
        echo "2. Re-run this verification script"
        echo "3. Check the installation logs for more details"
    fi
    
    # Return appropriate exit code
    if [[ $errors -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
