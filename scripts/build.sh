#!/bin/bash
# REDLINE Web GUI Multi-Platform Docker Build Script
# Supports multiple architectures and Python versions

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="redline-web"
IMAGE_TAG="latest"
CONTAINER_NAME="redline-web-container"
HOST_PORT="8080"
CONTAINER_PORT="8080"
NGINX_PORT="80"

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

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if required files exist
check_files() {
    local required_files=(
        "Dockerfile"
        "requirements.txt"
        "web_app.py"
        "main.py"
        "data_config.ini"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file '$file' not found"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Function to create .dockerignore
create_dockerignore() {
    cat > .dockerignore << EOF
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode
.idea
*.swp
*.swo
*~

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Documentation
README.md
*.md
docs/

# Tests
tests/
test_*

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Logs
*.log
logs/

# Data (optional - comment out if you want to include data)
data/
*.csv
*.json
*.parquet
*.feather
*.duckdb

# Build artifacts
build/
dist/
*.egg-info/
EOF
    print_success "Created .dockerignore file"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Build with BuildKit for better performance
    export DOCKER_BUILDKIT=1
    
    docker build \
        --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
        --tag "${IMAGE_NAME}:ubuntu-24.04-python3.11" \
        --tag "${IMAGE_NAME}:$(date +%Y%m%d)" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --progress=plain \
        .
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to show image details
show_image_info() {
    print_status "Docker image information:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    print_status "Image layers:"
    docker history "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.CreatedBy}}\t{{.Size}}"
}

# Function to test the image
test_image() {
    print_status "Testing Docker image..."
    
    # Run a quick test to ensure the image works
    docker run --rm \
        --name "redline-test-$(date +%s)" \
        "${IMAGE_NAME}:${IMAGE_TAG}" \
        python3.11 -c "import flask; print('Flask version:', flask.__version__)"
    
    if [[ $? -eq 0 ]]; then
        print_success "Image test passed"
    else
        print_error "Image test failed"
        exit 1
    fi
}

# Function to create run script
create_run_script() {
    cat > run-container.sh << 'EOF'
#!/bin/bash
# REDLINE Web GUI Container Run Script

set -euo pipefail

# Configuration
IMAGE_NAME="redline-web"
IMAGE_TAG="latest"
CONTAINER_NAME="redline-web-container"
HOST_PORT="8080"
CONTAINER_PORT="8080"
NGINX_PORT="80"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop existing container if running
if docker ps -q -f name="${CONTAINER_NAME}" | grep -q .; then
    print_status "Stopping existing container..."
    docker stop "${CONTAINER_NAME}"
fi

# Remove existing container if it exists
if docker ps -aq -f name="${CONTAINER_NAME}" | grep -q .; then
    print_status "Removing existing container..."
    docker rm "${CONTAINER_NAME}"
fi

# Create data directory
mkdir -p ./data
mkdir -p ./logs

# Run the container
print_status "Starting REDLINE Web GUI container..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    -p "${NGINX_PORT}:80" \
    -v "$(pwd)/data:/opt/redline/data" \
    -v "$(pwd)/logs:/var/log/redline" \
    -v "$(pwd)/config:/opt/redline/config" \
    -e TZ=UTC \
    -e PYTHONPATH=/opt/redline \
    "${IMAGE_NAME}:${IMAGE_TAG}"

# Wait for container to start
print_status "Waiting for container to start..."
sleep 5

# Check if container is running
if docker ps -q -f name="${CONTAINER_NAME}" | grep -q .; then
    print_success "Container started successfully"
    print_status "Web GUI available at: http://localhost:${HOST_PORT}"
    print_status "Nginx proxy available at: http://localhost:${NGINX_PORT}"
    print_status "Container logs: docker logs ${CONTAINER_NAME}"
    print_status "Container shell: docker exec -it ${CONTAINER_NAME} /bin/bash"
else
    print_error "Failed to start container"
    docker logs "${CONTAINER_NAME}"
    exit 1
fi
EOF
    
    chmod +x run-container.sh
    print_success "Created run-container.sh script"
}

# Function to create stop script
create_stop_script() {
    cat > stop-container.sh << 'EOF'
#!/bin/bash
# REDLINE Web GUI Container Stop Script

set -euo pipefail

# Configuration
CONTAINER_NAME="redline-web-container"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if container exists
if ! docker ps -aq -f name="${CONTAINER_NAME}" | grep -q .; then
    print_error "Container '${CONTAINER_NAME}' not found"
    exit 1
fi

# Stop the container
if docker ps -q -f name="${CONTAINER_NAME}" | grep -q .; then
    print_status "Stopping container..."
    docker stop "${CONTAINER_NAME}"
    print_success "Container stopped"
else
    print_status "Container is already stopped"
fi

# Remove the container
print_status "Removing container..."
docker rm "${CONTAINER_NAME}"
print_success "Container removed"
EOF
    
    chmod +x stop-container.sh
    print_success "Created stop-container.sh script"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -t, --tag TAG       Set Docker image tag (default: latest)"
    echo "  -n, --name NAME     Set image name (default: redline-web)"
    echo "  --no-test           Skip image testing"
    echo "  --no-scripts        Skip creating run/stop scripts"
    echo ""
    echo "Examples:"
    echo "  $0                  # Build with default settings"
    echo "  $0 -t v1.0.0       # Build with specific tag"
    echo "  $0 --no-test       # Build without testing"
}

# Main function
main() {
    local skip_test=false
    local skip_scripts=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -n|--name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            --no-test)
                skip_test=true
                shift
                ;;
            --no-scripts)
                skip_scripts=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_status "Starting REDLINE Web GUI Docker build process..."
    print_status "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Pre-build checks
    check_docker
    check_files
    create_dockerignore
    
    # Build process
    build_image
    show_image_info
    
    # Post-build
    if [[ "$skip_test" == false ]]; then
        test_image
    fi
    
    if [[ "$skip_scripts" == false ]]; then
        create_run_script
        create_stop_script
    fi
    
    print_success "Build process completed successfully!"
    print_status "Next steps:"
    print_status "1. Run container: ./run-container.sh"
    print_status "2. Access web GUI: http://localhost:8080"
    print_status "3. Stop container: ./stop-container.sh"
    print_status "4. View logs: docker logs ${CONTAINER_NAME}"
}

# Run main function
main "$@"
