# REDLINE Uncompiled Docker Image Setup

## Overview

This document outlines the uncompiled Docker image setup for REDLINE, designed for development and debugging purposes. The uncompiled version maintains the same multi-platform structure as the existing optimized and compiled versions while removing compilation steps that can make debugging difficult.

## Files Created

### 1. Dockerfile.webgui.uncompiled
- **Purpose**: Main Docker image definition for uncompiled version
- **Key Features**:
  - Multi-stage build for efficient image size
  - Removes Python bytecode compilation (`PYTHONDONTWRITEBYTECODE=0`)
  - Skips asset minification for easier debugging  
  - Uses development Flask environment
  - Gunicorn with reload enabled and debug logging
  - Relaxed worker settings (1 worker, 2 threads vs production settings)

### 2. build_multiplatform_uncompiled.sh
- **Purpose**: Production build script for pushing to registries
- **Features**:
  - Builds for AMD64 and ARM64 platforms simultaneously
  - Creates tags: `uncompiled`, `dev`, `debug`, and versioned variants
  - Pushes to Docker registry for distribution
  - Uses Docker BuildX for multi-platform support

### 3. build_multiplatform_uncompiled_local.sh  
- **Purpose**: Local development build script
- **Features**:
  - Builds multi-platform images locally without pushing
  - Loads ARM64 version for local testing on M3 machines
  - Includes comprehensive testing and health check validation
  - Efficient disk space management

### 4. docker-compose-dev.yml
- **Purpose**: Development environment orchestration
- **Features**:
  - Pre-configured for uncompiled image
  - Optional Redis and PostgreSQL services
  - Volume mounts for data persistence
  - Support for live source code mounting
  - Multiple profiles for different development needs

### 5. test_uncompiled_build.sh
- **Purpose**: Comprehensive testing script
- **Features**:
  - Automated build and deployment testing
  - Health check validation
  - Container status monitoring
  - Detailed logging and error reporting

## Key Differences from Compiled Versions

| Feature | Compiled Version | Uncompiled Version |
|---------|------------------|-------------------|
| Python Bytecode | Pre-compiled with `compileall` | Source files preserved |
| Asset Minification | CSS/JS minified | Original files maintained |
| Flask Environment | Production | Development |
| Gunicorn Workers | 2+ workers, optimized | 1 worker, reload enabled |
| Logging Level | Info | Debug |
| Startup Time | ~20% faster | Standard Python startup |
| Image Purpose | Production deployment | Development/debugging |

## Configuration Fixes Applied

### Gunicorn Configuration
Fixed issues in `gunicorn.conf.py`:
- Changed user from 'redline' to 'appuser' (matches Docker user)
- Changed group from 'redline' to 'appuser'
- Updated pidfile path from `/var/run/redline/gunicorn.pid` to `/tmp/gunicorn.pid`

## Usage Examples

### Basic Development
```bash
# Build uncompiled image locally
./build_multiplatform_uncompiled_local.sh

# Run with docker-compose
docker-compose -f docker-compose-dev.yml up -d

# Direct docker run
docker run -d -p 8080:8080 -v redline-data:/app/data redline-webgui:dev
```

### Live Development with Source Mounting
```bash
# Mount source code for live editing
docker run -d -p 8080:8080 \
  -v $(pwd):/app \
  -v redline-data:/app/data \
  redline-webgui:dev
```

### Multi-Platform Production Build
```bash
# Build and push multi-platform images
./build_multiplatform_uncompiled.sh
```

## Available Image Tags

| Tag | Description | Use Case |
|-----|-------------|----------|
| `redline-webgui:uncompiled` | Main uncompiled version | General development |
| `redline-webgui:dev` | Development alias | Development workflows |
| `redline-webgui:debug` | Debug alias | Debugging sessions |
| `redline-webgui:v1.0.0-multiplatform-uncompiled` | Versioned release | Specific version deployment |

## Platform Support

✅ **AMD64** (Intel/Dell machines)  
✅ **ARM64** (Apple Silicon M1/M2/M3)  
🔄 **Automatic platform detection and deployment**

## Development Benefits

1. **Source Code Visibility**: Python files remain uncompiled for easier debugging
2. **Live Reload**: Gunicorn reload enables development without rebuilds
3. **Debug Logging**: Verbose logging for troubleshooting
4. **Asset Accessibility**: Original CSS/JS files for frontend debugging
5. **Development Environment**: Flask debug mode enabled
6. **Container Persistence**: Development data persists across restarts

## Testing Results

✅ **Image builds successfully** on ARM64 (M3 native)  
✅ **Health endpoint responding** (`/health` returns JSON status)  
✅ **Web interface accessible** (serves HTML correctly)  
✅ **Multi-platform support** (AMD64 + ARM64 manifests created)  
✅ **Configuration issues resolved** (Gunicorn user/pidfile fixed)  

## Next Steps

1. **Cross-Platform Testing**: Test on AMD64 systems (Dell machines)
2. **Development Workflow**: Integrate with IDE debugging tools
3. **Documentation**: Add debugging guides for development team
4. **CI/CD Integration**: Include uncompiled builds in pipeline
5. **Performance Baseline**: Establish development vs production metrics

## Notes

- **Not for Production**: This image is specifically for development/debugging
- **Performance**: Slower startup and runtime compared to compiled versions
- **Memory Usage**: May use more memory due to lack of optimization
- **Security**: Uses development settings, not hardened for production

## Architecture Support Matrix

| Platform | Build Status | Test Status | Notes |
|----------|-------------|-------------|-------|
| ARM64 (M3) | ✅ Successful | ✅ Verified | Native testing completed |
| AMD64 (Intel) | ✅ Successful | ⏳ Pending | Cross-platform manifest ready |
| Multi-Platform | ✅ Successful | ⏳ Pending | BuildX manifests created |

---

**Created**: October 29, 2025  
**Status**: Ready for Development Use  
**Maintainer**: REDLINE Development Team
