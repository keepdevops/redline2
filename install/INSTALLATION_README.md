# REDLINE Installation Guide

This guide covers installing REDLINE on different platforms using the provided installation scripts.

## 🚀 Quick Installation

### Automatic Installation (Recommended)

```bash
# Download and run the installation script
curl -fsSL https://raw.githubusercontent.com/redline/redline/main/install.sh | bash

# Or clone the repository and run locally
git clone https://github.com/redline/redline.git
cd redline
./install.sh
```

### Manual Installation

```bash
# For Ubuntu Intel/AMD
./install_ubuntu_intel.sh

# For Ubuntu ARM64/Apple Silicon
./install_ubuntu_arm.sh

# For macOS (Intel/Apple Silicon)
./install_macos.sh

# For Windows (WSL2)
./install_windows.sh
```

## 📋 Prerequisites

### Ubuntu
- Ubuntu 20.04 LTS or later
- sudo privileges
- Internet connection
- At least 2GB RAM
- At least 5GB free disk space

### macOS
- macOS 10.15 or later
- Xcode Command Line Tools
- Homebrew (optional but recommended)
- At least 2GB RAM
- At least 5GB free disk space

### Windows
- Windows 10/11 with WSL2
- Ubuntu 20.04 LTS or later in WSL2
- At least 2GB RAM
- At least 5GB free disk space

## 🔧 What Gets Installed

### Core Components
- **Python 3.11+** - Main runtime environment
- **Docker & Docker Compose** - Containerization platform
- **REDLINE Application** - Data analysis toolkit
- **Dependencies** - All required Python packages

### Applications
- **Tkinter GUI** - Traditional desktop interface
- **Flask Web App** - Modern web interface
- **Docker Images** - Containerized deployment options

### Services
- **Systemd Services** - Automatic startup on boot
- **Desktop Shortcuts** - Easy access from desktop
- **Configuration Files** - Pre-configured settings

## 🎯 Installation Options

### 1. Tkinter GUI Only
```bash
./install.sh --gui-only
```

### 2. Web App Only
```bash
./install.sh --web-only
```

### 3. Docker Only
```bash
./install.sh --docker-only
```

### 4. Full Installation (Default)
```bash
./install.sh
```

## 🚀 Post-Installation

### Starting REDLINE

#### Tkinter GUI
```bash
# Start GUI
sudo systemctl start redline-gui
# OR
cd /home/redline/redline && ./start_gui.sh
```

#### Web Interface
```bash
# Start web app
sudo systemctl start redline-web
# OR
cd /home/redline/redline && ./start_web.sh
# Then open: http://localhost:8080
```

#### Docker Services
```bash
# Start Docker services
sudo systemctl start redline-docker
# OR
cd /home/redline/redline && ./start_docker.sh
# Then open: http://localhost:8080
```

### Stopping REDLINE
```bash
# Stop all services
sudo systemctl stop redline-gui
sudo systemctl stop redline-web
sudo systemctl stop redline-docker

# OR stop Docker services
cd /home/redline/redline && ./stop_docker.sh
```

## 🔍 Access Information

### Web Interface
- **URL**: http://localhost:8080
- **Default Port**: 8080
- **Features**: Data loading, analysis, conversion, visualization

### VNC Access (Docker)
- **Host**: localhost
- **Port**: 5900
- **Password**: redline123
- **Features**: Remote GUI access

### File Locations
- **Installation**: `/home/redline/redline/`
- **Data**: `/home/redline/redline/data/`
- **Logs**: `/home/redline/redline/logs/`
- **Configuration**: `/home/redline/redline/redline.conf`

## 🛠️ Configuration

### Environment Variables
```bash
# Edit configuration
nano /home/redline/redline/docker.env
nano /home/redline/redline/redline.conf
```

### Docker Configuration
```bash
# Edit Docker Compose
nano /home/redline/redline/docker-compose.yml
```

### Service Configuration
```bash
# Edit systemd services
sudo nano /etc/systemd/system/redline-gui.service
sudo nano /etc/systemd/system/redline-web.service
sudo nano /etc/systemd/system/redline-docker.service
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Fix permissions
sudo chown -R redline:redline /home/redline/redline
sudo chmod +x /home/redline/redline/*.sh
```

#### 2. Docker Not Running
```bash
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 3. Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8080
sudo lsof -i :5900

# Kill the process
sudo kill -9 <PID>
```

#### 4. X Server Not Running (GUI)
```bash
# Start X server
sudo systemctl start display-manager
# OR
startx
```

#### 5. Firewall Issues
```bash
# Allow ports through firewall
sudo ufw allow 8080/tcp
sudo ufw allow 5900/tcp
```

### Logs and Debugging

#### View Logs
```bash
# Application logs
tail -f /home/redline/redline/logs/redline.log

# System service logs
sudo journalctl -u redline-gui -f
sudo journalctl -u redline-web -f
sudo journalctl -u redline-docker -f

# Docker logs
docker logs redline-web
docker logs redline-vnc
```

#### Debug Mode
```bash
# Run with debug output
cd /home/redline/redline
export DEBUG=true
./start_web.sh
```

## 📚 Additional Resources

### Documentation
- [User Guide](REDLINE_USER_GUIDE.md)
- [Docker Guide](DOCKER_MULTI_PLATFORM_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)

### Support
- [GitHub Issues](https://github.com/redline/redline/issues)
- [Discord Community](https://discord.gg/redline)
- [Documentation](https://docs.redline.dev)

### Examples
- [Sample Data](examples/sample_data/)
- [Tutorials](examples/tutorials/)
- [Scripts](examples/scripts/)

## 🔄 Updates

### Updating REDLINE
```bash
cd /home/redline/redline
git pull
sudo systemctl restart redline-web
sudo systemctl restart redline-gui
```

### Updating Docker Images
```bash
cd /home/redline/redline
docker-compose pull
docker-compose up -d
```

## 🗑️ Uninstallation

### Remove REDLINE
```bash
# Stop all services
sudo systemctl stop redline-gui
sudo systemctl stop redline-web
sudo systemctl stop redline-docker

# Remove systemd services
sudo systemctl disable redline-gui
sudo systemctl disable redline-web
sudo systemctl disable redline-docker
sudo rm /etc/systemd/system/redline-*.service
sudo systemctl daemon-reload

# Remove user and data
sudo userdel -r redline
sudo rm -rf /home/redline

# Remove Docker images
docker rmi redline:latest
docker rmi redline-web:latest
```

## 📄 License

This installation script and REDLINE are licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Need help?** Check out our [FAQ](FAQ.md) or [contact support](https://github.com/redline/redline/issues).
