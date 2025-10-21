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

# Create conservative requirements if it doesn't exist
if [ ! -f "requirements-conservative.txt" ]; then
    echo "Creating conservative requirements..."
    cat > requirements-conservative.txt << 'EOF'
flask==2.2.5
flask-socketio==5.3.4
gunicorn==20.1.0
pandas==1.5.3
numpy==1.24.2
duckdb==0.8.1
requests==2.28.2
EOF
    echo "✅ Created requirements-conservative.txt"
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

RUN pip3 --version

COPY requirements-conservative.txt /opt/redline/
RUN pip3 install -r /opt/redline/requirements-conservative.txt

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
