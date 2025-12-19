# License Server Optimization Guide

## Optimizations Applied

### 1. **Dockerfile Optimizations**
- **Minimal dependencies**: Only install Flask, Flask-CORS, and Gunicorn (not entire requirements.txt)
- **Selective copying**: Copy only license server files instead of entire project
- **Production WSGI server**: Use Gunicorn instead of Flask dev server
- **Security**: Run as non-root user
- **Layer optimization**: Combined operations to reduce layers

### 2. **Code Optimizations**
- **Debounced file saves**: Save licenses at most every 5 seconds (reduces I/O)
- **Atomic writes**: Write to temp file then rename (prevents corruption)
- **Request caching**: Added middleware to ensure saves happen after requests
- **Threading enabled**: Better concurrent request handling

### 3. **Performance Improvements**
- **Before**: Flask dev server, saves on every operation
- **After**: Gunicorn with 2 workers, debounced saves

## Expected Improvements

- **Build time**: 50-70% faster (minimal dependencies)
- **Image size**: 60-80% smaller (only Flask dependencies)
- **Startup time**: Faster (fewer imports)
- **Request handling**: Better (Gunicorn + threading)
- **I/O performance**: Better (debounced saves)

## Usage

### Docker Build:
```bash
docker build -f Dockerfile.license-server -t redline-license-server:latest .
```

### Docker Run:
```bash
docker run -d \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -e LICENSE_SERVER_PORT=5001 \
  redline-license-server:latest
```

### Local Development (with Gunicorn):
```bash
# Install gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 2 -b 0.0.0.0:5001 --threads 2 licensing.server.license_server:app
```

### Local Development (Flask dev server):
```bash
python3 licensing/server/license_server.py
```

## Configuration

Environment variables:
- `LICENSE_SERVER_PORT`: Port to run on (default: 5001)
- `LICENSE_SECRET_KEY`: Secret key for license generation
- `FLASK_ENV`: Set to 'production' for production mode
- `USE_GUNICORN`: Set to 'true' to use Gunicorn (if running directly)
- `DEBUG`: Set to 'true' for debug mode

