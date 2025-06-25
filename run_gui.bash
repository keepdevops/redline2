#!/bin/bash

# REDLINE GUI Docker Runner for macOS
# This script sets up X11 forwarding to run the GUI from within Docker

echo "Setting up X11 forwarding for REDLINE GUI..."

# Get local IP address
LOCAL_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
echo "Local IP: $LOCAL_IP"

# Start XQuartz if not running
if ! pgrep -x "XQuartz" > /dev/null; then
    echo "Starting XQuartz..."
    open -a XQuartz
    sleep 3
fi

# Set display and allow connections
export DISPLAY=:0
echo "Allowing X11 connections from $LOCAL_IP..."
xhost + $LOCAL_IP

# Check if we're on ARM or Intel Mac
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    DOCKER_IMAGE="redline_arm"
    echo "Running on Apple Silicon (ARM64)"
else
    DOCKER_IMAGE="redline_x86"
    echo "Running on Intel Mac (x86_64)"
fi

echo "Starting REDLINE container with GUI support..."

# Run Docker container with X11 forwarding
docker run -it --rm \
    -e DISPLAY=$LOCAL_IP:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd)/data:/app/data \
    -v $(pwd):/app/host \
    --name redline_gui \
    $DOCKER_IMAGE \
    python3 /app/host/data_module_shared.py --task gui

echo "REDLINE GUI session ended." 