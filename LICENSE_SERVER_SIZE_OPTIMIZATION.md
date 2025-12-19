# License Server Size Optimization

## Optimizations Applied

### 1. **Multi-Stage Build**
- **Builder stage**: Installs dependencies only
- **Runtime stage**: Copies only installed packages, not source code
- **Result**: Final image contains only runtime files

### 2. **Minimal Dependencies**
- **Before**: Entire requirements.txt (~500MB+ with pandas, numpy, etc.)
- **After**: Only Flask and Flask-CORS (~50MB)
- **Reduction**: ~90% smaller dependency footprint

### 3. **Selective File Copying**
- **Before**: `COPY . /app/` (entire project, ~5GB with data/)
- **After**: Only license server files + config_paths utility
- **Reduction**: ~99% smaller file footprint

### 4. **Minimal Runtime Dependencies**
- Only curl for healthcheck
- No build tools in final image
- No unnecessary system packages

## Expected Size Reduction

**Before:**
- Base image: ~150MB (python:3.11-slim)
- Dependencies: ~500MB (full requirements.txt)
- Application files: ~5GB (entire project)
- **Total: ~5.6GB**

**After:**
- Base image: ~150MB (python:3.11-slim)
- Dependencies: ~50MB (Flask + Flask-CORS only)
- Application files: ~1MB (license server files only)
- **Total: ~200MB**

**Size reduction: ~96% smaller (5.6GB → 200MB)**

## Build and Test

```bash
# Build optimized image
docker build -f Dockerfile.license-server -t redline-license-server:optimized .

# Check image size
docker images | grep redline-license-server

# Run container
docker run -d -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  redline-license-server:optimized

# Test health endpoint
curl http://localhost:5001/api/health
```

## What's Included

✅ Flask and Flask-CORS (only web framework dependencies)
✅ License server Python files
✅ Config paths utility (for license file location)
✅ curl (for healthcheck)

## What's Excluded

❌ Entire requirements.txt (pandas, numpy, etc.)
❌ All other application code
❌ Data files
❌ Documentation
❌ Build tools
❌ Test files

