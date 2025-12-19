# VarioSync License Server - Standalone Optimization

## Overview

The license server has been separated from the main VarioSync application and optimized for minimal size and independence.

## Key Changes

### 1. **Standalone License Server** (`license_server_standalone.py`)
- **No dependencies** on VarioSync application code
- **No imports** from `redline.utils.config_paths`
- **Self-contained** license file path management
- **Same functionality** as original, but completely independent

### 2. **Optimized Dockerfile** (`Dockerfile.license-server`)
- **Multi-stage build** (builder + runtime)
- **Minimal dependencies**: Only Flask + Flask-CORS (~50MB vs ~500MB)
- **No VarioSync code**: Only standalone license server file
- **No duplication**: Completely separate from main app

### 3. **Size Optimization**
- **Before**: ~5.6GB (full VarioSync app + requirements.txt)
- **After**: ~200MB (Flask + Flask-CORS + standalone server)
- **Reduction**: ~96% smaller

## Build and Deploy

### Build Standalone License Server:
```bash
docker build -f Dockerfile.license-server -t variosync-license-server:standalone .
```

### Run Standalone License Server:
```bash
docker run -d \
  -p 5001:5001 \
  -v variosync-licenses:/app/data \
  -e LICENSE_SERVER_PORT=5001 \
  -e LICENSE_DB_FILE=/app/data/licenses.json \
  variosync-license-server:standalone
```

### Check Image Size:
```bash
docker images | grep variosync-license-server
```

## What's Included

✅ Flask and Flask-CORS (only web framework)
✅ Standalone license server (no VarioSync dependencies)
✅ curl (for healthcheck)

## What's Excluded

❌ Entire VarioSync application code
❌ requirements.txt (pandas, numpy, etc.)
❌ All redline/ modules
❌ Data files
❌ Documentation

## Benefits

1. **Complete Separation**: License server is independent
2. **Minimal Size**: 96% smaller image
3. **Fast Builds**: Only installs Flask dependencies
4. **Easy Deployment**: Can be deployed separately
5. **No Duplication**: Single standalone service

