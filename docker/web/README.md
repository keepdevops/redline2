# REDLINE Web App Docker Usage Guide

## Quick Start

### 1. Build Web App Image
```bash
./build.sh
```

### 2. Start Web App Container
```bash
./start_web_container.sh
```

### 3. Test Installation
```bash
./test_web.sh
```

### 4. Access Web Application
- **Direct Flask**: http://localhost:5000
- **Via Nginx**: http://localhost:80

### 5. Run Web App
```bash
# Access container
docker exec -it redline-web-container bash

# Activate environment
source /opt/conda/bin/activate redline-web

# Development mode
./start_web.sh

# Production mode (with Gunicorn)
./start_production.sh
```

## Platform Support

This Docker image supports:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## Web App Features

- **Flask-based web interface**
- **Real-time data processing**
- **Interactive charts and visualizations**
- **File upload and processing**
- **REST API endpoints**
- **WebSocket support for real-time updates**
- **Production-ready with Gunicorn**
- **Nginx reverse proxy**

## Production Deployment

### Using Gunicorn
```bash
# Start production server
./start_production.sh

# Or manually
source /opt/conda/bin/activate redline-web
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent web_app:app
```

### Using Nginx (Reverse Proxy)
```bash
# Nginx is pre-configured and running
# Access via: http://localhost:80
```

## API Endpoints

- **GET /**: Main dashboard
- **POST /upload**: File upload
- **GET /data**: Data processing
- **GET /charts**: Chart generation
- **WebSocket /socket.io**: Real-time updates

## Environment Variables

```bash
export FLASK_APP=web_app.py
export FLASK_ENV=production
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
```

## Commands

```bash
# Build image
./build.sh

# Start container
./start_web_container.sh

# Test web app
./test_web.sh

# Remove container
docker rm -f redline-web-container

# Remove image
docker rmi redline-web
```

## Troubleshooting

### Port Issues
```bash
# Check if ports are available
netstat -tlnp | grep :5000
netstat -tlnp | grep :80
```

### Web App Not Loading
```bash
# Check container status
docker ps

# Check logs
docker logs redline-web-container

# Test web app directly
docker exec -it redline-web-container ./test_web.sh
```

### Platform Issues
```bash
# Check platform
uname -m

# Force specific platform
docker buildx build --platform linux/amd64 --tag redline-web --load .
```
