#!/bin/bash
echo "🖥️  Starting REDLINE GUI Container"
echo "=================================="

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^redline-universal-container-gui$"; then
    echo "Container redline-universal-container-gui already exists. Removing..."
    docker rm -f redline-universal-container-gui
fi

# Check if X11 forwarding is available
if [ -z "$DISPLAY" ]; then
    echo "⚠️  Warning: DISPLAY not set. GUI may not work."
    echo "For GUI support, run with X11 forwarding:"
    echo "xhost +local:docker"
    echo "export DISPLAY=$DISPLAY"
fi

# Start container with X11 forwarding
docker run -it --name redline-universal-container-gui \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd):/app/host \
    --net=host \
    redline-universal \
    ./start_gui.sh

echo "GUI Container started! Access it with: docker exec -it redline-universal-container-gui bash"
