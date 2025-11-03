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

# Web Interface (Recommended - Production Ready)
docker-compose up -d
# Access at http://localhost:8080

# X11 Mode (For Desktop GUI)
docker-compose --profile x11 up

# Headless Mode (CLI only)
docker-compose --profile headless up

# Development Mode
docker-compose --profile dev up
```

### Option 2: Scripts

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Web Interface (Production)
docker run -d --name redline -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  keepdevops/redline:20251101

# X11 Mode (Desktop GUI)
./scripts/run_docker_x11.sh

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

# No additional clients needed for web interface
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

### 2. Web Interface (Production Ready)

**Best for**: Production deployments, remote access, cloud deployments

```bash
# Using Docker Compose
docker-compose up -d

# Using production image
docker run -d --name redline \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  keepdevops/redline:20251101
```

**Features**:
- Modern web interface
- RESTful API access
- Multi-user support
- Production-ready Gunicorn server
- No additional clients required

**Access**:
- URL: http://localhost:8080
- Swagger API Docs: http://localhost:8080/docs
- Dashboard: http://localhost:8080/dashboard

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
DISPLAY=:0  # For X11 mode only
WEB_PORT=8080
```

### Profile-based Deployment

```bash
# List available profiles
docker-compose config --profiles

# Run specific profile
docker-compose up -d  # Web interface (default, recommended)
docker-compose --profile x11 up  # Desktop GUI with X11
docker-compose --profile headless up  # CLI mode
docker-compose --profile dev up  # Development mode

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Configuration

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  redline-web:
    environment:
      - PORT=8080
    volumes:
      - ./custom-data:/app/data
      - ./config:/app/config
    ports:
      - "8080:8080"  # Web interface port
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

# With custom environment (Web interface)
docker run -d --name redline \
  --env PORT=8080 \
  --publish 8080:8080 \
  -v $(pwd)/data:/app/data \
  keepdevops/redline:20251101

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
docker stop redline

# Remove container
docker rm redline

# View container logs
docker logs redline

# Execute command in running container
docker exec -it redline /bin/bash

# Copy files to/from container
docker cp redline:/app/data ./local-data
docker cp ./local-file redline:/app/
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

# Alternative: Use web interface instead
docker-compose up -d
# Access at http://localhost:8080
```

#### 2. Web Interface Connection Issues

**Problem**: Cannot access web interface

**Solutions**:
```bash
# Check if web port is accessible
curl http://localhost:8080/health

# Check container logs
docker logs redline

# Verify container is running
docker ps | grep redline

# Test web interface
curl http://localhost:8080
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
  --publish 8080:8080 \
  keepdevops/redline:20251101
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
# Use secrets for sensitive configuration
docker run -d \
  --env SECRET_KEY_FILE=/run/secrets/secret_key \
  --secret secret_key \
  -p 8080:8080 \
  keepdevops/redline:20251101
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
docker-compose down
docker-compose up -d
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
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [X11 Forwarding Guide](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding)

## 🆘 Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker logs <container-name>`
3. Check system requirements and prerequisites
4. Create an issue in the project repository

---

**Happy Dockerizing! 🐳**
