# REDLINE Tkinter GUI Docker Setup Guide

## 🐳 **Multi-Platform Docker Support**

This guide covers setting up REDLINE Tkinter GUI using Docker with support for both AMD64 and ARM64 architectures.

## 📋 **Prerequisites**

### **System Requirements**
- **Docker**: 20.10+ with Buildx support
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Display**: X11-compatible display server

### **Platform Support**
- **AMD64 (x86_64)**: Intel/AMD processors
- **ARM64 (aarch64)**: ARM processors (Apple Silicon, ARM servers)
- **Multi-platform**: Single image supporting both architectures

## 🚀 **Quick Start**

### **1. Build for Your Platform**

#### **AMD64 (Intel/AMD)**
```bash
# Build for AMD64
./build_gui_docker.sh build-amd64

# Test GUI components
./build_gui_docker.sh test-amd64

# Run GUI application
./build_gui_docker.sh run-amd64
```

#### **ARM64 (Apple Silicon/ARM)**
```bash
# Build for ARM64
./build_gui_docker.sh build-arm64

# Test GUI components
./build_gui_docker.sh test-arm64

# Run GUI application
./build_gui_docker.sh run-arm64
```

#### **Multi-Platform Build**
```bash
# Build for both platforms
./build_gui_docker.sh build-multi
```

### **2. Using Docker Compose**

```bash
# Start GUI with Docker Compose
docker-compose -f docker-compose.gui.yml up

# Start with virtual display (headless)
docker-compose -f docker-compose.gui.yml up xvfb redline-gui
```

## 🔧 **Detailed Setup**

### **X11 Display Configuration**

#### **Linux (Native)**
```bash
# Allow X11 forwarding
xhost +local:docker

# Set display
export DISPLAY=:0

# Run GUI
./build_gui_docker.sh run-amd64
```

#### **macOS (XQuartz)**
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
./build_gui_docker.sh run-amd64
```

#### **Windows (WSL2 + VcXsrv)**
```bash
# Install VcXsrv and start X server
# Set display in WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Run GUI
./build_gui_docker.sh run-amd64
```

### **Headless Mode (Virtual Display)**

```bash
# Start virtual display server
docker-compose -f docker-compose.gui.yml up xvfb -d

# Run GUI with virtual display
docker run --rm \
  --network host \
  -e DISPLAY=:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  redline-gui:latest
```

## 📁 **File Structure**

```
redline/
├── Dockerfile.gui              # Multi-platform GUI Dockerfile
├── docker-compose.gui.yml      # GUI Docker Compose configuration
├── build_gui_docker.sh         # Build script for both platforms
├── main.py                     # Tkinter GUI application
├── redline/                    # Application modules
├── data/                       # Data directory
└── logs/                       # Log directory
```

## 🛠️ **Build Script Commands**

### **Available Commands**
```bash
./build_gui_docker.sh build-amd64    # Build for AMD64
./build_gui_docker.sh build-arm64    # Build for ARM64
./build_gui_docker.sh build-multi    # Build multi-platform
./build_gui_docker.sh test-amd64     # Test AMD64 components
./build_gui_docker.sh test-arm64     # Test ARM64 components
./build_gui_docker.sh run-amd64      # Run AMD64 GUI
./build_gui_docker.sh run-arm64      # Run ARM64 GUI
./build_gui_docker.sh help           # Show help
```

### **Manual Docker Commands**

#### **Build for AMD64**
```bash
docker build \
  --platform linux/amd64 \
  --file Dockerfile.gui \
  --tag redline-gui:latest-amd64 \
  .
```

#### **Build for ARM64**
```bash
docker build \
  --platform linux/arm64 \
  --file Dockerfile.gui \
  --tag redline-gui:latest-arm64 \
  .
```

#### **Run GUI Application**
```bash
# AMD64
docker run --rm \
  --platform linux/amd64 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/data:/app/data \
  redline-gui:latest-amd64

# ARM64
docker run --rm \
  --platform linux/arm64 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/data:/app/data \
  redline-gui:latest-arm64
```

## 🔍 **Testing and Validation**

### **Test GUI Components**
```bash
# Test AMD64
docker run --rm \
  --platform linux/amd64 \
  redline-gui:latest-amd64 \
  /app/test_gui.sh

# Test ARM64
docker run --rm \
  --platform linux/arm64 \
  redline-gui:latest-arm64 \
  /app/test_gui.sh
```

### **Expected Test Output**
```
Testing REDLINE GUI components...
✓ Tkinter available
✓ Pandas available
✓ NumPy available
✓ Matplotlib available
✓ DuckDB available
✓ GUI module available
✓ All GUI components tested successfully!
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Display Connection Failed**
```bash
# Check X11 forwarding
echo $DISPLAY

# Allow X11 connections
xhost +local:docker

# Test X11
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw ubuntu:22.04 xeyes
```

#### **Permission Denied**
```bash
# Fix X11 permissions
sudo chmod 1777 /tmp/.X11-unix
sudo chown root:root /tmp/.X11-unix
```

#### **Platform Not Supported**
```bash
# Check available platforms
docker buildx ls

# Create new builder
docker buildx create --name redline-builder --use
```

#### **GUI Not Starting**
```bash
# Check logs
docker logs redline-gui-container

# Run in interactive mode
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  redline-gui:latest bash
```

### **Performance Optimization**

#### **Resource Limits**
```yaml
# In docker-compose.gui.yml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

#### **Build Optimization**
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Use multi-stage builds
docker build --target gui --tag redline-gui:latest .
```

## 📊 **Architecture Comparison**

| Feature | AMD64 | ARM64 | Multi-Platform |
|---------|-------|-------|----------------|
| **Performance** | High | High | Optimized per platform |
| **Compatibility** | Universal | ARM devices | Both platforms |
| **Build Time** | Fast | Fast | Slower (2x) |
| **Image Size** | ~500MB | ~500MB | ~500MB |
| **Memory Usage** | 512MB-2GB | 512MB-2GB | Platform dependent |

## 🚀 **Production Deployment**

### **Docker Registry**
```bash
# Tag for registry
docker tag redline-gui:latest your-registry/redline-gui:latest

# Push multi-platform
docker buildx build --platform linux/amd64,linux/arm64 --push --tag your-registry/redline-gui:latest .
```

### **Kubernetes Deployment**
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
- **build_gui_docker.sh**: Build script for both platforms
- **REDLINE_USER_GUIDE.md**: Complete user guide
- **TROUBLESHOOTING_GUIDE.md**: Detailed troubleshooting

---

**REDLINE Tkinter GUI Docker: Multi-platform, production-ready.** 🐳
