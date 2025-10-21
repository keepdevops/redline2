#!/bin/bash
set -e

# REDLINE Universal Docker Build and Run Script
# Universal platform support with multi-architecture builds
# Supports both GUI and Web App in a single image
# NO SUDO REQUIRED - Docker handles all system operations

echo "🚀 REDLINE Universal Docker Build Script"
echo "========================================"
echo "✅ No sudo privileges required!"
echo "🐳 All operations run inside Docker containers"
echo ""

# Colors for output
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

# Configuration
IMAGE_NAME="redline-universal"
CONTAINER_NAME="redline-universal-container"
CONDA_ENV_NAME="redline-universal"
DOCKERFILE="Dockerfile"

# Detect platform
detect_platform() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            PLATFORM="linux/amd64"
            ;;
        arm64|aarch64)
            PLATFORM="linux/arm64"
            ;;
        armv7l)
            PLATFORM="linux/arm/v7"
            ;;
        *)
            PLATFORM="linux/amd64"
            print_warning "Unknown architecture $arch, defaulting to linux/amd64"
            ;;
    esac
    print_status "Detected platform: $PLATFORM"
}

# Check Docker and buildx support
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        echo ""
        echo "📋 Docker Installation Options (No sudo required):"
        echo "1. Snap (recommended): snap install docker"
        echo "2. Add to docker group: sudo usermod -aG docker \$USER (then logout/login)"
        echo "3. Docker Desktop: Download from https://docker.com"
        exit 1
    fi
    
    # Check if user can run docker without sudo
    if ! docker ps &> /dev/null; then
        print_error "Cannot run Docker commands. User not in docker group."
        echo ""
        echo "🔧 Quick Fix:"
        echo "sudo usermod -aG docker \$USER"
        echo "newgrp docker  # or logout/login"
        echo ""
        echo "Alternative (no sudo): snap install docker"
        exit 1
    fi
    
    # Check if buildx is available
    if docker buildx version &> /dev/null; then
        BUILDX_AVAILABLE=true
        print_status "Docker buildx is available"
    else
        BUILDX_AVAILABLE=false
        print_warning "Docker buildx not available, using standard build"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Universal Docker image..."
    
    # Navigate to universal directory
    cd "$(dirname "$0")"
    
    if [ "$BUILDX_AVAILABLE" = true ]; then
        # Use buildx for multi-platform support
        print_status "Building with Docker buildx for platform: $PLATFORM"
        docker buildx build \
            --platform $PLATFORM \
            --tag $IMAGE_NAME \
            --file $DOCKERFILE \
            --load \
            ../..
    else
        # Standard build
        print_status "Building with standard Docker build"
        docker build -f $DOCKERFILE -t $IMAGE_NAME ../..
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Universal Docker image built successfully: $IMAGE_NAME"
    else
        print_error "Universal Docker image build failed"
        exit 1
    fi
}

# Create GUI startup script
create_gui_startup_script() {
    print_status "Creating GUI startup script..."
    
    cat > start_gui_container.sh << EOF
#!/bin/bash
echo "🖥️  Starting REDLINE GUI Container"
echo "=================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME-gui$"; then
    echo "Container $CONTAINER_NAME-gui already exists. Removing..."
    docker rm -f $CONTAINER_NAME-gui
fi

# Check if X11 forwarding is available
if [ -z "\$DISPLAY" ]; then
    echo "⚠️  Warning: DISPLAY not set. GUI may not work."
    echo "For GUI support, run with X11 forwarding:"
    echo "xhost +local:docker"
    echo "export DISPLAY=\$DISPLAY"
fi

# Start container with X11 forwarding
docker run -it --name $CONTAINER_NAME-gui \\
    -e DISPLAY=\$DISPLAY \\
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
    -v \$(pwd):/app/host \\
    --net=host \\
    $IMAGE_NAME \\
    ./start_gui.sh

echo "GUI Container started! Access it with: docker exec -it $CONTAINER_NAME-gui bash"
EOF

    chmod +x start_gui_container.sh
    print_success "GUI startup script created: start_gui_container.sh"
}

# Create web app startup script
create_web_startup_script() {
    print_status "Creating Web App startup script..."
    
    cat > start_web_container.sh << EOF
#!/bin/bash
echo "🌐 Starting REDLINE Web App Container"
echo "===================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME-web$"; then
    echo "Container $CONTAINER_NAME-web already exists. Removing..."
    docker rm -f $CONTAINER_NAME-web
fi

# Start container with port mapping
docker run -d --name $CONTAINER_NAME-web \\
    -p 5000:5000 \\
    -p 80:80 \\
    -v \$(pwd):/app/host \\
    $IMAGE_NAME \\
    ./start_production.sh

echo "Web App Container started!"
echo "Access the web app at: http://localhost:5000"
echo "Access via nginx at: http://localhost:80"
echo "Container access: docker exec -it $CONTAINER_NAME-web bash"
EOF

    chmod +x start_web_container.sh
    print_success "Web App startup script created: start_web_container.sh"
}

# Create test script
create_test_script() {
    print_status "Creating Universal test script..."
    
    cat > test_universal.sh << EOF
#!/bin/bash
echo "🧪 Testing REDLINE Universal Docker Installation"
echo "================================================"

# Test if image exists
if docker images | grep -q $IMAGE_NAME; then
    echo "✅ Docker image exists: $IMAGE_NAME"
else
    echo "❌ Docker image not found: $IMAGE_NAME"
    exit 1
fi

# Test universal components
echo "Testing universal components..."
docker run --rm $IMAGE_NAME /bin/bash -c "
    source /opt/conda/bin/activate redline-universal && \\
    echo 'Testing GUI components...' && \\
    python -c 'import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)' && \\
    python -c 'from redline.gui.main_window import StockAnalyzerGUI; print(\"✅ GUI module imported successfully\")' && \\
    echo 'Testing Web App components...' && \\
    python -c 'import flask; print(\"✅ Flask version:\", flask.__version__)' && \\
    python -c 'from redline.web import create_app; app = create_app(); print(\"✅ Web app created successfully\")' && \\
    echo 'Testing Core components...' && \\
    python -c 'from redline.core.data_loader import DataLoader; print(\"✅ DataLoader imported successfully\")' && \\
    python -c 'from redline.database.connector import DatabaseConnector; print(\"✅ DatabaseConnector imported successfully\")' && \\
    echo '✅ All universal tests passed!'
"

echo "Universal test complete!"
EOF

    chmod +x test_universal.sh
    print_success "Universal test script created: test_universal.sh"
}

# Create usage instructions
create_usage_instructions() {
    cat > README.md << EOF
# REDLINE Universal Docker Usage Guide

## Overview

This Docker image provides both GUI and Web App capabilities in a single container, optimized for universal platform support.

## Quick Start

### 1. Build Universal Image
\`\`\`bash
./build.sh
\`\`\`

### 2. Test Installation
\`\`\`bash
./test_universal.sh
\`\`\`

### 3. Run GUI Application
\`\`\`bash
# Enable X11 forwarding
xhost +local:docker
export DISPLAY=\$DISPLAY

# Start GUI container
./start_gui_container.sh
\`\`\`

### 4. Run Web Application
\`\`\`bash
# Start Web App container
./start_web_container.sh

# Access web app
# - Direct Flask: http://localhost:5000
# - Via Nginx: http://localhost:80
\`\`\`

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## Features

### GUI Features
- **Tkinter-based interface**
- **Data visualization with matplotlib**
- **Interactive charts and graphs**
- **File loading and processing**
- **Real-time data analysis**

### Web App Features
- **Flask-based web interface**
- **Real-time data processing**
- **Interactive charts and visualizations**
- **File upload and processing**
- **REST API endpoints**
- **WebSocket support for real-time updates**
- **Production-ready with Gunicorn**
- **Nginx reverse proxy**

## Usage Modes

### GUI Mode
\`\`\`bash
# Start GUI container
./start_gui_container.sh

# Or manually
docker run -it --name redline-gui \\
    -e DISPLAY=\$DISPLAY \\
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
    redline-universal \\
    ./start_gui.sh
\`\`\`

### Web App Mode
\`\`\`bash
# Start Web App container
./start_web_container.sh

# Or manually
docker run -d --name redline-web \\
    -p 5000:5000 \\
    -p 80:80 \\
    redline-universal \\
    ./start_production.sh
\`\`\`

### Interactive Mode
\`\`\`bash
# Start interactive container
docker run -it --name redline-interactive \\
    -e DISPLAY=\$DISPLAY \\
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
    -p 5000:5000 \\
    redline-universal \\
    /bin/bash

# Inside container:
source /opt/conda/bin/activate redline-universal
./start_gui.sh    # For GUI
./start_web.sh    # For web app
./start_production.sh  # For production web app
\`\`\`

## Environment Variables

\`\`\`bash
# GUI
export DISPLAY=\$DISPLAY

# Web App
export FLASK_APP=web_app.py
export FLASK_ENV=production
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
\`\`\`

## Commands

\`\`\`bash
# Build image
./build.sh

# Test installation
./test_universal.sh

# Start GUI
./start_gui_container.sh

# Start Web App
./start_web_container.sh

# Remove containers
docker rm -f $CONTAINER_NAME-gui $CONTAINER_NAME-web

# Remove image
docker rmi $IMAGE_NAME
\`\`\`

## Troubleshooting

### X11 Forwarding Issues (GUI)
\`\`\`bash
# Check if X11 is working
docker run --rm -e DISPLAY=\$DISPLAY $IMAGE_NAME xeyes

# If GUI doesn't appear, try:
xhost +local:docker
export DISPLAY=\$DISPLAY
\`\`\`

### Port Issues (Web App)
\`\`\`bash
# Check if ports are available
netstat -tlnp | grep :5000
netstat -tlnp | grep :80
\`\`\`

### Platform Issues
\`\`\`bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag $IMAGE_NAME --load .
\`\`\`

## Advantages

- **Single Image**: Both GUI and Web App in one container
- **Universal Platform**: Supports multiple architectures
- **Conda Environment**: Optimized package management
- **Production Ready**: Includes Gunicorn and Nginx
- **Easy Deployment**: Simple startup scripts
- **Comprehensive Testing**: Built-in test suite
EOF

    print_success "Usage instructions created: README.md"
}

# Main function
main() {
    print_status "Starting REDLINE Universal Docker setup..."
    echo ""
    
    detect_platform
    check_docker
    build_image
    create_gui_startup_script
    create_web_startup_script
    create_test_script
    create_usage_instructions
    
    print_success "REDLINE Universal Docker setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test universal installation: ./test_universal.sh"
    echo "2. Start GUI container: ./start_gui_container.sh"
    echo "3. Start Web App container: ./start_web_container.sh"
    echo "4. Access GUI: X11 forwarding required"
    echo "5. Access Web App: http://localhost:5000 or http://localhost:80"
    echo ""
    echo "📁 Files created:"
    echo "- Dockerfile (Universal Docker configuration)"
    echo "- start_gui_container.sh (GUI container startup)"
    echo "- start_web_container.sh (Web App container startup)"
    echo "- test_universal.sh (Universal installation test)"
    echo "- README.md (Usage instructions)"
    echo ""
    echo "🚀 Universal Docker image: $IMAGE_NAME"
    echo "📦 GUI Container: $CONTAINER_NAME-gui"
    echo "📦 Web App Container: $CONTAINER_NAME-web"
    echo "🌍 Platform: $PLATFORM"
    echo "🎯 Supports both GUI and Web App in a single image"
    echo ""
    echo "🔐 Sudo Requirements:"
    echo "✅ NO SUDO REQUIRED for Docker operations"
    echo "✅ All system operations run inside containers"
    echo "✅ Only Docker group membership needed (one-time setup)"
    echo ""
    echo "🚀 Quick Start:"
    echo "GUI: xhost +local:docker && ./start_gui_container.sh"
    echo "Web: ./start_web_container.sh && open http://localhost:5000"
}

# Run main function
main "$@"
