# REDLINE Web GUI Build Scripts

This directory contains scripts to build, run, and manage the REDLINE Web GUI Docker container.

## Scripts Overview

### 🚀 `start_web_gui.sh` - Master Startup Script
**One-command solution to build and start REDLINE Web GUI**

```bash
# Basic usage - build and start
./scripts/build/start_web_gui.sh

# Clean build and start
./scripts/build/start_web_gui.sh --clean

# Run in foreground to see logs
./scripts/build/start_web_gui.sh --foreground

# Use custom port
./scripts/build/start_web_gui.sh --port 8081
```

### 🔨 `build_web_gui.sh` - Build Script
**Builds the Docker image without BuildKit issues**

```bash
# Basic build
./scripts/build/build_web_gui.sh

# Clean build (removes old images)
./scripts/build/build_web_gui.sh --clean

# Custom options
./scripts/build/build_web_gui.sh --name my-redline --tag v1.0 --platform linux/amd64
```

### ▶️ `run_web_gui.sh` - Run Script
**Runs the Docker container**

```bash
# Run in background (default)
./scripts/build/run_web_gui.sh

# Run in foreground to see logs
./scripts/build/run_web_gui.sh --foreground

# Custom port
./scripts/build/run_web_gui.sh --port 8081
```

### 🛑 `shutdown_web_gui.sh` - Shutdown Script
**Stops and removes the container**

```bash
# Basic shutdown
./scripts/build/shutdown_web_gui.sh

# Remove images too
./scripts/build/shutdown_web_gui.sh --remove-image

# Clean everything
./scripts/build/shutdown_web_gui.sh --cleanup-all
```

## Quick Start for HP AMD64 Ubuntu

1. **One-command startup:**
   ```bash
   ./scripts/build/start_web_gui.sh
   ```

2. **Access in Firefox:**
   ```
   http://localhost:8080
   ```

3. **Shutdown when done:**
   ```bash
   ./scripts/build/shutdown_web_gui.sh
   ```

## Features

- ✅ **No BuildKit issues** - Uses standard Docker build
- ✅ **AMD64 compatible** - Built for HP Ubuntu machines
- ✅ **Flask web interface** - Full web GUI with real-time updates
- ✅ **Volume persistence** - Data survives container restarts
- ✅ **Port management** - Automatic port conflict detection
- ✅ **Container management** - Easy start/stop/restart
- ✅ **Log viewing** - Access container logs
- ✅ **Clean shutdown** - Proper cleanup options

## Prerequisites

- Docker installed and running
- Ubuntu 24.04 LTS (or compatible)
- AMD64 architecture
- Internet connection for downloading dependencies

## Troubleshooting

### OCI Shim Errors
These scripts avoid BuildKit issues that cause OCI shim errors by using standard Docker builds.

### Port Conflicts
Scripts automatically detect port conflicts and suggest alternatives.

### Permission Issues
Run with appropriate permissions:
```bash
sudo ./scripts/build/start_web_gui.sh
```

## Web Interface Features

Once running, the web interface provides:
- Data downloading and viewing
- Analysis and visualization
- Format conversion
- Real-time updates via SocketIO
- Background task processing
- Modern responsive UI

## Management Commands

```bash
# View logs
docker logs redline-web-gui

# Restart container
docker restart redline-web-gui

# Shell access
docker exec -it redline-web-gui /bin/bash

# Check status
docker ps --filter name=redline-web-gui
```
