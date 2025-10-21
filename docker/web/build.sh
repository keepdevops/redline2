#!/bin/bash
set -e

# REDLINE Web App Docker Build and Run Script
# Universal platform support with multi-architecture builds
# NO SUDO REQUIRED - Docker handles all system operations

echo "🌐 REDLINE Web App Docker Build Script"
echo "======================================"
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
IMAGE_NAME="redline-web"
CONTAINER_NAME="redline-web-container"
CONDA_ENV_NAME="redline-web"
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
    print_status "Building Web App Docker image..."
    
    # Navigate to web directory
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
        print_success "Web App Docker image built successfully: $IMAGE_NAME"
    else
        print_error "Web App Docker image build failed"
        exit 1
    fi
}

# Create startup script
create_startup_script() {
    print_status "Creating Web App startup script..."
    
    cat > start_web_container.sh << EOF
#!/bin/bash
echo "🌐 Starting REDLINE Web App Container"
echo "====================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container $CONTAINER_NAME already exists. Removing..."
    docker rm -f $CONTAINER_NAME
fi

# Start container with port mapping
docker run -it --name $CONTAINER_NAME \\
    -p 5000:5000 \\
    -p 80:80 \\
    -v \$(pwd):/app/host \\
    $IMAGE_NAME \\
    /bin/bash

echo "Web App Container started!"
echo "Access the web app at: http://localhost:5000"
echo "Access via nginx at: http://localhost:80"
echo "Container access: docker exec -it $CONTAINER_NAME bash"
EOF

    chmod +x start_web_container.sh
    print_success "Web App startup script created: start_web_container.sh"
}

# Create test script
create_test_script() {
    print_status "Creating Web App test script..."
    
    cat > test_web.sh << EOF
#!/bin/bash
echo "🧪 Testing REDLINE Web App Docker Installation"
echo "=============================================="

# Test if image exists
if docker images | grep -q $IMAGE_NAME; then
    echo "✅ Docker image exists: $IMAGE_NAME"
else
    echo "❌ Docker image not found: $IMAGE_NAME"
    exit 1
fi

# Test web app components
echo "Testing web app components..."
docker run --rm $IMAGE_NAME /bin/bash -c "
    source /opt/conda/bin/activate redline-web && \\
    python -c 'import flask; print(\"✅ Flask version:\", flask.__version__)' && \\
    python -c 'import flask_socketio; print(\"✅ Flask-SocketIO version:\", flask_socketio.__version__)' && \\
    python -c 'import gunicorn; print(\"✅ Gunicorn version:\", gunicorn.__version__)' && \\
    python -c 'from redline.web import create_app; app = create_app(); print(\"✅ REDLINE web app created successfully\")' && \\
    python -c 'from redline.core.data_loader import DataLoader; print(\"✅ REDLINE core modules working\")' && \\
    echo '✅ All web app tests passed!'
"

echo "Web app test complete!"
EOF

    chmod +x test_web.sh
    print_success "Web App test script created: test_web.sh"
}

# Create usage instructions
create_usage_instructions() {
    cat > README.md << EOF
# REDLINE Web App Docker Usage Guide

## Quick Start

### 1. Build Web App Image
\`\`\`bash
./build.sh
\`\`\`

### 2. Start Web App Container
\`\`\`bash
./start_web_container.sh
\`\`\`

### 3. Test Installation
\`\`\`bash
./test_web.sh
\`\`\`

### 4. Access Web Application
- **Direct Flask**: http://localhost:5000
- **Via Nginx**: http://localhost:80

### 5. Run Web App
\`\`\`bash
# Access container
docker exec -it $CONTAINER_NAME bash

# Activate environment
source /opt/conda/bin/activate redline-web

# Development mode
./start_web.sh

# Production mode (with Gunicorn)
./start_production.sh
\`\`\`

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## Web App Features

- **Flask-based web interface**
- **Real-time data processing**
- **Interactive charts and visualizations**
- **File upload and processing**
- **REST API endpoints**
- **WebSocket support for real-time updates**
- **Production-ready with Gunicorn**
- **Nginx reverse proxy**

## Production Deployment

### Using Gunicorn
\`\`\`bash
# Start production server
./start_production.sh

# Or manually
source /opt/conda/bin/activate redline-web
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent web_app:app
\`\`\`

### Using Nginx (Reverse Proxy)
\`\`\`bash
# Nginx is pre-configured and running
# Access via: http://localhost:80
\`\`\`

## API Endpoints

- **GET /**: Main dashboard
- **POST /upload**: File upload
- **GET /data**: Data processing
- **GET /charts**: Chart generation
- **WebSocket /socket.io**: Real-time updates

## Environment Variables

\`\`\`bash
export FLASK_APP=web_app.py
export FLASK_ENV=production
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
\`\`\`

## Commands

\`\`\`bash
# Build image
./build.sh

# Start container
./start_web_container.sh

# Test web app
./test_web.sh

# Remove container
docker rm -f $CONTAINER_NAME

# Remove image
docker rmi $IMAGE_NAME
\`\`\`

## Troubleshooting

### Port Issues
\`\`\`bash
# Check if ports are available
netstat -tlnp | grep :5000
netstat -tlnp | grep :80
\`\`\`

### Web App Not Loading
\`\`\`bash
# Check container status
docker ps

# Check logs
docker logs $CONTAINER_NAME

# Test web app directly
docker exec -it $CONTAINER_NAME ./test_web.sh
\`\`\`

### Platform Issues
\`\`\`bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag $IMAGE_NAME --load .
\`\`\`
EOF

    print_success "Usage instructions created: README.md"
}

# Main function
main() {
    print_status "Starting REDLINE Web App Docker setup..."
    echo ""
    
    detect_platform
    check_docker
    build_image
    create_startup_script
    create_test_script
    create_usage_instructions
    
    print_success "REDLINE Web App Docker setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test web app installation: ./test_web.sh"
    echo "2. Start web app container: ./start_web_container.sh"
    echo "3. Access web app: http://localhost:5000"
    echo "4. Access via nginx: http://localhost:80"
    echo ""
    echo "📁 Files created:"
    echo "- Dockerfile (Web app-optimized Docker configuration)"
    echo "- start_web_container.sh (Web app container startup)"
    echo "- test_web.sh (Web app installation test)"
    echo "- README.md (Usage instructions)"
    echo ""
    echo "🌐 Web App Docker image: $IMAGE_NAME"
    echo "📦 Web App Container: $CONTAINER_NAME"
    echo "🚀 Platform: $PLATFORM"
    echo "🚀 Optimized for Flask web applications with production features"
    echo ""
    echo "🔐 Sudo Requirements:"
    echo "✅ NO SUDO REQUIRED for Docker operations"
    echo "✅ All system operations run inside containers"
    echo "✅ Only Docker group membership needed (one-time setup)"
    echo ""
    echo "🚀 Quick Start:"
    echo "./start_web_container.sh && open http://localhost:5000"
}

# Run main function
main "$@"
