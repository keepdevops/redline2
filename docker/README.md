# REDLINE Docker Directory Structure

This directory contains organized Docker configurations for different REDLINE deployment scenarios.

## 🔐 **Sudo Requirements**

### **✅ NO SUDO REQUIRED for Docker Operations**

All Docker build scripts run **without sudo privileges**:
- ✅ **Docker Build**: Runs as regular user
- ✅ **Docker Run**: Runs as regular user  
- ✅ **Container Management**: All docker commands
- ✅ **Package Installation**: Happens inside containers
- ✅ **File Operations**: Uses user's home directory

### **📋 Prerequisites (One-Time Setup)**

**Option 1: Docker Group (Recommended)**
```bash
# One-time sudo setup
sudo usermod -aG docker $USER
newgrp docker  # or logout/login

# Verify
docker ps  # Should work without sudo
```

**Option 2: Snap Docker (No Sudo)**
```bash
# Install Docker via snap (no sudo required)
snap install docker

# Use snap docker commands
snap run docker build -f Dockerfile -t redline-web .
```

**Option 3: Docker Desktop**
```bash
# Download from https://docker.com
# Install Docker Desktop (includes GUI)
```

## 📁 Directory Structure

```
docker/
├── gui/                    # GUI-specific Docker configuration
│   ├── Dockerfile          # GUI-optimized Docker image
│   ├── build.sh            # GUI build and setup script
│   ├── start_gui_container.sh  # GUI container startup
│   ├── test_gui.sh         # GUI installation test
│   └── README.md           # GUI usage instructions
│
├── web/                    # Web App-specific Docker configuration
│   ├── Dockerfile          # Web App-optimized Docker image
│   ├── build.sh            # Web App build and setup script
│   ├── start_web_container.sh  # Web App container startup
│   ├── test_web.sh         # Web App installation test
│   └── README.md           # Web App usage instructions
│
└── universal/              # Universal Docker configuration
    ├── Dockerfile          # Universal Docker image (GUI + Web App)
    ├── build.sh            # Universal build and setup script
    ├── start_gui_container.sh  # GUI container startup
    ├── start_web_container.sh  # Web App container startup
    ├── test_universal.sh   # Universal installation test
    └── README.md           # Universal usage instructions
```

## 🎯 **Choose Your Deployment Strategy**

### **GUI-Only Deployment** (`docker/gui/`)
- **Best for**: Desktop applications, local development
- **Features**: Tkinter GUI, X11 forwarding, interactive charts
- **Platform**: Linux with X11 support
- **Use case**: Personal use, data analysis, visualization

### **Web App-Only Deployment** (`docker/web/`)
- **Best for**: Web services, production deployment
- **Features**: Flask web app, REST API, WebSocket support
- **Platform**: Any platform with Docker
- **Use case**: Web services, API endpoints, remote access

### **Universal Deployment** (`docker/universal/`)
- **Best for**: Full-featured applications, development environments
- **Features**: Both GUI and Web App in one image
- **Platform**: Universal platform support
- **Use case**: Complete REDLINE installation, flexible deployment

## 🚀 **Quick Start Guide**

### **🔧 One-Time Setup**
```bash
# Add user to docker group (sudo required once)
sudo usermod -aG docker $USER
newgrp docker  # or logout/login

# Verify Docker works without sudo
docker ps
```

### **🖥️ GUI Deployment**
```bash
cd docker/gui
./build.sh                    # Build GUI image (no sudo)
./start_gui_container.sh       # Start GUI container (no sudo)
```

### **🌐 Web App Deployment**
```bash
cd docker/web
./build.sh                    # Build Web App image (no sudo)
./start_web_container.sh      # Start Web App container (no sudo)
```

### **🚀 Universal Deployment**
```bash
cd docker/universal
./build.sh                    # Build Universal image (no sudo)
./start_gui_container.sh      # Start GUI (no sudo)
./start_web_container.sh     # Start Web App (no sudo)
```

## 🔧 **Platform Support**

All Docker configurations support:
- **linux/amd64** (Intel/AMD 64-bit)
- **linux/arm64** (ARM 64-bit)
- **linux/arm/v7** (ARM 32-bit)

## 📦 **Conda Environment**

Each Docker image uses a dedicated conda environment:
- **GUI**: `redline-gui`
- **Web App**: `redline-web`
- **Universal**: `redline-universal`

## 🎨 **Features Comparison**

| Feature | GUI | Web App | Universal |
|---------|-----|---------|-----------|
| **Tkinter GUI** | ✅ | ❌ | ✅ |
| **Flask Web App** | ❌ | ✅ | ✅ |
| **X11 Forwarding** | ✅ | ❌ | ✅ |
| **Nginx Reverse Proxy** | ❌ | ✅ | ✅ |
| **Gunicorn Production** | ❌ | ✅ | ✅ |
| **WebSocket Support** | ❌ | ✅ | ✅ |
| **File Upload** | ✅ | ✅ | ✅ |
| **Data Visualization** | ✅ | ✅ | ✅ |
| **REST API** | ❌ | ✅ | ✅ |
| **Real-time Updates** | ✅ | ✅ | ✅ |

## 🛠️ **Development Workflow**

### **Local Development**
1. Use `docker/gui/` for GUI development
2. Use `docker/web/` for web app development
3. Use `docker/universal/` for full-stack development

### **Testing**
1. Run test scripts in each directory
2. Verify platform compatibility
3. Test both GUI and Web App functionality

### **Production Deployment**
1. Use `docker/web/` for web services
2. Use `docker/universal/` for complete applications
3. Configure reverse proxy and load balancing

## 📚 **Documentation**

Each directory contains:
- **README.md**: Detailed usage instructions
- **build.sh**: Automated build and setup
- **test_*.sh**: Installation verification
- **start_*.sh**: Container startup scripts

## 🔍 **Troubleshooting**

### **Common Issues**
1. **X11 Forwarding**: Required for GUI applications
2. **Port Conflicts**: Check port availability
3. **Platform Compatibility**: Verify architecture support
4. **Conda Environment**: Ensure proper activation
5. **Docker Permissions**: User not in docker group

### **Docker Permission Issues**
```bash
# Error: "Cannot connect to the Docker daemon"
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker  # or logout/login

# Verify
docker ps  # Should work without sudo
```

### **Alternative: Snap Docker (No Sudo)**
```bash
# Install Docker via snap
snap install docker

# Use snap docker commands
snap run docker build -f Dockerfile -t redline-web .
snap run docker run -d --name redline-web-container redline-web
```

### **Support**
- Check individual README.md files
- Run test scripts for verification
- Review Docker logs for errors
- Verify platform compatibility

## 🎯 **Recommendations**

- **For Desktop Use**: Use `docker/gui/`
- **For Web Services**: Use `docker/web/`
- **For Complete Solution**: Use `docker/universal/`
- **For Development**: Use `docker/universal/`
- **For Production**: Use `docker/web/` or `docker/universal/`

Choose the deployment strategy that best fits your needs!
