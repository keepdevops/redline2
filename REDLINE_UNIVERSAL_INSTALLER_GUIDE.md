# REDLINE Universal Installer Guide

## 🚀 **One-Install Script for All Implementation Options**

The `install_redline.sh` script provides a unified installation experience for all REDLINE GUI implementation options.

## 📋 **Installation Options**

### **1. 🌐 Web-Based GUI (Recommended)**
**Best for**: Universal access, easy setup
**Requirements**: Docker
**Access**: Web browser at `http://localhost:6080`

**Features**:
- ✅ No X11 required
- ✅ Works on any device with web browser
- ✅ Easy deployment and scaling
- ✅ Good performance

### **2. 🖥️ Tkinter GUI with X11**
**Best for**: Native performance, desktop use
**Requirements**: X11 (XQuartz on macOS)
**Access**: Native desktop application

**Features**:
- ✅ Best performance
- ✅ Native desktop integration
- ✅ Full GUI capabilities
- ⚠️ Requires X11 setup

### **3. 🔄 Hybrid (Tkinter + Web Fallback)**
**Best for**: Flexibility, automatic fallback
**Requirements**: X11 + Docker
**Access**: Desktop or web browser

**Features**:
- ✅ Tries Tkinter first
- ✅ Falls back to web GUI if X11 unavailable
- ✅ Best of both worlds
- ✅ Automatic detection

### **4. 🐳 Docker Compose Setup**
**Best for**: Production, multiple services
**Requirements**: Docker Compose
**Access**: Web browser

**Features**:
- ✅ Multiple services
- ✅ Web app + Web GUI
- ✅ Production ready
- ✅ Easy scaling

### **5. 🏠 Native Installation**
**Best for**: Simple setup, no Docker
**Requirements**: Python only
**Access**: Web browser at `http://localhost:8080`

**Features**:
- ✅ No Docker required
- ✅ Simple setup
- ✅ Web application only
- ✅ Lightweight

## 🚀 **Quick Start**

### **Interactive Installation**
```bash
# Run the installer
./install_redline.sh

# Follow the interactive menu
# Choose option 1 (Web-Based GUI)
# Wait for installation
# Run the generated startup script
```

### **Non-Interactive Installation**
```bash
# Install specific option
./install_redline.sh webgui      # Web-based GUI
./install_redline.sh tkinter     # Tkinter GUI
./install_redline.sh hybrid      # Hybrid setup
./install_redline.sh compose     # Docker Compose
./install_redline.sh native      # Native installation
```

## 🎯 **Installation Process**

### **1. Dependency Checking**
The installer automatically checks for:
- ✅ Python3
- ✅ pip3
- ✅ Docker (for containerized options)
- ✅ Git (optional)

### **2. Platform Detection**
Automatically detects:
- ✅ Operating System (macOS, Linux, Windows)
- ✅ Architecture (AMD64, ARM64)
- ✅ Available tools and dependencies

### **3. Installation Options**
Each option installs:
- ✅ Required dependencies
- ✅ Configuration files
- ✅ Startup scripts
- ✅ Management tools

## 📁 **Generated Files**

### **Startup Scripts**
- `start_webgui.sh` - Start web-based GUI
- `start_tkinter.sh` - Start Tkinter GUI
- `start_hybrid.sh` - Start hybrid GUI
- `start_compose.sh` - Start Docker Compose
- `start_native.sh` - Start native web app

### **Setup Scripts**
- `setup_x11_macos.sh` - X11 setup for macOS
- `manage_redline.sh` - Unified management script

### **Configuration Files**
- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile.webgui` - Web-based GUI Dockerfile

## 🔧 **Management Commands**

### **Unified Management**
```bash
# Start services
./manage_redline.sh start-webgui
./manage_redline.sh start-tkinter
./manage_redline.sh start-hybrid
./manage_redline.sh start-compose
./manage_redline.sh start-native

# Stop all services
./manage_redline.sh stop

# Show status
./manage_redline.sh status
```

### **Individual Startup**
```bash
# Web-based GUI
./start_webgui.sh

# Tkinter GUI
./start_tkinter.sh

# Hybrid GUI
./start_hybrid.sh

# Docker Compose
./start_compose.sh

# Native web app
./start_native.sh
```

## 🌐 **Access URLs**

### **Web-Based GUI**
- **URL**: `http://localhost:6080`
- **Password**: `redline123`
- **VNC**: `localhost:5901`

### **Web Application**
- **URL**: `http://localhost:8080`
- **No password required**

### **Tkinter GUI**
- **Access**: Native desktop application
- **No URL required**

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Docker Not Found**
```bash
# Install Docker
# macOS: Download Docker Desktop
# Linux: sudo apt install docker.io
# Windows: Install Docker Desktop
```

#### **X11 Not Working (macOS)**
```bash
# Install XQuartz
brew install --cask xquartz

# Start XQuartz
open -a XQuartz

# Allow connections
xhost +localhost
```

#### **Python Dependencies Missing**
```bash
# Install manually
pip3 install pandas numpy matplotlib seaborn plotly flask requests duckdb pyarrow fastparquet
```

#### **Port Conflicts**
```bash
# Check port usage
netstat -an | grep 6080
netstat -an | grep 8080

# Stop conflicting services
./manage_redline.sh stop
```

### **Debug Mode**
```bash
# Check status
./install_redline.sh status

# View logs
docker logs redline-webgui
docker logs redline-web

# Check processes
ps aux | grep -E "(web_app\.py|main\.py)"
```

## 📊 **Platform-Specific Notes**

### **macOS**
- ✅ Web-based GUI: Full support
- ✅ Tkinter GUI: Requires XQuartz
- ✅ Hybrid: Automatic fallback
- ⚠️ X11 setup required for Tkinter

### **Linux**
- ✅ Web-based GUI: Full support
- ✅ Tkinter GUI: Native X11 support
- ✅ Hybrid: Full support
- ✅ All options work well

### **Windows**
- ✅ Web-based GUI: Full support
- ⚠️ Tkinter GUI: Requires WSL2 + VcXsrv
- ✅ Hybrid: Web fallback works
- ⚠️ X11 setup complex

## 🎯 **Recommendations**

### **For Beginners**
1. **Choose Web-Based GUI** (Option 1)
2. **Simple setup**, no X11 required
3. **Universal access** through web browser

### **For Developers**
1. **Choose Hybrid** (Option 3)
2. **Best of both worlds**
3. **Automatic fallback** if X11 unavailable

### **For Production**
1. **Choose Docker Compose** (Option 4)
2. **Multiple services**
3. **Production ready**

### **For Simple Setup**
1. **Choose Native** (Option 5)
2. **No Docker required**
3. **Web application only**

## 🏆 **Benefits**

### **✅ Unified Experience**
- **One script** for all installation options
- **Interactive menu** for easy selection
- **Automatic dependency checking**
- **Platform detection**

### **✅ Flexibility**
- **Multiple deployment options**
- **Easy switching between options**
- **Unified management**
- **Comprehensive documentation**

### **✅ Reliability**
- **Automatic fallback** options
- **Error handling** and recovery
- **Status monitoring**
- **Troubleshooting guides**

---

**REDLINE Universal Installer: One script to rule them all!** 🚀
