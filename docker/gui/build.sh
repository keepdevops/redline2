#!/bin/bash
set -e

# REDLINE GUI Docker Build and Run Script
# Universal platform support with multi-architecture builds

echo "🖥️  REDLINE GUI Docker Build Script"
echo "==================================="

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
IMAGE_NAME="redline-gui"
CONTAINER_NAME="redline-gui-container"
CONDA_ENV_NAME="redline-gui"
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
    print_status "Building GUI Docker image..."
    
    # Navigate to GUI directory
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
        print_success "GUI Docker image built successfully: $IMAGE_NAME"
    else
        print_error "GUI Docker image build failed"
        exit 1
    fi
}

# Create startup script
create_startup_script() {
    print_status "Creating GUI startup script..."
    
    cat > start_gui_container.sh << EOF
#!/bin/bash
echo "🖥️  Starting REDLINE GUI Container"
echo "================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container $CONTAINER_NAME already exists. Removing..."
    docker rm -f $CONTAINER_NAME
fi

# Check if X11 forwarding is available
if [ -z "\$DISPLAY" ]; then
    echo "⚠️  Warning: DISPLAY not set. GUI may not work."
    echo "For GUI support, run with X11 forwarding:"
    echo "xhost +local:docker"
    echo "export DISPLAY=\$DISPLAY"
fi

# Start container with X11 forwarding
docker run -it --name $CONTAINER_NAME \\
    -e DISPLAY=\$DISPLAY \\
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
    -v \$(pwd):/app/host \\
    --net=host \\
    $IMAGE_NAME \\
    /bin/bash

echo "GUI Container started! Access it with: docker exec -it $CONTAINER_NAME bash"
echo "To run GUI: docker exec -it $CONTAINER_NAME ./start_gui.sh"
EOF

    chmod +x start_gui_container.sh
    print_success "GUI startup script created: start_gui_container.sh"
}

# Create test script
create_test_script() {
    print_status "Creating GUI test script..."
    
    cat > test_gui.sh << EOF
#!/bin/bash
echo "🧪 Testing REDLINE GUI Docker Installation"
echo "=========================================="

# Test if image exists
if docker images | grep -q $IMAGE_NAME; then
    echo "✅ Docker image exists: $IMAGE_NAME"
else
    echo "❌ Docker image not found: $IMAGE_NAME"
    exit 1
fi

# Test GUI components
echo "Testing GUI components..."
docker run --rm -e DISPLAY=\$DISPLAY $IMAGE_NAME /bin/bash -c "
    source /opt/conda/bin/activate redline-gui && \\
    python -c 'import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)' && \\
    python -c 'import pandas; print(\"✅ Pandas version:\", pandas.__version__)' && \\
    python -c 'import matplotlib; print(\"✅ Matplotlib version:\", matplotlib.__version__)' && \\
    python -c 'from redline.gui.main_window import StockAnalyzerGUI; print(\"✅ REDLINE GUI modules working\")' && \\
    echo '✅ All GUI tests passed!'
"

echo "GUI test complete!"
EOF

    chmod +x test_gui.sh
    print_success "GUI test script created: test_gui.sh"
}

# Create usage instructions
create_usage_instructions() {
    cat > README.md << EOF
# REDLINE GUI Docker Usage Guide

## Quick Start

### 1. Build GUI Image
\`\`\`bash
./build.sh
\`\`\`

### 2. Enable X11 Forwarding (for GUI)
\`\`\`bash
# Allow Docker to access X11
xhost +local:docker

# Set display (if not already set)
export DISPLAY=\$DISPLAY
\`\`\`

### 3. Start GUI Container
\`\`\`bash
./start_gui_container.sh
\`\`\`

### 4. Test Installation
\`\`\`bash
./test_gui.sh
\`\`\`

### 5. Run GUI Application
\`\`\`bash
# Access container
docker exec -it $CONTAINER_NAME bash

# Activate environment
source /opt/conda/bin/activate redline-gui

# Run GUI
python main.py

# Or use startup script
./start_gui.sh
\`\`\`

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## GUI Features

- **Tkinter-based interface**
- **Data visualization with matplotlib**
- **Interactive charts and graphs**
- **File loading and processing**
- **Real-time data analysis**

## Troubleshooting

### X11 Forwarding Issues
\`\`\`bash
# Check if X11 is working
docker run --rm -e DISPLAY=\$DISPLAY $IMAGE_NAME xeyes

# If GUI doesn't appear, try:
xhost +local:docker
export DISPLAY=\$DISPLAY
\`\`\`

### Platform Issues
\`\`\`bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag $IMAGE_NAME --load .
\`\`\`

## Commands

\`\`\`bash
# Build image
./build.sh

# Start container
./start_gui_container.sh

# Test installation
./test_gui.sh

# Remove container
docker rm -f $CONTAINER_NAME

# Remove image
docker rmi $IMAGE_NAME
\`\`\`
EOF

    print_success "Usage instructions created: README.md"
}

# Main function
main() {
    print_status "Starting REDLINE GUI Docker setup..."
    echo ""
    
    detect_platform
    check_docker
    build_image
    create_startup_script
    create_test_script
    create_usage_instructions
    
    print_success "REDLINE GUI Docker setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Enable X11 forwarding: xhost +local:docker"
    echo "2. Test GUI installation: ./test_gui.sh"
    echo "3. Start GUI container: ./start_gui_container.sh"
    echo "4. Run GUI: docker exec -it $CONTAINER_NAME ./start_gui.sh"
    echo ""
    echo "📁 Files created:"
    echo "- Dockerfile (GUI-optimized Docker configuration)"
    echo "- start_gui_container.sh (GUI container startup)"
    echo "- test_gui.sh (GUI installation test)"
    echo "- README.md (Usage instructions)"
    echo ""
    echo "🖥️  GUI Docker image: $IMAGE_NAME"
    echo "📦 GUI Container: $CONTAINER_NAME"
    echo "🎨 Platform: $PLATFORM"
    echo "🎨 Optimized for Tkinter GUI applications"
}

# Run main function
main "$@"
