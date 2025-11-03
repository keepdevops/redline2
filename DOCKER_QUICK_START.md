# 🐳 REDLINE Docker Quick Start

## Quick Deployment Options

### 1. Web Interface (Recommended - Production Ready)

```bash
# Start REDLINE web interface
docker-compose up -d

# Or use the production image
docker run -d --name redline \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  keepdevops/redline:20251101

# Access at http://localhost:8080
```

### 2. X11 Mode (For Desktop GUI with X11)

```bash
# Allow X11 connections
xhost +local:docker

# Start REDLINE with X11 forwarding
./scripts/run_docker_x11.sh
```

### 3. Headless Mode (CLI Only)

```bash
# Run REDLINE in CLI mode
./scripts/run_docker_headless.sh cli

# Run REDLINE GUI with virtual display
./scripts/run_docker_headless.sh gui
```

### 4. Docker Compose (All Modes)

```bash
# Web Interface (Recommended)
docker-compose up -d
# Access at http://localhost:8080

# X11 Mode (For Desktop GUI)
docker-compose --profile x11 up

# Headless Mode
docker-compose --profile headless up

# Development Mode
docker-compose --profile dev up
```

## Prerequisites

- Docker 20.10+ with Docker Compose v2
- Ubuntu 20.04+ (tested on 24.04)
- 4GB RAM minimum

## Test Your Setup

```bash
# Run the test script
./test_docker_setup.sh
```

## Full Documentation

See [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) for comprehensive documentation.

## Troubleshooting

### Web Interface Issues
- Check if port 8080 is available: `netstat -tuln | grep 8080`
- Check container logs: `docker logs redline`
- Verify container is running: `docker ps`

### X11 Issues
- Set DISPLAY: `export DISPLAY=:0`
- Allow X11: `xhost +local:docker`
- Use web interface instead if X11 doesn't work

### Permission Issues
- Fix data permissions: `sudo chown -R $USER:$USER ./data`
- Run with user mapping: `docker run --user $(id -u):$(id -g) ...`

## Support

For detailed troubleshooting and advanced configuration, see the full [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md).
