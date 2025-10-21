#!/bin/bash

# REDLINE Simple Docker Build - One Command Solution
# This script builds REDLINE with minimal dependencies

set -e

echo "=== REDLINE Simple Docker Build ==="
echo ""

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "❌ Error: web_app.py not found"
    echo "Please run this script from the REDLINE project root directory"
    exit 1
fi

echo "✅ Found web_app.py - we're in the right directory"
echo ""

# Create ultra-minimal requirements if it doesn't exist
if [ ! -f "requirements-ultra-minimal.txt" ]; then
    echo "Creating ultra-minimal requirements..."
    cat > requirements-ultra-minimal.txt << 'EOF'
flask==2.3.3
flask-socketio==5.3.6
gunicorn==21.2.0
pandas==2.0.3
numpy==1.24.3
duckdb==0.8.1
requests==2.31.0
EOF
    echo "✅ Created requirements-ultra-minimal.txt"
fi

# Create ultra-simple Dockerfile if it doesn't exist
if [ ! -f "dockerfiles/Dockerfile.ultra-simple" ]; then
    echo "Creating ultra-simple Dockerfile..."
    mkdir -p dockerfiles
    cat > dockerfiles/Dockerfile.ultra-simple << 'EOF'
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/redline

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

COPY requirements-ultra-minimal.txt /opt/redline/
RUN pip3 install -r /opt/redline/requirements-ultra-minimal.txt

COPY . /opt/redline/

RUN mkdir -p /opt/redline/data /opt/redline/logs

EXPOSE 8080

CMD ["python3", "web_app.py"]
EOF
    echo "✅ Created dockerfiles/Dockerfile.ultra-simple"
fi

echo ""
echo "Building REDLINE Docker image..."
echo ""

# Build the Docker image
docker build \
    --file dockerfiles/Dockerfile.ultra-simple \
    --tag redline-simple:latest \
    .

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "To run the container:"
echo "  docker run -d --name redline-simple -p 8080:8080 redline-simple:latest"
echo ""
echo "To access the web interface:"
echo "  http://localhost:8080"
echo ""
echo "To stop the container:"
echo "  docker stop redline-simple"
echo "  docker rm redline-simple"
