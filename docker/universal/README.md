# REDLINE Universal Docker Usage Guide

## Overview

This Docker image provides both GUI and Web App capabilities in a single container, optimized for universal platform support.

## Quick Start

### 1. Build Universal Image
```bash
./build.sh
```

### 2. Test Installation
```bash
# Basic test
./test_universal.sh

# Comprehensive multi-platform test
./test_all_platforms.sh
```

### 3. Run GUI Application
```bash
# Enable X11 forwarding
xhost +local:docker
export DISPLAY=$DISPLAY

# Start GUI container
./start_gui_container.sh
```

### 4. Run Web Application
```bash
# Start Web App container
./start_web_container.sh

# Access web app
# - Direct Flask: http://localhost:5000
# - Via Nginx: http://localhost:80
```

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## Features

### GUI Features
- **Tkinter-based interface**
- **Data visualization with matplotlib**
- **Interactive charts and graphs**
- **File loading and processing**
- **Real-time data analysis**

### Web App Features
- **Flask-based web interface**
- **Real-time data processing**
- **Interactive charts and visualizations**
- **File upload and processing**
- **REST API endpoints**
- **WebSocket support for real-time updates**
- **Production-ready with Gunicorn**
- **Nginx reverse proxy**

## Usage Modes

### GUI Mode
```bash
# Start GUI container
./start_gui_container.sh

# Or manually
docker run -it --name redline-gui \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    redline-universal \
    ./start_gui.sh
```

### Web App Mode
```bash
# Start Web App container
./start_web_container.sh

# Or manually
docker run -d --name redline-web \
    -p 5000:5000 \
    -p 80:80 \
    redline-universal \
    ./start_production.sh
```

### Interactive Mode
```bash
# Start interactive container
docker run -it --name redline-interactive \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -p 5000:5000 \
    redline-universal \
    /bin/bash

# Inside container:
source /opt/conda/bin/activate redline-universal
./start_gui.sh    # For GUI
./start_web.sh    # For web app
./start_production.sh  # For production web app
```

## Environment Variables

```bash
# GUI
export DISPLAY=$DISPLAY

# Web App
export FLASK_APP=web_app.py
export FLASK_ENV=production
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
```

## Testing

### Basic Testing
```bash
# Quick test of installation
./test_universal.sh
```

### Comprehensive Testing
```bash
# Full test suite across all platforms
./test_all_platforms.sh
```

The comprehensive test suite includes:
- **Platform Detection**: Tests on AMD64, ARM64, and ARMv7
- **Container Functionality**: Basic container operations
- **Conda Environment**: Environment activation and package management
- **Python Packages**: All required packages (pandas, numpy, matplotlib, flask, etc.)
- **GUI Components**: Tkinter and matplotlib GUI backend
- **Web Components**: Flask, Gunicorn, and Nginx
- **REDLINE Modules**: Core, GUI, and Web modules
- **Startup Scripts**: All startup scripts availability
- **Platform-Specific**: Architecture detection and compatibility
- **Networking**: Port binding and connectivity
- **File System**: File operations and permissions

## Commands

```bash
# Build image
./build.sh

# Test installation
./test_universal.sh

# Comprehensive testing
./test_all_platforms.sh

# Start GUI
./start_gui_container.sh

# Start Web App
./start_web_container.sh

# Remove containers
docker rm -f redline-universal-container-gui redline-universal-container-web

# Remove image
docker rmi redline-universal
```

## Troubleshooting

### X11 Forwarding Issues (GUI)
```bash
# Check if X11 is working
docker run --rm -e DISPLAY=$DISPLAY redline-universal xeyes

# If GUI doesn't appear, try:
xhost +local:docker
export DISPLAY=$DISPLAY
```

### Port Issues (Web App)
```bash
# Check if ports are available
netstat -tlnp | grep :5000
netstat -tlnp | grep :80
```

### Platform Issues
```bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag redline-universal --load .
```

## Advantages

- **Single Image**: Both GUI and Web App in one container
- **Universal Platform**: Supports multiple architectures
- **Conda Environment**: Optimized package management
- **Production Ready**: Includes Gunicorn and Nginx
- **Easy Deployment**: Simple startup scripts
- **Comprehensive Testing**: Built-in test suite
