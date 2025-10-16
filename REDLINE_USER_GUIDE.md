# REDLINE Financial Data Analyzer - User Guide

## 🚀 **Overview**

REDLINE is a comprehensive financial data analysis application that allows you to download, view, analyze, and manage financial market data from multiple sources. The application features a modern GUI with modular architecture for reliable performance.

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

### **Starting REDLINE**
```bash
# Navigate to the REDLINE directory
cd /path/to/redline

# Run the application
python main.py
```

### **System Requirements**
- Python 3.11+ (recommended)
- Required packages: pandas, tkinter, yfinance, duckdb (optional)
- macOS, Windows, or Linux

### **First Launch**
1. REDLINE will start with the **Data** tab active
2. The application uses fallback mechanisms for missing dependencies
3. All core functionality works without external database requirements

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
- **CSV** - Comma-separated values
- **Parquet** - Columnar storage format
- **JSON** - JavaScript Object Notation
- **Feather** - Fast columnar format

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

## 🔧 **Troubleshooting**

### **Common Issues**

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
