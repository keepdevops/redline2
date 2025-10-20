# REDLINE Universal Installation Guide

## 🚀 **Complete Installation Without GitHub Verification**

This guide provides comprehensive installation instructions for REDLINE on both Docker and bare metal environments, with all dependencies and imports included.

## 📋 **Quick Start**

### **Universal Installation**
```bash
# From REDLINE project root
./universal_install.sh
```

### **Installation Options**
```bash
./universal_install.sh --mode bare-metal    # Bare metal installation
./universal_install.sh --mode docker        # Docker installation
./universal_install.sh --mode minimal       # Minimal installation
./universal_install.sh --web-only          # Web interface only
```

## 🎯 **Installation Modes**

### **1. Auto Mode (Default)**
- Automatically detects environment and installs appropriate components
- Recommended for most users

### **2. Bare Metal Mode**
- Installs directly on the system without Docker
- Full Python environment with all dependencies
- Best for development and testing

### **3. Docker Mode**
- Creates Docker environment with REDLINE
- Containerized installation
- Best for production deployment

### **4. Minimal Mode**
- Installs only essential components
- Python + web interface only
- Lightweight installation

### **5. Web-Only Mode**
- Installs only web interface components
- No GUI or Docker components
- Best for server deployments

## 📦 **Complete Dependency List**

### **Required Dependencies (14)**
| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | >=2.0.0 | Core data manipulation |
| `numpy` | >=1.24.0 | Numerical computing |
| `configparser` | >=5.3.0 | Configuration parsing |
| `pyarrow` | >=10.0.0 | Parquet/Arrow data handling |
| `polars` | >=0.20.0 | High-performance DataFrame |
| `duckdb` | >=0.8.0 | SQL database engine |
| `yfinance` | >=0.2.0 | Yahoo Finance data |
| `flask` | >=2.3.0 | Web application framework |
| `flask-socketio` | >=5.3.0 | Real-time communication |
| `flask-compress` | >=1.13 | Response compression |
| `requests` | >=2.31.0 | HTTP library |
| `urllib3` | >=2.0.0 | HTTP client |
| `python-dateutil` | >=2.8.0 | Date/time utilities |
| `pytz` | >=2023.3 | Timezone support |

### **Optional Dependencies (10)**
| Package | Version | Purpose |
|---------|---------|---------|
| `matplotlib` | >=3.7.0 | Data visualization |
| `seaborn` | >=0.12.0 | Statistical visualization |
| `scipy` | >=1.9.0 | Scientific computing |
| `scikit-learn` | >=1.3.0 | Machine learning |
| `openpyxl` | >=3.1.0 | Excel file support |
| `xlsxwriter` | >=3.1.0 | Excel writing |
| `psutil` | >=5.9.0 | System monitoring |
| `gunicorn` | >=21.0.0 | WSGI HTTP server |
| `celery` | >=5.3.0 | Background task processing |
| `redis` | >=4.5.0 | Redis client |

## 🖥️ **Platform Support**

### **Linux (Ubuntu/Debian)**
- **System Packages**: python3, python3-pip, python3-venv, python3-tk, build-essential
- **GUI Support**: Tkinter via python3-tk and python3-tkinter
- **Docker Support**: Full Docker installation and configuration

### **Linux (CentOS/RHEL/Fedora)**
- **System Packages**: python3, python3-pip, python3-devel, gcc, tkinter
- **GUI Support**: Tkinter via system packages
- **Docker Support**: Full Docker installation and configuration

### **macOS**
- **System Packages**: python3, git, curl, wget (via Homebrew)
- **GUI Support**: Tkinter via system Python
- **Docker Support**: Docker Desktop (manual installation required)

### **Windows (WSL)**
- **System Packages**: python3, python3-pip, curl, wget
- **GUI Support**: Limited (use web interface)
- **Docker Support**: Docker Desktop (manual installation required)

## 🐳 **Docker Installation**

### **Docker Compose Setup**
```yaml
version: '3.8'

services:
  redline-web:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - WEB_PORT=8080
      - FLASK_ENV=production
    restart: unless-stopped
```

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data logs

# Expose port
EXPOSE 8080

# Default command
CMD ["python3", "web_app.py"]
```

## 🔧 **Bare Metal Installation**

### **System Requirements**
- **Python**: 3.11 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free space minimum
- **Network**: Internet connection for package installation

### **Installation Steps**
1. **Install system packages** (OS-specific)
2. **Create Python virtual environment**
3. **Install Python dependencies**
4. **Create data directories**
5. **Create startup scripts**
6. **Create configuration files**
7. **Run installation tests**

### **Directory Structure**
```
~/redline/
├── venv/                    # Python virtual environment
├── data/                    # Data storage
│   ├── downloaded/         # Downloaded data files
│   └── converted/          # Converted data files
├── logs/                    # Application logs
├── start_web.sh            # Web interface startup
├── start_gui.sh            # GUI startup
├── start_docker.sh         # Docker startup
├── redline.conf            # Configuration file
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker image definition
└── main.py                 # Main application entry point
```

## 🚀 **Starting REDLINE**

### **Web Interface (Recommended)**
```bash
cd ~/redline
./start_web.sh
# Then open: http://localhost:8080
```

### **GUI Interface**
```bash
cd ~/redline
./start_gui.sh
```

### **Docker Services**
```bash
cd ~/redline
./start_docker.sh
```

## 🧪 **Verification and Testing**

### **Quick Verification**
```bash
cd ~/redline
source venv/bin/activate
python3 -c "import pandas, numpy, flask, duckdb; print('✅ All core packages working')"
```

### **Comprehensive Testing**
```bash
cd ~/redline
source venv/bin/activate
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

# Test all required packages
packages = ['pandas', 'numpy', 'flask', 'duckdb', 'pyarrow', 'polars', 'yfinance']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} imported successfully')
    except ImportError as e:
        print(f'❌ {pkg} import failed: {e}')

print('🎉 Package verification complete')
"
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Tkinter Issues (Ubuntu 24.04)**
```bash
# Fix Tkinter installation
sudo apt-get install python3-tk python3-tkinter
# Or install via pip
pip install tk
```

#### **2. Pandas Import Error**
```bash
# Fix pandas installation
cd ~/redline
source venv/bin/activate
pip install --upgrade pandas numpy
```

#### **3. Docker Permission Issues**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

#### **4. Port 8080 Already in Use**
```bash
# Use different port
export WEB_PORT=8081
./start_web.sh
```

#### **5. GUI Not Working**
```bash
# Use web interface instead
./start_web.sh
# Then open: http://localhost:8080
```

### **Log Files**
- **Application logs**: `~/redline/logs/`
- **Installation logs**: Check terminal output
- **Docker logs**: `docker-compose logs`

## 📚 **Configuration**

### **Environment Variables**
```bash
export WEB_PORT=8080          # Web interface port
export FLASK_ENV=production   # Flask environment
export FLASK_DEBUG=false      # Flask debug mode
```

### **Configuration File**
```ini
# ~/redline/redline.conf
[DEFAULT]
data_dir = ./data
logs_dir = ./logs
web_port = 8080

[WEB]
host = 0.0.0.0
port = 8080
debug = false

[GUI]
display = :0
theme = default

[DATABASE]
db_path = ./data/redline_data.duckdb
backup_enabled = true
```

## 🔒 **Security Considerations**

### **Firewall Configuration**
```bash
# Allow web interface access
sudo ufw allow 8080/tcp
```

### **User Permissions**
- REDLINE runs as the current user (not root)
- Data directories are user-owned
- Docker group membership for container access

### **Network Security**
- Web interface binds to 0.0.0.0 (all interfaces)
- Consider using reverse proxy for production
- Enable HTTPS in production environments

## 📊 **Performance Optimization**

### **System Optimization**
- **Memory**: Increase swap space if needed
- **Storage**: Use SSD for better I/O performance
- **Network**: Ensure stable internet connection

### **Python Optimization**
- **Virtual Environment**: Always use virtual environment
- **Package Versions**: Use specific versions for stability
- **Memory Usage**: Monitor memory usage for large datasets

### **Docker Optimization**
- **Resource Limits**: Set appropriate CPU/memory limits
- **Volume Mounts**: Use named volumes for persistent data
- **Image Caching**: Use multi-stage builds for smaller images

## 🎯 **Production Deployment**

### **Docker Production Setup**
```bash
# Build production image
docker build -t redline:latest .

# Run with production settings
docker run -d \
  --name redline-web \
  -p 8080:8080 \
  -v redline-data:/app/data \
  -v redline-logs:/app/logs \
  -e FLASK_ENV=production \
  redline:latest
```

### **Systemd Service (Linux)**
```ini
# /etc/systemd/system/redline.service
[Unit]
Description=REDLINE Web Interface
After=network.target

[Service]
Type=simple
User=redline
WorkingDirectory=/home/redline/redline
ExecStart=/home/redline/redline/start_web.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📞 **Support and Maintenance**

### **Regular Maintenance**
- **Update packages**: `pip install --upgrade -r requirements.txt`
- **Clean logs**: Remove old log files periodically
- **Backup data**: Regular backup of data directory
- **Monitor resources**: Check disk space and memory usage

### **Getting Help**
- **Check logs**: Review application and system logs
- **Verify installation**: Run verification scripts
- **Test components**: Test web interface and GUI separately
- **Check dependencies**: Ensure all packages are installed

---

## ✅ **Installation Complete!**

**REDLINE is now installed with all dependencies and ready to use!**

- **Web Interface**: http://localhost:8080
- **Installation Directory**: `~/redline/`
- **Startup Scripts**: `./start_web.sh`, `./start_gui.sh`, `./start_docker.sh`
- **Configuration**: `~/redline/redline.conf`
- **Data Storage**: `~/redline/data/`
- **Logs**: `~/redline/logs/`

**For any issues, check the troubleshooting section or run the verification scripts.** 🎉
