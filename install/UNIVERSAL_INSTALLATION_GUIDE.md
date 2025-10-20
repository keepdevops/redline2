# REDLINE Universal Installation Guide

This guide covers the most generic and flexible approach to installing REDLINE across different platforms and environments.

## 🎯 **Universal Installation Philosophy**

The universal installer is designed to:
- ✅ **Auto-detect** your platform and environment
- ✅ **Adapt** to different operating systems and architectures
- ✅ **Minimize** user input and configuration
- ✅ **Maximize** compatibility across different scenarios
- ✅ **Provide** multiple installation modes

## 🚀 **Quick Start Options**

### **Option 1: One-Liner Installation (Easiest)**
```bash
# From anywhere (requires internet)
curl -fsSL https://raw.githubusercontent.com/redline/redline/main/install.sh | bash

# Or using wget
wget -qO- https://raw.githubusercontent.com/redline/redline/main/install.sh | bash
```

### **Option 2: Local Universal Installation**
```bash
# From REDLINE directory
./install/install_universal.sh
```

### **Option 3: Custom Installation**
```bash
# With specific options
./install/install_universal.sh --mode minimal --skip-docker
```

## 📋 **Installation Modes**

### **Auto Mode (Default)**
```bash
./install/install_universal.sh
```
- **What it does**: Automatically detects your environment and installs appropriate components
- **Best for**: Most users who want a hassle-free installation

### **Minimal Mode**
```bash
./install/install_universal.sh --mode minimal
```
- **What it does**: Installs only essential components (Python + web interface)
- **Best for**: Systems with limited resources or when you only need basic functionality

### **Full Mode**
```bash
./install/install_universal.sh --mode full
```
- **What it does**: Installs everything (Python + Docker + GUI + web interface)
- **Best for**: Users who want all features and capabilities

### **Web-Only Mode**
```bash
./install/install_universal.sh --mode web-only
```
- **What it does**: Installs only the web interface components
- **Best for**: Headless servers or when you only need the web interface

### **Docker-Only Mode**
```bash
./install/install_universal.sh --mode docker-only
```
- **What it does**: Installs only Docker components
- **Best for**: When you want to use REDLINE exclusively through Docker

## 🌍 **Supported Platforms**

### **Operating Systems**
- ✅ **Ubuntu** (18.04, 20.04, 22.04, 24.04 LTS)
- ✅ **Debian** (9, 10, 11, 12)
- ✅ **CentOS** (7, 8, Stream)
- ✅ **Red Hat Enterprise Linux** (7, 8, 9)
- ✅ **Fedora** (30+)
- ✅ **macOS** (10.15+, Intel and Apple Silicon)
- ✅ **Windows** (WSL2)

### **Architectures**
- ✅ **x86_64 (AMD64)** - Intel/AMD processors
- ✅ **ARM64** - Apple Silicon, ARM servers
- ✅ **ARM32** - Raspberry Pi, ARM devices

## 🔧 **Installation Options**

### **Basic Options**
```bash
./install/install_universal.sh [OPTIONS]
```

| Option | Description | Example |
|--------|-------------|---------|
| `--mode MODE` | Installation mode | `--mode minimal` |
| `--user USER` | Install for specific user | `--user myuser` |
| `--dir DIRECTORY` | Installation directory | `--dir /opt/redline` |
| `--skip-docker` | Skip Docker installation | `--skip-docker` |
| `--skip-gui` | Skip GUI components | `--skip-gui` |
| `--web-only` | Install only web interface | `--web-only` |
| `--help` | Show help message | `--help` |

### **Advanced Examples**

#### **Install for Specific User**
```bash
./install/install_universal.sh --user dataanalyst --dir /home/dataanalyst/redline
```

#### **Minimal Installation Without Docker**
```bash
./install/install_universal.sh --mode minimal --skip-docker
```

#### **Web-Only Installation**
```bash
./install/install_universal.sh --web-only
```

#### **Custom Directory Installation**
```bash
./install/install_universal.sh --dir /opt/redline
```

## 🔍 **Environment Detection**

The universal installer automatically detects:

### **System Information**
- Operating system and version
- Architecture (x86_64, ARM64, ARM32)
- Package manager (apt, yum, dnf, brew)

### **Capabilities**
- Sudo access availability
- Internet connectivity
- Docker availability
- Python installation
- GUI support (display server)
- Local REDLINE files

### **Auto-Adaptation**
Based on detected capabilities, the installer:
- Chooses appropriate package managers
- Installs compatible packages
- Configures environment-specific settings
- Provides fallback options

## 📁 **Installation Structure**

After installation, REDLINE is organized as:

```
~/redline/ (or custom directory)
├── main.py                 # Main application
├── web_app.py             # Flask web application
├── redline/               # Application modules
├── venv/                  # Python virtual environment
├── data/                  # Data storage
├── logs/                  # Application logs
├── start_web.sh           # Start web interface
├── start_gui.sh           # Start GUI (if available)
├── start_docker.sh        # Start Docker services (if available)
├── redline.conf           # Configuration file
└── requirements.txt       # Python dependencies
```

## 🚀 **Starting REDLINE**

### **Web Interface (Always Available)**
```bash
cd ~/redline
./start_web.sh
# Open browser: http://localhost:8080
```

### **GUI Interface (If Available)**
```bash
cd ~/redline
./start_gui.sh
```

### **Docker Services (If Available)**
```bash
cd ~/redline
./start_docker.sh
# Open browser: http://localhost:8080
```

## 🔧 **Configuration**

### **Web Port Configuration**
Edit `~/redline/redline.conf`:
```ini
[WEB]
port = 8080  # Change to your preferred port
```

### **Data Directory Configuration**
Edit `~/redline/redline.conf`:
```ini
[DEFAULT]
data_dir = ./data  # Change to your preferred data directory
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Permission Denied**
```bash
# Ensure you have proper permissions
sudo chown -R $USER:$USER ~/redline
chmod +x ~/redline/*.sh
```

#### **2. Python Not Found**
```bash
# Install Python manually
# Ubuntu/Debian:
sudo apt-get install python3 python3-pip

# CentOS/RHEL:
sudo yum install python3 python3-pip

# macOS:
brew install python3
```

#### **3. Tkinter Not Working**
```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS:
# Tkinter is included with Python
```

#### **4. Docker Issues**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

### **Platform-Specific Issues**

#### **Ubuntu 24.04 LTS**
```bash
# Fix Tkinter package issues
sudo apt-get install python3-tk python3-tkinter
```

#### **macOS**
```bash
# Install Homebrew if not available
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### **Windows WSL2**
```bash
# Ensure WSL2 is properly configured
wsl --update
```

## 🧪 **Verification**

### **Test Installation**
```bash
cd ~/redline
source venv/bin/activate

# Test Python
python3 --version

# Test Flask
python3 -c "import flask; print('Flask works!')"

# Test Tkinter (optional)
python3 -c "import tkinter; print('GUI works!')"

# Test web interface
./start_web.sh
# Check http://localhost:8080
```

### **Check Services**
```bash
# Check if web interface is running
curl http://localhost:8080/health

# Check Docker (if installed)
docker --version
docker-compose --version
```

## 📊 **Performance Optimization**

### **Minimal Resource Usage**
```bash
# Use minimal installation
./install/install_universal.sh --mode minimal --skip-docker
```

### **Production Deployment**
```bash
# Use full installation with custom directory
./install/install_universal.sh --mode full --dir /opt/redline
```

### **Development Setup**
```bash
# Use auto mode for development
./install/install_universal.sh --mode auto
```

## 🔄 **Updating REDLINE**

### **Update Installation**
```bash
cd ~/redline
git pull  # If installed from git
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### **Reinstall**
```bash
# Remove old installation
rm -rf ~/redline

# Reinstall
./install/install_universal.sh
```

## 📚 **Additional Resources**

- **Platform-Specific Guides**: Check other installation guides for detailed platform instructions
- **Docker Guide**: `DOCKER_MULTI_PLATFORM_GUIDE.md`
- **User Guide**: `REDLINE_USER_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`

## 🤝 **Support**

### **Getting Help**
1. Check this guide first
2. Run the installer with `--help` for options
3. Check platform-specific troubleshooting
4. Verify your environment meets requirements

### **Reporting Issues**
When reporting issues, include:
- Operating system and version
- Architecture (x86_64, ARM64, etc.)
- Installation mode used
- Error messages
- Environment capabilities

---

**The universal installer is designed to work everywhere, adapt to your environment, and provide the best REDLINE experience possible!** 🎉
