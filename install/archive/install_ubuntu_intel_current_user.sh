#!/bin/bash
set -e

# REDLINE Ubuntu Intel Installation Script (Current User)
# Installs and configures REDLINE for the current user with both Tkinter GUI and Flask Web App using Docker

echo "🚀 REDLINE Ubuntu Intel Installation Script (Current User)"
echo "========================================================="

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

# Configuration variables - use current user
CURRENT_USER="$USER"
REDLINE_HOME="$HOME"
REDLINE_DIR="$REDLINE_HOME/redline"
DOCKER_COMPOSE_VERSION="2.20.0"
PYTHON_VERSION="3.11"

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to check if running on Ubuntu
check_ubuntu() {
    if ! command -v lsb_release &> /dev/null; then
        print_error "lsb_release not found. Please install lsb-release: sudo apt-get install lsb-release"
        exit 1
    fi
    
    local distro=$(lsb_release -si)
    local version=$(lsb_release -sr)
    
    if [[ "$distro" != "Ubuntu" ]]; then
        print_error "This script is designed for Ubuntu. Detected: $distro"
        exit 1
    fi
    
    print_success "Detected Ubuntu $version"
}

# Function to check if running on Intel platform
check_intel() {
    local arch=$(uname -m)
    local cpu_info=$(lscpu | grep "Model name" | head -1)
    
    if [[ "$arch" != "x86_64" ]]; then
        print_error "This script is designed for Intel x86_64 platforms. Detected: $arch"
        exit 1
    fi
    
    if [[ "$cpu_info" == *"Intel"* ]]; then
        print_success "Detected Intel CPU: $cpu_info"
    else
        print_warning "Intel CPU not detected, but proceeding with x86_64 installation"
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    
    sudo apt-get update
    sudo apt-get upgrade -y
    
    print_success "System packages updated"
}

# Function to install essential packages
install_essentials() {
    print_status "Installing essential packages..."
    
    # Install Tkinter with better error handling
    print_status "Installing Tkinter for GUI support..."
    install_tkinter_success=false
    
    # Try different package names for different Ubuntu versions
    for package in "python3-tk" "python3-tkinter" "python3-tk-dev"; do
        if sudo apt-get install -y "$package" 2>/dev/null; then
            print_success "Tkinter installed via $package"
            install_tkinter_success=true
            break
        fi
    done
    
    # If system packages failed, note that pip will handle it later
    if [ "$install_tkinter_success" = false ]; then
        print_warning "System Tkinter packages not available"
        print_status "Tkinter will be installed via pip in virtual environment"
    fi
    
    # Install other essential packages
    sudo apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        jq \
        build-essential \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        x11-utils \
        xauth \
        xvfb \
        x11vnc \
        fluxbox \
        procps \
        htop \
        nano \
        vim \
        libx11-dev \
        libxext-dev \
        libxrender-dev \
        libxtst-dev \
        libxi-dev
    
    print_success "Essential packages installed"
}

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Remove old Docker versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index
    sudo apt-get update
    
    # Install Docker Engine
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $CURRENT_USER
    
    # Enable Docker to start on boot
    sudo systemctl enable docker
    sudo systemctl start docker
    
    print_success "Docker installed successfully"
}

# Function to install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    # Install Docker Compose standalone
    local compose_version=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)
    sudo curl -L "https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
}

# Function to clone REDLINE repository
clone_redline() {
    print_status "Setting up REDLINE directory..."
    
    if [ -d "$REDLINE_DIR" ]; then
        print_warning "REDLINE directory already exists."
        
        # Check if it's a git repository
        if git rev-parse --git-dir > /dev/null 2>&1; then
            print_status "This is a git repository, updating..."
            cd "$REDLINE_DIR"
            git pull
        else
            print_warning "Not a git repository, using existing files..."
            print_status "Skipping git operations"
        fi
    else
        print_status "Cloning REDLINE repository..."
        git clone https://github.com/redline/redline.git "$REDLINE_DIR"
    fi
    
    print_success "REDLINE directory setup complete"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    cd "$REDLINE_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install packages
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install Tkinter via pip if system packages weren't available
    print_status "Installing Tkinter via pip..."
    pip install tk || {
        print_warning "Failed to install Tkinter via pip, but continuing..."
    }
    
    # Install requirements
    pip install -r requirements.txt
    pip install -r requirements_ubuntu.txt 2>/dev/null || {
        print_warning "requirements_ubuntu.txt not found, skipping Ubuntu-specific packages"
    }
    
    print_success "Python environment setup complete"
}

# Function to create data directories
create_data_directories() {
    print_status "Creating data directories..."
    
    mkdir -p "$REDLINE_DIR/data"
    mkdir -p "$REDLINE_DIR/data/downloaded"
    mkdir -p "$REDLINE_DIR/data/converted"
    mkdir -p "$REDLINE_DIR/data/stooq_format"
    mkdir -p "$REDLINE_DIR/logs"
    
    print_success "Data directories created"
}

# Function to setup Docker images
setup_docker_images() {
    print_status "Setting up Docker images..."
    
    cd "$REDLINE_DIR"
    
    # Build Docker images
    docker build --platform linux/amd64 -f Dockerfile.x86 -t redline:x86 .
    docker build --platform linux/amd64 -f Dockerfile.web -t redline-web:x86 .
    
    print_success "Docker images built successfully"
}

# Function to create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Tkinter GUI startup script
    tee "$REDLINE_DIR/start_gui.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Tkinter GUI..."

# Check if X server is running
if ! xset q &>/dev/null; then
    echo "❌ X server not running. Please start X server first."
    exit 1
fi

# Start the GUI
source venv/bin/activate
python3 main.py --task=gui
EOF

    # Flask Web App startup script
    tee "$REDLINE_DIR/start_web.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Flask Web App..."

# Start the web app
source venv/bin/activate
export WEB_PORT=${WEB_PORT:-8080}
export FLASK_APP=web_app.py
export FLASK_ENV=production
python3 web_app.py
EOF

    # Docker startup script
    tee "$REDLINE_DIR/start_docker.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Docker Services..."

# Start Docker services
docker-compose --profile x86 up -d

echo "✅ REDLINE Docker services started"
echo "🌐 Web interface: http://localhost:8080"
echo "📊 VNC access: localhost:5900 (password: redline123)"
EOF

    # Stop script
    tee "$REDLINE_DIR/stop_docker.sh" > /dev/null <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🛑 Stopping REDLINE Docker Services..."

# Stop Docker services
docker-compose down

echo "✅ REDLINE Docker services stopped"
EOF

    # Make scripts executable
    chmod +x "$REDLINE_DIR"/*.sh
    
    print_success "Startup scripts created"
}

# Function to create desktop shortcuts
create_desktop_shortcuts() {
    print_status "Creating desktop shortcuts..."
    
    # Create Desktop directory if it doesn't exist
    mkdir -p "$REDLINE_HOME/Desktop"
    
    # Tkinter GUI shortcut
    tee "$REDLINE_HOME/Desktop/REDLINE-GUI.desktop" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE GUI
Comment=REDLINE Data Analyzer - Tkinter GUI
Exec=$REDLINE_DIR/start_gui.sh
Icon=applications-science
Terminal=true
Categories=Science;DataAnalysis;
EOF

    # Flask Web App shortcut
    tee "$REDLINE_HOME/Desktop/REDLINE-Web.desktop" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Web
Comment=REDLINE Data Analyzer - Web Interface
Exec=$REDLINE_DIR/start_web.sh
Icon=applications-internet
Terminal=true
Categories=Science;DataAnalysis;Network;
EOF

    # Docker shortcut
    tee "$REDLINE_HOME/Desktop/REDLINE-Docker.desktop" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=REDLINE Docker
Comment=REDLINE Data Analyzer - Docker Services
Exec=$REDLINE_DIR/start_docker.sh
Icon=docker
Terminal=true
Categories=Science;DataAnalysis;Development;
EOF

    # Make shortcuts executable
    chmod +x "$REDLINE_HOME/Desktop"/*.desktop
    
    print_success "Desktop shortcuts created"
}

# Function to create configuration files
create_config_files() {
    print_status "Creating configuration files..."
    
    # Docker environment file
    tee "$REDLINE_DIR/docker.env" > /dev/null <<EOF
# REDLINE Docker Environment Configuration
TARGET_PLATFORM=linux/amd64
BUILD_MODE=auto
WEB_PORT=8080
VNC_PORT=5900
VNC_PASSWORD=redline123
DISPLAY=:0
DATA_DIR=./data
LOGS_DIR=./logs
ENABLE_HEALTH_CHECKS=true
LOG_LEVEL=INFO
EOF

    # Application configuration
    tee "$REDLINE_DIR/redline.conf" > /dev/null <<EOF
# REDLINE Application Configuration
[DEFAULT]
data_dir = ./data
logs_dir = ./logs
web_port = 8080
vnc_port = 5900
vnc_password = redline123

[GUI]
display = :0
theme = default
font_size = 10

[WEB]
host = 0.0.0.0
port = 8080
debug = false
workers = 4

[DOCKER]
platform = linux/amd64
profile = x86
auto_start = false
EOF

    print_success "Configuration files created"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Check if ufw is available
    if command -v ufw &> /dev/null; then
        # Allow web interface
        sudo ufw allow 8080/tcp comment "REDLINE Web Interface"
        
        # Allow VNC
        sudo ufw allow 5900/tcp comment "REDLINE VNC"
        
        print_success "Firewall configured"
    else
        print_warning "UFW not available, skipping firewall configuration"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running installation tests..."
    
    cd "$REDLINE_DIR"
    
    # Test Docker
    if docker --version &>/dev/null; then
        print_success "Docker test passed"
    else
        print_error "Docker test failed"
        return 1
    fi
    
    # Test Docker Compose
    if docker-compose --version &>/dev/null; then
        print_success "Docker Compose test passed"
    else
        print_error "Docker Compose test failed"
        return 1
    fi
    
    # Test Python environment
    if source venv/bin/activate && python3 --version &>/dev/null; then
        print_success "Python environment test passed"
    else
        print_error "Python environment test failed"
        return 1
    fi
    
    # Test Tkinter installation
    print_status "Testing Tkinter installation..."
    if source venv/bin/activate && python3 -c 'import tkinter; print("Tkinter version:", tkinter.TkVersion)' &>/dev/null; then
        print_success "Tkinter test passed"
    else
        print_warning "Tkinter test failed - GUI may not work properly"
        print_status "This is common on headless servers. Web interface will still work."
    fi
    
    print_success "All tests passed"
}

# Function to show installation summary
show_summary() {
    print_success "REDLINE installation completed successfully!"
    echo ""
    echo "📋 Installation Summary:"
    echo "========================"
    echo "• User: $CURRENT_USER"
    echo "• Installation directory: $REDLINE_DIR"
    echo "• Docker: $(docker --version)"
    echo "• Docker Compose: $(docker-compose --version)"
    echo "• Python: $(python3 --version)"
    echo ""
    echo "🚀 How to start REDLINE:"
    echo "========================"
    echo ""
    echo "1. Tkinter GUI (requires X server):"
    echo "   cd $REDLINE_DIR && ./start_gui.sh"
    echo ""
    echo "2. Flask Web App:"
    echo "   cd $REDLINE_DIR && ./start_web.sh"
    echo "   # Then open: http://localhost:8080"
    echo ""
    echo "3. Docker Services:"
    echo "   cd $REDLINE_DIR && ./start_docker.sh"
    echo "   # Then open: http://localhost:8080"
    echo ""
    echo "🛑 How to stop REDLINE:"
    echo "======================"
    echo "cd $REDLINE_DIR && ./stop_docker.sh"
    echo ""
    echo "📊 Access Information:"
    echo "====================="
    echo "• Web Interface: http://localhost:8080"
    echo "• VNC Access: localhost:5900 (password: redline123)"
    echo "• Logs: $REDLINE_DIR/logs/"
    echo "• Data: $REDLINE_DIR/data/"
    echo ""
    echo "🔧 Configuration:"
    echo "================="
    echo "• Docker config: $REDLINE_DIR/docker.env"
    echo "• App config: $REDLINE_DIR/redline.conf"
    echo "• Desktop shortcuts: $REDLINE_HOME/Desktop/"
    echo ""
    echo "📚 Documentation:"
    echo "================="
    echo "• Docker guide: $REDLINE_DIR/DOCKER_MULTI_PLATFORM_GUIDE.md"
    echo "• User guide: $REDLINE_DIR/REDLINE_USER_GUIDE.md"
    echo ""
    echo "⚠️  Important Notes:"
    echo "==================="
    echo "• You may need to log out and log back in for Docker group changes to take effect"
    echo "• For GUI access, ensure X server is running"
    echo "• Check firewall settings if you can't access the web interface"
    echo "• All files are installed in your home directory: $REDLINE_DIR"
}

# Main installation function
main() {
    print_status "Starting REDLINE installation for current user ($CURRENT_USER)..."
    
    # Pre-installation checks
    check_root
    check_ubuntu
    check_intel
    
    # Installation steps
    update_system
    install_essentials
    install_docker
    install_docker_compose
    clone_redline
    setup_python_env
    create_data_directories
    setup_docker_images
    create_startup_scripts
    create_desktop_shortcuts
    create_config_files
    setup_firewall
    run_tests
    
    # Show summary
    show_summary
    
    print_success "Installation completed successfully!"
}

# Run main function
main "$@"
