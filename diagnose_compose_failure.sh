#!/bin/bash

# Deep Docker Compose Diagnosis Script

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

print_header "DEEP DOCKER COMPOSE DIAGNOSIS"
echo ""

# 1. System Information
print_status "1. System Information:"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || uname -a)"
echo "Python: $(python3 --version)"
echo "Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
echo ""

# 2. Network Connectivity
print_status "2. Network Connectivity:"
if ping -c 1 github.com >/dev/null 2>&1; then
    print_success "GitHub accessible"
else
    print_error "GitHub not accessible - network issue"
fi

if ping -c 1 pypi.org >/dev/null 2>&1; then
    print_success "PyPI accessible"
else
    print_error "PyPI not accessible - network issue"
fi
echo ""

# 3. Python Environment
print_status "3. Python Environment:"
echo "Python path: $(which python3)"
echo "Pip path: $(which pip3)"
echo "Pip version: $(pip3 --version 2>/dev/null || echo 'Not available')"

# Check Python modules
python3 -c "import sys; print('Python modules path:', sys.path)" 2>/dev/null || echo "Python module path check failed"
echo ""

# 4. Package Manager Status
print_status "4. Package Manager Status:"
if sudo apt update >/dev/null 2>&1; then
    print_success "APT package manager working"
else
    print_error "APT package manager issues"
fi
echo ""

# 5. Docker Status
print_status "5. Docker Status:"
if docker info >/dev/null 2>&1; then
    print_success "Docker daemon running"
    docker info | grep -E "(Server Version|Storage Driver|Logging Driver)" | head -3
else
    print_error "Docker daemon not running or not accessible"
fi
echo ""

# 6. Permission Check
print_status "6. Permission Check:"
if [ -w /usr/local/bin ]; then
    print_success "Can write to /usr/local/bin"
else
    print_warning "Cannot write to /usr/local/bin (need sudo)"
fi

if groups | grep -q docker; then
    print_success "User in docker group"
else
    print_warning "User not in docker group"
fi
echo ""

# 7. Alternative Installation Methods
print_status "7. Testing Alternative Installation Methods:"

# Method 1: Snap
if command -v snap >/dev/null 2>&1; then
    print_status "Testing snap installation..."
    sudo snap install docker-compose 2>/dev/null && print_success "Snap installation successful" || print_warning "Snap installation failed"
fi

# Method 2: Flatpak
if command -v flatpak >/dev/null 2>&1; then
    print_status "Testing flatpak installation..."
    flatpak install flathub com.docker.compose 2>/dev/null && print_success "Flatpak installation successful" || print_warning "Flatpak installation failed"
fi

# Method 3: AppImage
print_status "Testing AppImage download..."
if wget -q https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -O /tmp/docker-compose-appimage 2>/dev/null; then
    chmod +x /tmp/docker-compose-appimage
    /tmp/docker-compose-appimage version >/dev/null 2>&1 && print_success "AppImage download successful" || print_warning "AppImage execution failed"
else
    print_warning "AppImage download failed"
fi
echo ""

# 8. Create Alternative Solutions
print_status "8. Creating Alternative Solutions..."

# Solution 1: Use working Options 1-3
cat > use_working_options.sh << 'EOF'
#!/bin/bash

echo "🎯 ALTERNATIVE SOLUTION: Use Working Options"
echo "============================================="
echo ""
echo "Since Docker Compose (Option 4) is failing, use the working options:"
echo ""
echo "✅ Option 1: Web-based GUI (WORKS)"
echo "   ./install_redline_fixed.sh"
echo "   Choose option 1"
echo "   Access: http://localhost:6080"
echo ""
echo "✅ Option 2: Tkinter GUI with X11 (WORKS)"
echo "   ./install_redline_fixed.sh"
echo "   Choose option 2"
echo "   Run: ./start_tkinter.sh"
echo ""
echo "✅ Option 3: Hybrid GUI (WORKS)"
echo "   ./install_redline_fixed.sh"
echo "   Choose option 3"
echo "   Run: ./start_hybrid.sh"
echo ""
echo "💡 All three options provide the same functionality as Option 4!"
echo "   Option 4 (Docker Compose) is just orchestration - not essential."
EOF

chmod +x use_working_options.sh

# Solution 2: Manual Docker commands
cat > manual_docker.sh << 'EOF'
#!/bin/bash

echo "🔧 MANUAL DOCKER SOLUTION"
echo "========================="
echo ""
echo "Instead of Docker Compose, use manual Docker commands:"
echo ""
echo "1. Build the image:"
echo "   docker build -f Dockerfile.webgui.simple -t redline-webgui ."
echo ""
echo "2. Run the container:"
echo "   docker run -d --name redline-web-app \\"
echo "     -p 8080:8080 -p 6080:6080 \\"
echo "     -v \$(pwd)/data:/opt/redline/data \\"
echo "     -v \$(pwd)/logs:/var/log/redline \\"
echo "     -v \$(pwd)/config:/opt/redline/config \\"
echo "     redline-webgui"
echo ""
echo "3. Check status:"
echo "   docker ps"
echo ""
echo "4. View logs:"
echo "   docker logs redline-web-app"
echo ""
echo "5. Stop container:"
echo "   docker stop redline-web-app"
echo "   docker rm redline-web-app"
EOF

chmod +x manual_docker.sh

# Solution 3: Native installation
cat > native_install.sh << 'EOF'
#!/bin/bash

echo "🏠 NATIVE INSTALLATION SOLUTION"
echo "==============================="
echo ""
echo "Install REDLINE natively without Docker:"
echo ""
echo "1. Install Python dependencies:"
echo "   sudo apt install python3-pip python3-venv"
echo "   pip3 install -r requirements.txt"
echo ""
echo "2. Start web app:"
echo "   python3 web_app.py"
echo ""
echo "3. Access: http://localhost:8080"
echo ""
echo "💡 This gives you the web app without Docker complexity!"
EOF

chmod +x native_install.sh

print_success "Alternative solutions created"

echo ""

# 9. Recommendations
print_status "9. Recommendations:"
echo ""
if [ -f "use_working_options.sh" ]; then
    echo "🎯 IMMEDIATE SOLUTION:"
    echo "   ./use_working_options.sh"
    echo ""
fi

echo "🔧 DOCKER COMPOSE ALTERNATIVES:"
echo "   ./manual_docker.sh    # Manual Docker commands"
echo "   ./native_install.sh   # Native installation"
echo ""

echo "📋 NEXT STEPS:"
echo "1. Use working Options 1-3 (recommended)"
echo "2. Or use manual Docker commands"
echo "3. Or install natively"
echo "4. Docker Compose is not essential for REDLINE functionality"
echo ""

print_success "Diagnosis complete!"
