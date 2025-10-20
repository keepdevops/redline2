# REDLINE Installation

## 🚀 **Quick Start**

### **Universal Installation (Recommended)**
```bash
# From REDLINE project root
./install.sh
```

### **One-Liner Installation**
```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/redline/main/install.sh | bash
```

## 📋 **Installation Options**

### **Installation Modes**
- **`auto`** - Automatically detect and install appropriate components (default)
- **`minimal`** - Install only essential components (Python + web)
- **`full`** - Install everything (Python + Docker + GUI + web)

### **Command Line Options**
```bash
./install.sh --mode minimal          # Minimal installation
./install.sh --mode web-only         # Web interface only
./install.sh --skip-docker           # Skip Docker installation
./install.sh --skip-gui              # Skip GUI components
./install.sh --user username         # Install for specific user
./install.sh --dir /path/to/redline  # Custom installation directory
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Pandas Import Error**
```bash
# Quick fix
./quick_fix_pandas.sh

# Or use the comprehensive fix
./install/archive/fix_pandas_import.sh
```

#### **2. Tkinter Issues (Ubuntu 24.04)**
```bash
# Fix Tkinter installation
./install/archive/fix_tkinter_ubuntu24.sh
```

#### **3. User Creation Issues**
```bash
# Fix user creation
./install/archive/fix_user_creation.sh
```

#### **4. General Import Issues**
```bash
# Comprehensive import fix
./install/archive/fix_import_issues.sh
```

### **Dependency Verification**
```bash
# Check all dependencies
./install/check_dependencies.sh

# Run comprehensive test
python3 test_all_dependencies.py
```

## 📁 **Directory Structure**

```
install/
├── README.md                    # This file
├── check_dependencies.sh        # Dependency verification
├── archive/                     # Legacy installation scripts
│   ├── install_*.sh            # Old installation scripts
│   ├── fix_*.sh                # Troubleshooting scripts
│   └── test_*.sh               # Testing scripts
└── *.md                        # Documentation files
```

## 🎯 **What Gets Installed**

### **Required Dependencies (14)**
- **Data Processing**: pandas, numpy, configparser
- **Data Storage**: pyarrow, polars, duckdb
- **Financial Data**: yfinance
- **Web Framework**: flask, flask-socketio, flask-compress
- **Utilities**: requests, urllib3, python-dateutil, pytz

### **Optional Dependencies (8)**
- **Scientific Computing**: matplotlib, seaborn, scipy, scikit-learn
- **File I/O**: openpyxl, xlsxwriter
- **System/Monitoring**: psutil, tkinter

### **System Components**
- **Python 3.11+** with virtual environment
- **Docker** (if supported and not skipped)
- **Startup scripts** for web, GUI, and Docker
- **Configuration files** and data directories

## 🚀 **After Installation**

### **Start REDLINE**
```bash
cd ~/redline

# Web interface (recommended)
./start_web.sh
# Then open: http://localhost:8080

# GUI interface (if available)
./start_gui.sh

# Docker services (if available)
./start_docker.sh
```

### **Access Points**
- **Web Interface**: http://localhost:8080
- **Installation Directory**: `~/redline/`
- **Logs**: `~/redline/logs/`
- **Data**: `~/redline/data/`

## 📚 **Documentation**

- **Universal Installation Guide**: `UNIVERSAL_INSTALLATION_GUIDE.md`
- **Local Installation Guide**: `LOCAL_INSTALLATION_GUIDE.md`
- **Dependency Analysis**: `../DEPENDENCY_ANALYSIS_REPORT.md`

## 🔧 **Legacy Scripts**

Legacy installation scripts are available in the `archive/` directory for troubleshooting specific issues:

- `install_universal.sh` - Previous universal installer
- `fix_pandas_import.sh` - Pandas import fix
- `fix_tkinter_ubuntu24.sh` - Ubuntu 24.04 Tkinter fix
- `fix_user_creation.sh` - User creation fix
- `fix_import_issues.sh` - Comprehensive import fix

---

**For the latest installation method, always use `./install.sh` from the project root!** 🎉