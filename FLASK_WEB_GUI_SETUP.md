# REDLINE Flask Web GUI Setup Guide

<div align="center">

![Flask Web GUI](https://img.shields.io/badge/Flask%20Web%20GUI-Modern%20Interface-blue?style=for-the-badge&logo=flask)

**Complete guide for setting up and using the REDLINE Flask web interface**

[![Flask](https://img.shields.io/badge/Flask-2.3+-green?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)

</div>

---

## 🚀 **Quick Start (2 Minutes)**

### **Step 1: Install Flask Dependencies**
```bash
# Install Flask and related packages
pip install flask flask-socketio gunicorn

# Or install all requirements
pip install -r requirements.txt
```

### **Step 2: Start the Web Interface**
```bash
# Start the Flask web server
python web_app.py

# The web interface will be available at:
# http://localhost:8080
```

### **Step 3: Access the Web Interface**
1. **Open your browser** and go to `http://localhost:8080`
2. **Explore the interface** - all features are identical to the desktop GUI
3. **Download data** using the Download tab
4. **View and filter data** using the Data tab

---

## 🌟 **Flask Web GUI Features**

### **✅ Complete Feature Parity**
| Feature | Desktop GUI | Flask Web GUI | Status |
|---------|-------------|---------------|--------|
| **Data Tab** | ✅ | ✅ | **Identical** |
| **Download Tab** | ✅ | ✅ | **Identical** |
| **Analysis Tab** | ✅ | ✅ | **Identical** |
| **Converter Tab** | ✅ | ✅ | **Identical** |
| **Settings Tab** | ✅ | ✅ | **Identical** |
| **Theme System** | ✅ | ✅ | **Enhanced** |

### **🎨 Modern Web Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Color-blind Friendly**: Multiple accessible color themes
- **Real-time Updates**: Live data loading and filtering
- **Modern UI**: Bootstrap 5 with custom styling
- **Theme Switching**: 7 different color schemes

### **⚡ Performance Features**
- **Virtual Scrolling**: Handle 10M+ rows efficiently
- **Chunked Loading**: Large file support with memory optimization
- **Real-time Filtering**: Instant filter results
- **Export Functionality**: Download filtered data in multiple formats

---

## 🔧 **Installation Methods**

### **Method 1: Direct Installation**
```bash
# Install Flask dependencies
pip install flask flask-socketio gunicorn

# Start web interface
python web_app.py
```

### **Method 2: Using Requirements**
```bash
# Install all dependencies including Flask
pip install -r requirements.txt

# Start web interface
python web_app.py
```

### **Method 3: Docker (Recommended)**
```bash
# Build and run with Docker
docker build -f Dockerfile.web -t redline-web:latest .
docker run -p 8080:8080 -v "$PWD/data:/app/data" redline-web:latest

# Or use Docker Compose
docker-compose --profile web up
```

### **Method 4: Conda Environment**
```bash
# Create conda environment
conda create -n redline-web python=3.11

# Activate environment
conda activate redline-web

# Install dependencies
pip install flask flask-socketio gunicorn pandas numpy pyarrow polars duckdb yfinance

# Start web interface
python web_app.py
```

---

## 🌐 **Web Interface Overview**

### **Main Dashboard**
- **Welcome Screen**: Overview of all available features
- **Quick Access**: Direct links to all tabs
- **Status Indicators**: Real-time system status
- **Theme Switcher**: Change color schemes instantly

### **Data Tab**
- **File Browser**: Browse and select data files
- **Data Preview**: View data before loading
- **Advanced Filtering**: Filter by date, price, volume, etc.
- **Export Options**: Save filtered data in multiple formats
- **Large File Support**: Handle files with millions of rows

### **Download Tab**
- **Yahoo Finance**: Free stock data downloads
- **Stooq Integration**: High-quality historical data
- **Batch Downloads**: Download multiple tickers at once
- **Date Range Selection**: 1Y, 2Y, 5Y, or custom ranges
- **Progress Tracking**: Real-time download progress

### **Analysis Tab**
- **Statistical Analysis**: Mean, median, standard deviation
- **Trend Analysis**: Price trends and volume analysis
- **Correlation Analysis**: Asset relationships
- **Data Quality**: Missing values and outlier detection

### **Converter Tab**
- **Format Conversion**: CSV, JSON, Parquet, Feather, DuckDB
- **Batch Processing**: Convert multiple files at once
- **Data Cleaning**: Remove duplicates and fill missing values
- **Progress Tracking**: Real-time conversion progress

### **Settings Tab**
- **Theme Management**: Switch between color schemes
- **Configuration**: Data paths and performance settings
- **System Status**: Memory usage and performance metrics

---

## 🎨 **Theme System**

### **Available Themes**
| Theme | Description | Best For |
|-------|-------------|----------|
| **Default** | Color-blind friendly blue theme | General use |
| **High Contrast** | Black and white with high contrast | Accessibility |
| **Ocean** | Blue ocean-inspired theme | Professional |
| **Forest** | Green nature-inspired theme | Easy on eyes |
| **Sunset** | Warm orange and yellow theme | Creative work |
| **Monochrome** | Black and white theme | Minimalist |
| **Dark** | Dark mode theme | Low light |

### **Theme Switching**
1. **Click the Theme button** in the top navigation
2. **Select your preferred theme** from the dropdown
3. **Theme is applied instantly** and saved for future sessions
4. **Theme preference is stored** in browser localStorage

---

## 🐳 **Docker Deployment**

### **Quick Docker Setup**
```bash
# Build the web-optimized Docker image
docker build -f Dockerfile.web -t redline-web:latest .

# Run the container
docker run -d --name redline-web -p 8080:8080 \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  redline-web:latest
```

### **Docker Compose**
```bash
# Start web service
docker-compose --profile web up -d

# Check logs
docker-compose logs redline-web

# Stop service
docker-compose --profile web down
```

### **Production Deployment**
```bash
# Use gunicorn for production
docker run -d --name redline-web-prod -p 8080:8080 \
  -e FLASK_ENV=production \
  -v "$PWD/data:/app/data" \
  redline-web:latest \
  gunicorn --bind 0.0.0.0:8080 web_app:app
```

---

## 🔧 **Configuration**

### **Environment Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_PORT` | `8080` | Port for web interface |
| `FLASK_ENV` | `development` | Flask environment |
| `HOST` | `0.0.0.0` | Host to bind to |

### **Custom Configuration**
```bash
# Set custom port
export WEB_PORT=8081
python web_app.py

# Set Flask environment
export FLASK_ENV=production
python web_app.py
```

---

## 🚀 **Performance Optimization**

### **Large File Handling**
- **Chunked Loading**: Files are loaded in chunks to prevent memory issues
- **Virtual Scrolling**: Only visible rows are rendered
- **Memory Monitoring**: Real-time memory usage display
- **Optimized Formats**: Use Parquet or DuckDB for large datasets

### **Recommended Settings**
```python
# For large datasets (10M+ rows)
# Use Parquet format for storage
# Enable virtual scrolling
# Monitor memory usage
# Close unused tabs
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8080

# Use a different port
export WEB_PORT=8081
python web_app.py
```

#### **Flask Not Found**
```bash
# Install Flask
pip install flask flask-socketio gunicorn

# Verify installation
python -c "import flask; print('Flask installed successfully')"
```

#### **Data Files Not Found**
```bash
# Check data directory
ls -la data/

# Ensure data directory exists
mkdir -p data
```

#### **Memory Issues**
```bash
# Use smaller chunk sizes
# Enable virtual scrolling
# Use Parquet format for large files
# Monitor memory usage in browser
```

---

## 📊 **API Endpoints**

### **Data Operations**
- `POST /data/load` - Load data from file
- `POST /data/filter` - Apply filters to data
- `GET /data/columns/<filename>` - Get column information
- `POST /data/export` - Export filtered data

### **System Operations**
- `GET /api/files` - List available files
- `GET /status` - System status
- `GET /health` - Health check

### **Theme Operations**
- `GET /api/themes` - Get available themes
- `POST /api/theme` - Set theme preference
- `GET /api/theme` - Get current theme

---

## 🎯 **Best Practices**

### **Development**
1. **Use virtual environments** for dependency isolation
2. **Test with different browsers** for compatibility
3. **Monitor memory usage** with large datasets
4. **Use Docker** for consistent deployment

### **Production**
1. **Use gunicorn** for production WSGI server
2. **Set up reverse proxy** (nginx) for better performance
3. **Enable HTTPS** for secure connections
4. **Monitor logs** for errors and performance

### **Data Management**
1. **Use Parquet format** for large datasets
2. **Enable virtual scrolling** for 10M+ rows
3. **Monitor memory usage** in real-time
4. **Backup data** regularly

---

## 🆘 **Getting Help**

### **Support Resources**
- **Documentation**: [README.md](README.md)
- **User Guide**: [REDLINE_USER_GUIDE.md](REDLINE_USER_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)
- **GitHub Issues**: Report bugs and feature requests

### **Common Commands**
```bash
# Check if Flask is running
curl http://localhost:8080/health

# View logs
docker logs redline-web

# Restart service
docker restart redline-web

# Check port usage
netstat -tlnp | grep :8080
```

---

<div align="center">

**Your REDLINE Flask Web GUI is now ready! 🎉**

[![Next Step](https://img.shields.io/badge/Next%20Step-User%20Guide-blue?style=for-the-badge&logo=book)](REDLINE_USER_GUIDE.md)

</div>
