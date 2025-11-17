# REDLINE Multi-Platform Installation Guide

This guide provides step-by-step installation instructions for REDLINE across all supported platforms.

## Quick Installation

### 🍎 macOS
1. Download `REDLINE-1.0.0-macOS.dmg` from [GitHub Releases](https://github.com/keepdevops/redline2/releases)
2. Double-click DMG to mount
3. Drag `REDLINE.app` and `REDLINE Web.app` to Applications folder
4. Launch from Applications or Spotlight

### 🪟 Windows
1. Download `REDLINE-1.0.0-Setup.exe` from [GitHub Releases](https://github.com/keepdevops/redline2/releases)
2. Right-click installer → "Run as administrator"
3. Follow installation wizard
4. Launch from Start Menu or Desktop

### 🐧 Ubuntu
```bash
# Download DEB package
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0/redline-financial_1.0.0_amd64.deb

# Install package
sudo dpkg -i redline-financial_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Start REDLINE
cd ~
redline-web
```

## Detailed Installation Instructions

### macOS Installation

**System Requirements:**
- macOS 10.15 (Catalina) or later
- 500 MB free disk space
- Internet connection for data download

**Step-by-Step:**
1. **Download**: Get `REDLINE-1.0.0-macOS.dmg` from GitHub Releases
2. **Mount**: Double-click DMG file to mount the disk image
3. **Install**: Drag both `REDLINE.app` and `REDLINE Web.app` to Applications folder
4. **Launch**: 
   - Open Applications folder
   - Double-click `REDLINE.app` for GUI version
   - Double-click `REDLINE Web.app` for web version
5. **Access**: Web interface opens automatically at `http://localhost:8080`

**Troubleshooting:**
- **"App is damaged"**: Go to System Preferences > Security & Privacy > Allow apps from anywhere
- **Apps won't launch**: Check System Preferences > Security & Privacy for blocked apps
- **Web interface not loading**: Ensure port 8080 is not in use by another application

### Windows Installation

**System Requirements:**
- Windows 10 or later
- 500 MB free disk space
- Administrator privileges for installation
- Internet connection for data download

**Step-by-Step:**
1. **Download**: Get `REDLINE-1.0.0-Setup.exe` from GitHub Releases
2. **Run**: Right-click installer → "Run as administrator"
3. **Security Warning**: Click "More info" → "Run anyway" (normal for unsigned installers)
4. **Installation Wizard**:
   - Accept license agreement
   - Choose installation directory (default: `C:\Program Files\REDLINE`)
   - Select components (GUI and Web applications)
   - Choose Start Menu folder
   - Optionally create Desktop shortcuts
5. **Complete**: Click "Finish" to complete installation
6. **Launch**: 
   - Start Menu → REDLINE → REDLINE Financial
   - Or Desktop shortcut (if created)
   - Or Command Prompt: `redline-web`

**Command Line Usage:**
```cmd
# Start web interface
redline-web

# Start GUI application
redline-gui

# Check installation
where redline-web
```

**Troubleshooting:**
- **"Windows protected your PC"**: Click "More info" → "Run anyway"
- **PATH not found**: Restart Command Prompt or reboot computer
- **Permission denied**: Ensure installer was run as Administrator
- **Port 8080 in use**: Close other applications using port 8080

### Ubuntu Installation

**System Requirements:**
- Ubuntu 20.04 LTS or later
- 500 MB free disk space
- Internet connection for data download
- `sudo` privileges for installation

**Step-by-Step:**
1. **Download DEB Package**:
   ```bash
   wget https://github.com/keepdevops/redline2/releases/download/v1.0.0/redline-financial_1.0.0_amd64.deb
   ```

2. **Install Package**:
   ```bash
   sudo dpkg -i redline-financial_1.0.0_amd64.deb
   ```

3. **Fix Dependencies** (if needed):
   ```bash
   sudo apt-get install -f
   ```

4. **Start REDLINE**:
   ```bash
   cd ~
   redline-web
   ```

5. **Access Web Interface**: Open browser to `http://localhost:8080`

**Important Notes:**
- **Always run `cd ~`** before starting REDLINE (critical requirement)
- Data is stored in `~/redline-data/`
- Web interface runs on `localhost:8080`
- Both GUI and web applications are available

**Command Line Usage:**
```bash
# Check installation
which redline-web
which redline-gui

# Start web interface
cd ~
redline-web

# Start GUI application
cd ~
redline-gui

# Check data directory
ls ~/redline-data/
```

**Desktop Integration:**
- Applications menu: REDLINE Financial, REDLINE Web
- Command line: `redline-web`, `redline-gui`
- Data directory: `~/redline-data/`

**Troubleshooting:**
- **"cd ~" requirement**: Always run from home directory
- **Permission errors**: Check ownership of `~/redline-data/`
- **Desktop entries missing**: Run `update-desktop-database`
- **Port 8080 in use**: Check with `netstat -tlnp | grep 8080`

## Alternative Installation Methods

### PyPI Package (Python Developers)
```bash
pip install redline-financial
redline-web
```

### Docker (Any Platform)
```bash
docker pull redline-financial/redline:latest
docker run -p 8080:8080 redline-financial/redline:latest
```

### Source Code
```bash
git clone https://github.com/keepdevops/redline2.git
cd redline2
pip install -r requirements.txt
python web_app.py
```

## Post-Installation

### First Launch
1. **Web Interface**: Automatically opens at `http://localhost:8080`
2. **GUI Application**: Opens desktop window
3. **Data Directory**: Created automatically in appropriate location
4. **Configuration**: Default settings applied

### Configuration
- **Data Storage**: Configured automatically
- **Port Settings**: Default port 8080 (configurable)
- **API Keys**: Add your own keys in Settings
- **Themes**: Multiple color themes available

### Uninstallation

**macOS:**
- Drag apps from Applications folder to Trash
- Empty Trash to complete removal

**Windows:**
- Control Panel → Programs → Uninstall REDLINE Financial
- Or Start Menu → REDLINE → Uninstall REDLINE

**Ubuntu:**
```bash
sudo apt-get remove redline-financial
```

## Getting Help

### Documentation
- [GitHub Repository](https://github.com/keepdevops/redline2)
- [User Guide](https://github.com/keepdevops/redline2/blob/main/REDLINE_USER_GUIDE.md)
- [Developer Guide](https://github.com/keepdevops/redline2/blob/main/REDLINE_DEVELOPER_GUIDE.md)

### Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community support and questions
- **Email**: support@redline.example.com

### Common Issues
- **Port conflicts**: Change port in Settings or close conflicting applications
- **Permission errors**: Ensure proper user permissions
- **Data access**: Check data directory permissions
- **Network issues**: Verify internet connection for data download

---

**Welcome to REDLINE!** 🚀

Start exploring financial data analysis with our powerful, multi-platform tools.











