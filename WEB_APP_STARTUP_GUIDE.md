# REDLINE Flask Web Application - Startup Guide

## Quick Start Scripts

This guide provides multiple ways to start the REDLINE Flask web application, from simple one-command startup to comprehensive installation and configuration.

## 🚀 **Quick Start (Recommended)**

### **Simple Startup**
```bash
./quick_start_web.sh
```
- Starts the app on port 8082 (default)
- Automatically installs Flask and pandas if missing
- Creates necessary directories
- Kills any existing process on the port

### **Custom Port**
```bash
./quick_start_web.sh 8080
```
- Starts the app on port 8080 (or any port you specify)

## 🔧 **Advanced Startup Scripts**

### **1. Comprehensive Startup Script**
```bash
./start_web_app.sh
```
**Features:**
- Complete dependency checking and installation
- Port conflict resolution
- Health monitoring
- Detailed logging and status messages
- Multiple command-line options

**Usage Examples:**
```bash
# Start with default settings
./start_web_app.sh

# Start on custom port
./start_web_app.sh -p 8080

# Start in debug mode
./start_web_app.sh -d

# Kill existing process and start
./start_web_app.sh -k -p 8082

# Check dependencies only
./start_web_app.sh --check-deps
```

### **2. Complete Installation and Startup**
```bash
./install_and_start_web.sh
```
**Features:**
- Installs ALL required dependencies (Flask, pandas, financial data libraries, etc.)
- Creates all necessary directories
- Comprehensive error checking
- Option to install only or skip installation

**Usage Examples:**
```bash
# Install everything and start
./install_and_start_web.sh

# Install on custom port
./install_and_start_web.sh -p 8080

# Install dependencies only (don't start)
./install_and_start_web.sh --install-only

# Start without installing (if already installed)
./install_and_start_web.sh --skip-install
```

## 🪟 **Windows Users**

### **Windows Batch File**
```cmd
start_web_app.bat
```
**Usage:**
```cmd
# Start with default settings
start_web_app.bat

# Start on custom port
start_web_app.bat -p 8080

# Start in debug mode
start_web_app.bat -d

# Kill existing process and start
start_web_app.bat -k -p 8082
```

## 📋 **Manual Startup (If Scripts Don't Work)**

### **Step 1: Install Dependencies**
```bash
pip3 install flask flask-socketio flask-compress pandas numpy duckdb pyarrow
```

### **Step 2: Create Directories**
```bash
mkdir -p data/uploads data/converted logs
```

### **Step 3: Set Environment Variables**
```bash
export WEB_PORT=8082
export HOST=0.0.0.0
export DEBUG=false
export FLASK_APP=web_app.py
```

### **Step 4: Start the Application**
```bash
python3 web_app.py
```

## 🌐 **Accessing the Application**

Once started, access your REDLINE web application at:
- **Local:** http://localhost:8082
- **Network:** http://[your-ip]:8082

## 🎨 **Features Available**

### **Font Color Customization**
- Look for the floating palette button (🎨) on the right side of the screen
- Click to open the color customization panel
- Customize individual text colors or choose from preset schemes
- Changes are saved automatically

### **Available Tabs**
- **📊 Data Tab**: Load, filter, and analyze financial data
- **⬇️ Download Tab**: Download fresh financial data from various sources
- **🔄 Converter Tab**: Convert between different file formats
- **📈 Analysis Tab**: Perform comprehensive financial and statistical analysis
- **⚙️ Settings Tab**: Configure application settings
- **📋 Tasks Tab**: Monitor background operations

## 🔍 **Troubleshooting**

### **Port Already in Use**
```bash
# Kill existing process and start
./start_web_app.sh -k -p 8082

# Or find and kill manually
lsof -ti :8082 | xargs kill -9
```

### **Missing Dependencies**
```bash
# Install all dependencies
./install_and_start_web.sh --install-only

# Or install manually
pip3 install flask flask-socketio flask-compress pandas numpy duckdb
```

### **Permission Issues**
```bash
# Make scripts executable
chmod +x *.sh

# Run with sudo if needed (not recommended for production)
sudo ./start_web_app.sh
```

### **Python Path Issues**
```bash
# Use python3 explicitly
python3 web_app.py

# Or check Python version
python3 --version
```

## 📊 **Performance Tips**

### **For Large Datasets**
- Use the virtual scrolling feature in the Data tab
- Enable background task processing for long operations
- Use the optimized database connector for better performance

### **For Development**
- Start in debug mode: `./start_web_app.sh -d`
- Enable auto-reload for faster development
- Check logs in the `logs/` directory

## 🛡️ **Security Notes**

- The application runs on `0.0.0.0` by default (accessible from network)
- For production, consider using a reverse proxy (nginx, Apache)
- Use environment variables for sensitive configuration
- Enable HTTPS in production environments

## 📝 **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_PORT` | 8082 | Port number for the web application |
| `HOST` | 0.0.0.0 | Host address to bind to |
| `DEBUG` | false | Enable debug mode |
| `FLASK_APP` | web_app.py | Flask application entry point |

## 🆘 **Getting Help**

### **Check Application Health**
```bash
curl http://localhost:8082/health
```

### **View Application Logs**
```bash
tail -f redline_web.log
```

### **Test API Endpoints**
```bash
# Test font color API
curl http://localhost:8082/api/font-colors

# Test theme API
curl http://localhost:8082/api/themes
```

---

**🎉 Enjoy using your REDLINE Flask Web Application with full font color customization capabilities!**
