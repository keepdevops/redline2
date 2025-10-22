# REDLINE Installation & Setup Guide

## 🚀 **Quick Start**

Get REDLINE running in minutes with our streamlined installation process.

### **Prerequisites**
- **Python 3.8+** (3.9+ recommended)
- **4GB RAM** minimum (8GB recommended)
- **1GB free disk space**
- **Internet connection** (for data downloads)

### **Installation Methods**

#### **Method 1: Universal Installer (Recommended)**
```bash
# Download and run the universal installer
curl -fsSL https://raw.githubusercontent.com/your-repo/redline/main/universal_install.sh | bash

# Or download and run manually
wget https://raw.githubusercontent.com/your-repo/redline/main/universal_install.sh
chmod +x universal_install.sh
./universal_install.sh
```

#### **Method 2: Manual Installation**
```bash
# Clone the repository
git clone https://github.com/your-repo/redline.git
cd redline

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import redline; print('REDLINE installed successfully!')"
```

#### **Method 3: Docker Installation**
```bash
# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Build and run with Docker Compose
docker-compose up -d

# Access web interface
open http://localhost:8080
```

## 🖥️ **Platform-Specific Instructions**

### **Windows**

#### **Using Python**
```cmd
# Install Python 3.9+ from python.org
# Open Command Prompt as Administrator

# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Install dependencies
pip install -r requirements.txt

# Start web application
python web_app.py

# Start GUI application
python main.py
```

#### **Using Anaconda**
```cmd
# Create conda environment
conda create -n redline python=3.9
conda activate redline

# Install dependencies
pip install -r requirements.txt

# Start application
python web_app.py
```

### **macOS**

#### **Using Homebrew**
```bash
# Install Python
brew install python@3.9

# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Install dependencies
pip3 install -r requirements.txt

# Start application
python3 web_app.py
```

#### **Using MacPorts**
```bash
# Install Python
sudo port install python39

# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Install dependencies
python3.9 -m pip install -r requirements.txt

# Start application
python3.9 web_app.py
```

### **Linux (Ubuntu/Debian)**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-pip python3.9-venv git -y

# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Create virtual environment
python3.9 -m venv redline_env
source redline_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start application
python web_app.py
```

### **Linux (CentOS/RHEL/Fedora)**

```bash
# Install Python and dependencies
sudo dnf install python39 python39-pip git -y

# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Create virtual environment
python3.9 -m venv redline_env
source redline_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start application
python web_app.py
```

## 🐳 **Docker Installation**

### **Docker Compose (Recommended)**

```bash
# Clone repository
git clone https://github.com/your-repo/redline.git
cd redline

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Docker Run**

```bash
# Build image
docker build -t redline .

# Run container
docker run -d \
  --name redline \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  redline

# Access application
open http://localhost:8080
```

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file in the project root:

```bash
# Application Configuration
REDLINE_PORT=8080
REDLINE_HOST=0.0.0.0
REDLINE_DEBUG=False

# Database Configuration
REDLINE_DB_PATH=data/redline_data.duckdb
REDLINE_DB_POOL_SIZE=8

# Data Configuration
REDLINE_DATA_DIR=data
REDLINE_UPLOAD_DIR=data/uploads
REDLINE_MAX_FILE_SIZE=100MB

# API Configuration
REDLINE_API_RATE_LIMIT=1000
REDLINE_API_TIMEOUT=30

# Theme Configuration
REDLINE_DEFAULT_THEME=theme-default
REDLINE_THEME_CUSTOMIZATION=True
```

### **Configuration File**

Edit `data_config.ini`:

```ini
[general]
name = REDLINE
version = 1.0.0
debug = False

[database]
path = data/redline_data.duckdb
pool_size = 8
cache_size = 64

[data]
data_dir = data
upload_dir = data/uploads
max_file_size = 104857600
supported_formats = csv,parquet,feather,json,duckdb,txt

[api]
rate_limit = 1000
timeout = 30
cors_enabled = True

[themes]
default_theme = theme-default
customization_enabled = True
```

## 🚀 **Starting the Application**

### **Web Application**

```bash
# Start web server
python web_app.py

# Or with custom port
WEB_PORT=8082 python web_app.py

# Or with environment file
python -m dotenv run python web_app.py
```

**Access the application at:**
- **Local**: http://localhost:8080
- **Network**: http://your-ip:8080

### **GUI Application**

```bash
# Start GUI application
python main.py

# Or with specific configuration
python main.py --config custom_config.ini
```

### **Both Applications**

```bash
# Start web application in background
python web_app.py &

# Start GUI application
python main.py
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Python Version Issues**
```bash
# Check Python version
python --version

# If version is too old, install Python 3.9+
# Windows: Download from python.org
# macOS: brew install python@3.9
# Linux: sudo apt install python3.9
```

#### **Dependency Issues**
```bash
# Update pip
pip install --upgrade pip

# Install dependencies with verbose output
pip install -r requirements.txt -v

# Install specific problematic package
pip install pandas numpy duckdb flask
```

#### **Permission Issues**
```bash
# Linux/macOS: Fix permissions
sudo chown -R $USER:$USER /path/to/redline
chmod +x *.sh

# Windows: Run Command Prompt as Administrator
```

#### **Port Already in Use**
```bash
# Find process using port 8080
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
WEB_PORT=8082 python web_app.py
```

#### **Database Issues**
```bash
# Reset database
rm data/redline_data.duckdb
python -c "from redline.database.connector import DatabaseConnector; DatabaseConnector().initialize()"

# Check database permissions
ls -la data/
```

#### **Memory Issues**
```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS
wmic memorychip  # Windows

# Reduce memory usage
export REDLINE_DB_POOL_SIZE=4
export REDLINE_MAX_FILE_SIZE=50MB
```

### **Log Files**

Check log files for detailed error information:

```bash
# Application logs
tail -f redline.log

# Web application logs
tail -f redline_web.log

# Database logs
tail -f redline_data.log
```

### **Debug Mode**

Enable debug mode for detailed error information:

```bash
# Set debug environment variable
export REDLINE_DEBUG=True

# Or edit configuration file
echo "debug = True" >> data_config.ini

# Start application
python web_app.py
```

## 🔍 **Verification**

### **Installation Verification**

Run the verification script:

```bash
# Run verification
python verify_installation.py

# Or use the shell script
./verify_installation.sh
```

### **Manual Verification**

```bash
# Test Python imports
python -c "
import redline
from redline.core.data_loader import DataLoader
from redline.database.connector import DatabaseConnector
print('✅ All imports successful')
"

# Test web application
curl http://localhost:8080/api/status

# Test GUI application
python -c "
import tkinter as tk
from redline.gui.main_window import StockAnalyzerGUI
print('✅ GUI components available')
"
```

### **Performance Test**

```bash
# Run performance tests
python -m pytest tests/performance/ -v

# Or run specific tests
python tests/test_performance.py
```

## 📦 **Package Management**

### **Virtual Environments**

#### **Using venv**
```bash
# Create virtual environment
python -m venv redline_env

# Activate (Linux/macOS)
source redline_env/bin/activate

# Activate (Windows)
redline_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

#### **Using conda**
```bash
# Create conda environment
conda create -n redline python=3.9

# Activate environment
conda activate redline

# Install dependencies
pip install -r requirements.txt

# Deactivate
conda deactivate
```

### **Dependency Management**

#### **requirements.txt**
```
flask>=2.3.0
pandas>=1.5.0
numpy>=1.21.0
duckdb>=0.8.0
tkinter
requests>=2.28.0
```

#### **requirements-dev.txt**
```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
```

## 🔄 **Updates**

### **Updating REDLINE**

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
pkill -f "web_app.py"
python web_app.py &
```

### **Rollback**

```bash
# Check git log
git log --oneline

# Rollback to previous version
git reset --hard <commit-hash>

# Reinstall dependencies if needed
pip install -r requirements.txt
```

## 🛠️ **Development Setup**

### **Development Dependencies**

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8 redline/
black redline/
mypy redline/
```

### **IDE Configuration**

#### **VS Code**
```json
{
    "python.defaultInterpreterPath": "./redline_env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

#### **PyCharm**
- Set Python interpreter to virtual environment
- Enable pytest as test runner
- Configure code style to use Black formatter

## 📚 **Additional Resources**

- **Documentation**: [REDLINE Comprehensive Documentation](REDLINE_COMPREHENSIVE_DOCUMENTATION.md)
- **API Reference**: [REDLINE API Reference](REDLINE_API_REFERENCE.md)
- **User Guide**: [REDLINE User Guide](REDLINE_USER_GUIDE.md)
- **Developer Guide**: [REDLINE Developer Guide](REDLINE_DEVELOPER_GUIDE.md)

## 🆘 **Getting Help**

### **Support Channels**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and tutorials
- **Community Forums**: User community support
- **Email Support**: support@redline.dev

### **Common Commands**

```bash
# Check system status
curl http://localhost:8080/api/status

# View application logs
tail -f redline.log

# Restart application
pkill -f "web_app.py" && python web_app.py &

# Reset configuration
cp data_config.ini.backup data_config.ini

# Clear cache
rm -rf __pycache__/
rm -rf redline/__pycache__/
```

---

**REDLINE: Easy to install, powerful to use.** 🚀
