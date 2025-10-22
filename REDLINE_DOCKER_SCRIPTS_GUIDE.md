# REDLINE Tkinter GUI Docker Scripts Guide

## 🐳 **Docker Management Scripts**

This guide covers the comprehensive Docker management scripts for REDLINE Tkinter GUI with multi-platform support.

## 📋 **Available Scripts**

### **1. build_docker_gui.sh**
Builds Docker images for AMD64 and ARM64 architectures.

```bash
# Build for specific platform
./build_docker_gui.sh build-amd64
./build_docker_gui.sh build-arm64

# Build multi-platform image
./build_docker_gui.sh build-multi

# Build all platforms
./build_docker_gui.sh build-all

# Test built images
./build_docker_gui.sh test-amd64
./build_docker_gui.sh test-arm64

# Clean up images
./build_docker_gui.sh clean
```

### **2. run_docker_gui.sh**
Runs Docker containers with proper X11 forwarding and volume mounting.

```bash
# Run for specific platform
./run_docker_gui.sh run-amd64
./run_docker_gui.sh run-arm64

# Run for current platform
./run_docker_gui.sh run-auto

# Run in background
./run_docker_gui.sh background

# Show status and logs
./run_docker_gui.sh status
./run_docker_gui.sh logs
```

### **3. stop_docker_gui.sh**
Stops and removes Docker containers and cleans up resources.

```bash
# Stop main container
./stop_docker_gui.sh stop

# Stop all containers
./stop_docker_gui.sh stop-all

# Remove images
./stop_docker_gui.sh remove-images

# Remove volumes
./stop_docker_gui.sh remove-volumes

# Complete cleanup
./stop_docker_gui.sh cleanup

# Show status
./stop_docker_gui.sh status
```

### **4. docker_gui_manager.sh**
Complete management script with interactive menu.

```bash
# Interactive menu
./docker_gui_manager.sh

# Quick start
./docker_gui_manager.sh quick-start

# Build and run
./docker_gui_manager.sh build-and-run

# Restart
./docker_gui_manager.sh restart

# Show status
./docker_gui_manager.sh status
```

## 🚀 **Quick Start Guide**

### **1. First Time Setup**

```bash
# Make scripts executable
chmod +x *.sh

# Build for your platform
./build_docker_gui.sh build-auto

# Run GUI
./run_docker_gui.sh run-auto
```

### **2. Using the Manager Script**

```bash
# Interactive menu
./docker_gui_manager.sh

# Or quick start
./docker_gui_manager.sh quick-start
```

### **3. Manual Operations**

```bash
# Build
./build_docker_gui.sh build-amd64

# Run
./run_docker_gui.sh run-amd64

# Stop
./stop_docker_gui.sh stop
```

## 🔧 **Platform-Specific Usage**

### **AMD64 (Intel/AMD)**

```bash
# Build
./build_docker_gui.sh build-amd64

# Run
./run_docker_gui.sh run-amd64

# Test
./build_docker_gui.sh test-amd64
```

### **ARM64 (Apple Silicon/ARM)**

```bash
# Build
./build_docker_gui.sh build-arm64

# Run
./run_docker_gui.sh run-arm64

# Test
./build_docker_gui.sh test-arm64
```

### **Multi-Platform**

```bash
# Build for both platforms
./build_docker_gui.sh build-multi

# Run on current platform
./run_docker_gui.sh run-auto
```

## 🖥️ **X11 Display Setup**

### **Linux (Native)**

```bash
# Allow X11 forwarding
xhost +local:docker

# Set display
export DISPLAY=:0

# Run GUI
./run_docker_gui.sh run-auto
```

### **macOS (XQuartz)**

```bash
# Install XQuartz
brew install --cask xquartz

# Start XQuartz
open -a XQuartz

# Allow connections
xhost +localhost

# Set display
export DISPLAY=localhost:0

# Run GUI
./run_docker_gui.sh run-auto
```

### **Windows (WSL2 + VcXsrv)**

```bash
# Set display in WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Run GUI
./run_docker_gui.sh run-auto
```

## 📊 **Script Features**

### **Build Script Features**
- ✅ Multi-platform support (AMD64, ARM64)
- ✅ Build optimization with layer caching
- ✅ Image testing and validation
- ✅ Cleanup operations
- ✅ Progress reporting
- ✅ Error handling

### **Run Script Features**
- ✅ Automatic X11 setup
- ✅ Volume mounting
- ✅ Environment configuration
- ✅ Background mode
- ✅ Status monitoring
- ✅ Log viewing

### **Stop Script Features**
- ✅ Graceful container stopping
- ✅ Resource cleanup
- ✅ Image removal
- ✅ Volume cleanup
- ✅ Network cleanup
- ✅ Status reporting

### **Manager Script Features**
- ✅ Interactive menu
- ✅ Quick start functionality
- ✅ Build and run automation
- ✅ Restart capabilities
- ✅ Status monitoring
- ✅ Log viewing

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Script Not Executable**
```bash
chmod +x *.sh
```

#### **Docker Not Running**
```bash
# Start Docker Desktop
# Or start Docker service
sudo systemctl start docker
```

#### **X11 Connection Failed**
```bash
# Check display
echo $DISPLAY

# Allow X11 connections
xhost +local:docker

# Test X11
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw ubuntu:22.04 xeyes
```

#### **Image Not Found**
```bash
# Build image first
./build_docker_gui.sh build-auto
```

#### **Permission Denied**
```bash
# Fix X11 permissions
sudo chmod 1777 /tmp/.X11-unix
sudo chown root:root /tmp/.X11-unix
```

### **Debug Mode**

```bash
# Run with verbose output
./run_docker_gui.sh run-auto --verbose

# Show detailed logs
./run_docker_gui.sh logs
```

## 📈 **Performance Optimization**

### **Build Optimization**
```bash
# Use BuildKit
export DOCKER_BUILDKIT=1

# Build with no cache
./build_docker_gui.sh build-auto --no-cache
```

### **Run Optimization**
```bash
# Run in background
./run_docker_gui.sh background

# Monitor resources
docker stats redline-gui-container
```

### **Resource Limits**
```bash
# Set memory limit
docker run --memory=2g redline-gui:latest

# Set CPU limit
docker run --cpus=2.0 redline-gui:latest
```

## 🚀 **Production Deployment**

### **Docker Registry**
```bash
# Tag for registry
docker tag redline-gui:latest your-registry/redline-gui:latest

# Push to registry
docker push your-registry/redline-gui:latest
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redline-gui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redline-gui
  template:
    metadata:
      labels:
        app: redline-gui
    spec:
      containers:
      - name: redline-gui
        image: redline-gui:latest
        env:
        - name: DISPLAY
          value: ":0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "2"
```

## 📚 **Additional Resources**

- **Dockerfile.gui**: Multi-platform GUI Dockerfile
- **docker-compose.gui.yml**: GUI Docker Compose configuration
- **REDLINE_GUI_DOCKER_GUIDE.md**: Complete Docker guide
- **REDLINE_INSTALLATION_GUIDE.md**: Installation instructions

## 🎯 **Quick Reference**

### **Most Common Commands**
```bash
# Quick start
./docker_gui_manager.sh quick-start

# Build and run
./docker_gui_manager.sh build-and-run

# Stop
./stop_docker_gui.sh stop

# Status
./docker_gui_manager.sh status
```

### **Emergency Commands**
```bash
# Stop everything
./stop_docker_gui.sh cleanup

# Restart
./docker_gui_manager.sh restart

# Test
./docker_gui_manager.sh test
```

---

**REDLINE Tkinter GUI Docker Scripts: Complete automation for multi-platform deployment.** 🐳
