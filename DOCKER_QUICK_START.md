# 🐳 REDLINE Docker Quick Start

## Quick Deployment Options

### 1. VNC Mode (Recommended for Remote Access)

```bash
# Start REDLINE with VNC server
./scripts/run_docker_vnc.sh

# Connect with VNC client
vncviewer localhost:5900
# Password: redline123
```

### 2. X11 Mode (For Local Development)

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
# VNC Mode
docker-compose --profile vnc up

# X11 Mode
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

### VNC Connection Issues
- Check if port 5900 is available: `netstat -tuln | grep 5900`
- Try different VNC client: `sudo apt-get install tigervnc-viewer`
- Check container logs: `docker logs redline-vnc`

### X11 Issues
- Set DISPLAY: `export DISPLAY=:0`
- Allow X11: `xhost +local:docker`
- Use VNC mode instead if X11 doesn't work

### Permission Issues
- Fix data permissions: `sudo chown -R $USER:$USER ./data`
- Run with user mapping: `docker run --user $(id -u):$(id -g) ...`

## Support

For detailed troubleshooting and advanced configuration, see the full [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md).
