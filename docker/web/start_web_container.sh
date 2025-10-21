#!/bin/bash
echo "🌐 Starting REDLINE Web App Container"
echo "====================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^redline-web-container$"; then
    echo "Container redline-web-container already exists. Removing..."
    docker rm -f redline-web-container
fi

# Start container with port mapping
docker run -it --name redline-web-container \
    -p 5000:5000 \
    -p 80:80 \
    -v $(pwd):/app/host \
    redline-web \
    /bin/bash

echo "Web App Container started!"
echo "Access the web app at: http://localhost:5000"
echo "Access via nginx at: http://localhost:80"
echo "Container access: docker exec -it redline-web-container bash"
