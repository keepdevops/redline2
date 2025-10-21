#!/bin/bash
echo "🌐 Starting REDLINE Web App Container"
echo "===================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^redline-universal-container-web$"; then
    echo "Container redline-universal-container-web already exists. Removing..."
    docker rm -f redline-universal-container-web
fi

# Start container with port mapping
docker run -d --name redline-universal-container-web \
    -p 5000:5000 \
    -p 80:80 \
    -v $(pwd):/app/host \
    redline-universal \
    ./start_production.sh

echo "Web App Container started!"
echo "Access the web app at: http://localhost:5000"
echo "Access via nginx at: http://localhost:80"
echo "Container access: docker exec -it redline-universal-container-web bash"
