# REDLINE Web Application Docker Build Guide

## Overview

This guide provides comprehensive instructions for building the REDLINE Flask web application using Docker buildx for Linux containers. The build scripts support multi-platform builds, testing, and registry pushing.

## 🚀 **Quick Start**

### **Simple Build**
```bash
./quick_build_web.sh
```

### **Custom Build**
```bash
./build_web_docker.sh -i redline-web -t v1.0.0 -p linux/amd64
```

## 📁 **Available Build Scripts**

### **1. `quick_build_web.sh` - Simple & Fast**
```bash
./quick_build_web.sh [IMAGE_NAME] [TAG] [PLATFORM]
```
**Features:**
- ✅ One-command Docker build
- ✅ Automatic buildx setup
- ✅ Basic validation
- ✅ Quick testing instructions

**Usage Examples:**
```bash
# Default build
./quick_build_web.sh

# Custom name and tag
./quick_build_web.sh my-redline v1.0.0

# ARM64 build
./quick_build_web.sh redline-web latest linux/arm64
```

### **2. `build_web_docker.sh` - Full-Featured**
```bash
./build_web_docker.sh [OPTIONS]
```
**Features:**
- ✅ Multi-platform builds
- ✅ Registry pushing
- ✅ Image testing
- ✅ Cache control
- ✅ Comprehensive validation
- ✅ Buildx management

**Usage Examples:**
```bash
# Basic build
./build_web_docker.sh

# Multi-platform build and push
./build_web_docker.sh -p linux/amd64,linux/arm64 --push

# Build with testing
./build_web_docker.sh --test --no-cache

# Custom configuration
./build_web_docker.sh -i redline-web -t v1.0.0 -p linux/arm64 --push
```

### **3. `build_web_docker.bat` - Windows Support**
```cmd
build_web_docker.bat [OPTIONS]
```
**Features:**
- ✅ Windows batch file support
- ✅ Same functionality as Linux scripts
- ✅ Windows-specific process management

## 🐳 **Docker Configuration**

### **Dockerfile.web**
The build uses `Dockerfile.web` which is optimized for web deployment:

```dockerfile
FROM python:3.11-slim

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV WEB_PORT=8080
ENV FLASK_APP=web_app.py

# Install system dependencies
RUN apt-get update && apt-get install -y curl wget git

# Create non-root user
RUN useradd -m -s /bin/bash redline

# Set working directory
WORKDIR /app

# Copy requirements and install packages
COPY requirements_docker.txt ./
RUN pip install --upgrade pip && pip install -r requirements_docker.txt

# Copy application files
COPY main.py data_config.ini ./
COPY redline/ ./redline/
COPY web_app.py ./

# Create data directories
RUN mkdir -p data data/converted data/downloaded data/stooq_format && \
    chown -R redline:redline /app

# Switch to non-root user
USER redline

# Expose port and health check
EXPOSE ${WEB_PORT}
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${WEB_PORT}/health || exit 1

# Run the web application
CMD ["python", "web_app.py"]
```

### **requirements_docker.txt**
Contains all Python dependencies needed for the web application:
- Flask and related packages
- Data processing libraries (pandas, numpy, duckdb)
- Financial data libraries
- Background task processing (Celery, Redis)

## 🏗️ **Build Options**

### **Platform Support**
- **`linux/amd64`** - Intel/AMD 64-bit Linux (default)
- **`linux/arm64`** - ARM 64-bit Linux (Apple Silicon, ARM servers)
- **`linux/arm/v7`** - ARM v7 Linux (Raspberry Pi, etc.)
- **Multi-platform** - Build for multiple platforms simultaneously

### **Build Features**
- **Multi-platform builds** - Build for multiple architectures at once
- **Registry pushing** - Push directly to Docker registries
- **Image testing** - Automatic health checks after build
- **Cache control** - Option to build without cache
- **Buildx management** - Automatic setup and cleanup

## 🔧 **Advanced Usage**

### **Multi-Platform Builds**
```bash
# Build for multiple platforms
./build_web_docker.sh -p linux/amd64,linux/arm64 --push

# Build for all common platforms
./build_web_docker.sh -p linux/amd64,linux/arm64,linux/arm/v7 --push
```

### **Registry Integration**
```bash
# Build and push to Docker Hub
./build_web_docker.sh -i username/redline-web -t latest --push

# Build and push to private registry
./build_web_docker.sh -i registry.company.com/redline-web -t v1.0.0 --push
```

### **Testing and Validation**
```bash
# Build with testing
./build_web_docker.sh --test

# Build without cache and test
./build_web_docker.sh --no-cache --test

# Test existing image
./build_web_docker.sh --test -i existing-image -t existing-tag
```

## 📋 **Build Process**

### **1. Pre-build Validation**
- Check Docker and buildx availability
- Validate required files (Dockerfile, requirements, web_app.py)
- Setup buildx builder instance

### **2. Docker Build**
- Create optimized Docker image
- Install system and Python dependencies
- Copy application files
- Set up proper permissions and security

### **3. Post-build Actions**
- Load image locally (if not pushing)
- Push to registry (if requested)
- Test image health (if requested)
- Cleanup temporary resources

## 🧪 **Testing**

### **Automatic Testing**
The build scripts can automatically test built images:

```bash
# Enable automatic testing
./build_web_docker.sh --test

# Test with custom port
./build_web_docker.sh --test --test-port 8080
```

### **Manual Testing**
```bash
# Run the container
docker run -p 8080:8080 redline-web:latest

# Test health endpoint
curl http://localhost:8080/health

# Test web interface
curl http://localhost:8080/
```

## 🚀 **Deployment**

### **Local Deployment**
```bash
# Build and run locally
./quick_build_web.sh
docker run -p 8080:8080 redline-web:latest
```

### **Cloud Deployment**
```bash
# Build and push to registry
./build_web_docker.sh --push -i your-registry/redline-web

# Deploy to cloud platform
# (Use your cloud provider's deployment tools)
```

### **Production Deployment**
```bash
# Multi-platform build for production
./build_web_docker.sh \
  -i production-registry/redline-web \
  -t v1.0.0 \
  -p linux/amd64,linux/arm64 \
  --push \
  --test
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Docker Not Running**
```bash
# Start Docker Desktop or Docker daemon
# On macOS/Windows: Start Docker Desktop
# On Linux: sudo systemctl start docker
```

#### **Buildx Not Available**
```bash
# Update Docker to latest version
# Docker buildx is included in Docker 19.03+
```

#### **Permission Issues**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

#### **Platform Not Supported**
```bash
# Check available platforms
docker buildx inspect

# Use supported platform
./build_web_docker.sh -p linux/amd64
```

### **Debug Mode**
```bash
# Build with verbose output
docker buildx build --platform linux/amd64 --progress=plain -t redline-web:latest .
```

### **Clean Build**
```bash
# Build without cache
./build_web_docker.sh --no-cache

# Clean up buildx builder
./build_web_docker.sh --clean
```

## 📊 **Performance Tips**

### **Build Optimization**
- Use multi-stage builds for smaller images
- Leverage Docker layer caching
- Use .dockerignore to exclude unnecessary files
- Build for specific target platforms

### **Registry Optimization**
- Use registry caching for faster builds
- Tag images with semantic versions
- Use multi-platform manifests for better distribution

## 🛡️ **Security Considerations**

### **Image Security**
- Use non-root user in container
- Keep base images updated
- Scan images for vulnerabilities
- Use minimal base images

### **Build Security**
- Use trusted base images
- Validate all dependencies
- Use multi-stage builds to reduce attack surface
- Enable content trust when pushing

## 📝 **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_PORT` | 8080 | Port for the web application |
| `FLASK_APP` | web_app.py | Flask application entry point |
| `PYTHONUNBUFFERED` | 1 | Python output buffering |

## 🆘 **Getting Help**

### **Script Help**
```bash
# Show help for any script
./build_web_docker.sh --help
./quick_build_web.sh --help
```

### **Docker Help**
```bash
# Docker buildx help
docker buildx --help

# Docker build help
docker build --help
```

### **Debug Information**
```bash
# Check Docker version
docker --version

# Check buildx version
docker buildx version

# Inspect buildx builder
docker buildx inspect
```

---

**🎉 Your REDLINE Web Application Docker build system is ready!**

**Start building with: `./quick_build_web.sh`** 🚀
