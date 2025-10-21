#!/bin/bash
set -e

# REDLINE Docker Installation Script
# Creates a Docker image with Ubuntu:latest and conda environment

echo "🐳 REDLINE Docker Installation Script"
echo "====================================="

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
IMAGE_NAME="redline-ubuntu-conda"
CONTAINER_NAME="redline-container"
CONDA_ENV_NAME="redline"

print_status "Creating Dockerfile for REDLINE with conda..."

# Create Dockerfile
cat > Dockerfile.redline << 'EOF'
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    tk \
    libtk8.6 \
    libtk8.6-dev \
    tcl8.6 \
    tcl8.6-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy

# Initialize conda
RUN $CONDA_DIR/bin/conda init bash

# Set working directory
WORKDIR /app

# Copy REDLINE files
COPY . /app/

# Create conda environment and install packages
RUN $CONDA_DIR/bin/conda create -n $CONDA_ENV_NAME python=3.11 -y && \
    $CONDA_DIR/bin/conda activate $CONDA_ENV_NAME && \
    $CONDA_DIR/bin/conda install -n $CONDA_ENV_NAME -c conda-forge \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scipy \
    scikit-learn \
    flask \
    requests \
    pyarrow \
    duckdb \
    -y

# Install remaining packages via pip in conda environment
RUN $CONDA_DIR/bin/conda run -n $CONDA_ENV_NAME pip install \
    yfinance \
    polars \
    flask-socketio \
    flask-compress \
    gunicorn \
    celery \
    redis \
    openpyxl \
    xlsxwriter \
    psutil \
    pytest \
    black \
    flake8 \
    configparser

# Create startup scripts
RUN echo '#!/bin/bash' > /app/start_gui.sh && \
    echo 'source /opt/conda/bin/activate redline' >> /app/start_gui.sh && \
    echo 'cd /app' >> /app/start_gui.sh && \
    echo 'python main.py' >> /app/start_gui.sh && \
    chmod +x /app/start_gui.sh

RUN echo '#!/bin/bash' > /app/start_web.sh && \
    echo 'source /opt/conda/bin/activate redline' >> /app/start_web.sh && \
    echo 'cd /app' >> /app/start_web.sh && \
    echo 'python web_app.py' >> /app/start_web.sh && \
    chmod +x /app/start_web.sh

# Create conda environment activation script
RUN echo '#!/bin/bash' > /app/activate_env.sh && \
    echo 'source /opt/conda/bin/activate redline' >> /app/activate_env.sh && \
    echo 'echo "REDLINE conda environment activated!"' >> /app/activate_env.sh && \
    chmod +x /app/activate_env.sh

# Expose ports
EXPOSE 5000

# Default command
CMD ["/bin/bash"]
EOF

print_success "Dockerfile created: Dockerfile.redline"

print_status "Building Docker image..."

# Build Docker image
docker build -f Dockerfile.redline -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully: $IMAGE_NAME"
else
    print_error "Docker image build failed"
    exit 1
fi

print_status "Creating startup script..."

# Create container startup script
cat > start_redline_container.sh << EOF
#!/bin/bash
echo "🚀 Starting REDLINE Container"
echo "============================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container $CONTAINER_NAME already exists. Removing..."
    docker rm -f $CONTAINER_NAME
fi

# Start container with port mapping
docker run -it --name $CONTAINER_NAME \\
    -p 5000:5000 \\
    -v \$(pwd):/app/host \\
    $IMAGE_NAME \\
    /bin/bash

echo "Container started! Access it with: docker exec -it $CONTAINER_NAME bash"
EOF

chmod +x start_redline_container.sh

print_status "Creating test script..."

# Create test script
cat > test_redline_docker.sh << EOF
#!/bin/bash
echo "🧪 Testing REDLINE Docker Installation"
echo "====================================="

# Test if image exists
if docker images | grep -q $IMAGE_NAME; then
    echo "✅ Docker image exists: $IMAGE_NAME"
else
    echo "❌ Docker image not found: $IMAGE_NAME"
    exit 1
fi

# Test conda environment
echo "Testing conda environment..."
docker run --rm $IMAGE_NAME /bin/bash -c "
    source /opt/conda/bin/activate redline && \\
    python -c 'import pandas; print(\"✅ Pandas version:\", pandas.__version__)' && \\
    python -c 'import numpy; print(\"✅ NumPy version:\", numpy.__version__)' && \\
    python -c 'import flask; print(\"✅ Flask version:\", flask.__version__)' && \\
    python -c 'import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)' && \\
    python -c 'from redline.core.data_loader import DataLoader; print(\"✅ REDLINE modules working\")' && \\
    echo '✅ All tests passed!'
"

echo "Test complete!"
EOF

chmod +x test_redline_docker.sh

print_status "Creating usage instructions..."

# Create usage instructions
cat > DOCKER_USAGE.md << EOF
# REDLINE Docker Usage Guide

## Quick Start

### 1. Start Container
\`\`\`bash
./start_redline_container.sh
\`\`\`

### 2. Access Container
\`\`\`bash
docker exec -it $CONTAINER_NAME bash
\`\`\`

### 3. Activate Environment
\`\`\`bash
source /opt/conda/bin/activate redline
\`\`\`

### 4. Run REDLINE
\`\`\`bash
# GUI Application
python main.py

# Web Application
python web_app.py

# Or use startup scripts
./start_gui.sh
./start_web.sh
\`\`\`

## Available Scripts

- \`start_redline_container.sh\` - Start the container
- \`test_redline_docker.sh\` - Test the installation
- \`activate_env.sh\` - Activate conda environment

## Ports

- Web application: http://localhost:5000

## File Access

- Host files are mounted at: /app/host
- Container files are at: /app

## Commands

\`\`\`bash
# Build image
docker build -f Dockerfile.redline -t $IMAGE_NAME .

# Run container
docker run -it --name $CONTAINER_NAME -p 5000:5000 $IMAGE_NAME

# Stop container
docker stop $CONTAINER_NAME

# Remove container
docker rm $CONTAINER_NAME

# Remove image
docker rmi $IMAGE_NAME
\`\`\`
EOF

print_success "Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test the installation: ./test_redline_docker.sh"
echo "2. Start the container: ./start_redline_container.sh"
echo "3. Access container: docker exec -it $CONTAINER_NAME bash"
echo "4. Activate environment: source /opt/conda/bin/activate redline"
echo "5. Run REDLINE: python main.py or python web_app.py"
echo ""
echo "📁 Files created:"
echo "- Dockerfile.redline (Docker configuration)"
echo "- start_redline_container.sh (Container startup)"
echo "- test_redline_docker.sh (Installation test)"
echo "- DOCKER_USAGE.md (Usage instructions)"
echo ""
echo "🐳 Docker image: $IMAGE_NAME"
echo "📦 Container: $CONTAINER_NAME"
echo "🌐 Web app: http://localhost:5000"
