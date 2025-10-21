# REDLINE Web GUI Multi-Distribution Docker Deployment

Complete multi-distribution Docker deployment solution for REDLINE Web GUI supporting multiple Linux distributions, architectures, and Python versions.

## 🐧 Supported Linux Distributions

### **Base Images and Characteristics**

| Distribution | Base Image | Size | Focus | Package Manager | Python Version |
|-------------|------------|------|-------|----------------|----------------|
| **Ubuntu** | `ubuntu:24.04` | ~200MB | General purpose | `apt` | 3.12+ |
| **Alpine** | `alpine:3.19` | ~50MB | Security, lightweight | `apk` | 3.11+ |
| **CentOS** | `quay.io/centos/centos:stream9` | ~300MB | Enterprise | `dnf` | 3.11+ |
| **Rocky** | `rockylinux:9` | ~300MB | RHEL-compatible | `dnf` | 3.11+ |
| **Debian** | `debian:12-slim` | ~150MB | Stable, server | `apt` | 3.11+ |
| **Arch** | `archlinux:latest` | ~400MB | Rolling release | `pacman` | 3.11+ |
| **Fedora** | `fedora:40` | ~350MB | Cutting-edge | `dnf` | 3.11+ |
| **OpenSUSE** | `opensuse/tumbleweed` | ~300MB | Enterprise | `zypper` | 3.11+ |

### **Architecture Support**
- ✅ **linux/amd64** - Intel/AMD 64-bit processors
- ✅ **linux/arm64** - ARM 64-bit processors (Apple Silicon, ARM servers)
- ✅ **linux/arm/v7** - ARM 32-bit processors (Raspberry Pi, IoT devices)

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ with Buildx support
- Docker Compose 2.0+
- 4GB+ RAM (for multi-distribution builds)
- 10GB+ disk space

### One-Command Multi-Distribution Deployment
```bash
# Clone and deploy all distributions
git clone <repository-url>
cd redline
./scripts/build-multidist.sh --all-distros
```

### Distribution-Specific Deployment
```bash
# Deploy specific distribution
./scripts/build-multidist.sh -d alpine
./scripts/build-multidist.sh -d ubuntu
./scripts/build-multidist.sh -d centos
./scripts/build-multidist.sh -d rocky
./scripts/build-multidist.sh -d debian
./scripts/build-multidist.sh -d arch
```

### Access Different Distributions
- **Ubuntu**: http://localhost:8080
- **Alpine**: http://localhost:8081
- **CentOS**: http://localhost:8082
- **Rocky**: http://localhost:8083
- **Debian**: http://localhost:8084
- **Arch**: http://localhost:8085
- **Load Balancer**: http://localhost:80
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

## 📁 Project Structure

```
redline/
├── Dockerfile                      # Ubuntu 24.04 LTS (default)
├── Dockerfile.multidist           # Multi-distribution template
├── dockerfiles/
│   ├── Dockerfile.alpine          # Alpine Linux 3.19
│   ├── Dockerfile.centos          # CentOS Stream 9
│   ├── Dockerfile.rhel            # Red Hat Enterprise Linux
│   ├── Dockerfile.rocky           # Rocky Linux 9
│   ├── Dockerfile.debian          # Debian 12 Slim
│   ├── Dockerfile.arch            # Arch Linux Latest
│   ├── Dockerfile.fedora          # Fedora 40
│   └── Dockerfile.opensuse        # OpenSUSE Tumbleweed
├── docker-compose.yml             # Single distribution
├── docker-compose.multidist.yml   # Multi-distribution
├── requirements.txt               # Multi-platform Python dependencies
├── scripts/
│   ├── build-multidist.sh         # Multi-distribution build script
│   ├── build-multiplatform.sh     # Multi-platform build script
│   └── deploy-multiplatform.sh    # Multi-platform deployment
└── config/
    ├── nginx-lb.conf              # Load balancer configuration
    ├── prometheus-multidist.yml   # Multi-distribution monitoring
    └── grafana/                   # Grafana dashboards
```

## 🐳 Multi-Distribution Docker Services

### Core Services (Per Distribution)
- **redline-web-ubuntu**: Ubuntu-based Flask application
- **redline-web-alpine**: Alpine-based Flask application
- **redline-web-centos**: CentOS-based Flask application
- **redline-web-rocky**: Rocky Linux-based Flask application
- **redline-web-debian**: Debian-based Flask application
- **redline-web-arch**: Arch Linux-based Flask application

### Shared Services
- **redis**: Caching and session storage
- **nginx-lb**: Load balancer for all distributions
- **prometheus**: Metrics collection and monitoring
- **grafana**: Dashboard and visualization

## 🛠️ Build Options

### Build All Distributions
```bash
./scripts/build-multidist.sh --all-distros
```

### Build Specific Distribution
```bash
./scripts/build-multidist.sh -d alpine
./scripts/build-multidist.sh -d ubuntu
./scripts/build-multidist.sh -d centos
```

### Build and Push to Registry
```bash
./scripts/build-multidist.sh --all-distros --push
```

### Platform-Specific Builds
```bash
# AMD64 only
./scripts/build-multidist.sh -d alpine -p linux/amd64

# ARM64 only
./scripts/build-multidist.sh -d alpine -p linux/arm64

# All platforms
./scripts/build-multidist.sh -d alpine -p linux/amd64,linux/arm64
```

### Test After Build
```bash
./scripts/build-multidist.sh -d alpine --test
```

## 🔧 Distribution-Specific Features

### **Alpine Linux** (Lightweight)
- **Size**: ~50MB base image
- **Security**: Minimal attack surface
- **Performance**: Fast startup, low memory usage
- **Use case**: Production, microservices, IoT
- **Package manager**: `apk`
- **Init system**: OpenRC

### **Ubuntu** (General Purpose)
- **Size**: ~200MB base image
- **Compatibility**: Wide software support
- **Performance**: Balanced performance and features
- **Use case**: Development, general production
- **Package manager**: `apt`
- **Init system**: systemd

### **CentOS/Rocky** (Enterprise)
- **Size**: ~300MB base image
- **Stability**: Long-term support
- **Performance**: Enterprise-grade reliability
- **Use case**: Enterprise, servers, compliance
- **Package manager**: `dnf`
- **Init system**: systemd

### **Debian** (Stable)
- **Size**: ~150MB base image
- **Stability**: Conservative updates
- **Performance**: Reliable, predictable
- **Use case**: Servers, embedded systems
- **Package manager**: `apt`
- **Init system**: systemd

### **Arch Linux** (Rolling)
- **Size**: ~400MB base image
- **Freshness**: Latest packages
- **Performance**: Cutting-edge features
- **Use case**: Development, testing
- **Package manager**: `pacman`
- **Init system**: systemd

## 🔒 Multi-Distribution Security Features

### Container Security
- **Non-root user** execution across all distributions
- **Distribution-specific security policies**
- **Resource limits** and quotas per distribution
- **Security scanning** for each distribution

### Network Security
- **Isolated networks** for each distribution
- **Load balancer** with SSL termination
- **Internal service communication**
- **Distribution-specific firewall rules**

### Application Security
- **Secret key management** across distributions
- **Distribution-specific security tools**
- **HTTPS support** with platform-specific certificates
- **Input validation** and sanitization

## 🚀 Multi-Distribution Performance Features

### Distribution-Specific Optimizations
- **Alpine**: Minimal memory footprint, fast startup
- **Ubuntu**: Balanced performance and compatibility
- **CentOS/Rocky**: Enterprise-grade reliability
- **Debian**: Stable, predictable performance
- **Arch**: Latest optimizations and features

### Application Performance
- **Gunicorn** with distribution-optimized workers
- **Redis caching** with distribution-specific configurations
- **Nginx load balancer** with distribution optimizations
- **Static file optimization** for each distribution
- **Database connection pooling**

### Resource Management
- **Distribution-specific memory limits**
- **CPU limits** based on distribution characteristics
- **Disk space monitoring** across distributions
- **Automatic cleanup** for each distribution

## 📝 Multi-Distribution Management Commands

### Service Management
```bash
# Start all distributions
docker-compose -f docker-compose.multidist.yml up -d

# Start specific distribution
docker-compose -f docker-compose.multidist.yml up -d redline-web-alpine

# Stop all distributions
docker-compose -f docker-compose.multidist.yml down

# Restart specific distribution
docker-compose -f docker-compose.multidist.yml restart redline-web-ubuntu
```

### Distribution-Specific Management
```bash
# View all distribution containers
docker-compose -f docker-compose.multidist.yml ps

# View logs for specific distribution
docker-compose -f docker-compose.multidist.yml logs redline-web-alpine

# Execute commands in specific distribution
docker-compose -f docker-compose.multidist.yml exec redline-web-ubuntu /bin/bash
```

### Load Balancer Management
```bash
# Check load balancer status
curl http://localhost/health

# View load balancer logs
docker-compose -f docker-compose.multidist.yml logs nginx-lb

# Reload load balancer configuration
docker-compose -f docker-compose.multidist.yml exec nginx-lb nginx -s reload
```

## 🔄 Multi-Distribution Updates and Maintenance

### Update All Distributions
```bash
# Pull latest changes
git pull

# Rebuild all distributions
./scripts/build-multidist.sh --all-distros --clean --force

# Rebuild and push to registry
./scripts/build-multidist.sh --all-distros --clean --force --push
```

### Update Specific Distribution
```bash
# Update Alpine only
./scripts/build-multidist.sh -d alpine --clean --force

# Update Ubuntu only
./scripts/build-multidist.sh -d ubuntu --clean --force
```

### Backup Data (Multi-Distribution)
```bash
# Backup data directory
tar -czf redline-backup-$(date +%Y%m%d).tar.gz data/

# Distribution-specific backup
docker-compose -f docker-compose.multidist.yml exec redline-web-alpine python3 -c "
import duckdb
conn = duckdb.connect('/opt/redline/data/redline_data.duckdb')
conn.execute('EXPORT DATABASE \"/backup/redline_db_alpine\"')"
```

## 🐛 Multi-Distribution Troubleshooting

### Common Issues

#### Distribution-Specific Build Failures
```bash
# Check distribution-specific Dockerfile
cat dockerfiles/Dockerfile.alpine

# Build specific distribution with verbose output
docker build -f dockerfiles/Dockerfile.alpine -t test-alpine .

# Check distribution-specific logs
docker-compose -f docker-compose.multidist.yml logs redline-web-alpine
```

#### Architecture Mismatch
```bash
# Check current platform
uname -m

# Check Docker platform
docker version

# Check image platform for each distribution
docker inspect redline-web-gui:alpine-latest | grep Architecture
docker inspect redline-web-gui:ubuntu-latest | grep Architecture
```

#### Container Won't Start (Distribution-Specific)
```bash
# Check distribution-specific compatibility
docker run --rm redline-web-gui:alpine-latest uname -a
docker run --rm redline-web-gui:ubuntu-latest uname -a

# Check distribution-specific logs
docker-compose -f docker-compose.multidist.yml logs redline-web-alpine
```

### Debug Mode (Multi-Distribution)
```bash
# Enable debug mode for specific distribution
docker-compose -f docker-compose.multidist.yml exec redline-web-alpine python3 -c "
import platform
print('Platform:', platform.platform())
print('Architecture:', platform.architecture())
print('Machine:', platform.machine())
print('Distribution: Alpine Linux')
"
```

## 📊 Performance Comparison

### Image Sizes
| Distribution | Base Size | With REDLINE | Startup Time | Memory Usage |
|-------------|-----------|--------------|--------------|--------------|
| **Alpine** | ~50MB | ~150MB | ~2s | ~50MB |
| **Ubuntu** | ~200MB | ~400MB | ~5s | ~100MB |
| **CentOS** | ~300MB | ~500MB | ~8s | ~120MB |
| **Rocky** | ~300MB | ~500MB | ~8s | ~120MB |
| **Debian** | ~150MB | ~350MB | ~4s | ~80MB |
| **Arch** | ~400MB | ~600MB | ~6s | ~110MB |

### Use Case Recommendations
- **Production (High Performance)**: Alpine Linux
- **Development (Compatibility)**: Ubuntu
- **Enterprise (Compliance)**: CentOS/Rocky
- **Stable (Reliability)**: Debian
- **Testing (Latest Features)**: Arch Linux

## 📚 Additional Resources

### Documentation
- [Docker Multi-Distribution Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Alpine Linux Documentation](https://docs.alpinelinux.org/)
- [CentOS Documentation](https://docs.centos.org/)
- [Rocky Linux Documentation](https://docs.rockylinux.org/)
- [Debian Documentation](https://www.debian.org/doc/)
- [Arch Linux Documentation](https://wiki.archlinux.org/)

### Distribution-Specific Resources
- [Alpine Security Guide](https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html)
- [CentOS Enterprise Guide](https://docs.centos.org/en-US/centos/stream/)
- [Rocky Linux Migration Guide](https://docs.rockylinux.org/guides/migrate2rocky/)
- [Debian Server Guide](https://www.debian.org/doc/manuals/debian-handbook/)

## 🎯 Production Multi-Distribution Deployment

### Production Checklist
- [ ] Choose appropriate distribution for use case
- [ ] Set strong SECRET_KEY for each distribution
- [ ] Configure Redis password
- [ ] Set up SSL certificates for load balancer
- [ ] Configure distribution-specific firewall rules
- [ ] Set up monitoring alerts for each distribution
- [ ] Configure log rotation for each distribution
- [ ] Set up backup strategy for each distribution
- [ ] Test disaster recovery for each distribution

### Multi-Distribution Scaling
```bash
# Scale specific distribution
docker-compose -f docker-compose.multidist.yml up -d --scale redline-web-alpine=3

# Scale all distributions
docker-compose -f docker-compose.multidist.yml up -d --scale redline-web-ubuntu=2 --scale redline-web-alpine=2
```

### High Availability (Multi-Distribution)
- Use Docker Swarm or Kubernetes with multi-distribution support
- Set up database replication across distributions
- Configure health checks for each distribution
- Implement circuit breakers for distribution-specific issues
- Set up monitoring and alerting for each distribution

---

**REDLINE Web GUI Multi-Distribution Docker Deployment** - Modern, secure, and scalable financial data analysis platform supporting multiple Linux distributions, architectures, and Python versions.
