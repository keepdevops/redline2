# REDLINE GUI Docker Usage Guide

## Quick Start

### 1. Build GUI Image
```bash
./build.sh
```

### 2. Enable X11 Forwarding (for GUI)
```bash
# Allow Docker to access X11
xhost +local:docker

# Set display (if not already set)
export DISPLAY=$DISPLAY
```

### 3. Start GUI Container
```bash
./start_gui_container.sh
```

### 4. Test Installation
```bash
./test_gui.sh
```

### 5. Run GUI Application
```bash
# Access container
docker exec -it redline-gui-container bash

# Activate environment
source /opt/conda/bin/activate redline-gui

# Run GUI
python main.py

# Or use startup script
./start_gui.sh
```

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## GUI Features

- **Tkinter-based interface**
- **Data visualization with matplotlib**
- **Interactive charts and graphs**
- **File loading and processing**
- **Real-time data analysis**

## Troubleshooting

### X11 Forwarding Issues
```bash
# Check if X11 is working
docker run --rm -e DISPLAY=$DISPLAY redline-gui xeyes

# If GUI doesn't appear, try:
xhost +local:docker
export DISPLAY=$DISPLAY
```

### Platform Issues
```bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag redline-gui --load .
```

## Commands

```bash
# Build image
./build.sh

# Start container
./start_gui_container.sh

# Test installation
./test_gui.sh

# Remove container
docker rm -f redline-gui-container

# Remove image
docker rmi redline-gui
```
