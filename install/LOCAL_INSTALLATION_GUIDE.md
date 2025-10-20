# REDLINE Local Installation Guide

This guide explains how to install REDLINE using local files without requiring GitHub authorization.

## 🎯 **When to Use Local Installation**

Use the local installation script when:
- ✅ You don't have GitHub authorization set up
- ✅ You want to install from existing REDLINE files
- ✅ You're working in an environment without internet access to GitHub
- ✅ You want to install for the current user without creating additional users

## 🚀 **Quick Start**

### **Prerequisites**
1. You must be in the REDLINE root directory (where `main.py` and `redline/` folder exist)
2. Ubuntu 24.04 LTS (Intel/AMD x86_64)
3. Sudo privileges for package installation

### **Installation**
```bash
# From the REDLINE root directory
./install/install_local_current_user.sh
```

## 📋 **What the Script Does**

### **1. System Setup**
- Updates Ubuntu packages
- Installs essential packages (Python, Docker, Tkinter, etc.)
- Fixes Ubuntu 24.04 Tkinter package issues

### **2. Local File Copy**
- Copies all REDLINE files to `~/redline/`
- Sets proper file permissions
- Creates necessary directories

### **3. Python Environment**
- Creates Python virtual environment
- Installs all required packages
- Tests Tkinter and Flask installation

### **4. Docker Setup (Optional)**
- Installs Docker and Docker Compose
- Builds Docker images if Docker files exist
- Configures Docker for current user

### **5. User Experience**
- Creates startup scripts
- Creates desktop shortcuts
- Sets up configuration files
- Configures firewall rules

## 🔧 **Installation Options**

### **Option 1: Full Installation (Recommended)**
```bash
# Install everything including Docker
./install/install_local_current_user.sh
```

### **Option 2: Python Only**
If you don't want Docker, you can modify the script to skip Docker installation.

## 📁 **Directory Structure After Installation**

```
~/redline/
├── main.py                 # Main application
├── web_app.py             # Flask web application
├── redline/               # Application modules
├── data/                  # Data storage
│   ├── downloaded/
│   ├── converted/
│   └── stooq_format/
├── logs/                  # Application logs
├── venv/                  # Python virtual environment
├── start_gui.sh           # Start Tkinter GUI
├── start_web.sh           # Start Flask web app
├── start_docker.sh        # Start Docker services
├── stop_docker.sh         # Stop Docker services
├── docker.env             # Docker configuration
├── redline.conf           # Application configuration
└── requirements.txt       # Python dependencies
```

## 🚀 **How to Start REDLINE**

### **Tkinter GUI**
```bash
cd ~/redline
./start_gui.sh
```

### **Flask Web App**
```bash
cd ~/redline
./start_web.sh
# Open browser: http://localhost:8080
```

### **Docker Services**
```bash
cd ~/redline
./start_docker.sh
# Open browser: http://localhost:8080
# VNC access: localhost:5900 (password: redline123)
```

## 🛑 **How to Stop REDLINE**

### **Stop Docker Services**
```bash
cd ~/redline
./stop_docker.sh
```

### **Stop Web App**
Press `Ctrl+C` in the terminal where the web app is running.

### **Stop GUI**
Close the GUI window or press `Ctrl+C` in the terminal.

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"lsb_release not found"**
   ```bash
   sudo apt-get install lsb-release
   ```

2. **"Package tkinter not found"**
   ```bash
   ./install/fix_tkinter_ubuntu24.sh
   ```

3. **"Permission denied"**
   ```bash
   chmod +x ~/redline/*.sh
   ```

4. **"Docker not found"**
   - Docker installation is optional
   - Use `start_web.sh` instead of `start_docker.sh`

### **Verification**
```bash
# Test Python environment
cd ~/redline
source venv/bin/activate
python3 --version

# Test Tkinter
python3 -c "import tkinter; print('Tkinter works!')"

# Test Flask
python3 -c "import flask; print('Flask works!')"
```

## 📊 **Access Information**

- **Web Interface**: http://localhost:8080
- **VNC Access**: localhost:5900 (password: redline123)
- **Logs**: `~/redline/logs/`
- **Data**: `~/redline/data/`
- **Configuration**: `~/redline/redline.conf`

## 🔧 **Configuration**

### **Web Port**
Edit `~/redline/redline.conf`:
```ini
[WEB]
port = 8080  # Change to your preferred port
```

### **Docker Settings**
Edit `~/redline/docker.env`:
```bash
WEB_PORT=8080
VNC_PORT=5900
VNC_PASSWORD=redline123
```

## 📚 **Additional Resources**

- **Main Documentation**: `~/redline/README.md`
- **Docker Guide**: `~/redline/DOCKER_MULTI_PLATFORM_GUIDE.md`
- **User Guide**: `~/redline/REDLINE_USER_GUIDE.md`

## ⚠️ **Important Notes**

1. **No GitHub Required**: This installation uses local files only
2. **Current User**: Installs for the current user, no additional users created
3. **Home Directory**: All files are installed in `~/redline/`
4. **Docker Optional**: Docker installation can be skipped if not needed
5. **Firewall**: Web ports (8080, 5900) are automatically configured

## 🤝 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Run the verification commands
3. Check the logs in `~/redline/logs/`
4. Ensure you have proper permissions for file access

---

**Happy analyzing with REDLINE!** 🎉
