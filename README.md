# REDLINE - Financial Data Analyzer & Management Tool

REDLINE is a comprehensive **financial data analysis application** that provides data downloading, viewing, filtering, and analysis capabilities with a modern GUI interface. It supports multiple data sources and formats for professional financial data analysis.

## 🎯 **Core Purpose**
REDLINE is a complete financial data analysis platform that enables users to:
- **Download** financial data from multiple sources (Yahoo Finance, Stooq, etc.)
- **View** and explore large datasets with virtual scrolling
- **Filter** data using advanced filtering capabilities
- **Analyze** data with statistical and trend analysis tools
- **Convert** between different data formats
- **Manage** financial data workflows efficiently

The application provides both GUI and command-line interfaces for processing large datasets efficiently.

## 📁 **Supported File Formats**

### **Input Formats**
- **CSV** (.csv) - Comma-separated values
- **TXT** (.txt) - Text files (including Stooq format)
- **JSON** (.json) - JavaScript Object Notation
- **DuckDB** (.duckdb) - Embedded analytical database
- **Parquet** (.parquet) - Columnar storage format
- **Feather** (.feather) - Fast binary format
- **Keras** (.h5) - TensorFlow/Keras model files
- **NumPy** (.npz) - NumPy compressed arrays

### **Output Formats**
- **CSV** - Standard comma-separated values
- **JSON** - JavaScript Object Notation
- **DuckDB** - Embedded analytical database
- **Parquet** - Columnar storage format
- **Feather** - Fast binary format
- **HDF5** - Hierarchical Data Format
- **Pickle** - Python serialization format

## 🖥️ **GUI Interface Features**

### **Main Application Window**
- **1200x800 minimum window size**
- **Main toolbar** with quick access buttons
- **Tabbed interface** for organized workflow
- **Performance monitoring** with real-time memory usage

### **Data Tab**
- **File Loading**
  - Browse and select files (CSV, Parquet, JSON, Feather)
  - Automatic format detection
  - Virtual scrolling for large datasets
  - Real-time data preview

- **Data Operations**
  - **Save Data** - Export current data to file
  - **Filter Data** - Advanced filtering with multiple criteria
  - **Refresh Data** - Reload data from source file
  - **Clear Data** - Remove current data from display

- **Advanced Filtering**
  - **Date Range Filtering** - Filter by date ranges with presets
  - **Numeric Filtering** - Min/max ranges for numeric columns
  - **Text Filtering** - Contains/exact match for text columns
  - **Custom Expressions** - SQL-like query expressions
  - **Real-time Preview** - See filter results before applying

### **Download Tab**
- **Data Sources**
  - **Yahoo Finance** - Free, reliable financial data (recommended)
  - **Stooq.com** - High-quality data with manual authentication
  - **Multi-Source** - Fallback system with multiple providers

- **Download Features**
  - **Ticker Input** - Manual entry or quick-select buttons
  - **Date Range Selection** - Custom dates or presets (1Y, 2Y, 5Y, Max)
  - **Output Format** - Stooq format for REDLINE compatibility
  - **Progress Tracking** - Real-time download progress
  - **Results Management** - View, load, and manage downloaded files

### **Analysis Tab**
- **Statistical Analysis**
  - Basic statistics (mean, median, std dev, min/max)
  - Data quality metrics
  - Missing value analysis

- **Trend Analysis**
  - Price trend analysis with date range support
  - Volume analysis and statistics
  - Correlation analysis between assets

- **Market Analysis**
  - High volume day detection
  - Volatility metrics
  - Performance indicators

### **Data View Tab**
- **File Browser**
  - Hierarchical file listing
  - Multiple file selection
  - File status indicators
  - Refresh functionality

- **Data Viewer**
  - **TreeView display** with sortable columns
  - **Pagination controls** (50, 100, 200, 500, 1000 rows per page)
  - **Ticker navigation** (Previous/Next ticker buttons)
  - **Global search** with case-sensitive option
  - **Column filtering** for each data column

- **Advanced Features**
  - **Virtual Scrolling** for large datasets (10M+ rows)
  - **Advanced Filtering** with SQL-like query builder
  - **Memory optimization** with automatic garbage collection
  - **Performance monitoring** with real-time memory usage

- **Data Management**
  - **Export data** (current page or all data)
  - **Remove files** from storage
  - **Show statistics** for data analysis
  - **Copy data** to clipboard

## 🔧 **Data Processing Capabilities**

### **Data Validation**
- **Schema validation** for required columns
- **Stooq format detection** and parsing
- **Data type validation** and conversion
- **Missing value handling**

### **Data Cleaning**
- **Column standardization** (OHLCV format)
- **Numeric data cleaning** (remove arrays/lists)
- **Timestamp conversion** to datetime format
- **Duplicate removal** with statistics

### **Data Balancing**
- **Ticker distribution analysis**
- **Automatic record balancing** per ticker
- **Minimum record requirements**
- **Data quality indicators**

### **Format Conversion**
- **Cross-format conversion** (any input to any output)
- **Batch processing** of multiple files
- **Schema preservation** during conversion
- **Metadata handling**

## 🚀 **Performance Features**

### **Memory Optimization**
- **Virtual scrolling** - Only loads visible data
- **Lazy loading** - Loads data on demand
- **Intelligent caching** - Caches frequently accessed data
- **Memory monitoring** - Real-time RAM usage display
- **Automatic garbage collection**

### **Large Dataset Handling**
- **10M+ row support** with virtual scrolling
- **Database-backed storage** (DuckDB)
- **Efficient pagination** for large datasets
- **Background processing** to prevent UI freezing

### **Advanced Filtering**
- **SQL-like query builder** with visual interface
- **Multiple operators**: equals, contains, greater_than, between, in, is_null, etc.
- **Complex conditions** with AND/OR logic
- **Query saving/loading** for reuse
- **Real-time filtering** results

## 📊 **Data Analysis Features**

### **Statistical Analysis**
- **Data distribution analysis**
- **Ticker record counts**
- **Date range coverage**
- **Missing value statistics**
- **Data quality metrics**

### **File Analysis**
- **Stooq format analysis** with detailed reporting
- **Timestamp analysis** for data continuity
- **Format detection** and validation
- **File size and structure reporting**

### **Keras Model Support**
- **Model loading** and validation
- **Model statistics** display
- **Input/output shape analysis**
- **Layer information** extraction

## 🛠️ **Technical Features**

### **Multi-threading**
- **Background processing** for file operations
- **UI responsiveness** during long operations
- **Thread-safe updates** to GUI components
- **Progress tracking** across threads

### **Error Handling**
- **Enhanced error messages** with suggestions
- **File validation** before processing
- **Graceful failure** handling
- **Error logging** with detailed information

### **Configuration Management**
- **INI file configuration** (data_config.ini)
- **Database path configuration**
- **Format-specific settings**
- **User preferences** storage

### **Logging and Monitoring**
- **Comprehensive logging** (redline.log)
- **Performance monitoring**
- **Memory usage tracking**
- **Operation statistics**

## 📚 **Documentation and Help**

### **Built-in Help**
- **Context-sensitive help** for each tab
- **User manual** with detailed instructions
- **Tooltips** for buttons and controls
- **Error suggestions** and troubleshooting

### **Manual Content**
- **Data Loader manual** - Step-by-step file processing
- **Data View manual** - Navigation and analysis features
- **Troubleshooting guide** - Common issues and solutions
- **Best practices** for data processing

## 🔌 **Integration Capabilities**

### **Database Integration**
- **DuckDB** as primary storage engine
- **SQL query support** for data retrieval
- **Table management** and optimization
- **Connection pooling** for performance

### **Machine Learning Integration**
- **TensorFlow/Keras** model support
- **Data preprocessing** for ML pipelines
- **Format conversion** for ML frameworks
- **Batch processing** for training data

### **External Data Sources** (Planned/Partially Implemented)
- **YFinance** - Yahoo Finance data download
- **Tiingo** - Financial data API integration
- **Enhanced Stooq** - Improved Stooq format support

## 🎨 **User Experience Features**

### **Keyboard Shortcuts**
- **Search focus** (Ctrl+F)
- **Select all** (Ctrl+A)
- **Copy selection** (Ctrl+C)
- **Refresh data** (F5)

### **Visual Feedback**
- **Progress indicators** for long operations
- **Status messages** for user actions
- **Color-coded** file status indicators
- **Responsive UI** with loading states

### **Accessibility**
- **High contrast** text and backgrounds
- **Keyboard navigation** support
- **Screen reader** friendly interface
- **Adjustable** window sizes

## 🔒 **Data Security and Integrity**

### **Data Validation**
- **Input validation** for all user inputs
- **File integrity** checks
- **Data type** verification
- **Schema compliance** validation

### **Safe Operations**
- **File backup** before processing
- **Atomic operations** for data safety
- **Error recovery** mechanisms
- **Data preservation** during conversion

## 🚀 **Quick Start**

### **Prerequisites**
1. **XQuartz**: Required for GUI on macOS
   - Download from: https://www.xquartz.org/
   - Or check if installed: `ls /Applications/Utilities/XQuartz.app`

2. **Docker**: Make sure Docker Desktop is running

### **Running the GUI**
1. **Simple method** (recommended):
   ```bash
   ./run_gui.bash
   ```

2. **Test X11 forwarding first** (if you encounter issues):
   ```bash
   ./test_x11.bash
   ```

3. **Alternative method** (if the simple method fails):
   ```bash
   # Install socat first
   brew install socat
   # Then run
   ./run_gui_socat.bash
   ```

### **Command-Line Usage**
You can run Redline in different modes using the `--task` argument:

- `gui` — Launches the graphical user interface (default)
- `load` — Loads data files into the DuckDB database
- `convert` — Converts data files between supported formats
- `preprocess` — Preprocesses data for machine learning or reinforcement learning

**Examples:**
```sh
python3 -m data_module --task=gui
python3 -m data_module --task=load
python3 -m data_module --task=convert
python3 -m data_module --task=preprocess
```

## 🔧 **Installation**

### **Dependencies**
```bash
pip install pandas numpy duckdb pyarrow polars tensorflow tkinter
```

### **Optional Dependencies**
```bash
pip install yfinance tiingo psutil
```

## 📖 **Documentation**

- **GUI_TROUBLESHOOTING.md** - Troubleshooting guide for GUI issues
- **PERFORMANCE_IMPROVEMENTS.md** - Performance optimization details
- **REDLINE_SOFTWARE_DESIGN.md** - Software architecture and design

## 🤝 **Contributing**

REDLINE is designed with a modular architecture that makes it easy to extend:
- Add new file format support
- Implement new data sources
- Enhance preprocessing capabilities
- Improve performance features

## 📄 **License**

This project is designed for financial data processing and machine learning workflows.

---

This comprehensive feature set makes REDLINE a powerful tool for financial data processing, conversion, and analysis, suitable for both individual users and machine learning workflows.
# redline2
# redline2
# redline2
