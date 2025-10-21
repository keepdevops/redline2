#!/bin/bash
set -e

# REDLINE Flask Web App Docker Installation Script
# Creates a Docker image optimized for web applications

echo "🌐 REDLINE Flask Web App Docker Installation Script"
echo "=================================================="

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

print_status "Creating Dockerfile for REDLINE Flask Web App..."

# Create Dockerfile for Web App
cat > Dockerfile.web << 'EOF'
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Install system dependencies for web app
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    nginx \
    supervisor \
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

# Create conda environment optimized for web app
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
    -y

# Install web-specific packages via pip
RUN $CONDA_DIR/bin/conda run -n $CONDA_ENV_NAME pip install \
    flask \
    flask-socketio \
    flask-compress \
    gunicorn \
    celery \
    redis \
    yfinance \
    polars \
    openpyxl \
    xlsxwriter \
    psutil \
    configparser \
    gevent \
    gevent-websocket

# Create web app startup script
RUN echo '#!/bin/bash' > /app/start_web.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/start_web.sh && \
    echo 'cd /app' >> /app/start_web.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_web.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_HOST=0.0.0.0' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_PORT=5000' >> /app/start_web.sh && \
    echo 'python web_app.py' >> /app/start_web.sh && \
    chmod +x /app/start_web.sh

# Create production startup script with Gunicorn
RUN echo '#!/bin/bash' > /app/start_production.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/start_production.sh && \
    echo 'cd /app' >> /app/start_production.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_production.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_production.sh && \
    echo 'gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --worker-connections 1000 web_app:app' >> /app/start_production.sh && \
    chmod +x /app/start_production.sh

# Create web app test script
RUN echo '#!/bin/bash' > /app/test_web.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/test_web.sh && \
    echo 'cd /app' >> /app/test_web.sh && \
    echo 'python -c "import flask; print(\"Flask version:\", flask.__version__)"' >> /app/test_web.sh && \
    echo 'python -c "from redline.web import create_app; app = create_app(); print(\"Web app created successfully\")"' >> /app/test_web.sh && \
    echo 'python -c "from redline.core.data_loader import DataLoader; print(\"DataLoader imported successfully\")"' >> /app/test_web.sh && \
    chmod +x /app/test_web.sh

# Create nginx configuration
RUN echo 'server {' > /etc/nginx/sites-available/redline && \
    echo '    listen 80;' >> /etc/nginx/sites-available/redline && \
    echo '    server_name localhost;' >> /etc/nginx/sites-available/redline && \
    echo '    location / {' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_pass http://127.0.0.1:5000;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header Host \$host;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Real-IP \$remote_addr;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Forwarded-Proto \$scheme;' >> /etc/nginx/sites-available/redline && \
    echo '    }' >> /etc/nginx/sites-available/redline && \
    echo '}' >> /etc/nginx/sites-available/redline

# Enable nginx site
RUN ln -s /etc/nginx/sites-available/redline /etc/nginx/sites-enabled/ && \
    rm /etc/nginx/sites-enabled/default

# Expose ports
EXPOSE 5000 80

# Default command
CMD ["/app/start_production.sh"]
EOF

print_success "Dockerfile created: Dockerfile.web"

print_status "Building Web App Docker image..."

# Build Docker image
docker build -f Dockerfile.web -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    print_success "Web App Docker image built successfully: $IMAGE_NAME"
else
    print_error "Web App Docker image build failed"
    exit 1
fi

print_status "Creating web app startup script..."

# Create web app container startup script
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

print_status "Creating web app test script..."

# Create web app test script
cat > test_web_docker.sh << EOF
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

chmod +x test_web_docker.sh

print_status "Creating web app usage instructions..."

# Create web app usage instructions
cat > WEB_DOCKER_USAGE.md << EOF
# REDLINE Web App Docker Usage Guide

## Quick Start

### 1. Start Web App Container
\`\`\`bash
./start_web_container.sh
\`\`\`

### 2. Access Web Application
- **Direct Flask**: http://localhost:5000
- **Via Nginx**: http://localhost:80

### 3. Access Container
\`\`\`bash
docker exec -it $CONTAINER_NAME bash
\`\`\`

### 4. Run Web App
\`\`\`bash
# Development mode
./start_web.sh

# Production mode (with Gunicorn)
./start_production.sh
\`\`\`

## Web App Features

- **Flask-based web interface**
- **Real-time data processing**
- **Interactive charts and visualizations**
- **File upload and processing**
- **REST API endpoints**
- **WebSocket support for real-time updates**
- **Production-ready with Gunicorn**

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
# Build web app image
docker build -f Dockerfile.web -t $IMAGE_NAME .

# Run web app container
docker run -it --name $CONTAINER_NAME -p 5000:5000 -p 80:80 $IMAGE_NAME

# Test web app
./test_web_docker.sh

# Check logs
docker logs $CONTAINER_NAME
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
EOF

print_success "Web App Docker installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test web app installation: ./test_web_docker.sh"
echo "2. Start web app container: ./start_web_container.sh"
echo "3. Access web app: http://localhost:5000"
echo "4. Access via nginx: http://localhost:80"
echo ""
echo "📁 Files created:"
echo "- Dockerfile.web (Web app-optimized Docker configuration)"
echo "- start_web_container.sh (Web app container startup)"
echo "- test_web_docker.sh (Web app installation test)"
echo "- WEB_DOCKER_USAGE.md (Web app usage instructions)"
echo ""
echo "🌐 Web App Docker image: $IMAGE_NAME"
echo "📦 Web App Container: $CONTAINER_NAME"
echo "🚀 Optimized for Flask web applications with production features"
