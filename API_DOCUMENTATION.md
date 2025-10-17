# REDLINE API Documentation

<div align="center">

![API Documentation](https://img.shields.io/badge/API-Documentation-purple?style=for-the-badge&logo=code)

**Developer guide for REDLINE's internal APIs**

[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](README.md)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-blue)](README.md)

</div>

---

## 🏗️ **Architecture Overview**

REDLINE is built with a modular architecture that separates concerns and provides clean APIs for each component.

### **Core Modules**

```
redline/
├── core/           # Core data processing
├── gui/            # User interface components
├── downloaders/    # Data source integrations
├── database/       # Database operations
├── utils/          # Utility functions
└── tests/          # Test suite
```

---

## 📊 **Core Data Processing API**

### **DataLoader Class**

**Location**: `redline/core/data_loader.py`

**Purpose**: Load and validate financial data from various file formats.

#### **Key Methods**

```python
class DataLoader:
    def load_file(self, file_path: str, format: str = None) -> pd.DataFrame:
        """
        Load data from a file.
        
        Args:
            file_path: Path to the data file
            format: File format (auto-detected if None)
            
        Returns:
            DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is unsupported
        """
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate data structure and quality.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported format strings
        """
```

#### **Usage Example**

```python
from redline.core.data_loader import DataLoader

# Initialize loader
loader = DataLoader()

# Load data
data = loader.load_file("data/AAPL.csv")

# Validate data
if loader.validate_data(data):
    print("Data is valid")
else:
    print("Data validation failed")
```

### **FormatConverter Class**

**Location**: `redline/core/format_converter.py`

**Purpose**: Convert data between different file formats.

#### **Key Methods**

```python
class FormatConverter:
    def convert_file(self, input_path: str, output_path: str, 
                    output_format: str) -> bool:
        """
        Convert file from one format to another.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            output_format: Target format
            
        Returns:
            True if conversion successful
        """
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported output formats.
        
        Returns:
            List of supported format strings
        """
    
    def batch_convert(self, file_paths: List[str], 
                     output_dir: str, output_format: str) -> Dict[str, bool]:
        """
        Convert multiple files in batch.
        
        Args:
            file_paths: List of input file paths
            output_dir: Output directory
            output_format: Target format
            
        Returns:
            Dictionary mapping file paths to success status
        """
```

#### **Usage Example**

```python
from redline.core.format_converter import FormatConverter

# Initialize converter
converter = FormatConverter()

# Convert single file
success = converter.convert_file(
    "data/AAPL.csv", 
    "data/AAPL.parquet", 
    "parquet"
)

# Batch convert
files = ["data/AAPL.csv", "data/MSFT.csv"]
results = converter.batch_convert(files, "output/", "parquet")
```

### **DataValidator Class**

**Location**: `redline/core/data_validator.py`

**Purpose**: Validate data quality and structure.

#### **Key Methods**

```python
class DataValidator:
    def validate_schema(self, data: pd.DataFrame) -> bool:
        """
        Validate data schema (required columns, types).
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if schema is valid
        """
    
    def check_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Check data quality metrics.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with quality metrics
        """
    
    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect data anomalies and outliers.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            List of detected anomalies
        """
```

---

## 📥 **Data Download API**

### **YahooDownloader Class**

**Location**: `redline/downloaders/yahoo_downloader.py`

**Purpose**: Download financial data from Yahoo Finance.

#### **Key Methods**

```python
class YahooDownloader:
    def download_ticker(self, ticker: str, start_date: str, 
                       end_date: str) -> pd.DataFrame:
        """
        Download data for a single ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLCV data
        """
    
    def download_multiple(self, tickers: List[str], 
                         start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple tickers.
        
        Args:
            tickers: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
    
    def get_available_tickers(self) -> List[str]:
        """
        Get list of available ticker symbols.
        
        Returns:
            List of ticker symbols
        """
```

#### **Usage Example**

```python
from redline.downloaders.yahoo_downloader import YahooDownloader

# Initialize downloader
downloader = YahooDownloader()

# Download single ticker
data = downloader.download_ticker(
    "AAPL", 
    "2023-01-01", 
    "2024-01-01"
)

# Download multiple tickers
tickers = ["AAPL", "MSFT", "GOOGL"]
all_data = downloader.download_multiple(
    tickers, 
    "2023-01-01", 
    "2024-01-01"
)
```

### **StooqDownloader Class**

**Location**: `redline/downloaders/stooq_downloader.py`

**Purpose**: Download data from Stooq.com.

#### **Key Methods**

```python
class StooqDownloader:
    def download_ticker(self, ticker: str, start_date: str, 
                       end_date: str) -> pd.DataFrame:
        """
        Download data from Stooq.
        
        Args:
            ticker: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with Stooq format data
        """
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with Stooq (if required).
        
        Args:
            username: Stooq username
            password: Stooq password
            
        Returns:
            True if authentication successful
        """
```

---

## 🗄️ **Database API**

### **DatabaseConnector Class**

**Location**: `redline/database/connector.py`

**Purpose**: Manage database connections and operations.

#### **Key Methods**

```python
class DatabaseConnector:
    def __init__(self, db_path: str = "redline_data.duckdb"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to DuckDB database file
        """
    
    def create_table(self, table_name: str, data: pd.DataFrame) -> bool:
        """
        Create table from DataFrame.
        
        Args:
            table_name: Name of the table
            data: DataFrame to store
            
        Returns:
            True if table created successfully
        """
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query.
        
        Args:
            sql: SQL query string
            
        Returns:
            DataFrame with query results
        """
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get table information.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table metadata
        """
```

#### **Usage Example**

```python
from redline.database.connector import DatabaseConnector

# Initialize connector
db = DatabaseConnector("my_data.duckdb")

# Create table
success = db.create_table("aapl_data", data)

# Query data
result = db.query("SELECT * FROM aapl_data WHERE Date > '2023-01-01'")

# Get table info
info = db.get_table_info("aapl_data")
```

### **QueryBuilder Class**

**Location**: `redline/database/query_builder.py`

**Purpose**: Build SQL queries programmatically.

#### **Key Methods**

```python
class QueryBuilder:
    def select(self, columns: List[str]) -> 'QueryBuilder':
        """Add SELECT clause."""
    
    def from_table(self, table: str) -> 'QueryBuilder':
        """Add FROM clause."""
    
    def where(self, condition: str) -> 'QueryBuilder':
        """Add WHERE clause."""
    
    def order_by(self, column: str, ascending: bool = True) -> 'QueryBuilder':
        """Add ORDER BY clause."""
    
    def build(self) -> str:
        """Build the final SQL query."""
```

#### **Usage Example**

```python
from redline.database.query_builder import QueryBuilder

# Build query
query = (QueryBuilder()
    .select(["Date", "Close", "Volume"])
    .from_table("aapl_data")
    .where("Date > '2023-01-01'")
    .order_by("Date", ascending=True)
    .build())

# Execute query
result = db.query(query)
```

---

## 🎨 **GUI API**

### **BaseTab Class**

**Location**: `redline/gui/base_tab.py`

**Purpose**: Base class for all GUI tabs.

#### **Key Methods**

```python
class BaseTab:
    def __init__(self, parent, logger):
        """
        Initialize tab.
        
        Args:
            parent: Parent widget
            logger: Logger instance
        """
    
    def setup_ui(self) -> None:
        """Setup user interface elements."""
    
    def refresh_data(self) -> None:
        """Refresh displayed data."""
    
    def clear_data(self) -> None:
        """Clear displayed data."""
```

### **DataTab Class**

**Location**: `redline/gui/data_tab.py`

**Purpose**: Data loading and viewing interface.

#### **Key Methods**

```python
class DataTab(BaseTab):
    def load_file(self, file_path: str) -> bool:
        """
        Load data from file.
        
        Args:
            file_path: Path to data file
            
        Returns:
            True if load successful
        """
    
    def apply_filter(self, filter_config: Dict[str, Any]) -> None:
        """
        Apply data filter.
        
        Args:
            filter_config: Filter configuration
        """
    
    def export_data(self, output_path: str, format: str) -> bool:
        """
        Export current data.
        
        Args:
            output_path: Output file path
            format: Export format
            
        Returns:
            True if export successful
        """
```

---

## 🧪 **Testing API**

### **Test Framework**

**Location**: `redline/tests/`

**Purpose**: Comprehensive test suite for all components.

#### **Test Structure**

```python
import unittest
from redline.core.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        """Setup test fixtures."""
        self.loader = DataLoader()
    
    def test_load_csv(self):
        """Test CSV file loading."""
        # Test implementation
    
    def test_validate_data(self):
        """Test data validation."""
        # Test implementation
```

#### **Running Tests**

```bash
# Run all tests
python -m pytest redline/tests/

# Run specific test
python -m pytest redline/tests/test_data_loader.py

# Run with coverage
python -m pytest --cov=redline redline/tests/
```

---

## 🔧 **Configuration API**

### **Configuration Management**

**Location**: `redline/utils/config.py`

**Purpose**: Manage application configuration.

#### **Key Methods**

```python
class Config:
    def __init__(self, config_file: str = "data_config.ini"):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file
        """
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value
            
        Returns:
            Configuration value
        """
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
    
    def save(self) -> None:
        """Save configuration to file."""
```

---

## 📚 **Extension Guide**

### **Adding New Data Sources**

1. **Create downloader class** in `redline/downloaders/`
2. **Implement required methods**:
   - `download_ticker()`
   - `get_available_tickers()`
3. **Add to downloader registry** in `redline/downloaders/__init__.py`
4. **Write tests** in `redline/tests/`

### **Adding New File Formats**

1. **Update schema** in `redline/core/schema.py`
2. **Implement format support** in `redline/core/format_converter.py`
3. **Add validation** in `redline/core/data_validator.py`
4. **Update tests** and documentation

### **Adding New GUI Tabs**

1. **Create tab class** inheriting from `BaseTab`
2. **Implement required methods**:
   - `setup_ui()`
   - `refresh_data()`
3. **Add to main application** in `redline/gui/main_window.py`
4. **Write integration tests**

---

## 🚀 **Performance Optimization**

### **Best Practices**

1. **Use efficient data formats** (Parquet, DuckDB)
2. **Implement lazy loading** for large datasets
3. **Use virtual scrolling** for GUI components
4. **Cache frequently accessed data**
5. **Use batch operations** when possible

### **Memory Management**

```python
# Example: Efficient data loading
def load_large_dataset(file_path: str) -> pd.DataFrame:
    """Load large dataset efficiently."""
    # Use chunking for very large files
    chunks = pd.read_csv(file_path, chunksize=10000)
    
    # Process chunks and combine
    data = pd.concat(chunks, ignore_index=True)
    
    # Optimize data types
    data = optimize_dtypes(data)
    
    return data

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame data types for memory efficiency."""
    for col in df.columns:
        if df[col].dtype == 'object':
            # Convert to category if low cardinality
            if df[col].nunique() < len(df) * 0.5:
                df[col] = df[col].astype('category')
    
    return df
```

---

## 📖 **Additional Resources**

- **[User Guide](REDLINE_USER_GUIDE.md)**: Complete user documentation
- **[Quick Start Guide](QUICK_START_GUIDE.md)**: 5-minute setup guide
- **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)**: Common issues and solutions
- **[Software Design](REDLINE_SOFTWARE_DESIGN.md)**: Architecture and design decisions

---

<div align="center">

**Ready to contribute? Check out our [Contributing Guide](CONTRIBUTING.md)**

[![Contributing](https://img.shields.io/badge/Contributing-Welcome-green?style=for-the-badge&logo=github)](CONTRIBUTING.md)

</div>
