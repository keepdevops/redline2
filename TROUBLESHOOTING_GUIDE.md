# REDLINE Troubleshooting Guide

<div align="center">

![Troubleshooting](https://img.shields.io/badge/Troubleshooting-Guide-orange?style=for-the-badge&logo=wrench)

**Solutions to common REDLINE issues**

[![Status](https://img.shields.io/badge/Status-Updated%20Regularly-green)](README.md)
[![Support](https://img.shields.io/badge/Support-GitHub%20Issues-lightgrey)](https://github.com/your-repo/redline/issues)

</div>

---

## 🚨 **Quick Fixes**

### **Most Common Issues**

| Issue | Quick Fix | Time |
|-------|-----------|------|
| **GUI won't start** | Run `./test_x11.bash` | 30 seconds |
| **Download fails** | Check internet, try Yahoo Finance | 1 minute |
| **Memory errors** | Use Parquet format, close apps | 2 minutes |
| **File not found** | Check file paths in settings | 1 minute |

---

## 🔧 **Detailed Solutions**

### **GUI and Display Issues**

#### **Problem: GUI won't start or appears blank**

**Symptoms:**
- Application starts but window is blank
- Error messages about X11 or display
- GUI opens but is unresponsive

**Solutions:**

**1. Test X11 Forwarding (Docker)**
```bash
# Test if X11 is working
./test_x11.bash

# If test fails, try socat method
brew install socat  # On macOS
./run_gui_socat.bash
```

**2. Check XQuartz (macOS)**
```bash
# Check if XQuartz is installed
ls /Applications/Utilities/XQuartz.app

# If not installed, download from:
# https://www.xquartz.org/
```

**3. Verify Docker Setup**
```bash
# Check if Docker is running
docker ps

# Restart Docker Desktop if needed
# Then try again:
./run_gui.bash
```

#### **Problem: GUI is slow or unresponsive**

**Symptoms:**
- Interface is sluggish
- Buttons don't respond quickly
- Memory usage is high

**Solutions:**

**1. Check Memory Usage**
- Look at the status bar for memory usage
- Close other applications
- Use Parquet format for large datasets

**2. Enable Virtual Scrolling**
- Go to Settings tab
- Enable "Virtual Scrolling" for large datasets
- This reduces memory usage by 96%

**3. Optimize Data Formats**
```bash
# Convert large CSV files to Parquet
# Go to Converter tab
# Select CSV files → Convert to Parquet
# Parquet files are 10x smaller and 5x faster
```

---

### **Data Download Issues**

#### **Problem: Download fails or times out**

**Symptoms:**
- Download progress stops
- Error messages about network
- No data is downloaded

**Solutions:**

**1. Check Internet Connection**
```bash
# Test internet connectivity
ping google.com
ping yahoo.com
```

**2. Try Different Data Sources**
- **Yahoo Finance**: Most reliable, free
- **Stooq**: High quality, requires manual setup
- **Multi-Source**: Fallback system

**3. Adjust Download Settings**
- Reduce date range (try 1Y instead of Max)
- Download one ticker at a time
- Check if ticker symbol is valid

**4. Common Ticker Symbols**
```
AAPL - Apple Inc.
MSFT - Microsoft Corporation
GOOGL - Alphabet Inc.
TSLA - Tesla Inc.
AMZN - Amazon.com Inc.
```

#### **Problem: Downloaded data is corrupted or incomplete**

**Symptoms:**
- Data loads but shows errors
- Missing columns or rows
- File appears empty

**Solutions:**

**1. Verify File Format**
- Check if file is in correct format
- Ensure file is not corrupted
- Try downloading again

**2. Check Data Validation**
- Go to Analysis tab
- Look for data quality metrics
- Check for missing values

**3. Re-download Data**
- Delete the corrupted file
- Try downloading again
- Use different date range

---

### **File Format Issues**

#### **Problem: "Unsupported format" error**

**Symptoms:**
- Error message when loading files
- Format not recognized
- Conversion fails

**Solutions:**

**1. Check Supported Formats**
| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| CSV | .csv | ✅ | ✅ |
| JSON | .json | ✅ | ✅ |
| DuckDB | .duckdb | ✅ | ✅ |
| Parquet | .parquet | ✅ | ✅ |
| Feather | .feather | ✅ | ✅ |
| TXT | .txt | ✅ | ❌ |

**2. Convert to Supported Format**
- Use Converter tab to convert files
- CSV is most compatible
- Parquet is best for large datasets

**3. Check File Structure**
- Ensure file has proper headers
- Check for required columns (Date, Open, High, Low, Close, Volume)
- Verify data types

#### **Problem: File conversion fails**

**Symptoms:**
- Conversion process stops
- Error messages during conversion
- Output file is corrupted

**Solutions:**

**1. Check Input File**
- Verify input file is not corrupted
- Check file permissions
- Ensure file is not locked by another application

**2. Check Output Directory**
- Verify output directory exists
- Check write permissions
- Ensure sufficient disk space

**3. Try Different Formats**
- Convert to CSV first (most compatible)
- Then convert to desired format
- Use Parquet for large datasets

---

### **Performance Issues**

#### **Problem: Application is slow with large datasets**

**Symptoms:**
- Loading takes a long time
- Interface becomes unresponsive
- High memory usage

**Solutions:**

**1. Use Efficient Formats**
- **Parquet**: Best for large datasets (10x smaller)
- **DuckDB**: Best for analysis and queries
- **Feather**: Best for speed

**2. Enable Virtual Scrolling**
- Go to Settings tab
- Enable "Virtual Scrolling"
- This loads data on demand

**3. Optimize Memory Usage**
- Close unused tabs
- Clear data when not needed
- Monitor memory usage in status bar

**4. Performance Benchmarks**
| Dataset Size | Memory Usage | Load Time | Recommended Format |
|--------------|--------------|-----------|-------------------|
| 100K rows | ~50MB | 2-3 seconds | Any format |
| 1M rows | ~200MB | 5-10 seconds | Parquet/DuckDB |
| 10M rows | ~1GB | 30-60 seconds | Parquet/DuckDB |

---

### **Docker-Specific Issues**

#### **Problem: Docker container won't start**

**Symptoms:**
- Docker command fails
- Container exits immediately
- Permission errors

**Solutions:**

**1. Check Docker Status**
```bash
# Check if Docker is running
docker ps

# Check Docker version
docker --version

# Restart Docker Desktop if needed
```

**2. Check Port Availability**
```bash
# Check if ports are available
netstat -an | grep 6000
netstat -an | grep 6001

# Kill processes using these ports if needed
```

**3. Check File Permissions**
```bash
# Ensure scripts are executable
chmod +x run_gui.bash
chmod +x test_x11.bash

# Check file ownership
ls -la *.bash
```

#### **Problem: X11 forwarding issues in Docker**

**Symptoms:**
- GUI won't display
- X11 connection errors
- Permission denied errors

**Solutions:**

**1. Test X11 Setup**
```bash
# Test X11 forwarding
./test_x11.bash

# If test fails, try socat method
brew install socat  # On macOS
./run_gui_socat.bash
```

**2. Check XQuartz (macOS)**
```bash
# Check XQuartz installation
ls /Applications/Utilities/XQuartz.app

# Start XQuartz
open -a XQuartz

# Allow connections from network clients
# In XQuartz preferences → Security → Allow connections
```

**3. Alternative: Use Local Installation**
```bash
# If Docker continues to fail, use local installation
pip install pandas yfinance duckdb pyarrow polars tkinter
python main.py
```

---

## 📊 **Diagnostic Commands**

### **System Information**
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(pandas|yfinance|duckdb|pyarrow|polars|tkinter)"

# Check system resources
top -l 1 | head -10  # macOS
htop  # Linux
```

### **REDLINE-Specific Diagnostics**
```bash
# Check Docker logs
docker logs redline_gui --tail 100

# Test X11 forwarding
./test_x11.bash

# Check file permissions
ls -la *.bash
ls -la data/
```

### **Network Diagnostics**
```bash
# Test internet connectivity
ping google.com
ping yahoo.com

# Test DNS resolution
nslookup yahoo.com
nslookup google.com
```

---

## 🆘 **Getting Help**

### **Before Asking for Help**

1. **Check this guide** for your specific issue
2. **Run diagnostic commands** to gather information
3. **Check logs** for error messages
4. **Try the quick fixes** first

### **When Reporting Issues**

Include the following information:

```bash
# System information
python --version
pip list | grep -E "(pandas|yfinance|duckdb|pyarrow|polars|tkinter)"

# Docker information (if using Docker)
docker --version
docker logs redline_gui --tail 100

# Error messages
# Copy the exact error message
# Include steps to reproduce
```

### **Support Channels**

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/your-repo/redline/issues)
- **Documentation**: [Complete User Guide](REDLINE_USER_GUIDE.md)
- **Quick Start**: [5-minute setup guide](QUICK_START_GUIDE.md)

---

## 🎯 **Prevention Tips**

### **Best Practices**

1. **Use Docker** for consistent environment
2. **Use Parquet format** for large datasets
3. **Enable virtual scrolling** for 10M+ rows
4. **Monitor memory usage** regularly
5. **Keep Docker Desktop updated**
6. **Use stable internet connection** for downloads

### **Regular Maintenance**

- **Clear old data** files periodically
- **Update Docker images** regularly
- **Check disk space** before large downloads
- **Monitor system resources** during heavy usage

---

<div align="center">

**Still need help? Check out our [Complete User Guide](REDLINE_USER_GUIDE.md)**

[![User Guide](https://img.shields.io/badge/User%20Guide-Complete%20Guide-blue?style=for-the-badge&logo=book)](REDLINE_USER_GUIDE.md)

</div>
