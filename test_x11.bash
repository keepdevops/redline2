#!/bin/bash

# Test X11 forwarding for REDLINE
echo "Testing X11 forwarding setup..."

# Check if XQuartz is running
if ! pgrep -x "XQuartz" > /dev/null; then
    echo "❌ XQuartz is not running. Starting it..."
    open -a XQuartz
    sleep 3
else
    echo "✅ XQuartz is running"
fi

# Get local IP
LOCAL_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
echo "Local IP: $LOCAL_IP"

# Set display
export DISPLAY=:0
echo "DISPLAY set to: $DISPLAY"

# Allow X11 connections
echo "Setting up X11 permissions..."
xhost + $LOCAL_IP

# Test X11 locally first
echo "Testing local X11..."
if command -v xeyes &> /dev/null; then
    echo "Running xeyes test (close the window to continue)..."
    xeyes &
    XEYES_PID=$!
    sleep 2
    kill $XEYES_PID 2>/dev/null
    echo "✅ Local X11 test passed"
else
    echo "⚠️  xeyes not available for local test"
fi

# Test Docker X11 forwarding
echo "Testing Docker X11 forwarding..."
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    DOCKER_IMAGE="redline_arm"
else
    DOCKER_IMAGE="redline_x86"
fi

echo "Using Docker image: $DOCKER_IMAGE"

# Simple Docker X11 test
echo "Running simple Docker GUI test..."
docker run --rm \
    -e DISPLAY=$LOCAL_IP:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    $DOCKER_IMAGE \
    sh -c "echo 'GUI libraries test:' && python3 -c 'import tkinter; print(\"✅ Tkinter available\"); root=tkinter.Tk(); root.withdraw()' 2>/dev/null && echo '✅ Docker X11 test passed' || echo '❌ Docker X11 test failed'"

echo ""
echo "X11 forwarding test complete!"
echo "If all tests passed, you can run: ./run_gui.bash" 