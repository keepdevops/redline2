# REDLINE Universal Installer

## 🚀 **Complete Universal Installation**

This directory contains all the files needed for a complete REDLINE installation without GitHub verification, supporting both Docker and bare metal installations.

## 📁 **Files in This Directory**

- **`universal_install.sh`** - Main universal installer script
- **`verify_installation.sh`** - Installation verification script
- **`requirements_complete.txt`** - Complete requirements file
- **`install.sh`** - Simplified installer (from install/ directory)
- **`verify.sh`** - Quick verification script (from install/ directory)
- **`check_dependencies.sh`** - Comprehensive dependency checker (from install/ directory)
- **`UNIVERSAL_INSTALLATION_GUIDE.md`** - Comprehensive installation guide

## 🎯 **Quick Start**

### **Universal Installation**
```bash
# From REDLINE project root
./universal_installer/universal_install.sh
```

### **Installation Options**
```bash
./universal_installer/universal_install.sh --mode bare-metal    # Bare metal installation
./universal_installer/universal_install.sh --mode docker        # Docker installation
./universal_installer/universal_install.sh --mode minimal       # Minimal installation
./universal_installer/universal_install.sh --web-only          # Web interface only
```

### **Verification**
```bash
./universal_installer/verify_installation.sh
```

## 📦 **Complete Dependency Coverage**

### **Required Dependencies (14) ✅**
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

### **Optional Dependencies (10) ✅**
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

- ✅ **Linux**: Ubuntu, Debian, CentOS, RHEL, Fedora
- ✅ **macOS**: Homebrew integration
- ✅ **Windows**: WSL support
- ✅ **Docker**: Multi-platform Docker builds

## 🐳 **Docker Support**

The installer includes complete Docker support with:
- **Docker Compose** configuration
- **Dockerfile** for containerized deployment
- **Volume mounts** for persistent data
- **Environment variables** for configuration

## 🔧 **Bare Metal Support**

The installer supports bare metal installation with:
- **System package installation** (OS-specific)
- **Python virtual environment** setup
- **All dependencies** installed with proper versions
- **Startup scripts** for web, GUI, and Docker
- **Configuration files** and data directories

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
./universal_installer/verify_installation.sh
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

## 📚 **Documentation**

- **`UNIVERSAL_INSTALLATION_GUIDE.md`** - Comprehensive installation guide with detailed instructions
- **`requirements_complete.txt`** - Complete list of all dependencies
- **`verify_installation.sh`** - Installation verification script

## 🔒 **Security Considerations**

- REDLINE runs as the current user (not root)
- Data directories are user-owned
- Docker group membership for container access
- Web interface binds to 0.0.0.0 (all interfaces)
- Consider using reverse proxy for production

## 📊 **Performance Optimization**

- **Virtual Environment**: Always use virtual environment
- **Package Versions**: Use specific versions for stability
- **Memory Usage**: Monitor memory usage for large datasets
- **Docker Optimization**: Use named volumes for persistent data

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

---

## ✅ **Ready to Use!**

**The universal installer is complete and production-ready!**

- **No GitHub verification required**
- **All dependencies included**
- **Docker and bare metal support**
- **Cross-platform compatibility**
- **Comprehensive documentation**
- **Built-in verification and testing**

**Just run `./universal_installer/universal_install.sh` to get started!** 🚀
