# REDLINE Installation Scripts

This directory contains all installation scripts and documentation for REDLINE.

## 📁 Files in this directory:

### 🚀 Installation Scripts
- **`install.sh`** - Main installation wrapper script with auto-detection
- **`install_ubuntu_intel.sh`** - Complete Ubuntu Intel installation script
- **`verify_installation.sh`** - Installation verification and testing script

### 🔧 Troubleshooting Scripts
- **`fix_tkinter_ubuntu24.sh`** - Fix Tkinter installation for Ubuntu 24.04 LTS
- **`test_tkinter_packages.sh`** - Test Tkinter package availability
- **`fix_user_creation.sh`** - Fix user creation issues
- **`install_ubuntu_intel_current_user.sh`** - Alternative installation for current user

### 📚 Documentation
- **`README.md`** - This file (overview of installation scripts)
- **`INSTALLATION_README.md`** - Comprehensive installation guide

## 🚀 Quick Start

### Automatic Installation (Recommended)
```bash
# From the project root directory
./install/install.sh

# Or from anywhere
cd install && ./install.sh
```

### Manual Installation
```bash
# Ubuntu Intel/AMD
cd install && ./install_ubuntu_intel.sh

# Verify installation
cd install && ./verify_installation.sh
```

## 📋 What Gets Installed

### Core Components
- **Python 3.11+** - Main runtime environment
- **Docker & Docker Compose** - Containerization platform
- **REDLINE Application** - Data analysis toolkit
- **All Dependencies** - Required Python packages

### Applications
- **Tkinter GUI** - Traditional desktop interface
- **Flask Web App** - Modern web interface (port 8080)
- **Docker Images** - Containerized deployment options

### Services & Integration
- **Systemd Services** - Automatic startup on boot
- **Desktop Shortcuts** - Easy access from desktop
- **Configuration Files** - Pre-configured settings
- **Firewall Rules** - Network access configuration

## 🎯 Supported Platforms

| Platform | Architecture | Script | Status |
|----------|-------------|---------|---------|
| Ubuntu | Intel/AMD x86_64 | `install_ubuntu_intel.sh` | ✅ Ready |
| Ubuntu | ARM64/Apple Silicon | `install_ubuntu_arm.sh` | 🚧 Planned |
| macOS | Intel/Apple Silicon | `install_macos.sh` | 🚧 Planned |
| Windows | WSL2 | `install_windows.sh` | 🚧 Planned |

## 🔧 Usage Examples

### Auto-detect Platform
```bash
./install.sh
```

### Force Specific Platform
```bash
./install.sh --platform ubuntu --arch amd64
```

### Show Help
```bash
./install.sh --help
```

### Verify Installation
```bash
./verify_installation.sh
```

## 🚀 Post-Installation Access

### Web Interface
```bash
# Start web app
sudo systemctl start redline-web
# Access at: http://localhost:8080
```

### Tkinter GUI
```bash
# Start GUI (requires X server)
sudo systemctl start redline-gui
```

### Docker Services
```bash
# Start Docker services
sudo systemctl start redline-docker
# Web: http://localhost:8080
# VNC: localhost:5900 (password: redline123)
```

## 🔍 Troubleshooting

### Common Issues
1. **Permission Denied**: Run with proper sudo privileges
2. **Docker Not Running**: Start Docker service
3. **Port Conflicts**: Check what's using ports 8080/5900
4. **X Server Issues**: Ensure display server is running for GUI

### Ubuntu 24.04 LTS Specific Issues
1. **"Package tkinter not found"**: This is a known issue with Ubuntu 24.04
   ```bash
   # Run the Tkinter fix script
   ./install/fix_tkinter_ubuntu24.sh
   
   # Or test available packages
   ./install/test_tkinter_packages.sh
   ```

2. **"User redline does not exist"**: User creation issues
   ```bash
   # Fix user creation
   ./install/fix_user_creation.sh
   
   # Or install for current user instead
   ./install/install_ubuntu_intel_current_user.sh
   ```

3. **Tkinter GUI not working**: On headless servers, use web interface instead
   ```bash
   # Web interface works without Tkinter
   sudo systemctl start redline-web
   # Access at: http://localhost:8080
   ```

### Verification
```bash
# Run verification script
./verify_installation.sh

# Check logs
sudo journalctl -u redline-web -f
sudo journalctl -u redline-gui -f

# Test Tkinter specifically
./install/test_tkinter_packages.sh
```

## 📚 Additional Resources

- **Main Documentation**: `INSTALLATION_README.md`
- **Docker Guide**: `../DOCKER_MULTI_PLATFORM_GUIDE.md`
- **User Guide**: `../REDLINE_USER_GUIDE.md`

## 🤝 Contributing

To add support for new platforms:
1. Create new installation script (e.g., `install_platform_arch.sh`)
2. Update `install.sh` to detect and use new script
3. Test on target platform
4. Update documentation

## 📄 License

These installation scripts are part of REDLINE and are licensed under the MIT License.
