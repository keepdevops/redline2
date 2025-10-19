# REDLINE Docker Deployment Guide

## 🐳 Complete Docker Deployment Guide for REDLINE GUI on Ubuntu

This guide provides comprehensive instructions for deploying REDLINE on Ubuntu using Docker with multiple display modes.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Deployment Modes](#deployment-modes)
4. [Docker Compose Usage](#docker-compose-usage)
5. [Manual Docker Commands](#manual-docker-commands)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)
8. [Security Considerations](#security-considerations)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd redline

# X11 Mode (requires X11 server)
docker-compose --profile x11 up

# VNC Mode (remote access)
docker-compose --profile vnc up

# Headless Mode (CLI only)
docker-compose --profile headless up

# Development Mode
docker-compose --profile dev up
```

### Option 2: Scripts

```bash
# Make scripts executable
chmod +x scripts/*.sh

# X11 Mode
./scripts/run_docker_x11.sh

# VNC Mode
./scripts/run_docker_vnc.sh

# Headless Mode
./scripts/run_docker_headless.sh
```

## 🔧 Prerequisites

### System Requirements

- **Ubuntu 20.04+** (tested on Ubuntu 24.04)
- **Docker 20.10+** with Docker Compose v2
- **4GB RAM minimum** (8GB recommended)
- **2GB disk space** for container and data

### Required Packages

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# For X11 mode, install X11 utilities
sudo apt-get install x11-xserver-utils
```

### X11 Mode Prerequisites

```bash
# Allow X11 connections from Docker
xhost +local:docker

# Set DISPLAY environment variable
export DISPLAY=:0

# Install VNC client (optional, for VNC mode)
sudo apt-get install tigervnc-viewer
```

## 🖥️ Deployment Modes

### 1. X11 Mode (Traditional GUI)

**Best for**: Local development, direct X11 forwarding

```bash
# Using Docker Compose
docker-compose --profile x11 up

# Using script
./scripts/run_docker_x11.sh

# Manual Docker command
docker run -it --rm \
  --name redline-x11 \
  --env DISPLAY=$DISPLAY \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --volume $(pwd)/data:/app/data \
  --network host \
  redline:latest \
  --mode=x11 --task=gui
```

**Features**:
- Direct X11 forwarding
- Native desktop integration
- Best performance
- Requires X11 server on host

### 2. VNC Mode (Remote Access)

**Best for**: Remote servers, cloud deployments, headless systems

```bash
# Using Docker Compose
VNC_PORT=5900 VNC_PASSWORD=mypass docker-compose --profile vnc up

# Using script
./scripts/run_docker_vnc.sh --port 5900 --password mypass

# Manual Docker command
docker run -it --rm \
  --name redline-vnc \
  --env VNC_PORT=5900 \
  --env VNC_PASSWORD=mypass \
  --volume $(pwd)/data:/app/data \
  --publish 5900:5900 \
  redline:latest \
  --mode=vnc --task=gui
```

**Features**:
- Remote desktop access
- Cross-platform VNC clients
- No X11 server required on host
- Secure password authentication

**VNC Connection**:
- Server: `localhost:5900`
- Password: `redline123` (default)
- Client: `vncviewer localhost:5900`

### 3. Headless Mode (CLI Only)

**Best for**: Automated scripts, batch processing, CI/CD

```bash
# Using Docker Compose
docker-compose --profile headless up

# Using script
./scripts/run_docker_headless.sh cli

# Manual Docker command
docker run -it --rm \
  --name redline-headless \
  --volume $(pwd)/data:/app/data \
  redline:latest \
  --mode=headless --task=cli
```

**Features**:
- Minimal resource usage
- No display requirements
- Perfect for automation
- Fast startup time

### 4. GUI Headless Mode (Virtual Display)

**Best for**: GUI applications without physical display

```bash
# Using Docker Compose
docker-compose --profile gui-headless up

# Using script
./scripts/run_docker_headless.sh gui

# Manual Docker command
docker run -it --rm \
  --name redline-gui-headless \
  --volume $(pwd)/data:/app/data \
  redline:latest \
  --mode=headless --task=gui
```

**Features**:
- GUI runs with virtual display (Xvfb)
- No physical display required
- Suitable for testing
- Automated GUI operations

### 5. Web Mode (Future)

**Best for**: Web-based access, cloud deployments

```bash
# Using Docker Compose
docker-compose --profile web up

# Manual Docker command
docker run -it --rm \
  --name redline-web \
  --volume $(pwd)/data:/app/data \
  --publish 8080:8080 \
  redline:latest \
  --mode=web
```

**Features**:
- Web-based interface
- Cross-platform access
- No client installation
- Cloud-friendly

## 🐳 Docker Compose Usage

### Environment Variables

Create a `.env` file for configuration:

```bash
# .env file
DISPLAY=:0
VNC_PORT=5900
VNC_PASSWORD=redline123
WEB_PORT=8080
```

### Profile-based Deployment

```bash
# List available profiles
docker-compose config --profiles

# Run specific profile
docker-compose --profile x11 up
docker-compose --profile vnc up
docker-compose --profile headless up
docker-compose --profile web up
docker-compose --profile dev up

# Run multiple profiles
docker-compose --profile vnc --profile headless up

# Run in background
docker-compose --profile vnc up -d

# View logs
docker-compose --profile vnc logs -f

# Stop services
docker-compose --profile vnc down
```

### Custom Configuration

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  redline-vnc:
    environment:
      - VNC_PASSWORD=mysecurepassword
    volumes:
      - ./custom-data:/app/data
      - ./config:/app/config
    ports:
      - "5901:5900"  # Custom port mapping
```

## 🔨 Manual Docker Commands

### Building the Image

```bash
# Build from Dockerfile
docker build -t redline:latest .

# Build with custom tag
docker build -t redline:v1.0.0 .

# Build without cache
docker build --no-cache -t redline:latest .
```

### Running Containers

```bash
# Basic run
docker run -it --rm redline:latest

# With data volume
docker run -it --rm \
  --volume $(pwd)/data:/app/data \
  redline:latest

# With custom environment
docker run -it --rm \
  --env VNC_PORT=5901 \
  --env VNC_PASSWORD=mypass \
  --publish 5901:5901 \
  redline:latest --mode=vnc

# Interactive shell
docker run -it --rm redline:latest /bin/bash
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop redline-vnc

# Remove container
docker rm redline-vnc

# View container logs
docker logs redline-vnc

# Execute command in running container
docker exec -it redline-vnc /bin/bash

# Copy files to/from container
docker cp redline-vnc:/app/data ./local-data
docker cp ./local-file redline-vnc:/app/
```

## 🔧 Troubleshooting

### Common Issues

#### 1. X11 Forwarding Issues

**Problem**: `cannot connect to X server`

**Solutions**:
```bash
# Check DISPLAY variable
echo $DISPLAY

# Allow X11 connections
xhost +local:docker

# Test X11 connection
xset q

# Alternative: Use VNC mode instead
./scripts/run_docker_vnc.sh
```

#### 2. VNC Connection Issues

**Problem**: Cannot connect to VNC server

**Solutions**:
```bash
# Check if VNC port is accessible
telnet localhost 5900

# Check container logs
docker logs redline-vnc

# Verify VNC password
# Default password: redline123

# Try different VNC client
sudo apt-get install tigervnc-viewer
vncviewer localhost:5900
```

#### 3. Permission Issues

**Problem**: Permission denied errors

**Solutions**:
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data

# Run with user mapping
docker run -it --rm \
  --user $(id -u):$(id -g) \
  --volume $(pwd)/data:/app/data \
  redline:latest
```

#### 4. Container Startup Issues

**Problem**: Container fails to start

**Solutions**:
```bash
# Check Docker logs
docker logs redline-container

# Run in debug mode
docker run -it --rm \
  --env DEBUG=1 \
  redline:latest /bin/bash

# Check system resources
docker system df
docker system prune  # Clean up if needed
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
docker run -it --rm \
  --env DEBUG=1 \
  --env LOG_LEVEL=DEBUG \
  redline:latest
```

### Health Checks

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health check logs
docker inspect redline-container | grep -A 10 Health
```

## ⚡ Performance Optimization

### Resource Limits

```bash
# Set memory and CPU limits
docker run -it --rm \
  --memory=4g \
  --cpus=2 \
  --volume $(pwd)/data:/app/data \
  redline:latest
```

### Volume Optimization

```bash
# Use named volumes for better performance
docker volume create redline-data
docker run -it --rm \
  --volume redline-data:/app/data \
  redline:latest
```

### Multi-stage Builds

The Dockerfile uses multi-stage builds for optimized image size:

```dockerfile
# Build stage
FROM ubuntu:24.04 as builder
# ... build dependencies ...

# Runtime stage
FROM ubuntu:24.04
# ... copy from builder ...
```

### Caching Strategies

```bash
# Use build cache
docker build --cache-from redline:latest -t redline:latest .

# Use registry cache
docker build --cache-from registry/redline:latest -t redline:latest .
```

## 🔒 Security Considerations

### Network Security

```bash
# Use custom network
docker network create redline-network
docker run -it --rm \
  --network redline-network \
  --publish 5900:5900 \
  redline:latest --mode=vnc
```

### Volume Security

```bash
# Use read-only volumes where possible
docker run -it --rm \
  --volume $(pwd)/data:/app/data:ro \
  redline:latest
```

### User Security

```bash
# Run as non-root user
docker run -it --rm \
  --user 1000:1000 \
  redline:latest
```

### Environment Security

```bash
# Use secrets for passwords
docker run -it --rm \
  --env VNC_PASSWORD_FILE=/run/secrets/vnc_password \
  --secret vnc_password \
  redline:latest
```

## 📊 Monitoring and Logging

### Log Management

```bash
# View real-time logs
docker logs -f redline-container

# Save logs to file
docker logs redline-container > redline.log

# Rotate logs
docker run -it --rm \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  redline:latest
```

### Resource Monitoring

```bash
# Monitor container resources
docker stats redline-container

# Monitor system resources
htop
```

## 🔄 Updates and Maintenance

### Updating the Image

```bash
# Pull latest changes
git pull

# Rebuild image
docker build -t redline:latest .

# Update running containers
docker-compose --profile vnc down
docker-compose --profile vnc up
```

### Backup and Restore

```bash
# Backup data
tar -czf redline-backup.tar.gz data/

# Restore data
tar -xzf redline-backup.tar.gz
```

### Cleanup

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [VNC Documentation](https://www.realvnc.com/docs/)
- [X11 Forwarding Guide](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding)

## 🆘 Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker logs <container-name>`
3. Check system requirements and prerequisites
4. Create an issue in the project repository

---

**Happy Dockerizing! 🐳**
