# Ubuntu Test Guide - Optimized REDLINE Docker Build

## Quick Start

### 1. Copy to Ubuntu Test Machine
```bash
# On your Mac
scp -r /Users/caribou/redline ubuntu-user@ubuntu-test-ip:/home/ubuntu/

# Or clone from GitHub
git clone https://github.com/keepdevops/redline2.git
cd redline2
```

### 2. Run Test Script
```bash
# Make executable
chmod +x test_ubuntu_optimized.sh

# Run full test suite
./test_ubuntu_optimized.sh
```

### 3. Access Application
```
http://ubuntu-test-ip:8080
```

## Manual Testing Steps

### Step 1: Prerequisites
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Build Image
```bash
cd /path/to/redline
DOCKER_BUILDKIT=1 docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .
```

**Expected Output:**
- Build time: ~2-3 minutes (first time), ~30 seconds (cached)
- Final image size: ~200 MB
- Success message: "Successfully built"

**Optimizations visible:**
- "Using cache" for build layers
- Multi-stage build output
- Minified assets creation
- Python bytecode compilation

### Step 3: Start Container
```bash
docker run -d \
  --name redline-webgui \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest
```

### Step 4: Verify Deployment

#### Check Container Status
```bash
docker ps
# Should show: redline-webgui  Up X minutes
```

#### Check Gunicorn Workers
```bash
docker exec redline-webgui ps aux | grep gunicorn
# Should show: 2 worker processes
```

#### Check Application Health
```bash
curl http://localhost:8080/health
# Should return: {"status":"healthy","service":"redline-web"}
```

#### View Logs
```bash
docker logs -f redline-webgui
# Should show: "Booting worker" x2, then "Listening at: http://0.0.0.0:8080"
```

#### Check Minified Assets
```bash
docker exec redline-webgui ls -lh /app/redline/web/static/js/*.min.js
docker exec redline-webgui ls -lh /app/redline/web/static/css/*.min.css
# Should show minified files with smaller sizes
```

## Feature Testing Checklist

### ✅ File Management
- [ ] Upload CSV file
- [ ] View uploaded file in file list
- [ ] Download file
- [ ] Delete file

### ✅ Data Viewing
- [ ] Load data from CSV
- [ ] View table with pagination
- [ ] Search/filter data
- [ ] Sort columns
- [ ] Export to different format

### ✅ Data Download
- [ ] Download single ticker from Yahoo Finance
- [ ] Batch download multiple tickers
- [ ] View download progress
- [ ] Verify downloaded data

### ✅ Analysis
- [ ] Run financial analysis
- [ ] Run correlation analysis
- [ ] View results/charts
- [ ] Export analysis results

### ✅ File Conversion
- [ ] Convert CSV to Parquet
- [ ] Convert CSV to JSON
- [ ] Convert CSV to Feather
- [ ] Convert CSV to DuckDB

### ✅ Settings
- [ ] Change theme (Light/Dark/Grayscale)
- [ ] Test database connection
- [ ] View system information
- [ ] Check application logs

## Performance Verification

### 1. Response Time
```bash
# Test health endpoint response time
time curl -s http://localhost:8080/health
# Expected: < 100ms
```

### 2. Concurrent Requests
```bash
# Test 10 concurrent requests
for i in {1..10}; do
  curl -s http://localhost:8080/health &
done
wait
```

### 3. Resource Usage
```bash
# Check memory and CPU usage
docker stats redline-webgui --no-stream
# Expected:
# - Memory: ~150-300 MB
# - CPU: < 5% at idle
```

### 4. Build Cache Efficiency
```bash
# First build (no cache)
time docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .
# Note: ~2-3 minutes

# Second build (with cache)
time docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .
# Note: ~30 seconds (75% faster)
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs redline-webgui

# Check if port is already in use
sudo netstat -tlnp | grep 8080

# Check Docker logs
sudo journalctl -u docker
```

### Application Not Responding
```bash
# Check container status
docker ps -a | grep redline-webgui

# Restart container
docker restart redline-webgui

# Check health
curl http://localhost:8080/health
```

### Gunicorn Not Starting
```bash
# Check container logs
docker logs redline-webgui 2>&1 | grep -i error

# Check running processes
docker exec redline-webgui ps aux | grep gunicorn

# Restart with shell access
docker exec -it redline-webgui bash
gunicorn --help
```

### Minified Assets Not Loading
```bash
# Check if minified files exist
docker exec redline-webgui ls -lh /app/redline/web/static/js/

# Check build logs for minification step
docker logs redline-webgui | grep -i minif

# Rebuild with verbose output
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest . --progress=plain
```

### Out of Memory
```bash
# Check available memory
free -h

# Increase Docker memory limit
# Edit /etc/docker/daemon.json:
# {
#   "default-ulimits": {
#     "memlock": {
#       "hard": -1,
#       "soft": -1
#     }
#   }
# }
# sudo systemctl restart docker
```

### Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Check disk space
df -h

# Rebuild with no cache
docker build --no-cache -f Dockerfile.webgui.simple -t redline-webgui:latest .
```

## Security Testing

### Check for Vulnerabilities
```bash
# Install pip-audit
pip install pip-audit

# Check installed packages in container
docker exec redline-webgui pip-audit

# Or build with vulnerability scanning
docker scout cves redline-webgui:latest
```

### Verify Non-Root User
```bash
# Check running user
docker exec redline-webgui whoami
# Should return: appuser

# Check process ownership
docker exec redline-webgui ps aux | head
# Should show appuser (not root)
```

## Expected Results

### Build Metrics
- **Build time (first)**: ~2-3 minutes
- **Build time (cached)**: ~30 seconds
- **Image size**: ~200 MB
- **Build cache hits**: 8-10 layers

### Runtime Metrics
- **Memory usage**: 150-300 MB
- **CPU usage (idle)**: < 5%
- **Response time**: < 100ms
- **Gunicorn workers**: 2
- **Threads per worker**: 4
- **Concurrent capacity**: 8 requests

### Asset Sizes
- **main.js**: ~14 KB (minified)
- **main.css**: ~12 KB (minified)
- **Total assets**: ~51 KB (66% reduction)

## Success Criteria

✅ Container starts without errors  
✅ Health check passes  
✅ Web interface loads at http://localhost:8080  
✅ All features work (upload, download, analysis, conversion)  
✅ Gunicorn shows 2 workers  
✅ Response times < 100ms  
✅ Minified assets load correctly  
✅ Application runs as non-root user  
✅ Memory usage < 300 MB  
✅ Build time (cached) < 1 minute  

## Next Steps After Testing

1. **Document Results**: Record test results, metrics, and any issues
2. **Update Documentation**: Add any Ubuntu-specific notes
3. **Security**: Update vulnerable packages if needed
4. **Performance**: Benchmark and compare with previous builds
5. **Deployment**: If tests pass, ready for production use

## Support

For issues or questions:
- Check `DOCKER_OPTIMIZATION_COMPLETE.md` for optimization details
- Check logs: `docker logs redline-webgui`
- Test script: `./test_ubuntu_optimized.sh`

