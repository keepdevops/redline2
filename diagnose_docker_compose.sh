#!/bin/bash

# Comprehensive Docker Compose Diagnostic Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_header "DOCKER COMPOSE DIAGNOSTIC REPORT"
echo ""

# 1. Check Docker Compose installation
print_header "1. DOCKER COMPOSE INSTALLATION"
echo "Location: $(which docker-compose 2>/dev/null || echo 'Not found')"
echo "Version check:"
docker-compose --version 2>&1 || print_error "Docker Compose version check failed"

echo ""

# 2. Check Python environment
print_header "2. PYTHON ENVIRONMENT"
echo "Python version: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Python path: $(which python3 2>/dev/null || echo 'Not found')"

echo ""
echo "Checking Python modules:"
python3 -c "import distutils" 2>/dev/null && print_success "distutils available" || print_error "distutils missing"
python3 -c "import setuptools" 2>/dev/null && print_success "setuptools available" || print_error "setuptools missing"

echo ""

# 3. Check system packages
print_header "3. SYSTEM PACKAGES"
echo "Checking installed packages:"
dpkg -l | grep -E "(docker-compose|python3-distutils|python3-setuptools)" 2>/dev/null || echo "No relevant packages found"

echo ""

# 4. Test Docker Compose functionality
print_header "4. FUNCTIONALITY TEST"
echo "Testing basic Docker Compose command:"
timeout 10 docker-compose --help >/dev/null 2>&1 && print_success "Docker Compose responds" || print_error "Docker Compose not responding"

echo ""

# 5. Check for specific error patterns
print_header "5. ERROR ANALYSIS"
echo "Running Docker Compose with error capture:"
docker-compose --version 2>&1 | head -5

echo ""

# 6. Check Docker daemon
print_header "6. DOCKER DAEMON STATUS"
docker info >/dev/null 2>&1 && print_success "Docker daemon running" || print_error "Docker daemon not accessible"

echo ""

# 7. Check file permissions
print_header "7. FILE PERMISSIONS"
if [ -f /usr/bin/docker-compose ]; then
    ls -la /usr/bin/docker-compose
    echo "Executable test:"
    /usr/bin/docker-compose --version 2>&1 | head -3
else
    print_error "Docker Compose binary not found at /usr/bin/docker-compose"
fi

echo ""

# 8. Check for conflicting installations
print_header "8. CONFLICTING INSTALLATIONS"
echo "Checking for multiple Docker Compose installations:"
find /usr -name "*docker-compose*" 2>/dev/null | head -10

echo ""

# 9. Check environment variables
print_header "9. ENVIRONMENT VARIABLES"
echo "PATH: $PATH"
echo "PYTHONPATH: ${PYTHONPATH:-'Not set'}"

echo ""

# 10. Generate fix recommendations
print_header "10. RECOMMENDED FIXES"
echo "Based on the diagnostic results:"
echo ""

if ! python3 -c "import distutils" 2>/dev/null; then
    print_warning "Missing distutils - install with: sudo apt install python3-distutils"
fi

if ! python3 -c "import setuptools" 2>/dev/null; then
    print_warning "Missing setuptools - install with: sudo apt install python3-setuptools"
fi

if ! docker info >/dev/null 2>&1; then
    print_warning "Docker daemon not running - start with: sudo systemctl start docker"
fi

echo ""
print_status "Run this script and share the output to get specific fix recommendations"
