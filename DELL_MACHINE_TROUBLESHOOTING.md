# Dell Machine Docker Build Troubleshooting

## Issue
Container starts but exits immediately (up less than 1 second) with no logs on Dell machine.

## Diagnosis Steps

### 1. Check Docker Installation
```bash
docker --version
docker info
docker run --rm hello-world
```

### 2. Check Available Images
```bash
docker images
```
If no `redline-webgui:latest` image exists, the build failed or wasn't completed.

### 3. Check System Resources
```bash
# Check disk space
df -h

# Check memory
free -h

# Check Docker space usage
docker system df
```

### 4. Build Image Step by Step

#### Option A: Use Regular Dockerfile (Larger but More Compatible)
```bash
docker build -f Dockerfile -t redline-webgui:latest .
```

#### Option B: Use Optimized Dockerfile
```bash
DOCKER_BUILDKIT=1 docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .
```

#### Option C: Build with Verbose Output
```bash
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest . --progress=plain --no-cache
```

### 5. Test Container Startup
```bash
# Start container with logs
docker run --name redline-webgui-test -p 8080:8080 redline-webgui:latest

# In another terminal, check logs immediately
docker logs -f redline-webgui-test

# Check container status
docker ps -a
```

### 6. Debug Container Issues

#### If Container Exits Immediately:
```bash
# Check exit code
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.ExitCode}}"

# Run with interactive shell to debug
docker run -it --entrypoint /bin/bash redline-webgui:latest

# Inside container, test manually:
cd /app
python3 web_app.py
```

#### If Build Fails:
```bash
# Clean Docker cache
docker system prune -a

# Try building with more memory
docker build --memory=4g -f Dockerfile.webgui.simple -t redline-webgui:latest .

# Check build logs
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest . 2>&1 | tee build.log
```

## Common Issues and Solutions

### Issue 1: "No space left on device"
```bash
# Clean Docker
docker system prune -a -f

# Check disk space
df -h

# Clean system if needed
sudo apt-get clean
sudo apt-get autoremove
```

### Issue 2: Build gets interrupted
- Check if system is running out of memory
- Try building with `--memory=2g` flag
- Build during off-peak hours
- Disable other applications during build

### Issue 3: Python import errors in container
```bash
# Test Python dependencies
docker run -it redline-webgui:latest python3 -c "import flask; print('Flask OK')"
docker run -it redline-webgui:latest python3 -c "import pandas; print('Pandas OK')"
docker run -it redline-webgui:latest python3 -c "import yfinance; print('yfinance OK')"
```

### Issue 4: Port conflicts
```bash
# Check what's using port 8080
sudo netstat -tlnp | grep 8080

# Use different port
docker run -d --name redline-webgui -p 8081:8080 redline-webgui:latest
```

## Quick Fix Commands

### Complete Reset and Rebuild
```bash
# Stop and remove all containers
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Remove all images
docker rmi $(docker images -q) 2>/dev/null || true

# Clean system
docker system prune -a -f

# Rebuild
git pull origin main
docker build -f Dockerfile -t redline-webgui:latest .

# Start container
docker run -d --name redline-webgui -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest

# Check logs
docker logs -f redline-webgui
```

### Use Pre-built Image (if available)
```bash
# Pull from registry instead of building
docker pull your-registry/redline-webgui:latest
docker tag your-registry/redline-webgui:latest redline-webgui:latest
```

## Expected Behavior

### Successful Build
- Build time: 3-5 minutes (first time)
- Final image size: 200MB-2GB depending on Dockerfile
- No error messages during build

### Successful Container Start
- Container status: "Up X seconds" (not "Exited")
- Logs show: "Starting REDLINE Web Application..."
- Web interface accessible at http://localhost:8080
- Health check passes: `curl http://localhost:8080/health`

## Dell-Specific Considerations

1. **Architecture**: Ensure Docker images match Dell machine architecture (x86_64)
2. **Resources**: Dell machines may have limited RAM/disk - monitor usage
3. **Network**: Corporate networks may block Docker Hub - check connectivity
4. **Security**: Corporate security software may interfere with Docker

## Support Commands

```bash
# System info
uname -a
docker version
docker info

# Resource usage
free -h
df -h
docker system df

# Network test
curl -I https://hub.docker.com

# Container debugging
docker run --rm -it redline-webgui:latest /bin/bash
```

## Next Steps

1. Run diagnosis steps above
2. Try building with regular Dockerfile first
3. If build succeeds, test container startup
4. If container exits immediately, check logs and debug interactively
5. Report specific error messages for further troubleshooting
