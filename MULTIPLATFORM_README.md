# REDLINE Web GUI Multi-Platform Docker Deployment

Complete multi-platform Docker deployment solution for REDLINE Web GUI supporting multiple architectures and Python versions.

## 🌍 Multi-Platform Support

### **Supported Platforms**
- **linux/amd64** - Intel/AMD 64-bit processors
- **linux/arm64** - ARM 64-bit processors (Apple Silicon, ARM servers)
- **linux/arm/v7** - ARM 32-bit processors (Raspberry Pi, etc.)

### **Supported Python Versions**
- **Python 3.11+** - Primary support
- **Python 3.12** - Latest Ubuntu 24.04 LTS default
- **Backward compatible** with Python 3.10+

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ with Buildx support
- Docker Compose 2.0+
- 2GB+ RAM
- 5GB+ disk space

### One-Command Multi-Platform Deployment
```bash
# Clone and deploy for all platforms
git clone <repository-url>
cd redline
./scripts/deploy-multiplatform.sh
```

### Platform-Specific Deployment
```bash
# Deploy for AMD64 only
./scripts/deploy-multiplatform.sh -p linux/amd64

# Deploy for ARM64 only
./scripts/deploy-multiplatform.sh -p linux/arm64

# Deploy for current platform only
./scripts/deploy-multiplatform.sh --no-multiarch
```

### Access the Application
- **Web GUI**: http://localhost:8080
- **Nginx Proxy**: http://localhost:8081
- **Prometheus**: http://localhost:9090
- **Health Check**: http://localhost:8080/health

## 📁 Project Structure

```
redline/
├── Dockerfile                      # Multi-platform Ubuntu 24.04 LTS
├── docker-compose.yml             # Full stack deployment
├── requirements.txt               # Multi-platform Python dependencies
├── web_app.py                     # Flask web application
├── main.py                        # Tkinter GUI (for reference)
├── data_config.ini                # Application configuration
├── scripts/
│   ├── build-multiplatform.sh     # Multi-platform Docker build
│   ├── deploy-multiplatform.sh    # Complete deployment automation
│   ├── start.sh                   # Container startup script
│   └── shutdown.sh                # Graceful shutdown script
├── config/                        # Configuration files
│   ├── nginx.conf
│   ├── redis.conf
│   ├── prometheus.yml
│   └── fluentd.conf
├── data/                          # Application data
├── logs/                          # Application logs
└── ssl/                           # SSL certificates (optional)
```

## 🐳 Multi-Platform Docker Services

### Core Services
- **redline-web**: Main Flask application (Multi-platform Ubuntu 24.04 LTS)
- **redis**: Caching and session storage
- **nginx-proxy**: Reverse proxy and load balancer

### Monitoring Services
- **prometheus**: Metrics collection and monitoring
- **fluentd**: Log aggregation and processing

## 🛠️ Deployment Options

### Full Multi-Platform Deployment
```bash
./scripts/deploy-multiplatform.sh
```

### Build Only (Multi-Platform)
```bash
./scripts/deploy-multiplatform.sh --build-only
```

### Build and Push to Registry
```bash
./scripts/deploy-multiplatform.sh --build-only --push
```

### Single Platform Deployment
```bash
./scripts/deploy-multiplatform.sh --no-multiarch
```

### Platform-Specific Builds
```bash
# AMD64 only
./scripts/build-multiplatform.sh -p linux/amd64

# ARM64 only
./scripts/build-multiplatform.sh -p linux/arm64

# All platforms
./scripts/build-multiplatform.sh -p linux/amd64,linux/arm64
```

## 🔧 Multi-Platform Configuration

### Environment Variables
Create `.env` file with:
```bash
SECRET_KEY=your-secret-key
REDIS_PASSWORD=your-redis-password
FLASK_ENV=production
HOST=0.0.0.0
PORT=8080
PYTHON_VERSION=3.11+
PLATFORM=multi-arch
```

### Platform Detection
The application automatically detects:
- **Architecture**: AMD64, ARM64, ARM32
- **Python Version**: 3.11, 3.12
- **Operating System**: Linux distributions
- **Container Runtime**: Docker, Podman

### Cross-Platform Compatibility
- **File paths**: Uses `platformdirs` for cross-platform paths
- **Dependencies**: All packages support multi-platform
- **Build process**: Docker Buildx handles architecture differences
- **Runtime**: Automatic platform detection and optimization

## 📊 Platform-Specific Features

### AMD64 (Intel/AMD)
- **Performance**: Optimized for x86_64 instruction set
- **Memory**: Supports large memory configurations
- **Compatibility**: Full compatibility with all libraries

### ARM64 (Apple Silicon, ARM Servers)
- **Performance**: Optimized for ARM64 instruction set
- **Efficiency**: Lower power consumption
- **Compatibility**: Native ARM64 binaries for all dependencies

### ARM32 (Raspberry Pi, IoT)
- **Performance**: Optimized for ARM32 instruction set
- **Size**: Smaller image size for resource-constrained devices
- **Compatibility**: Compatible with ARM32 libraries

## 🔒 Multi-Platform Security Features

### Container Security
- **Non-root user** execution across all platforms
- **Read-only root filesystem** where possible
- **Resource limits** and quotas
- **Security options** for each platform

### Network Security
- **Isolated networks** for each platform
- **Internal service communication**
- **External port exposure** only where needed
- **Platform-specific firewall rules**

### Application Security
- **Secret key management** across platforms
- **Redis password protection**
- **HTTPS support** with platform-specific certificates
- **Input validation** and sanitization

## 🚀 Multi-Platform Performance Features

### Ubuntu 24.04 LTS Features
- **Python 3.11+** with latest optimizations
- **Modern package management** (apt, snap, flatpak)
- **Systemd integration** for service management
- **Advanced security features** (AppArmor, SELinux)

### Application Performance
- **Gunicorn** with platform-optimized workers
- **Redis caching** with platform-specific configurations
- **Nginx reverse proxy** with platform optimizations
- **Static file optimization** for each platform
- **Database connection pooling**

### Resource Management
- **Platform-specific memory limits**
- **CPU limits** based on architecture
- **Disk space monitoring** across platforms
- **Automatic cleanup** for each platform

## 📝 Multi-Platform Management Commands

### Service Management
```bash
# Start services (all platforms)
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Scale services
docker-compose up -d --scale redline-web=2
```

### Platform-Specific Management
```bash
# View platform information
docker system info

# Check platform support
docker buildx ls

# Inspect multi-platform images
docker buildx imagetools inspect redline-web-gui:latest
```

### Container Management
```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# Execute commands in container
docker-compose exec redline-web /bin/bash
docker-compose exec redis redis-cli
```

## 🔄 Multi-Platform Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild for all platforms
./scripts/deploy-multiplatform.sh --clean --force

# Rebuild and push to registry
./scripts/deploy-multiplatform.sh --clean --force --push
```

### Platform-Specific Updates
```bash
# Update for specific platform
./scripts/build-multiplatform.sh -p linux/amd64 --push

# Update all platforms
./scripts/build-multiplatform.sh --push
```

### Backup Data (Multi-Platform)
```bash
# Backup data directory
tar -czf redline-backup-$(date +%Y%m%d).tar.gz data/

# Platform-specific backup
docker-compose exec redline-web python3 -c "
import duckdb
conn = duckdb.connect('/opt/redline/data/redline_data.duckdb')
conn.execute('EXPORT DATABASE \"/backup/redline_db\"')"
```

## 🐛 Multi-Platform Troubleshooting

### Common Issues

#### Platform-Specific Build Failures
```bash
# Check buildx support
docker buildx version

# Create buildx builder
docker buildx create --name multiarch --use

# Inspect builder
docker buildx inspect --bootstrap
```

#### Architecture Mismatch
```bash
# Check current platform
uname -m

# Check Docker platform
docker version

# Check image platform
docker inspect redline-web-gui:latest | grep Architecture
```

#### Container Won't Start (Platform-Specific)
```bash
# Check platform compatibility
docker run --rm --platform linux/amd64 redline-web-gui:latest uname -m
docker run --rm --platform linux/arm64 redline-web-gui:latest uname -m

# Check logs
docker-compose logs redline-web
```

### Debug Mode (Multi-Platform)
```bash
# Enable debug mode
export FLASK_DEBUG=true
docker-compose up -d

# View debug logs
docker-compose logs -f redline-web

# Platform-specific debugging
docker-compose exec redline-web python3 -c "
import platform
print('Platform:', platform.platform())
print('Architecture:', platform.architecture())
print('Machine:', platform.machine())
"
```

## 📚 Additional Resources

### Documentation
- [Docker Multi-Platform Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ubuntu 24.04 LTS Documentation](https://ubuntu.com/server/docs)

### Platform-Specific Resources
- [AMD64 Optimization Guide](https://docs.docker.com/buildx/working-with-buildx/)
- [ARM64 Development Guide](https://docs.docker.com/buildx/working-with-buildx/)
- [Multi-Architecture Best Practices](https://docs.docker.com/buildx/working-with-buildx/)

## 🎯 Production Multi-Platform Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure Redis password
- [ ] Set up SSL certificates for each platform
- [ ] Configure platform-specific firewall rules
- [ ] Set up monitoring alerts for each platform
- [ ] Configure log rotation for each platform
- [ ] Set up backup strategy for each platform
- [ ] Test disaster recovery for each platform

### Multi-Platform Scaling
```bash
# Scale web application across platforms
docker-compose up -d --scale redline-web=3

# Platform-specific scaling
docker service create --replicas 3 --platform linux/amd64 redline-web-gui:latest
docker service create --replicas 2 --platform linux/arm64 redline-web-gui:latest
```

### High Availability (Multi-Platform)
- Use Docker Swarm or Kubernetes with multi-platform support
- Set up database replication across platforms
- Configure health checks for each platform
- Implement circuit breakers for platform-specific issues
- Set up monitoring and alerting for each platform

---

**REDLINE Web GUI Multi-Platform Docker Deployment** - Modern, secure, and scalable financial data analysis platform supporting multiple architectures and Python versions.
