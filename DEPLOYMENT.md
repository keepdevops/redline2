# REDLINE Deployment Guide

This guide covers all deployment methods for REDLINE across different platforms and environments.

## 🚀 Quick Deployment Options

### 1. PyPI Package (Recommended for Python Users)
```bash
# Install latest version
pip install redline-financial

# Start applications
redline-gui    # Desktop GUI
redline-web    # Web interface
redline --help # CLI help
```

### 2. Docker (Recommended for Servers)
```bash
# Run web interface
docker run -p 8080:8080 redline-financial:latest

# Run with custom data directory
docker run -p 8080:8080 -v /path/to/data:/app/data redline-financial:latest
```

### 3. Standalone Executables (No Python Required)
```bash
# Download appropriate executable for your platform
# Windows: redline-gui-windows-x64.exe
# macOS: redline-gui-macos-arm64
# Linux: redline-gui-linux-x64

# Run directly
./redline-gui-macos-arm64
```

## 📋 Detailed Deployment Methods

### PyPI Package Deployment

#### Prerequisites
- Python 3.11+
- pip package manager

#### Installation
```bash
# Install latest version
pip install redline-financial

# Install specific version
pip install redline-financial==1.0.0

# Install with optional dependencies
pip install redline-financial[dev,test,docs]
```

#### Usage
```bash
# Start GUI application
redline-gui

# Start web application
redline-web

# Use CLI
redline download AAPL --start 2023-01-01 --end 2024-01-01
redline convert data.csv --output data.parquet
redline analyze data.parquet --stats
```

#### Updating
```bash
# Update to latest version
pip install --upgrade redline-financial

# Check current version
pip show redline-financial
```

### Docker Deployment

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+ (optional)

#### Single Container Deployment
```bash
# Pull latest image
docker pull redline-financial:latest

# Run web interface
docker run -d \
  --name redline-web \
  -p 8080:8080 \
  -v redline-data:/app/data \
  redline-financial:latest

# Access web interface
open http://localhost:8080
```

#### Docker Compose Deployment
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Start with Docker Compose
docker-compose -f docker-compose-working.yml up -d

# Check status
docker-compose -f docker-compose-working.yml ps

# View logs
docker-compose -f docker-compose-working.yml logs -f
```

#### Custom Configuration
```bash
# Run with custom environment variables
docker run -d \
  --name redline-web \
  -p 8080:8080 \
  -e REDLINE_PORT=8080 \
  -e REDLINE_HOST=0.0.0.0 \
  -e REDLINE_DEBUG=false \
  -v /host/data:/app/data \
  redline-financial:latest
```

#### Updating Docker Deployment
```bash
# Stop current container
docker stop redline-web
docker rm redline-web

# Pull latest image
docker pull redline-financial:latest

# Start new container
docker run -d \
  --name redline-web \
  -p 8080:8080 \
  -v redline-data:/app/data \
  redline-financial:latest
```

### Standalone Executable Deployment

#### Prerequisites
- No Python installation required
- Platform-specific executable

#### Installation
1. Download appropriate executable for your platform:
   - **Windows x64**: `redline-gui-windows-x64.exe`
   - **Windows ARM64**: `redline-gui-windows-arm64.exe`
   - **macOS Intel**: `redline-gui-macos-x64`
   - **macOS Apple Silicon**: `redline-gui-macos-arm64`
   - **Linux x64**: `redline-gui-linux-x64`
   - **Linux ARM64**: `redline-gui-linux-arm64`

2. Make executable (Linux/macOS):
   ```bash
   chmod +x redline-gui-*
   ```

3. Run directly:
   ```bash
   ./redline-gui-macos-arm64
   ```

#### Updating Executables
1. Download new executable
2. Replace old executable
3. Restart application

### Source Code Deployment

#### Prerequisites
- Python 3.11+
- Git
- pip package manager

#### Installation
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Install dependencies
pip install -r requirements.txt

# Start applications
python main.py      # GUI
python web_app.py   # Web interface
```

#### Updating Source Deployment
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart applications
```

### Universal Installer Deployment

#### Prerequisites
- Unix-like system (Linux, macOS)
- Bash shell
- Internet connection

#### Installation
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Run universal installer
./install_options_redline.sh
```

The installer provides 6 options:
1. **Web-based GUI** (Docker buildx)
2. **Tkinter GUI** (X11)
3. **Hybrid GUI** (Both web and desktop)
4. **Docker Compose** (Containerized)
5. **Working Docker Compose** (Recommended)
6. **Native Installation** (Direct Python)

## 🔧 Configuration

### Environment Variables
```bash
# Application settings
export REDLINE_PORT=8080
export REDLINE_HOST=0.0.0.0
export REDLINE_DEBUG=false

# Data settings
export REDLINE_DATA_DIR=/path/to/data
export REDLINE_CACHE_DIR=/path/to/cache

# License settings
export LICENSE_SERVER_URL=http://license.example.com
export LICENSE_KEY=your-license-key

# Update settings
export UPDATE_SERVER_URL=https://api.github.com/repos/keepdevops/redline2/releases
```

### Configuration File
Create `data_config.ini`:
```ini
[app]
port = 8080
host = 0.0.0.0
debug = false

[data]
data_dir = /path/to/data
cache_dir = /path/to/cache

[license]
server_url = http://license.example.com
license_key = your-license-key

[updates]
check_interval = 86400
auto_update = false
```

## 🌐 Platform-Specific Deployment

### Windows Deployment

#### PyPI Package
```powershell
# Install Python 3.11+
# Download from python.org

# Install REDLINE
pip install redline-financial

# Start applications
redline-gui
redline-web
```

#### Executable
```powershell
# Download redline-gui-windows-x64.exe
# Run directly
.\redline-gui-windows-x64.exe
```

#### Docker
```powershell
# Install Docker Desktop
# Run container
docker run -p 8080:8080 redline-financial:latest
```

### macOS Deployment

#### PyPI Package
```bash
# Install Python 3.11+
brew install python@3.11

# Install REDLINE
pip3 install redline-financial

# Start applications
redline-gui
redline-web
```

#### Executable
```bash
# Download redline-gui-macos-arm64 (Apple Silicon)
# or redline-gui-macos-x64 (Intel)

# Make executable
chmod +x redline-gui-macos-*

# Run
./redline-gui-macos-arm64
```

#### Docker
```bash
# Install Docker Desktop
# Run container
docker run -p 8080:8080 redline-financial:latest
```

### Linux Deployment

#### Ubuntu/Debian
```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-pip

# Install REDLINE
pip3 install redline-financial

# Start applications
redline-gui
redline-web
```

#### CentOS/RHEL
```bash
# Install Python 3.11+
sudo yum install python3.11 python3.11-pip

# Install REDLINE
pip3 install redline-financial

# Start applications
redline-gui
redline-web
```

#### Executable
```bash
# Download redline-gui-linux-x64
# Make executable
chmod +x redline-gui-linux-x64

# Run
./redline-gui-linux-x64
```

#### Docker
```bash
# Install Docker
sudo yum install docker
sudo systemctl start docker

# Run container
sudo docker run -p 8080:8080 redline-financial:latest
```

## 🔒 Production Deployment

### Security Considerations
1. **Use HTTPS** in production
2. **Set strong passwords** for web interface
3. **Configure firewall** rules
4. **Use environment variables** for sensitive data
5. **Regular updates** for security patches

### Performance Optimization
1. **Use Parquet/DuckDB** formats for large datasets
2. **Enable virtual scrolling** for 10M+ rows
3. **Configure memory limits** appropriately
4. **Use SSD storage** for better I/O performance
5. **Monitor resource usage**

### Monitoring
1. **Application logs** for debugging
2. **Resource monitoring** (CPU, memory, disk)
3. **Error tracking** and alerting
4. **Performance metrics** collection
5. **Health checks** for services

### Backup Strategy
1. **Regular data backups**
2. **Configuration backups**
3. **Version control** for customizations
4. **Disaster recovery** plan
5. **Testing restore** procedures

## 🆘 Troubleshooting

### Common Issues

#### PyPI Installation Issues
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -v redline-financial
```

#### Docker Issues
```bash
# Check Docker daemon
docker --version
docker info

# Check container logs
docker logs redline-web

# Restart Docker service
sudo systemctl restart docker
```

#### Executable Issues
```bash
# Check file permissions
ls -la redline-gui-*

# Make executable
chmod +x redline-gui-*

# Check dependencies
ldd redline-gui-linux-x64  # Linux
otool -L redline-gui-macos-arm64  # macOS
```

#### Web Interface Issues
```bash
# Check port availability
netstat -tlnp | grep 8080

# Check firewall
sudo ufw status

# Test connectivity
curl http://localhost:8080
```

### Getting Help
1. **Check logs** for error messages
2. **Review documentation** for configuration options
3. **Search GitHub issues** for similar problems
4. **Create new issue** with detailed information
5. **Contact support** for commercial licensing

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/keepdevops/redline2)
- **Issues**: [GitHub Issues](https://github.com/keepdevops/redline2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/keepdevops/redline2/discussions)
- **Email**: support@redline.example.com
- **Commercial Support**: Available for enterprise customers
