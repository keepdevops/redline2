# REDLINE Financial Data Analyzer - User Guide

<div align="center">

![REDLINE User Guide](https://img.shields.io/badge/REDLINE-User%20Guide-blue?style=for-the-badge&logo=book)

**Complete guide to using REDLINE for financial data analysis**

[![Version](https://img.shields.io/badge/Version-2.0-green)](README.md)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](README.md)
[![Support](https://img.shields.io/badge/Support-GitHub%20Issues-lightgrey)](https://github.com/your-repo/redline/issues)

</div>

---

## 🆕 **What's New in Version 2.0**

### **✨ Data Viewing Improvements**
- **Automatic Column Header Cleaning**: Fixed "undefined" and "Unnamed: 0" issues across all data views
- **Universal Format Support**: Works with Bloomberg, Alpha Vantage, Finnhub, and custom CSV formats
- **Multi-File View**: View multiple data files simultaneously with clean headers
- **Analysis Display Fix**: Proper display of column names with angle brackets in correlation analysis
- **Cross-Platform Compatibility**: ARM64 (Apple Silicon) + AMD64 support

### **📊 Enhanced Features**
- **Smart Data Loading**: Automatically detects and fixes malformed CSV headers
- **HTML-Escaped Columns**: Proper rendering of column names in analysis results
- **Uncompiled Docker Mode**: Development-friendly container for easier debugging
- **Production Ready**: Comprehensive testing across all financial data formats

---

## 🌟 **Welcome to REDLINE**

REDLINE is a comprehensive financial data analysis application that allows you to download, view, analyze, and manage financial market data from multiple sources. The application features a modern GUI with modular architecture for reliable performance.

**What you'll learn in this guide:**
- 🚀 How to get started quickly
- 📊 How to load and analyze data
- 📥 How to download financial data
- 🔄 How to convert between formats
- ⚙️ How to configure settings
- 🔧 How to troubleshoot issues

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Data Tab](#data-tab)
4. [Download Tab](#download-tab)
5. [Analysis Tab](#analysis-tab)
6. [Settings Tab](#settings-tab)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Data Sources](#data-sources)
9. [File Formats](#file-formats)
10. [Troubleshooting](#troubleshooting)

## 🎯 **Getting Started**

### **Quick Start (5 Minutes)**

#### **Step 1: Choose Your Installation Method**
| Method | Best For | Time Required | Access |
|--------|----------|---------------|---------|
| **Web-based GUI** | Modern interface, cross-platform | 2 minutes | http://localhost:8080 |
| **Tkinter GUI** | Desktop users, X11 support | 3 minutes | Desktop application |
| **Hybrid GUI** | Both web and desktop options | 4 minutes | Both interfaces |
| **Docker Compose** | Containerized deployment | 5 minutes | http://localhost:8080 |
| **Native Python** | Developers, customization | 5 minutes | http://localhost:8080 |

#### **Step 2: Start REDLINE**

**Option A: Universal Installer (Recommended)**
```bash
# Clone and run
git clone https://github.com/your-repo/redline.git
cd redline
./install_options_redline.sh
```

**Option B: Manual Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Start web application
python3 web_app.py
# Access: http://localhost:8080

# Or start GUI application
python3 main.py
```

**Option C: Test Installation**
```bash
# Test if everything works
./install_options_redline.sh
# Choose option 6 (Dependency Check)
```

#### **Step 3: First Data Download**
1. **Go to Download tab**
2. **Enter a ticker**: Try `AAPL` (Apple)
3. **Select date range**: Choose `2Y` (2 years)
4. **Click Download**
5. **Wait for completion**

#### **Step 4: Load and View Data**
1. **Go to Data tab**
2. **Click "Load Data"**
3. **Select your downloaded file**
4. **Explore the data**

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.11+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 1GB | 5GB+ |
| **OS** | Windows 10, macOS 10.14, Ubuntu 18.04 | Latest versions |

### **Required Packages**
```bash
# Core packages (automatically installed with Docker)
pandas yfinance duckdb pyarrow polars tkinter

# Optional packages for enhanced features
tensorflow scikit-learn matplotlib
```

### **First Launch Checklist**
- [ ] **Application starts** without errors
- [ ] **All tabs are visible** (Data, Download, Analysis, Settings)
- [ ] **Status bar shows** "Ready" message
- [ ] **Memory usage** is displayed in status bar
- [ ] **No error messages** in the console

## 🖥️ **Main Interface**

### **Tab Navigation**
- **Data** - Load, view, and manage financial data files
- **Download** - Download data from various financial sources
- **Analysis** - Perform statistical and trend analysis
- **Settings** - Configure application preferences

### **Window Layout**
- **Top Menu Bar** - File operations and navigation
- **Tab Interface** - Switch between different functionality areas
- **Status Bar** - Shows current operation status and progress
- **Main Content Area** - Context-sensitive based on active tab

## 📊 **Data Tab**

### **Loading Data**
1. Click **"Open File"** button or press `Ctrl+O`
2. Navigate to your data file (CSV, Parquet, JSON, etc.)
3. Select the file and click **"Open"**
4. Data will load automatically in the virtual scrolling table

### **Supported File Formats**
- **CSV** - Comma-separated values (recommended for compatibility)
- **Parquet** - Columnar storage format (recommended for large datasets)
- **JSON** - JavaScript Object Notation
- **Feather** - Fast columnar format
- **DuckDB** - Embedded analytical database (recommended for analysis)
- **TXT** - Stooq format files (read-only)

### **Format Limitations**
- **TXT Format**: Read-only support for Stooq format files
- **Keras/TensorFlow**: Not currently supported (will be added in future releases)
- **Recommended**: Use CSV for compatibility, Parquet for large datasets, DuckDB for analysis

### **Data Display**
- **Virtual Scrolling** - Efficiently handles large datasets
- **Column Headers** - Click to sort data
- **Row Selection** - Click rows to select data
- **Search Function** - Press `Ctrl+F` to search data

### **Data Operations**
- **Save Data** - Export current data to file
- **Filter Data** - Apply date range or other filters
- **Refresh Data** - Reload data from source file
- **Clear Data** - Remove current data from display

### **Supported Data Formats**
- **Stooq Format** - `<TICKER>`, `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>`, `<VOL>`
- **Standard Format** - Standard financial data columns
- **Yahoo Finance** - Direct Yahoo Finance data format

## 📥 **Download Tab**

### **Data Sources**

#### **Yahoo Finance (Recommended)**
- ✅ **Free** - No API key required
- ✅ **Reliable** - High uptime and data quality
- ✅ **Fast** - Quick download speeds
- ✅ **Comprehensive** - Stocks, ETFs, indices, crypto

#### **Stooq.com**
- ⚠️ **Manual Authentication** - Requires 2FA login
- ✅ **High Quality** - Professional-grade data
- ✅ **Global Coverage** - International markets
- 🔧 **Manual Process** - Website-based download

#### **Multi-Source**
- 🔄 **Fallback System** - Tries multiple sources
- ✅ **Reliability** - Ensures data availability
- 📊 **Format Conversion** - Automatic Stooq format output

### **Download Process**

#### **Step 1: Select Data Source**
- Choose from Yahoo Finance, Stooq, or Multi-Source
- Yahoo Finance is recommended for most users

#### **Step 2: Enter Ticker Symbols**
- **Manual Entry**: Type ticker symbols (comma-separated)
- **Quick Select**: Click buttons for popular stocks (AAPL, MSFT, GOOGL, etc.)
- **Examples**: `AAPL`, `AAPL,MSFT,GOOGL`, `TSLA,NVDA`

#### **Step 3: Set Date Range**
- **Custom Dates**: Enter start and end dates (YYYY-MM-DD)
- **Quick Presets**: 
  - **1Y** - Last 1 year
  - **2Y** - Last 2 years  
  - **5Y** - Last 5 years
  - **Max** - Maximum available data

#### **Step 4: Configure Output**
- **Output Directory**: Choose where to save files
- **Output Format**: 
  - **Stooq** - REDLINE-compatible format (recommended)
  - **Standard** - Original source format

#### **Step 5: Start Download**
- Click **"Start Download"** button
- Monitor progress in the progress bar
- View results in the results table
- Use **"Stop"** button to cancel if needed

### **Download Results**
- **Results Table** - Shows all download attempts
- **Columns**: Ticker, Rows, Date Range, Source, Status, File
- **Context Menu** - Right-click for options:
  - **Open File** - View downloaded file
  - **Load in REDLINE** - Import data directly
  - **Delete File** - Remove downloaded file

### **Manual Stooq Download**
1. Select **"Stooq.com"** as data source
2. Click **"Open Stooq Website"** button
3. Complete manual authentication and 2FA
4. Navigate to historical data section
5. Download CSV files manually
6. Use **"Open File"** in Data tab to load them

## 📈 **Analysis Tab**

### **Available Analysis Types**

#### **Statistical Analysis**
- **Basic Statistics** - Mean, median, standard deviation, min/max
- **Close Price Statistics** - Detailed price analysis
- **Data Quality** - Missing values, outliers detection

#### **Price Trend Analysis**
- **Price Movement** - Historical price trends
- **Date Range Analysis** - Performance over time periods
- **Volatility Metrics** - Price volatility calculations

#### **Correlation Analysis**
- **Inter-Asset Correlation** - Relationships between different assets
- **Market Correlation** - Correlation with market indices
- **Time-Series Correlation** - Correlation over time

#### **Volume Analysis**
- **Volume Statistics** - Average, median, max/min volume
- **High Volume Days** - Days with unusual volume activity
- **Volume Trends** - Volume patterns over time

### **Running Analysis**
1. Ensure data is loaded in the **Data** tab
2. Switch to the **Analysis** tab
3. Click the desired analysis button
4. View results in the analysis results area
5. Results are automatically formatted and displayed

### **Supported Data Formats**
- **Stooq Format** - `<CLOSE>`, `<DATE>`, `<VOL>` columns
- **Standard Format** - `close`, `timestamp`, `vol` columns
- **Automatic Detection** - REDLINE detects format automatically

## ⚙️ **Settings Tab**

### **Data Settings**
- **Database Path** - Location of local database files
- **CSV Directory** - Default directory for CSV files
- **JSON Directory** - Default directory for JSON files
- **Parquet Directory** - Default directory for Parquet files

### **Display Settings**
- **Theme** - Application appearance
- **Font Size** - Text size in interface
- **Grid Lines** - Show/hide table grid lines
- **Row Height** - Height of table rows

### **Advanced Settings**
- **Logging Level** - Debug, Info, Warning, Error
- **Cache Size** - Memory usage for data caching
- **Thread Pool Size** - Number of concurrent operations
- **Auto-Save** - Automatic saving of data changes

### **Applying Settings**
1. Modify settings in the appropriate section
2. Click **"Apply"** button to save changes
3. Some changes may require application restart

## ⌨️ **Keyboard Shortcuts**

### **File Operations**
- `Ctrl+O` - Open file
- `Ctrl+S` - Save current data
- `Ctrl+N` - New data session

### **Navigation**
- `F2` - Next tab
- `F3` - Previous tab
- `Tab` - Cycle through interface elements

### **Data Operations**
- `Ctrl+R` - Refresh data
- `Ctrl+F` - Search data
- `Ctrl+A` - Select all data
- `Ctrl+C` - Copy selected data

### **Analysis**
- `F5` - Run statistical analysis
- `F6` - Run correlation analysis
- `F7` - Run volume analysis
- `F8` - Run price trend analysis

### **Help**
- `F1` - Show help dialog
- `Ctrl+H` - Show keyboard shortcuts

## 📊 **Data Sources**

### **Yahoo Finance**
- **URL**: finance.yahoo.com
- **Coverage**: Global stocks, ETFs, indices, crypto, forex
- **Update Frequency**: Real-time during market hours
- **Historical Data**: Up to 40+ years for some assets
- **Limitations**: Rate limiting (delays between requests)

### **Stooq.com**
- **URL**: stooq.com
- **Coverage**: Global markets with high-quality data
- **Authentication**: Manual login required (2FA)
- **Update Frequency**: Daily updates
- **Historical Data**: Extensive historical coverage
- **Limitations**: Manual download process

### **Multi-Source**
- **Fallback Strategy**: Yahoo → Alpha Vantage → IEX Cloud → Finnhub
- **Reliability**: High (multiple backup sources)
- **Coverage**: Comprehensive global coverage
- **Format**: Automatic conversion to Stooq format

## 📁 **File Formats**

### **Stooq Format (Recommended)**
```csv
<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
AAPL,20241016,000000,230.53,231.04,228.78,230.71,34082200
```
**Note:** REDLINE automatically handles malformed headers with leading commas.

### **Standard Format**
```csv
Date,Open,High,Low,Close,Volume
2024-10-16,230.53,231.04,228.78,230.71,34082200
```

### **Yahoo Finance Format**
```csv
Date,Open,High,Low,Close,Adj Close,Volume
2024-10-16,230.53,231.04,228.78,230.71,230.71,34082200
```

### **Supported Formats**
REDLINE supports multiple financial data formats with automatic column cleaning:
- **Bloomberg**: `security, date, time, px_open, px_high, px_low, px_last, px_volume`
- **Alpha Vantage**: `symbol, timestamp, open, high, low, close, volume`
- **Finnhub**: Compact single-letter format (`c, h, l, o, t, v`)
- **Custom formats**: Automatic detection and cleaning of malformed headers

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"Undefined" or "Unnamed: 0" in Column Headers**
- **Cause**: Malformed CSV files with extra commas or index columns
- **Solution**: REDLINE automatically cleans column headers (fixed in v2.0)
- **Details**: The application removes unnamed index columns and fixes malformed headers
- **No Action Required**: This is handled automatically by the data loading system

#### **"DuckDB not available" Error**
- **Cause**: Optional database dependency not installed
- **Solution**: Application automatically falls back to pandas-only mode
- **Impact**: No impact on core functionality

#### **"Required columns not found" Error**
- **Cause**: Data file doesn't have expected column names
- **Solution**: REDLINE supports both Stooq and standard formats automatically
- **Check**: Ensure file has price and date columns

#### **GUI Hanging or Freezing**
- **Cause**: Large dataset or blocking operation
- **Solution**: Use virtual scrolling for large files
- **Prevention**: Process data in smaller chunks

#### **Download Failures**
- **Yahoo Finance**: Check internet connection and ticker validity
- **Stooq**: Complete manual authentication process
- **Rate Limiting**: Add delays between requests

### **Performance Optimization**

#### **Large Datasets**
- Use virtual scrolling (automatic)
- Process data in chunks
- Consider using Parquet format for storage
- Close unused applications

#### **Memory Usage**
- Adjust cache size in Settings
- Use data filtering to reduce dataset size
- Restart application periodically for large sessions

#### **Download Speed**
- Use Yahoo Finance for fastest downloads
- Download multiple tickers in batches
- Avoid peak market hours for better performance

### **Getting Help**

#### **Log Files**
- Check `redline.log` for detailed error information
- Enable debug logging in Settings for more details
- Log files are created in the application directory

#### **Data Validation**
- Verify ticker symbols are correct
- Check date ranges are valid
- Ensure output directory has write permissions

#### **Format Issues**
- REDLINE automatically detects most formats
- Use Stooq format for best compatibility
- Convert files using the built-in format converter

## 🎉 **Tips and Best Practices**

### **Data Management**
1. **Use Stooq Format** - Best compatibility with REDLINE
2. **Organize Files** - Create separate directories for different data types
3. **Backup Data** - Keep copies of important datasets
4. **Validate Data** - Check for missing values and outliers

### **Analysis Workflow**
1. **Load Data** - Import your financial data
2. **Explore Data** - Use basic statistics to understand the dataset
3. **Run Analysis** - Perform trend and correlation analysis
4. **Export Results** - Save analysis results for reporting

### **Download Strategy**
1. **Start with Yahoo** - Use Yahoo Finance for initial data acquisition
2. **Use Manual Stooq** - For high-quality data requiring manual verification
3. **Batch Downloads** - Download multiple tickers together for efficiency
4. **Date Ranges** - Use appropriate date ranges for your analysis needs

### **Performance Tips**
1. **Close Unused Tabs** - Free up memory by closing unnecessary tabs
2. **Use Filters** - Reduce dataset size with date or other filters
3. **Regular Restarts** - Restart application for long analysis sessions
4. **Monitor Resources** - Watch system memory and CPU usage

---

## 📞 **Support**

For additional help or to report issues:
1. Check the troubleshooting section above
2. Review log files for error details
3. Ensure you're using the latest version
4. Verify system requirements are met

**REDLINE Financial Data Analyzer** - Professional-grade financial data analysis made accessible.
