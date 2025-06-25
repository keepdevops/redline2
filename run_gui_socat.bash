#!/bin/bash

# REDLINE GUI Docker Runner for macOS (using socat)
# Alternative approach using socat for X11 forwarding

echo "Setting up X11 forwarding with socat for REDLINE GUI..."

# Check if socat is installed
if ! command -v socat &> /dev/null; then
    echo "socat is required but not installed."
    echo "Please install it with: brew install socat"
    echo "Or use the regular run_gui.bash script instead."
    exit 1
fi

# Start XQuartz if not running
if ! pgrep -x "XQuartz" > /dev/null; then
    echo "Starting XQuartz..."
    open -a XQuartz
    sleep 3
fi

# Get local IP
LOCAL_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
echo "Local IP: $LOCAL_IP"

# Start socat to forward X11
echo "Starting socat X11 forwarder..."
socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" &
SOCAT_PID=$!

# Allow X11 connections
export DISPLAY=:0
xhost + $LOCAL_IP

# Check architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    DOCKER_IMAGE="redline_arm"
    echo "Running on Apple Silicon (ARM64)"
else
    DOCKER_IMAGE="redline_x86"
    echo "Running on Intel Mac (x86_64)"
fi

echo "Starting REDLINE container with GUI support..."

# Function to cleanup on exit
cleanup() {
    echo "Cleaning up..."
    kill $SOCAT_PID 2>/dev/null
    xhost - $LOCAL_IP 2>/dev/null
}
trap cleanup EXIT

# Run Docker container
docker run -it --rm \
    -e DISPLAY=$LOCAL_IP:0 \
    -v $(pwd)/data:/app/data \
    -v $(pwd):/app/host \
    --name redline_gui \
    $DOCKER_IMAGE \
    python3 /app/host/data_module_shared.py --task gui

echo "REDLINE GUI session ended." 