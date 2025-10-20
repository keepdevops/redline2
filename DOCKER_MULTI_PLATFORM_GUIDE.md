# REDLINE Multi-Platform Docker Guide

This guide covers building and deploying REDLINE across different platforms using Docker.

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ with BuildKit support
- Docker Compose 2.0+
- Docker Buildx (for multi-platform builds)

### Basic Usage

```bash
# Build for current platform
./build_docker_all.sh

# Build for specific platform
./build_docker_all.sh -p amd64
./build_docker_all.sh -p arm64

# Build web-only images
./build_docker_all.sh -w

# Build multi-platform images
./build_docker_all.sh -m

# Test all platforms
./test_docker_multi_platform.sh
```

## 📋 Supported Platforms

| Platform | Architecture | Dockerfile | Status |
|----------|-------------|------------|---------|
| Intel/AMD | x86_64 (amd64) | `Dockerfile.x86` | ✅ Full Support |
| Apple Silicon | ARM64 | `Dockerfile.arm` | ✅ Full Support |
| ARM Servers | ARM64 | `Dockerfile.arm` | ✅ Full Support |
| Web Only | Any | `Dockerfile.web` | ✅ Optimized |

## 🏗️ Build Configurations

### 1. Full Application (Multi-Platform)

**Dockerfile**: `Dockerfile`
- Supports all modes: X11, VNC, Web, Headless
- Full GUI support with virtual display
- Optimized for each platform

```bash
# Build for current platform
docker build -t redline:latest .

# Build for specific platform
docker build --platform linux/amd64 -t redline:amd64 .
docker build --platform linux/arm64 -t redline:arm64 .
```

### 2. Web-Only Application

**Dockerfile**: `Dockerfile.web`
- Minimal image for web interface only
- Faster builds and smaller images
- Optimized for production deployment

```bash
# Build web-only image
docker build -f Dockerfile.web -t redline-web:latest .

# Build for specific platform
docker build --platform linux/amd64 -f Dockerfile.web -t redline-web:amd64 .
```

### 3. Platform-Optimized Builds

**x86_64**: `Dockerfile.x86`
- Optimized for Intel/AMD processors
- Uses x86-specific optimizations
- Higher thread counts for better performance

**ARM64**: `Dockerfile.arm`
- Optimized for Apple Silicon and ARM servers
- ARM-specific library optimizations
- Optimized thread counts for ARM processors

## 🐳 Docker Compose Profiles

### Available Profiles

```bash
# Web interface only
docker-compose --profile web up

# x86_64 optimized
docker-compose --profile x86 up

# ARM64 optimized (Apple Silicon)
docker-compose --profile arm up

# Traditional GUI with X11
docker-compose --profile x11 up

# Remote GUI with VNC
docker-compose --profile vnc up

# Headless CLI mode
docker-compose --profile headless up

# Development mode
docker-compose --profile dev up
```

### Environment Configuration

1. Copy the environment template:
```bash
cp docker.env.template docker.env
```

2. Customize the configuration:
```bash
# Edit docker.env
nano docker.env
```

3. Use with Docker Compose:
```bash
docker-compose --env-file docker.env --profile web up
```

## 🔧 Build Scripts

### build_docker_all.sh

Comprehensive build script for all platforms and configurations.

```bash
# Show help
./build_docker_all.sh --help

# Build all platforms
./build_docker_all.sh

# Build for specific platform
./build_docker_all.sh -p amd64
./build_docker_all.sh -p arm64

# Build web-only
./build_docker_all.sh -w

# Build multi-platform with buildx
./build_docker_all.sh -m

# Build and push to registry
./build_docker_all.sh -r myregistry.com --push
```

### test_docker_multi_platform.sh

Test script to verify builds work correctly across platforms.

```bash
# Run all tests
./test_docker_multi_platform.sh

# Tests include:
# - Individual platform builds
# - Multi-platform builds (if buildx available)
# - Docker Compose integration
# - Container functionality
```

## 🚀 Deployment Examples

### 1. Local Development

```bash
# Start web interface
docker-compose --profile web up -d

# Access at http://localhost:8080
```

### 2. Production Deployment

```bash
# Build production image
./build_docker_all.sh -w

# Run with production settings
docker run -d \
  --name redline-prod \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  redline-web:latest
```

### 3. Multi-Platform Registry

```bash
# Build and push to registry
./build_docker_all.sh -r myregistry.com --push

# Pull and run on any platform
docker run -d \
  --name redline \
  -p 8080:8080 \
  myregistry.com/redline:latest
```

### 4. Apple Silicon (M1/M2) Optimization

```bash
# Build ARM64 optimized image
./build_docker_all.sh -p arm64

# Run with ARM optimizations
docker run -d \
  --name redline-arm \
  --platform linux/arm64 \
  -p 8080:8080 \
  redline:arm64
```

## 🔍 Platform Detection

The build scripts automatically detect the current platform and optimize accordingly:

```bash
# Check current platform
docker version --format '{{.Server.Os}}/{{.Server.Arch}}'

# Check available platforms
docker buildx ls
```

## 📊 Performance Optimizations

### x86_64 Optimizations
- 8-thread OpenBLAS configuration
- Intel MKL support
- Optimized memory allocation
- SSE/AVX instruction sets

### ARM64 Optimizations
- 4-thread OpenBLAS configuration
- ARM-specific library paths
- Optimized for Apple Silicon
- NEON instruction set support

### Web-Only Optimizations
- Minimal base image (python:3.11-slim)
- Reduced dependencies
- Faster startup times
- Smaller image size

## 🛠️ Troubleshooting

### Common Issues

1. **Buildx not available**
   ```bash
   # Install buildx plugin
   docker buildx install
   ```

2. **Platform not supported**
   ```bash
   # Check available platforms
   docker buildx ls
   
   # Create new builder
   docker buildx create --name multiarch --use
   ```

3. **ARM64 build fails**
   ```bash
   # Enable emulation
   docker run --privileged --rm tonistiigi/binfmt --install all
   ```

4. **Permission issues**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER .
   chmod +x *.sh
   ```

### Debug Mode

```bash
# Build with debug output
DOCKER_BUILDKIT=0 docker build -t redline:debug .

# Run with debug logging
docker run -e DEBUG=true redline:debug
```

## 📈 Monitoring and Logs

### Health Checks

All images include health checks:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health check logs
docker inspect <container_name> | jq '.[0].State.Health'
```

### Logging

```bash
# View container logs
docker logs -f <container_name>

# View with timestamps
docker logs -f -t <container_name>
```

## 🔐 Security Considerations

### Best Practices

1. **Non-root user**: All containers run as `redline` user
2. **Minimal base images**: Web-only images use slim base
3. **Security scanning**: Regular vulnerability scans recommended
4. **Network isolation**: Use Docker networks for communication
5. **Secret management**: Use Docker secrets for sensitive data

### Security Scanning

```bash
# Scan image for vulnerabilities
docker scan redline:latest

# Scan with specific platform
docker scan --platform linux/amd64 redline:amd64
```

## 📚 Additional Resources

- [Docker Multi-Platform Builds](https://docs.docker.com/buildx/working-with-buildx/)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [REDLINE Documentation](../README.md)

## 🤝 Contributing

When adding new platform support:

1. Create platform-specific Dockerfile
2. Update build scripts
3. Add to docker-compose.yml
4. Update this documentation
5. Test on target platform

## 📄 License

This Docker configuration is part of the REDLINE project and follows the same license terms.
