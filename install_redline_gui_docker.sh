#!/bin/bash
set -e

# REDLINE Tkinter GUI Docker Installation Script
# Creates a Docker image optimized for GUI applications

echo "🖥️  REDLINE Tkinter GUI Docker Installation Script"
echo "================================================="

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

print_status "Creating Dockerfile for REDLINE Tkinter GUI..."

# Create Dockerfile for GUI
cat > Dockerfile.gui << 'EOF'
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV DISPLAY=:0

# Install system dependencies for GUI
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    # Tkinter GUI dependencies
    tk \
    libtk8.6 \
    libtk8.6-dev \
    tcl8.6 \
    tcl8.6-dev \
    # X11 forwarding for GUI
    x11-apps \
    xauth \
    xvfb \
    # Additional GUI libraries
    libx11-6 \
    libx11-dev \
    libxext6 \
    libxext-dev \
    libxrender1 \
    libxrender-dev \
    libxtst6 \
    libxtst-dev \
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

# Create conda environment optimized for GUI
RUN $CONDA_DIR/bin/conda create -n $CONDA_ENV_NAME python=3.11 -y && \
    $CONDA_DIR/bin/conda activate $CONDA_ENV_NAME && \
    $CONDA_DIR/bin/conda install -n $CONDA_ENV_NAME -c conda-forge \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scipy \
    scikit-learn \
    requests \
    pyarrow \
    duckdb \
    pillow \
    -y

# Install GUI-specific packages via pip
RUN $CONDA_DIR/bin/conda run -n $CONDA_ENV_NAME pip install \
    yfinance \
    polars \
    openpyxl \
    xlsxwriter \
    psutil \
    configparser

# Create GUI startup script
RUN echo '#!/bin/bash' > /app/start_gui.sh && \
    echo 'source /opt/conda/bin/activate redline-gui' >> /app/start_gui.sh && \
    echo 'cd /app' >> /app/start_gui.sh && \
    echo 'export DISPLAY=${DISPLAY:-:0}' >> /app/start_gui.sh && \
    echo 'python main.py' >> /app/start_gui.sh && \
    chmod +x /app/start_gui.sh

# Create GUI test script
RUN echo '#!/bin/bash' > /app/test_gui.sh && \
    echo 'source /opt/conda/bin/activate redline-gui' >> /app/test_gui.sh && \
    echo 'cd /app' >> /app/test_gui.sh && \
    echo 'export DISPLAY=${DISPLAY:-:0}' >> /app/test_gui.sh && \
    echo 'python -c "import tkinter; print(\"Tkinter version:\", tkinter.TkVersion)"' >> /app/test_gui.sh && \
    echo 'python -c "from redline.gui.main_window import StockAnalyzerGUI; print(\"GUI module imported successfully\")"' >> /app/test_gui.sh && \
    chmod +x /app/test_gui.sh

# Default command
CMD ["/bin/bash"]
EOF

print_success "Dockerfile created: Dockerfile.gui"

print_status "Building GUI Docker image..."

# Build Docker image
docker build -f Dockerfile.gui -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    print_success "GUI Docker image built successfully: $IMAGE_NAME"
else
    print_error "GUI Docker image build failed"
    exit 1
fi

print_status "Creating GUI startup script..."

# Create GUI container startup script
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

print_status "Creating GUI test script..."

# Create GUI test script
cat > test_gui_docker.sh << EOF
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

chmod +x test_gui_docker.sh

print_status "Creating GUI usage instructions..."

# Create GUI usage instructions
cat > GUI_DOCKER_USAGE.md << EOF
# REDLINE GUI Docker Usage Guide

## Quick Start

### 1. Enable X11 Forwarding (for GUI)
\`\`\`bash
# Allow Docker to access X11
xhost +local:docker

# Set display (if not already set)
export DISPLAY=\$DISPLAY
\`\`\`

### 2. Start GUI Container
\`\`\`bash
./start_gui_container.sh
\`\`\`

### 3. Access Container
\`\`\`bash
docker exec -it $CONTAINER_NAME bash
\`\`\`

### 4. Run GUI Application
\`\`\`bash
# Activate environment
source /opt/conda/bin/activate redline-gui

# Run GUI
python main.py

# Or use startup script
./start_gui.sh
\`\`\`

## GUI Features

- **Tkinter-based interface**
- **Data visualization with matplotlib**
- **Interactive charts and graphs**
- **File loading and processing**
- **Real-time data analysis**

## Troubleshooting GUI Issues

### X11 Forwarding Issues
\`\`\`bash
# Check if X11 is working
docker run --rm -e DISPLAY=\$DISPLAY $IMAGE_NAME xeyes

# If GUI doesn't appear, try:
xhost +local:docker
export DISPLAY=\$DISPLAY
\`\`\`

### Display Issues
\`\`\`bash
# Check display
echo \$DISPLAY

# Test tkinter
docker run --rm -e DISPLAY=\$DISPLAY $IMAGE_NAME python -c "import tkinter; tkinter.Tk().mainloop()"
\`\`\`

## Commands

\`\`\`bash
# Build GUI image
docker build -f Dockerfile.gui -t $IMAGE_NAME .

# Run GUI container
docker run -it --name $CONTAINER_NAME -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw $IMAGE_NAME

# Test GUI
./test_gui_docker.sh
\`\`\`
EOF

print_success "GUI Docker installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Enable X11 forwarding: xhost +local:docker"
echo "2. Test GUI installation: ./test_gui_docker.sh"
echo "3. Start GUI container: ./start_gui_container.sh"
echo "4. Run GUI: docker exec -it $CONTAINER_NAME ./start_gui.sh"
echo ""
echo "📁 Files created:"
echo "- Dockerfile.gui (GUI-optimized Docker configuration)"
echo "- start_gui_container.sh (GUI container startup)"
echo "- test_gui_docker.sh (GUI installation test)"
echo "- GUI_DOCKER_USAGE.md (GUI usage instructions)"
echo ""
echo "🖥️  GUI Docker image: $IMAGE_NAME"
echo "📦 GUI Container: $CONTAINER_NAME"
echo "🎨 Optimized for Tkinter GUI applications"
