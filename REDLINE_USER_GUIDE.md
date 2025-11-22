# REDLINE Financial Data Analyzer - User Guide

<div align="center">

![REDLINE User Guide](https://img.shields.io/badge/REDLINE-User%20Guide-blue?style=for-the-badge&logo=book)

**Complete guide to using REDLINE for financial data analysis**

[![Version](https://img.shields.io/badge/Version-2.0-green)](README.md)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](README.md)
[![Support](https://img.shields.io/badge/Support-Subscription%20Service-blue)](https://redfindat.com)

</div>

---

## 🆕 **What's New in Version 2.1.0**

### **✨ Data Management Enhancements**
- **Massive.com Integration**: Download data from Massive.com via REST API and WebSocket (15-min delayed and real-time feeds)
- **Multi-File Data View**: View multiple files simultaneously with pagination per file
- **Date Format Selection**: Choose from multiple date formats (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, etc.) in single and multi-file views
- **Column Editing**: Rename columns directly in data view (single file and global editing for multi-file)
- **Column Reordering**: Specify column order in converter (single conversion and batch merge)
- **Flexible Column Detection**: Analysis works with any column name format (case-insensitive, pattern matching)
- **Empty Column/Row Filtering**: Automatically filter out empty columns and rows in multi-file view
- **API Key Management**: Configure API keys for external data sources (Yahoo, Stooq, Alpha Vantage, Finnhub, Massive.com)

### **📊 Enhanced Features**
- **Smart Data Loading**: Automatically detects and fixes malformed CSV headers
- **Pagination**: Efficient pagination for large datasets and multi-file views
- **Virtual Scrolling**: Still available for single-file views
- **Batch Operations**: Process multiple files simultaneously with column alignment
- **Theme Customization**: 8 themes with live color customization
- **Balance Tracking**: Real-time balance display with usage tracking
- **Subscription Service**: Cloud-based access with license key management

---

## 🌟 **Welcome to REDLINE**

REDLINE is a comprehensive cloud-based financial data analysis platform that allows you to download, view, analyze, and manage financial market data from multiple sources. Access REDLINE through your web browser with a subscription account.

**What you'll learn in this guide:**
- 🚀 How to get started with your subscription
- 📊 How to load and analyze data
- 📥 How to download financial data
- 🔄 How to convert between formats
- ⚙️ How to configure settings and API keys
- 🔧 How to troubleshoot issues

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Data Tab](#data-tab)
4. [Download Tab](#download-tab)
5. [Converter Tab](#converter-tab)
6. [Analysis Tab](#analysis-tab)
7. [Settings Tab](#settings-tab)
8. [Subscription & Payment](#subscription--payment)
9. [Data Sources](#data-sources)
10. [File Formats](#file-formats)
11. [Troubleshooting](#troubleshooting)

## 🎯 **Getting Started**

### **Step 1: Register for an Account**

1. **Visit the REDLINE website** (https://redfindat.com)
2. **Click "Register"** in the navigation bar
3. **Fill in your information**:
   - Name
   - Email address
   - Company (optional)
4. **Submit registration**
5. **Check your email** for your license key
6. **Log in** using your license key

### **Step 2: Access the Platform**

1. **Open your web browser** (Chrome, Firefox, Safari, or Edge)
2. **Navigate to** https://redfindat.com
3. **Enter your license key** when prompted
4. **Start using REDLINE** immediately

### **Step 3: First Data Download**

1. **Go to Download tab**
2. **Enter a ticker**: Try `AAPL` (Apple)
3. **Select date range**: Choose `2Y` (2 years)
4. **Click Download**
5. **Wait for completion**

### **Step 4: Load and View Data**

1. **Go to Data tab**
2. **Click "Load Data"**
3. **Select your downloaded file**
4. **Explore the data** with virtual scrolling

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Browser** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ | Latest version |
| **Internet** | Broadband connection | High-speed connection |
| **Screen** | 1280x720 | 1920x1080 or higher |

## 🖥️ **Main Interface**

### **Tab Navigation**
- **Data** - Load, view, and manage financial data files
- **Download** - Download data from various financial sources
- **Converter** - Convert files between different formats
- **Analysis** - Perform statistical and trend analysis
- **Settings** - Configure application preferences, themes, and API keys

### **Web Interface Layout**
- **Top Navigation Bar** - Quick access to all tabs and features
- **Main Content Area** - Context-sensitive based on active tab
- **Status Indicators** - Shows current operation status and progress
- **Theme Selector** - Switch between 8 available themes

## 📊 **Data Tab**

### **Loading Data**

1. Click **"Load Data"** button
2. Select your data file (CSV, Parquet, JSON, etc.)
3. Data will load automatically in the virtual scrolling table
4. Use the **date format selector** to customize how dates are displayed

### **Supported File Formats**
- **CSV** - Comma-separated values (recommended for compatibility)
- **Parquet** - Columnar storage format (recommended for large datasets)
- **JSON** - JavaScript Object Notation
- **Feather** - Fast columnar format
- **DuckDB** - Embedded analytical database (recommended for analysis)
- **TXT** - Stooq format files

### **Data Display Features**

- **Virtual Scrolling** - Efficiently handles large datasets (millions of rows)
- **Date Format Selection** - Choose from multiple date formats:
  - Auto (YYYY-MM-DD)
  - YYYY-MM-DD
  - MM/DD/YYYY
  - DD/MM/YYYY
  - YYYY/MM/DD
  - DD-MM-YYYY
  - MM-DD-YYYY
  - Raw (No Formatting)
- **Column Editing** - Click "Edit Columns" to rename column headers
- **Column Headers** - Click to sort data
- **Row Selection** - Click rows to select data
- **Search Function** - Use the search box to find specific values

### **Data Cleaning**

1. **Click "Clean Data"** button
2. **Configure cleaning options**:
   - **Remove Duplicate Rows**: Automatically removes exact duplicates
   - **Handle Missing Values**: Choose from:
     - Drop rows with missing values
     - Forward fill (use previous value)
     - Backward fill (use next value)
     - Don't handle missing values
   - **Clean Column Names**: Remove unnamed/empty columns
3. **Click "Apply"** to clean the data
4. **View cleaning statistics** (rows removed, missing values handled)
5. **Click "Save Cleaned"** to save the cleaned data to a new file

### **Data Operations**

- **Save Data** - Export current data to file
- **Filter Data** - Apply date range or other filters
- **Refresh Data** - Reload data from source file
- **Delete File** - Remove files from your account
- **Upload File** - Upload new data files

### **Supported Data Formats**
- **Stooq Format** - `<TICKER>`, `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>`, `<VOL>`
- **Standard Format** - Standard financial data columns
- **Yahoo Finance** - Direct Yahoo Finance data format
- **Bloomberg** - Bloomberg data format
- **Alpha Vantage** - Alpha Vantage API format
- **Finnhub** - Finnhub API format
- **Custom Formats** - Automatic detection and cleaning

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

#### **Alpha Vantage**
- ✅ **API Access** - Requires API key (free tier available)
- ✅ **Real-time Data** - Live market data
- ✅ **Historical Data** - Extensive historical coverage
- 📊 **Rate Limits** - Free tier: 5 calls/minute

#### **Finnhub**
- ✅ **API Access** - Requires API key (free tier available)
- ✅ **Real-time Data** - Live market data
- ✅ **Global Markets** - International coverage
- 📊 **Rate Limits** - Free tier: 60 calls/minute

#### **Custom API**
- ✅ **Flexible** - Configure your own data source
- ✅ **Custom Endpoints** - Use any REST API
- ✅ **API Key Management** - Secure API key storage
- 📊 **Rate Limiting** - Configurable rate limits

### **Download Process**

#### **Step 1: Select Data Source**
- Choose from Yahoo Finance, Stooq, Alpha Vantage, Finnhub, or Custom API
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
- **Output Format**: Choose CSV, Parquet, JSON, or DuckDB
- **Data Cleaning**: Apply cleaning options before saving

#### **Step 5: Start Download**
- Click **"Download"** button
- Monitor progress in the progress bar
- View results in the results table
- Use **"Stop"** button to cancel if needed

### **Batch Downloads**

1. **Enter multiple tickers** (comma-separated)
2. **Select date range**
3. **Click "Batch Download"**
4. **Monitor progress** for all tickers
5. **Download results** are saved automatically

### **Download History**

- **View all downloads** in the history table
- **Filter by date range** or ticker
- **Re-download** previous downloads
- **Delete** old download records

## 🔄 **Converter Tab**

### **Format Conversion**

1. **Select input file** from your data files
2. **Choose output format** (CSV, Parquet, JSON, Feather, DuckDB, TXT)
3. **Configure data cleaning options**:
   - **Remove Duplicate Rows**
   - **Handle Missing Values** (drop, forward fill, backward fill, none)
   - **Clean Column Names**
4. **Click "Convert"**
5. **Download converted file**

### **Batch Conversion**

1. **Select multiple files** (Ctrl+Click or Shift+Click)
2. **Choose output format**
3. **Configure cleaning options**
4. **Click "Batch Convert"**
5. **Monitor progress** for all files
6. **Download all converted files**

### **Conversion Features**

- **Bidirectional Conversion** - Convert between any supported formats
- **Data Cleaning** - Apply cleaning during conversion
- **Progress Tracking** - Real-time conversion progress
- **Error Handling** - Comprehensive error messages
- **Format Validation** - Automatic format detection

## 📈 **Analysis Tab**

### **Available Analysis Types**

#### **Basic Analysis**
- **Dataset Summary** - Total rows, columns, date range
- **Basic Statistics** - Mean, median, standard deviation, min/max
- **Data Quality** - Missing values, outliers detection

#### **Statistical Analysis**
- **Descriptive Statistics** - Comprehensive statistical measures
- **Close Price Statistics** - Detailed price analysis
- **Distribution Analysis** - Data distribution patterns

#### **Financial Analysis**
- **OHLCV Analysis** - Open, High, Low, Close, Volume analysis
- **Returns Analysis** - Price returns and volatility
- **Performance Metrics** - Sharpe ratio, maximum drawdown

#### **Correlation Analysis**
- **Inter-Asset Correlation** - Relationships between different assets
- **Market Correlation** - Correlation with market indices
- **Time-Series Correlation** - Correlation over time

#### **Volume Analysis**
- **Volume Statistics** - Average, median, max/min volume
- **High Volume Days** - Days with unusual volume activity
- **Volume Trends** - Volume patterns over time

### **Running Analysis**

1. **Load data** in the Data tab
2. **Switch to Analysis tab**
3. **Select analysis type**
4. **Click "Run Analysis"**
5. **View results** in the analysis results area
6. **Export results** to CSV or JSON

### **Analysis Features**

- **Automatic Date Exclusion** - Date/timestamp columns are excluded from statistical calculations
- **Number Formatting** - Large numbers formatted with comma separators
- **Export Results** - Save analysis results to file
- **Visual Charts** - Graphical representation of analysis results

## ⚙️ **Settings Tab**

### **Theme Customization**

- **8 Available Themes**: Default, High Contrast, Ocean, Forest, Sunset, Monochrome, Grayscale, Dark
- **Live Color Customization**: Adjust colors in real-time
- **Font Color Presets**: Choose from predefined color schemes
- **Save Preferences**: Your theme choices are saved automatically

### **API Key Management**

#### **Built-in Data Sources**
- **Alpha Vantage** - Enter your API key for Alpha Vantage
- **Finnhub** - Enter your API key for Finnhub
- **IEX Cloud** - Enter your API key for IEX Cloud

#### **Custom API Configuration**
1. **Click "Add Custom API"**
2. **Configure your API**:
   - **Name**: Display name for your API
   - **Base URL**: API base endpoint
   - **Endpoint**: Data endpoint path
   - **API Key**: Your API key (masked for security)
   - **Rate Limit**: Requests per minute
   - **Date Format**: Expected date format
   - **Parameter Names**: Ticker, date, API key parameter names
3. **Save configuration**
4. **Use in Download tab** - Your custom API will appear as a data source

### **Display Settings**

- **Date Format** - Default date format for data display
- **Number Format** - Number formatting preferences
- **Table Settings** - Row height, column width, grid lines

### **Account Settings**

- **License Key** - View your current license key
- **Hours Remaining** - Check your subscription balance
- **Usage History** - View your usage history
- **Payment** - Add hours to your account

## 💳 **Subscription & Payment**

### **License Key**

- **Registration**: Get your license key when you register
- **License Format**: `RL-DEV-XXXXXXXX-XXXXXXXX-XXXXXXXX`
- **Usage Tracking**: Hours are deducted based on usage time
- **Balance Check**: View remaining hours in Settings tab

### **Adding Hours**

1. **Go to Settings tab**
2. **Click "Add Hours"** or navigate to Payment tab
3. **Choose a package**:
   - 5 hours - $X.XX
   - 10 hours - $X.XX
   - 20 hours - $X.XX
   - 50 hours - $X.XX
   - Custom hours
4. **Complete payment** via Stripe
5. **Hours are added** automatically to your account

### **Usage Tracking**

- **Session-based**: Hours are tracked per active session
- **Automatic Deduction**: Hours are deducted when you use the platform
- **Real-time Balance**: Check your balance anytime in Settings
- **Usage History**: View detailed usage history

## 📊 **Data Sources**

### **Yahoo Finance**
- **URL**: finance.yahoo.com
- **Coverage**: Global stocks, ETFs, indices, crypto, forex
- **Update Frequency**: Real-time during market hours
- **Historical Data**: Up to 40+ years for some assets
- **Limitations**: Rate limiting (delays between requests)
- **API Key**: Not required

### **Stooq.com**
- **URL**: stooq.com
- **Coverage**: Global markets with high-quality data
- **Authentication**: Manual login required (2FA)
- **Update Frequency**: Daily updates
- **Historical Data**: Extensive historical coverage
- **Limitations**: Manual download process

### **Alpha Vantage**
- **URL**: alphavantage.co
- **Coverage**: Stocks, forex, crypto, commodities
- **API Key**: Required (free tier available)
- **Update Frequency**: Real-time and historical
- **Rate Limits**: Free tier: 5 calls/minute, 500 calls/day
- **Historical Data**: Up to 20+ years

### **Finnhub**
- **URL**: finnhub.io
- **Coverage**: Global stocks, forex, crypto
- **API Key**: Required (free tier available)
- **Update Frequency**: Real-time and historical
- **Rate Limits**: Free tier: 60 calls/minute
- **Historical Data**: Extensive coverage

### **Custom APIs**
- **Flexible Configuration**: Configure any REST API
- **API Key Management**: Secure storage and masking
- **Rate Limiting**: Configurable rate limits
- **Custom Parameters**: Support for custom parameter names

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

### **Supported Formats**
REDLINE supports multiple financial data formats with automatic column cleaning:
- **Bloomberg**: `security, date, time, px_open, px_high, px_low, px_last, px_volume`
- **Alpha Vantage**: `symbol, timestamp, open, high, low, close, volume`
- **Finnhub**: Compact single-letter format (`c, h, l, o, t, v`)
- **Custom formats**: Automatic detection and cleaning of malformed headers

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"License key missing" Error**
- **Cause**: License key not provided or expired
- **Solution**: Enter your license key in the login prompt or Settings tab
- **Check Balance**: Verify you have hours remaining in Settings

#### **"Failed to retrieve balance"**
- **Cause**: License server temporarily unavailable
- **Solution**: Check your internet connection and try again
- **Note**: The platform will continue to work with local tracking

#### **"File not found" Error**
- **Cause**: File was deleted or moved
- **Solution**: Re-upload or re-download the file
- **Check**: Verify file exists in your account

#### **"API key invalid" Error**
- **Cause**: API key is incorrect or expired
- **Solution**: Update your API key in Settings > API Keys
- **Check**: Verify API key is correct and has sufficient quota

#### **Date Format Issues**
- **Cause**: Date column format not recognized
- **Solution**: Use the date format selector to choose the correct format
- **Note**: REDLINE automatically detects YYYYMMDD numeric dates

### **Performance Optimization**

#### **Large Datasets**
- Use virtual scrolling (automatic)
- Process data in chunks
- Consider using Parquet format for storage
- Close unused browser tabs

#### **Download Speed**
- Use Yahoo Finance for fastest downloads
- Download multiple tickers in batches
- Avoid peak market hours for better performance
- Check your internet connection speed

### **Getting Help**

#### **Support Resources**
- **Help Page**: Access comprehensive documentation
- **Settings Tab**: View system information and logs
- **Email Support**: Contact support@redfindat.com

#### **Data Validation**
- Verify ticker symbols are correct
- Check date ranges are valid
- Ensure file formats are supported

#### **Format Issues**
- REDLINE automatically detects most formats
- Use Stooq format for best compatibility
- Convert files using the built-in format converter

## 🎉 **Tips and Best Practices**

### **Data Management**
1. **Use Stooq Format** - Best compatibility with REDLINE
2. **Organize Files** - Use descriptive filenames
3. **Clean Data First** - Apply data cleaning before analysis
4. **Validate Data** - Check for missing values and outliers

### **Analysis Workflow**
1. **Load Data** - Import your financial data
2. **Clean Data** - Remove duplicates and handle missing values
3. **Explore Data** - Use basic statistics to understand the dataset
4. **Run Analysis** - Perform trend and correlation analysis
5. **Export Results** - Save analysis results for reporting

### **Download Strategy**
1. **Start with Yahoo** - Use Yahoo Finance for initial data acquisition
2. **Use Custom APIs** - Configure your own data sources for specialized data
3. **Batch Downloads** - Download multiple tickers together for efficiency
4. **Date Ranges** - Use appropriate date ranges for your analysis needs

### **Performance Tips**
1. **Close Unused Tabs** - Free up browser memory
2. **Use Filters** - Reduce dataset size with date or other filters
3. **Monitor Balance** - Keep track of your subscription hours
4. **Optimize API Keys** - Use API keys with sufficient rate limits

---

## 📞 **Support**

For additional help or to report issues:
1. Check the troubleshooting section above
2. Review the Help page in the application
3. Contact support@redfindat.com
4. Ensure you're using the latest version

**REDLINE Financial Data Analyzer** - Professional-grade financial data analysis made accessible through cloud subscription service. 🌟
