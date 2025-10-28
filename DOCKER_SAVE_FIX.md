# Docker Save Issue - Multi-Platform Image Fix

## Problem
`docker save` only saved the ARM64 version of the multi-platform image, not the AMD64 version needed for the Dell machine.

## Root Cause
When using `docker buildx build --load` with multiple platforms, Docker only loads the image for the current architecture (ARM64 on M3 Mac). The AMD64 version exists in the build cache but isn't loaded locally.

## Solutions

### Solution 1: Build AMD64 Image Specifically for Dell
```bash
# Build only AMD64 version for Dell machine
docker buildx build --platform linux/amd64 \
  -f Dockerfile.webgui.simple \
  -t redline-webgui:amd64 --load .

# Save AMD64 image
docker save redline-webgui:amd64 -o redline-webgui-amd64.tar

# Transfer to Dell machine
scp redline-webgui-amd64.tar user@dell-machine:/home/user/

# On Dell machine
docker load -i redline-webgui-amd64.tar
docker tag redline-webgui:amd64 redline-webgui:latest
```

### Solution 2: Push to Registry (Recommended)
```bash
# Tag for registry (replace with your registry)
docker tag redline-webgui:latest your-registry/redline-webgui:latest

# Push multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 \
  -f Dockerfile.webgui.simple \
  -t your-registry/redline-webgui:latest --push .

# On Dell machine
docker pull your-registry/redline-webgui:latest
```

### Solution 3: Build Directly on Dell Machine (Simplest)
```bash
# On Dell machine
git clone https://github.com/keepdevops/redline2.git
cd redline2
git pull origin main

# Build for local architecture (AMD64)
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .

# Start container
docker run -d --name redline-webgui -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest
```

### Solution 4: Export/Import with Buildx
```bash
# Build and export to tar for specific platform
docker buildx build --platform linux/amd64 \
  -f Dockerfile.webgui.simple \
  -o type=docker,dest=redline-webgui-amd64.tar .

# Transfer and load on Dell
docker load -i redline-webgui-amd64.tar
```

## Verification Commands

### Check Current Image Architecture
```bash
docker inspect redline-webgui:latest | grep Architecture
# Should show: "Architecture": "amd64" on Dell machine
```

### Check Multi-Platform Support
```bash
# Only works with registry images
docker manifest inspect your-registry/redline-webgui:latest
```

### Test Container on Dell
```bash
# Start container
docker run -d --name redline-webgui -p 8080:8080 redline-webgui:latest

# Check it's running (not restarting)
docker ps | grep redline-webgui
# Should show: Up X seconds (not Restarting)

# Check logs
docker logs redline-webgui
# Should show Gunicorn workers starting, no "No such user" errors

# Test web interface
curl http://localhost:8080/health
# Should return: {"status":"healthy","service":"redline-web"}
```

## Recommended Approach for Dell Machine

**Use Solution 3** (build directly on Dell) because:
- ✅ Simplest - no file transfers needed
- ✅ Always correct architecture
- ✅ Latest code from GitHub
- ✅ No registry setup required
- ✅ Faster than transferring 650MB+ files

## Commands for Dell Machine
```bash
# 1. Clone/update repository
git clone https://github.com/keepdevops/redline2.git
cd redline2
git pull origin main

# 2. Build optimized image
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .

# 3. Start container
docker run -d --name redline-webgui -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest

# 4. Verify
docker ps | grep redline-webgui
curl http://localhost:8080/health
```

## Expected Results on Dell
- ✅ Container stays running (not restarting)
- ✅ Shows 2 Gunicorn worker processes
- ✅ Web interface accessible at http://localhost:8080
- ✅ Health check returns success
- ✅ All features work (upload, download, analysis)

The key insight is that multi-platform images need special handling for transfer between different architectures. Building directly on the target machine is often the most reliable approach.
