# REDLINE Docker Compose Management Guide

## Overview

This guide covers the complete Docker Compose management for REDLINE Option 4 installation, including the simple Docker Compose configuration and comprehensive management commands.

## Docker Compose Configuration

### Simple Configuration (Option 4)

The Docker Compose configuration created by Option 4 provides a clean, single-service setup:

```yaml
# REDLINE Docker Compose Configuration (Fixed)
# Simple web app + web GUI setup without dependency cycles

services:
  # REDLINE Web App + Web GUI (using working Option 1 approach)
  redline-webgui:
    build:
      context: .
      dockerfile: Dockerfile.webgui.universal
    image: redline-webgui:latest
    container_name: redline-web-app
    restart: unless-stopped
    
    # Ports
    ports:
      - "8080:8080"    # Flask web app
      - "6080:6080"    # noVNC web GUI
    
    # Environment variables
    environment:
      - FLASK_APP=web_app.py
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=8080
      - VNC_PASSWORD=redline123
      - DISPLAY=:1
      - VNC_PORT=5901
      - NO_VNC_PORT=6080
    
    # Volumes
    volumes:
      - ./data:/opt/redline/data
      - ./logs:/var/log/redline
      - ./config:/opt/redline/config
    
    # Working directory
    working_dir: /opt/redline
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.25'

# Networks
networks:
  default:
    driver: bridge
```

### Configuration Details

- **Service Name**: `redline-webgui`
- **Container Name**: `redline-web-app`
- **Image**: `redline-webgui:latest`
- **Dockerfile**: `Dockerfile.webgui.universal`
- **Restart Policy**: `unless-stopped`

### Ports

| Port | Service | Description |
|------|---------|-------------|
| 8080 | Flask Web App | Main web application |
| 6080 | noVNC Web GUI | Web-based GUI interface |

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_APP` | `web_app.py` | Flask application entry point |
| `FLASK_ENV` | `production` | Flask environment |
| `HOST` | `0.0.0.0` | Bind to all interfaces |
| `PORT` | `8080` | Flask application port |
| `VNC_PASSWORD` | `redline123` | VNC access password |
| `DISPLAY` | `:1` | X11 display |
| `VNC_PORT` | `5901` | VNC server port |
| `NO_VNC_PORT` | `6080` | noVNC web port |

### Volumes

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./data` | `/opt/redline/data` | Application data |
| `./logs` | `/var/log/redline` | Application logs |
| `./config` | `/opt/redline/config` | Configuration files |

### Resource Limits

- **Memory Limit**: 1GB
- **CPU Limit**: 1.0 cores
- **Memory Reservation**: 256MB
- **CPU Reservation**: 0.25 cores

## Management Commands

### Quick Start

1. **Copy the simple configuration:**
   ```bash
   cp docker-compose-option4.yml docker-compose.yml
   ```

2. **Start services:**
   ```bash
   ./manage_compose.sh start
   ```

3. **Access the application:**
   - **Web App**: http://localhost:8080
   - **Web GUI**: http://localhost:6080
   - **VNC Password**: redline123

### Complete Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Start REDLINE services | `./manage_compose.sh start` |
| `stop` | Stop REDLINE services | `./manage_compose.sh stop` |
| `restart` | Restart REDLINE services | `./manage_compose.sh restart` |
| `status` | Show service status and resource usage | `./manage_compose.sh status` |
| `logs` | Show service logs | `./manage_compose.sh logs` |
| `logs [service]` | Show logs for specific service | `./manage_compose.sh logs redline-webgui` |
| `rebuild` | Rebuild and restart services | `./manage_compose.sh rebuild` |
| `cleanup` | Remove all containers, networks, and volumes | `./manage_compose.sh cleanup` |
| `backup` | Backup docker-compose.yml | `./manage_compose.sh backup` |
| `restore` | Restore docker-compose.yml from backup | `./manage_compose.sh restore` |
| `help` | Show help information | `./manage_compose.sh help` |

### Direct Docker Compose Commands

You can also use Docker Compose commands directly:

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild services
docker-compose build --no-cache

# Remove everything
docker-compose down -v --remove-orphans
```

## Service Information

### Container Details

- **Container Name**: `redline-web-app`
- **Image**: `redline-webgui:latest`
- **Working Directory**: `/opt/redline`
- **User**: Default (root)

### Health Checks

- **Test**: `curl -f http://localhost:8080/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 60 seconds

### Network Configuration

- **Network Type**: Bridge
- **Network Name**: `redline_default`
- **Subnet**: Automatically assigned

## Troubleshooting

### Common Issues

1. **Docker Compose not found:**
   ```bash
   # Install Docker Compose
   pip3 install docker-compose
   ```

2. **Docker daemon not running:**
   ```bash
   # Linux
   sudo systemctl start docker
   
   # macOS
   # Start Docker Desktop
   ```

3. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :8080
   lsof -i :6080
   ```

4. **Permission issues:**
   ```bash
   # Fix file permissions
   chmod +x manage_compose.sh
   chmod +x start_compose.sh
   ```

5. **Docker Compose version warning:**
   ```bash
   # The 'version' attribute is obsolete in newer Docker Compose versions
   # The fixed configuration removes this attribute
   ```

6. **Dependency cycle detected:**
   ```bash
   # The fixed configuration removes complex dependencies
   # Uses single service approach to avoid cycles
   ```

### Log Analysis

```bash
# View all logs
./manage_compose.sh logs

# View specific service logs
./manage_compose.sh logs redline-webgui

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Resource Monitoring

```bash
# Check container status
./manage_compose.sh status

# Monitor resource usage
docker stats redline-web-app

# Check container health
docker inspect redline-web-app | grep -A 10 Health
```

## Security Considerations

### VNC Password

- **Default Password**: `redline123`
- **Change Password**: Modify `VNC_PASSWORD` environment variable
- **Security**: Use strong passwords in production

### Network Security

- **Port Exposure**: Only necessary ports are exposed
- **Internal Communication**: Services communicate via internal network
- **Firewall**: Consider firewall rules for production deployment

### Data Security

- **Volume Mounting**: Data is persisted on host system
- **Backup**: Regular backups of `./data` directory recommended
- **Permissions**: Ensure proper file permissions on mounted volumes

## Production Deployment

### Environment Variables

For production deployment, consider setting:

```bash
# Production environment
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export VNC_PASSWORD=your-secure-password
```

### Resource Scaling

Adjust resource limits based on usage:

```yaml
deploy:
  resources:
    limits:
      memory: 2G      # Increase for heavy usage
      cpus: '2.0'     # Increase for CPU-intensive tasks
    reservations:
      memory: 512M    # Increase minimum memory
      cpus: '0.5'     # Increase minimum CPU
```

### Monitoring

- **Health Checks**: Monitor container health status
- **Logs**: Set up log aggregation and monitoring
- **Metrics**: Consider Prometheus/Grafana for metrics
- **Alerts**: Set up alerts for service failures

## Backup and Recovery

### Backup Strategy

1. **Configuration Backup:**
   ```bash
   ./manage_compose.sh backup
   ```

2. **Data Backup:**
   ```bash
   tar -czf redline-data-backup-$(date +%Y%m%d).tar.gz ./data
   ```

3. **Image Backup:**
   ```bash
   docker save redline-webgui:latest | gzip > redline-image-backup.tar.gz
   ```

### Recovery Process

1. **Restore Configuration:**
   ```bash
   ./manage_compose.sh restore
   ```

2. **Restore Data:**
   ```bash
   tar -xzf redline-data-backup-YYYYMMDD.tar.gz
   ```

3. **Restore Image:**
   ```bash
   gunzip -c redline-image-backup.tar.gz | docker load
   ```

## Best Practices

1. **Regular Updates**: Keep Docker images updated
2. **Resource Monitoring**: Monitor resource usage regularly
3. **Log Management**: Implement log rotation and cleanup
4. **Security Updates**: Apply security patches promptly
5. **Backup Testing**: Regularly test backup and recovery procedures
6. **Documentation**: Keep configuration documentation updated

## Support

For issues with Docker Compose management:

1. Check the troubleshooting section above
2. Review logs: `./manage_compose.sh logs`
3. Check service status: `./manage_compose.sh status`
4. Consult the main REDLINE documentation
5. Check Docker and Docker Compose documentation
