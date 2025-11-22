# REDLINE - Professional Financial Data Analysis Platform

<div align="center">

![REDLINE Logo](https://img.shields.io/badge/REDLINE-Financial%20Data%20Analyzer-blue?style=for-the-badge&logo=chart-line)

**Professional-grade financial data analysis with modern GUI, web interface, and multi-platform distribution**

[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![PyPI](https://img.shields.io/badge/PyPI-Package-orange?logo=pypi)](https://pypi.org/project/redline-financial/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](README.md)

</div>

---

## 🌟 **What is REDLINE?**

REDLINE is a comprehensive **financial data analysis platform** that provides data downloading, viewing, filtering, and analysis capabilities with both modern GUI and web interfaces. It supports multiple data sources, formats, and deployment methods for professional financial data analysis.

**Perfect for:**
- 📊 **Financial Analysts** - Professional data analysis tools
- 🔬 **Data Scientists** - ML-ready data processing
- 🎓 **Researchers** - Academic financial research  
- 💻 **Developers** - Extensible platform for custom solutions
- 📈 **Traders** - Market data analysis and visualization

## 🚀 **Quick Start - Multiple Installation Methods**

### **Method 1: Pre-built Docker Images (Fastest)**
```bash
# For Intel/AMD64 machines (Dell, most servers)
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0-optimized/redline-webgui-amd64.tar
docker load -i redline-webgui-amd64.tar
docker tag redline-webgui:amd64 redline-webgui:latest

# For Apple Silicon (M1/M2/M3 Macs)
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0-optimized/redline-webgui-arm64.tar
docker load -i redline-webgui-arm64.tar
docker tag redline-webgui:arm64 redline-webgui:latest

# Start optimized container with Gunicorn
docker run -d --name redline-webgui -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest

# Access web interface
open http://localhost:8080
```

### **Method 2: Build from Source (Latest Features)**
```bash
# Clone and build optimized Docker image
git clone https://github.com/keepdevops/redline2.git
cd redline2
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .

# Start container
docker run -d --name redline-webgui -p 8080:8080 redline-webgui:latest
```

### **Method 3: PyPI Package**
```bash
# Install from PyPI
pip install redline-financial

# Start GUI application
redline-gui

# Start web application
redline-web

# Use CLI
redline --help
```

### **Method 4: Standalone Executables**
```bash
# Download for your platform:
# Windows: redline-gui-windows-x64.exe
# macOS: redline-gui-macos-arm64
# Linux: redline-gui-linux-x64

# Run directly (no Python installation required)
./redline-gui-macos-arm64
```

### **Method 5: Universal Installer**
```bash
# Clone and run installer
git clone https://github.com/keepdevops/redline2.git
cd redline2
./install_options_redline.sh
```

### **Method 6: Source Installation**
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Install dependencies
pip install -r requirements.txt

# Start applications
python main.py      # GUI
python web_app.py   # Web interface
```

## 🎯 **Core Features**

### **📊 Data Management**
- **Multi-format Support**: CSV, JSON, Parquet, Feather, DuckDB, TXT
- **Pagination & Virtual Scrolling**: Handle 10M+ rows efficiently with pagination for multi-file views
- **Multi-File Data View**: View and manage multiple files simultaneously with pagination per file
- **Date Format Selection**: Choose from multiple date formats in single and multi-file views
- **Column Editing**: Rename columns directly in data view (single file and global editing)
- **Column Reordering**: Specify column order in converter (single and batch operations)
- **Flexible Column Detection**: Analysis works with any column name format (case-insensitive, pattern matching)
- **Empty Column/Row Filtering**: Automatically filter out empty columns and rows
- **Real-time Filtering**: Advanced filtering with SQL-like queries
- **Batch Processing**: Process multiple files simultaneously with column alignment

### **📥 Data Sources**
- **Yahoo Finance**: Free, reliable financial data
- **Stooq.com**: High-quality historical data
- **Massive.com**: Professional data with REST API and WebSocket support (15-min delayed and real-time feeds)
- **Alpha Vantage & Finnhub**: Additional data sources with API key support
- **Multi-source**: Fallback mechanisms for data availability
- **Custom APIs**: Extensible data source framework

### **📈 Analysis Tools**
- **Financial Analysis**: OHLCV analysis with flexible column detection (works with any column names)
- **Statistical Analysis**: Mean, median, std dev, min/max
- **Trend Analysis**: Price trends, volume analysis
- **Correlation Analysis**: Asset relationships
- **Quality Metrics**: Missing values, outliers detection
- **Smart Column Detection**: Automatically detects price, volume, ticker, and timestamp columns regardless of naming

### **🔄 Format Conversion**
- **Batch Conversion**: Convert multiple files at once with column alignment
- **Column Reordering**: Specify preferred column order for single and batch conversions
- **Data Cleaning**: Remove duplicates, fill missing values
- **Schema Validation**: Automatic data structure validation
- **Performance Optimization**: 10x smaller file sizes with Parquet

## 🖥️ **Interface Options**

### **Desktop GUI (Tkinter)**
- **Modern Interface**: Responsive design, dark/light themes
- **Tabbed Workflow**: Organized into logical sections
- **Performance Monitor**: Real-time memory and CPU usage
- **Keyboard Shortcuts**: Efficient navigation

### **Web Interface (Flask + Gunicorn)**
- **Production Server**: Gunicorn WSGI server for high performance
- **Modern Web UI**: Responsive design, mobile-friendly
- **Real-time Updates**: WebSocket-based live updates
- **Multi-user Support**: Concurrent user sessions (8x capacity)
- **REST API**: Programmatic access to functionality
- **Asset Optimization**: Minified CSS/JS for faster loading
- **Theme System**: Light, Dark, Auto, and Grayscale themes

### **Command Line Interface**
- **Batch Operations**: Script-friendly commands
- **Automation**: Integration with other tools
- **Headless Mode**: Server deployment without GUI

## 📦 **Distribution Formats**

| Format | Platform | Installation | Best For |
|--------|----------|--------------|----------|
| **PyPI Package** | All | `pip install redline-financial` | Developers, Python users |
| **Docker Image** | All | `docker run redline-financial` | Servers, cloud deployment |
| **Executables** | Platform-specific | Download & run | End users, no Python required |
| **Source Archives** | All | Extract & install | Customization, development |

## 🚀 **Performance Features & Optimizations**

### **⚡ Production-Ready Architecture**
- **Gunicorn Server**: Production WSGI server with 2 workers × 4 threads (8x capacity)
- **Multi-Stage Docker Build**: 50% smaller images (~200MB runtime)
- **Asset Minification**: 25-40% smaller CSS/JS files for faster loading
- **Pre-compiled Bytecode**: 20% faster Python startup
- **Non-root Security**: Runs as unprivileged user for enhanced security
- **Health Checks**: Built-in monitoring and auto-restart capabilities

### **⚡ High-Performance Data Processing**
- **Virtual Scrolling**: Handle 10M+ rows without memory issues
- **Lazy Loading**: Load data on demand
- **Memory Optimization**: 96% reduction in memory usage
- **Parallel Processing**: Multi-threaded operations
- **Intelligent Caching**: Frequently accessed data caching
- **BuildKit Optimization**: 75% faster Docker builds with layer caching

### **📊 Performance Benchmarks**
| Dataset Size | Memory Usage | Load Time | Recommended Format | Docker Build Time |
|--------------|--------------|-----------|-------------------|-------------------|
| 100K rows | ~50MB | 2-3 seconds | Any format | 2-3 minutes |
| 1M rows | ~200MB | 5-10 seconds | Parquet/DuckDB | 2-3 minutes |
| 10M rows | ~1GB | 30-60 seconds | Parquet/DuckDB | 2-3 minutes |

### **🐳 Docker Optimizations**
- **Multi-platform Support**: ARM64 (Apple Silicon) and AMD64 (Intel/Dell)
- **Layer Caching**: Intelligent dependency caching for faster rebuilds
- **Minimal Base Image**: Python 3.11-slim for smaller footprint
- **Security Hardening**: Non-root user, minimal attack surface
- **Production Server**: Gunicorn replaces Flask dev server

## 🔧 **System Requirements**

### **Minimum Requirements**
- **Python**: 3.11+ (for source/PyPI installation)
- **Memory**: 4GB+ RAM (8GB+ recommended for large datasets)
- **Storage**: 1GB+ free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### **Platform Support**
- ✅ **Windows** (x64, ARM64)
- ✅ **macOS** (Intel, Apple Silicon)
- ✅ **Linux** (Ubuntu, CentOS, RHEL, x64, ARM64)
- ✅ **Docker** (Multi-platform containers)

## 📋 **Installation Guide**

### **PyPI Installation (Recommended)**
```bash
# Install latest version
pip install redline-financial

# Install specific version
pip install redline-financial==2.1.0

# Upgrade to latest
pip install --upgrade redline-financial
```

### **Docker Installation**

#### **Option 1: Pre-built Optimized Images (Recommended)**
```bash
# For Intel/AMD64 machines (Dell, most servers)
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0-optimized/redline-webgui-amd64.tar
docker load -i redline-webgui-amd64.tar
docker tag redline-webgui:amd64 redline-webgui:latest

# For Apple Silicon (M1/M2/M3 Macs)
wget https://github.com/keepdevops/redline2/releases/download/v1.0.0-optimized/redline-webgui-arm64.tar
docker load -i redline-webgui-arm64.tar
docker tag redline-webgui:arm64 redline-webgui:latest

# Start optimized container with Gunicorn
docker run -d --name redline-webgui -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  redline-webgui:latest

# Verify container is running
docker ps | grep redline-webgui
curl http://localhost:8080/health
```

#### **Option 2: Build from Source**
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Build optimized image
docker build -f Dockerfile.webgui.simple -t redline-webgui:latest .

# Start container
docker run -d --name redline-webgui -p 8080:8080 redline-webgui:latest
```

#### **Features of Optimized Docker Images**
- ✅ **Production Server**: Gunicorn with 2 workers × 4 threads
- ✅ **Multi-platform**: Works on both ARM64 and AMD64 architectures
- ✅ **50% Smaller**: Multi-stage build reduces image size
- ✅ **Security**: Non-root user, minimal attack surface
- ✅ **Performance**: Pre-compiled bytecode, minified assets
- ✅ **Monitoring**: Health checks and auto-restart

### **Docker Compose Installation**
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Start with Docker Compose
docker-compose -f docker-compose-working.yml up -d

# Access web interface
open http://localhost:8080
```

### **Executable Installation**
```bash
# Download appropriate executable for your platform
# Windows: redline-gui-windows-x64.exe
# macOS Intel: redline-gui-macos-x64
# macOS Apple Silicon: redline-gui-macos-arm64
# Linux: redline-gui-linux-x64

# Make executable (Linux/macOS)
chmod +x redline-gui-*

# Run directly
./redline-gui-macos-arm64
```

## 🔄 **Auto-Update System**

### **Check for Updates**
```bash
# Check for updates
redline --check-updates

# Auto-update
redline --update
```

### **Update Methods**
- **PyPI**: `pip install --upgrade redline-financial`
- **Docker**: `docker pull redline-financial:latest`
- **Executables**: Download and replace executable
- **Source**: Pull latest changes and reinstall

## 🔒 **Commercial Licensing**

### **License Types**
- **Trial**: 30-day evaluation, basic features
- **Standard**: 1-year license, 3 installations
- **Professional**: 1-year license, 10 installations, API access
- **Enterprise**: Unlimited installations, custom integrations

### **License Management**
```bash
# Validate license
redline --validate-license <license-key>

# Check license status
redline --license-status

# Register installation
redline --register-install
```

## 📚 **Usage Examples**

### **Example 1: Download and Analyze Stock Data**
```bash
# Start REDLINE
redline-gui

# Or use web interface
redline-web
# Access: http://localhost:8080

# Download data
# - Go to Download tab
# - Enter ticker: AAPL
# - Select date range: 2Y
# - Click Download

# Load and analyze
# - Go to Data tab
# - Load the downloaded file
# - Apply filters if needed
# - Export to Parquet for faster loading
```

### **Example 2: Batch Data Conversion**
```bash
# Convert multiple files
# - Go to Converter tab
# - Select multiple CSV files
# - Choose output format: Parquet
# - Enable batch conversion
# - Monitor progress

# Benefits
# - 10x smaller file sizes
# - 5x faster loading times
# - Better compression
```

### **Example 3: CLI Usage**
```bash
# Download data
redline download AAPL --start 2023-01-01 --end 2024-01-01

# Convert format
redline convert data.csv --output data.parquet

# Analyze data
redline analyze data.parquet --stats
```

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

| Issue | Solution | Prevention |
|-------|----------|------------|
| **GUI won't start** | Check Python version (3.11+) | Use `redline --version` |
| **Memory errors** | Use Parquet/DuckDB formats | Monitor memory usage |
| **Download failures** | Check internet connection | Use Yahoo Finance first |
| **Format errors** | Verify file format support | Check format table above |
| **Docker issues** | Check Docker daemon | Use `docker --version` |

### **Performance Optimization**
- **Use Parquet/DuckDB** for large datasets
- **Enable virtual scrolling** for 10M+ rows
- **Close unused tabs** to free memory
- **Monitor memory usage** in status bar

### **Getting Help**
- **Check logs**: Application logs in console
- **Test installation**: `redline --test`
- **Verify formats**: Check format support table
- **Report issues**: GitHub Issues with logs

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/keepdevops/redline2.git
cd redline2

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
python -m pytest redline/tests/

# Run linting
black redline/
flake8 redline/
```

### **Build System**
```bash
# Build all distributions
bash build/scripts/build_all.sh

# Build specific components
bash build/scripts/build_executables.sh
bash build/scripts/create_release.sh

# Clean build
bash build/scripts/build_all.sh --clean
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Yahoo Finance** for providing free financial data
- **Stooq.com** for high-quality historical data
- **DuckDB** for fast analytical processing
- **Pandas** for data manipulation capabilities
- **Flask** for web interface framework
- **PyInstaller** for executable creation

---

<div align="center">

**Made with ❤️ for the financial data community**

[![GitHub stars](https://img.shields.io/github/stars/keepdevops/redline2?style=social)](https://github.com/keepdevops/redline2)
[![GitHub forks](https://img.shields.io/github/forks/keepdevops/redline2?style=social)](https://github.com/keepdevops/redline2)
[![GitHub issues](https://img.shields.io/github/issues/keepdevops/redline2)](https://github.com/keepdevops/redline2/issues)

</div>