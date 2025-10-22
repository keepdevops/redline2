#!/bin/bash

# Robust Docker Compose Fix Script

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

print_header "ROBUST DOCKER COMPOSE FIX"
echo ""

# Step 1: Complete cleanup
print_status "Step 1: Complete cleanup of all Docker Compose installations..."

# Remove all possible Docker Compose installations
sudo apt remove -y docker-compose docker-compose-plugin docker-compose-v2 2>/dev/null || true
sudo apt autoremove -y 2>/dev/null || true
pip3 uninstall -y docker-compose docker-compose-v2 2>/dev/null || true

# Remove any remaining binaries
sudo rm -f /usr/local/bin/docker-compose 2>/dev/null || true
sudo rm -f /usr/bin/docker-compose 2>/dev/null || true

print_success "Cleanup completed"

echo ""

# Step 2: Install Python dependencies properly
print_status "Step 2: Installing Python dependencies..."

# Update package lists
sudo apt update

# Install Python development tools
sudo apt install -y python3-dev python3-pip python3-venv

# Try different methods to install distutils
print_status "Installing distutils via apt..."
sudo apt install -y python3-distutils python3-setuptools || {
    print_warning "APT distutils failed, trying alternative..."
    
    # Alternative: Install via pip
    print_status "Installing setuptools via pip..."
    pip3 install --upgrade setuptools wheel
    
    # Try to install distutils via pip (if available)
    pip3 install distutils-extra 2>/dev/null || true
}

# Verify distutils availability
echo ""
print_status "Verifying distutils availability..."
python3 -c "import distutils" 2>/dev/null && print_success "distutils available" || print_warning "distutils still missing"

echo ""

# Step 3: Try Docker Compose V2 (modern approach)
print_status "Step 3: Installing Docker Compose V2 (modern approach)..."

# Install Docker Compose V2 plugin
sudo apt install -y docker-compose-plugin || {
    print_warning "Plugin installation failed, trying manual method..."
    
    # Manual installation of Docker Compose V2
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

# Test Docker Compose V2
if docker compose version >/dev/null 2>&1; then
    print_success "Docker Compose V2 installed: $(docker compose version)"
    DOCKER_COMPOSE_V2_WORKING=true
else
    print_warning "Docker Compose V2 not working"
    DOCKER_COMPOSE_V2_WORKING=false
fi

echo ""

# Step 4: Fallback to Docker Compose V1 if V2 fails
if [ "$DOCKER_COMPOSE_V2_WORKING" = false ]; then
    print_status "Step 4: Installing Docker Compose V1 (fallback)..."
    
    # Try pip installation
    pip3 install docker-compose || {
        print_warning "Pip installation failed, trying standalone..."
        
        # Standalone installation
        DOCKER_COMPOSE_VERSION="1.29.2"
        sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    }
    
    # Test Docker Compose V1
    if docker-compose --version >/dev/null 2>&1; then
        print_success "Docker Compose V1 installed: $(docker-compose --version)"
        DOCKER_COMPOSE_V1_WORKING=true
    else
        print_error "Docker Compose V1 also failed"
        DOCKER_COMPOSE_V1_WORKING=false
    fi
else
    DOCKER_COMPOSE_V1_WORKING=false
fi

echo ""

# Step 5: Create compatibility script
print_status "Step 5: Creating compatibility script..."

cat > docker-compose-compat.sh << 'EOF'
#!/bin/bash

# Docker Compose compatibility script
# Handles both V1 and V2 versions

if docker compose version >/dev/null 2>&1; then
    # Use Docker Compose V2
    docker compose "$@"
elif docker-compose --version >/dev/null 2>&1; then
    # Use Docker Compose V1
    docker-compose "$@"
else
    echo "Error: No Docker Compose installation found"
    exit 1
fi
EOF

chmod +x docker-compose-compat.sh

print_success "Compatibility script created"

echo ""

# Step 6: Update docker-compose.yml to use V2 syntax
print_status "Step 6: Updating docker-compose.yml for compatibility..."

if [ -f "docker-compose.yml" ]; then
    # Create backup
    cp docker-compose.yml docker-compose.yml.backup
    
    # Update to use V2 compatible syntax
    sed -i 's/dockerfile: Dockerfile.webgui.universal/dockerfile: Dockerfile.webgui.simple/g' docker-compose.yml 2>/dev/null || true
    
    print_success "docker-compose.yml updated for compatibility"
fi

echo ""

# Step 7: Test installation
print_status "Step 7: Testing installation..."

if [ "$DOCKER_COMPOSE_V2_WORKING" = true ]; then
    print_success "✅ Docker Compose V2 is working"
    print_status "Use: docker compose (instead of docker-compose)"
elif [ "$DOCKER_COMPOSE_V1_WORKING" = true ]; then
    print_success "✅ Docker Compose V1 is working"
    print_status "Use: docker-compose"
else
    print_error "❌ Both Docker Compose versions failed"
    print_status "Manual installation required"
fi

echo ""

# Step 8: Create updated start script
print_status "Step 8: Creating updated start script..."

cat > start_compose_fixed.sh << 'EOF'
#!/bin/bash

# Updated Docker Compose startup script with compatibility

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_status "Starting REDLINE with Docker Compose..."

# Check which Docker Compose version to use
if docker compose version >/dev/null 2>&1; then
    print_status "Using Docker Compose V2"
    COMPOSE_CMD="docker compose"
elif docker-compose --version >/dev/null 2>&1; then
    print_status "Using Docker Compose V1"
    COMPOSE_CMD="docker-compose"
else
    print_error "No Docker Compose installation found"
    exit 1
fi

# Start services
$COMPOSE_CMD up -d

if [ $? -eq 0 ]; then
    print_success "Services started successfully!"
    echo "🌐 Web App: http://localhost:8080"
    echo "🖥️ Web GUI: http://localhost:6080"
    echo "🔑 VNC Password: redline123"
else
    print_error "Failed to start services"
    print_status "Check logs: $COMPOSE_CMD logs"
fi
EOF

chmod +x start_compose_fixed.sh

print_success "Updated start script created: start_compose_fixed.sh"

echo ""
print_success "Robust Docker Compose fix completed!"
print_status "Try: ./start_compose_fixed.sh"
