# REDLINE Developer Guide

## 🏗️ **Architecture Overview**

REDLINE uses a modular architecture with clear separation of concerns, making it easy to extend, maintain, and test. The application is organized into several key modules:

```
redline/
├── core/           # Core data processing and validation
├── database/       # Database operations and query building
├── gui/           # User interface components
├── downloaders/   # Data acquisition from external sources
├── utils/         # Utility functions and configuration
├── tests/         # Unit and integration tests
└── cli/          # Command-line interface tools
```

## 🔧 **Core Modules**

### **Core Data Processing (`redline/core/`)**

#### **DataLoader (`data_loader.py`)**
- Main data loading and processing functionality
- Handles multiple file formats (CSV, Parquet, JSON, Feather)
- Provides data validation and cleaning
- Supports both pandas and optional polars/pyarrow backends

```python
from redline.core.data_loader import DataLoader

loader = DataLoader()
data = loader.load_file_by_type("data.csv", "csv")
```

#### **DataValidator (`data_validator.py`)**
- Validates financial data files and structure
- Checks for required columns and data types
- Provides detailed validation reports
- Supports both Stooq and standard formats

```python
from redline.core.data_validator import DataValidator

validator = DataValidator()
is_valid = validator.validate_data("data.csv", "csv")
```

#### **DataCleaner (`data_cleaner.py`)**
- Cleans and standardizes financial data
- Handles missing values and outliers
- Converts data to consistent formats
- Provides data quality metrics

#### **FormatConverter (`format_converter.py`)**
- Converts between different data formats
- Supports pandas, polars, and pyarrow
- Handles file I/O operations
- Provides format-specific optimizations

#### **Schema (`schema.py`)**
- Defines data schemas and constants
- Standardizes column names and data types
- Provides format-specific configurations

### **Database Operations (`redline/database/`)**

#### **DatabaseConnector (`connector.py`)**
- Handles database connections (DuckDB)
- Provides basic CRUD operations
- Manages connection pooling and transactions
- Graceful fallback when database unavailable

```python
from redline.database.connector import DatabaseConnector

connector = DatabaseConnector()
data = connector.read_shared_data("table_name")
```

#### **QueryBuilder (`query_builder.py`)**
- Constructs complex database queries
- Provides query optimization
- Supports parameterized queries
- Handles query result formatting

#### **DatabaseOperations (`operations.py`)**
- Advanced database operations
- Data aggregation and analysis
- Backup and restore functionality
- Performance monitoring

### **GUI Components (`redline/gui/`)**

#### **Main Window (`main_window.py`)**
- Primary application window
- Tab management and navigation
- Keyboard shortcuts and event handling
- Application lifecycle management

#### **Data Tab (`data_tab.py`)**
- Data loading and viewing interface
- Virtual scrolling for large datasets
- File operations and data management
- Integration with analysis tools

#### **Download Tab (`download_tab.py`)**
- Data acquisition interface
- Multiple data source support
- Progress tracking and status updates
- Download management and results display

#### **Analysis Tab (`analysis_tab.py`)**
- Statistical analysis interface
- Trend analysis and visualization
- Correlation and volume analysis
- Results display and export

#### **Settings Tab (`settings_tab.py`)**
- Application configuration
- User preferences management
- System settings and optimization
- Logging and debugging options

#### **Widgets (`redline/gui/widgets/`)**
- **VirtualScrollingTreeview** - Efficient large dataset display
- **DataSource** - Abstract data source for virtual scrolling
- **ProgressTracker** - Progress tracking and status updates

### **Data Downloaders (`redline/downloaders/`)**

#### **Base Downloader (`base_downloader.py`)**
- Abstract base class for all downloaders
- Common functionality and error handling
- Standardized interface and data formats
- Rate limiting and retry logic

#### **Yahoo Downloader (`yahoo_downloader.py`)**
- Yahoo Finance data acquisition
- No authentication required
- High reliability and speed
- Automatic format conversion

```python
from redline.downloaders.yahoo_downloader import YahooDownloader

downloader = YahooDownloader()
data = downloader.download_data("AAPL", "2020-01-01", "2024-01-01")
```

#### **Stooq Downloader (`stooq_downloader.py`)**
- Stooq.com data acquisition
- Manual authentication support
- High-quality financial data
- Multiple access methods

#### **Multi-Source Downloader (`multi_source.py`)**
- Multiple data source support
- Fallback mechanisms
- Source selection and prioritization
- Unified data format output

#### **Bulk Downloader (`bulk_downloader.py`)**
- Large-scale data acquisition
- Parallel processing
- Progress tracking
- Error handling and recovery

#### **Format Handlers (`redline/downloaders/format_handlers/`)**
- Source-specific format conversions
- Data standardization
- Quality validation
- Performance optimization

### **Utilities (`redline/utils/`)**

#### **Configuration (`config.py`)**
- Application configuration management
- Environment-specific settings
- User preferences
- System optimization

#### **File Operations (`file_ops.py`)**
- File system operations
- Data backup and restore
- Directory management
- File validation and integrity

#### **Logging (`logging_config.py`)**
- Centralized logging configuration
- Multiple log levels and outputs
- Performance monitoring
- Debug information

### **CLI Tools (`redline/cli/`)**

#### **Download CLI (`download.py`)**
- Command-line data downloading
- Batch processing support
- Script automation
- Integration with GUI tools

#### **Analysis CLI (`analyze.py`)**
- Command-line analysis tools
- Batch analysis processing
- Report generation
- Integration with GUI analysis

## 🧪 **Testing Framework**

### **Test Structure**
```
redline/tests/
├── test_data_loader.py      # Core data loading tests
├── test_downloaders.py      # Downloader functionality tests
├── test_gui_components.py   # GUI component tests
├── test_database.py         # Database operation tests
└── integration_tests.py     # End-to-end integration tests
```

### **Running Tests**
```bash
# Run all tests
python -m pytest redline/tests/

# Run specific test file
python -m pytest redline/tests/test_data_loader.py

# Run with coverage
python -m pytest --cov=redline redline/tests/
```

### **Test Categories**

#### **Unit Tests**
- Individual component testing
- Mock external dependencies
- Fast execution
- Isolated functionality

#### **Integration Tests**
- Component interaction testing
- Real data processing
- End-to-end workflows
- Performance validation

#### **GUI Tests**
- User interface testing
- Event handling validation
- Layout and interaction testing
- Accessibility compliance

## 🔌 **Extension Points**

### **Adding New Data Sources**

1. **Create Downloader Class**
```python
from redline.downloaders.base_downloader import BaseDownloader

class NewSourceDownloader(BaseDownloader):
    def download_data(self, ticker, start_date, end_date):
        # Implementation here
        pass
```

2. **Register in Multi-Source Downloader**
```python
# Add to redline/downloaders/multi_source.py
def download_from_source(self, source, ticker, start_date, end_date):
    if source == 'new_source':
        return self.new_source_downloader.download_data(ticker, start_date, end_date)
```

3. **Update GUI Integration**
```python
# Add to redline/gui/download_tab.py
if source == "new_source":
    df = self.new_source_downloader.download_data(ticker, start_date, end_date)
```

### **Adding New Analysis Types**

1. **Create Analysis Method**
```python
# In redline/gui/analysis_tab.py
def run_custom_analysis(self):
    """Run custom analysis."""
    try:
        # Analysis implementation
        pass
    except Exception as e:
        self.logger.error(f"Custom analysis error: {str(e)}")
```

2. **Add GUI Button**
```python
# In analysis tab widget creation
ttk.Button(analysis_frame, text="Custom Analysis", 
          command=self.run_custom_analysis).pack(pady=5)
```

### **Adding New File Formats**

1. **Update Format Converter**
```python
# In redline/core/format_converter.py
def load_file_by_type(self, file_path, format):
    if format == 'new_format':
        # Implementation for new format
        pass
```

2. **Update Schema**
```python
# In redline/core/schema.py
EXT_TO_FORMAT = {
    '.csv': 'csv',
    '.parquet': 'parquet',
    '.json': 'json',
    '.new': 'new_format'  # Add new format
}
```

## 🚀 **Performance Optimization**

### **Memory Management**
- Use virtual scrolling for large datasets
- Implement data chunking for processing
- Clear unused data structures
- Monitor memory usage with profiling

### **Database Optimization**
- Use connection pooling
- Implement query caching
- Optimize database schemas
- Use appropriate indexes

### **GUI Performance**
- Lazy loading of components
- Efficient event handling
- Minimal UI updates
- Background processing for heavy operations

### **Data Processing**
- Use vectorized operations
- Implement parallel processing
- Cache frequently used data
- Optimize file I/O operations

## 🐛 **Debugging and Logging**

### **Logging Configuration**
```python
from redline.utils.logging_config import setup_logging

# Setup detailed logging
setup_logging(
    log_level="DEBUG",
    log_file="redline_debug.log",
    console_output=True
)
```

### **Common Debug Scenarios**

#### **Data Loading Issues**
```python
# Enable debug logging for data loader
logger = logging.getLogger('redline.core.data_loader')
logger.setLevel(logging.DEBUG)
```

#### **GUI Event Issues**
```python
# Add debug prints to event handlers
def on_button_click(self, event):
    print(f"Button clicked: {event}")
    # Rest of handler
```

#### **Download Failures**
```python
# Check network and API issues
import requests
response = requests.get("https://api.example.com/data")
print(f"Response: {response.status_code}")
```

### **Performance Profiling**
```python
import cProfile
import pstats

# Profile specific function
profiler = cProfile.Profile()
profiler.enable()
# Run your code
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

## 📦 **Dependencies**

### **Core Dependencies**
- **pandas** - Data manipulation and analysis
- **tkinter** - GUI framework (built-in)
- **yfinance** - Yahoo Finance data access
- **requests** - HTTP requests

### **Optional Dependencies**
- **duckdb** - Database operations (fallback available)
- **polars** - High-performance data processing (fallback available)
- **pyarrow** - Columnar data processing (fallback available)

### **Development Dependencies**
- **pytest** - Testing framework
- **pytest-cov** - Coverage testing
- **black** - Code formatting
- **flake8** - Code linting

### **Dependency Management**
```bash
# Install core dependencies
pip install pandas yfinance requests

# Install optional dependencies
pip install duckdb polars pyarrow

# Install development dependencies
pip install pytest pytest-cov black flake8
```

## 🔒 **Security Considerations**

### **Data Privacy**
- No data is sent to external servers (except data sources)
- Local data storage only
- User controls all data access

### **API Security**
- API keys stored locally in config files
- No hardcoded credentials
- Rate limiting to prevent abuse

### **File Security**
- Input validation for all file operations
- Safe file path handling
- No arbitrary code execution

## 📈 **Future Development**

### **Planned Features**
- Real-time data streaming
- Advanced charting and visualization
- Machine learning integration
- Portfolio management tools
- Risk analysis modules

### **Architecture Improvements**
- Plugin system for extensions
- Microservices architecture option
- Cloud deployment support
- API server mode

### **Performance Enhancements**
- GPU acceleration for calculations
- Distributed processing support
- Advanced caching strategies
- Real-time data processing

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a development branch
3. Install dependencies
4. Run tests to ensure everything works
5. Make your changes
6. Add tests for new functionality
7. Submit a pull request

### **Code Standards**
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for all classes and methods
- Write tests for new functionality
- Update documentation for changes

### **Pull Request Process**
1. Ensure all tests pass
2. Update documentation if needed
3. Add changelog entry
4. Request code review
5. Address feedback
6. Merge when approved

---

## 📚 **Additional Resources**

- **API Documentation** - Detailed API reference
- **Code Examples** - Sample implementations
- **Performance Benchmarks** - Speed and memory usage
- **Migration Guide** - Upgrading between versions
- **Community Forum** - Developer discussions and support

**REDLINE Developer Guide** - Building the future of financial data analysis.
