# REDLINE API Reference

## 🌐 **API Overview**

REDLINE provides a comprehensive RESTful API for all data operations, analysis, and management functions. The API is designed for both programmatic access and web interface integration.

## 📊 **Base URL**

```
http://localhost:8080/api
```

## 🔐 **Authentication**

Currently, REDLINE does not require authentication. Future versions will include user authentication and API key management.

## 📋 **Response Format**

All API responses follow a consistent JSON format:

```json
{
    "success": true,
    "data": {...},
    "error": null,
    "timestamp": "2024-10-21T20:00:00Z"
}
```

## 🏠 **System Endpoints**

### **GET /api/status**
Get system status and configuration.

**Response:**
```json
{
    "status": "running",
    "version": "1.1.0",
    "database": "available",
    "data_loader": "available",
    "supported_formats": ["csv", "parquet", "feather", "json", "duckdb"],
    "timestamp": "2024-10-21T20:00:00Z"
}
```

### **GET /api/health**
Health check endpoint for monitoring.

**Response:**
```json
{
    "status": "healthy",
    "uptime": 3600,
    "memory_usage": "45%",
    "database_connections": 3
}
```

## 📁 **File Management**

### **GET /api/files**
List all available data files.

**Response:**
```json
{
    "files": [
        {
            "name": "sample.csv",
            "size": 1024,
            "modified": 1698000000,
            "format": "csv",
            "path": "data/sample.csv"
        }
    ]
}
```

### **POST /api/upload**
Upload a new data file.

**Request:** `multipart/form-data`
- `file`: File to upload
- `format`: Optional format specification

**Response:**
```json
{
    "success": true,
    "filename": "uploaded_file.csv",
    "size": 2048,
    "format": "csv"
}
```

### **GET /api/data/{filename}**
Get data preview for a specific file.

**Parameters:**
- `filename`: Name of the file
- `limit`: Optional row limit (default: 100)

**Response:**
```json
{
    "filename": "sample.csv",
    "format": "csv",
    "columns": ["date", "open", "high", "low", "close", "volume"],
    "rows": 100,
    "total_rows": 1000,
    "preview": [
        ["2023-01-01", 100.0, 105.0, 95.0, 102.0, 1000],
        ["2023-01-02", 102.0, 108.0, 98.0, 106.0, 1200]
    ]
}
```

### **DELETE /api/files/{filename}**
Delete a data file.

**Response:**
```json
{
    "success": true,
    "message": "File deleted successfully"
}
```

## 📊 **Data Operations**

### **POST /data/load**
Load data from a file.

**Request:**
```json
{
    "filename": "sample.csv",
    "format": "csv",
    "options": {
        "header": true,
        "separator": ",",
        "encoding": "utf-8"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data_id": "data_123",
    "rows": 1000,
    "columns": 6,
    "format": "csv",
    "memory_usage": "2.5MB"
}
```

### **POST /data/load-from-path**
Load data from any file path on the system.

**Request:**
```json
{
    "file_path": "/path/to/file.csv",
    "format": "csv"
}
```

### **GET /data/browse**
Browse file system directories.

**Parameters:**
- `path`: Directory path (default: current directory)

**Response:**
```json
{
    "current_path": "/data",
    "directories": ["downloads", "uploads"],
    "files": [
        {
            "name": "sample.csv",
            "type": "file",
            "size": 1024,
            "modified": 1698000000
        }
    ]
}
```

## 🔬 **Analysis Operations**

### **POST /analysis/analyze**
Run data analysis.

**Request:**
```json
{
    "data_id": "data_123",
    "analysis_type": "financial",
    "options": {
        "include_correlation": true,
        "include_trends": true
    }
}
```

**Analysis Types:**
- `basic`: General statistical analysis
- `financial`: OHLCV financial analysis
- `statistical`: Descriptive statistics
- `correlation`: Correlation matrix
- `trend`: Time series trend analysis
- `volume`: Volume pattern analysis
- `price`: Price movement analysis

**Response:**
```json
{
    "success": true,
    "analysis_id": "analysis_456",
    "analysis_type": "financial",
    "results": {
        "summary": {
            "total_rows": 1000,
            "date_range": "2023-01-01 to 2023-12-31",
            "symbols": ["AAPL", "GOOGL"]
        },
        "statistics": {
            "mean_return": 0.02,
            "volatility": 0.15,
            "sharpe_ratio": 0.13
        },
        "correlation_matrix": {
            "AAPL": {"GOOGL": 0.75},
            "GOOGL": {"AAPL": 0.75}
        }
    }
}
```

### **GET /analysis/history**
Get analysis history.

**Response:**
```json
{
    "analyses": [
        {
            "id": "analysis_456",
            "type": "financial",
            "timestamp": "2024-10-21T20:00:00Z",
            "data_id": "data_123",
            "status": "completed"
        }
    ]
}
```

### **POST /analysis/export**
Export analysis results.

**Request:**
```json
{
    "analysis_id": "analysis_456",
    "format": "json",
    "include_data": false
}
```

## 🔄 **Format Conversion**

### **POST /converter/convert**
Convert data between formats.

**Request:**
```json
{
    "input_format": "csv",
    "output_format": "parquet",
    "input_file": "data/sample.csv",
    "output_file": "data/sample.parquet",
    "options": {
        "compression": "snappy"
    }
}
```

**Response:**
```json
{
    "success": true,
    "conversion_id": "conv_789",
    "input_file": "sample.csv",
    "output_file": "sample.parquet",
    "rows_converted": 1000,
    "processing_time": 0.5
}
```

### **POST /converter/batch**
Convert multiple files in batch.

**Request:**
```json
{
    "files": ["file1.csv", "file2.csv"],
    "output_format": "parquet",
    "options": {
        "parallel": true,
        "max_workers": 4
    }
}
```

### **GET /converter/history**
Get conversion history.

**Response:**
```json
{
    "conversions": [
        {
            "id": "conv_789",
            "input_format": "csv",
            "output_format": "parquet",
            "timestamp": "2024-10-21T20:00:00Z",
            "status": "completed"
        }
    ]
}
```

## 📥 **Data Download**

### **POST /download/stooq**
Download data from Stooq.

**Request:**
```json
{
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "output_format": "csv"
}
```

**Response:**
```json
{
    "success": true,
    "download_id": "dl_123",
    "symbol": "AAPL",
    "rows_downloaded": 252,
    "output_file": "data/AAPL_2023.csv",
    "source": "stooq"
}
```

### **GET /download/sources**
Get available download sources.

**Response:**
```json
{
    "sources": [
        {
            "name": "stooq",
            "description": "Stooq.com financial data",
            "supported_formats": ["csv", "txt"],
            "rate_limit": "unlimited"
        },
        {
            "name": "yahoo",
            "description": "Yahoo Finance data",
            "supported_formats": ["csv"],
            "rate_limit": "2000/hour"
        }
    ]
}
```

## 🎨 **Theme Management**

### **GET /api/themes**
Get available themes.

**Response:**
```json
{
    "themes": [
        {
            "name": "theme-default",
            "display_name": "Default",
            "description": "Clean, professional theme"
        },
        {
            "name": "theme-dark",
            "display_name": "Dark",
            "description": "Dark mode theme"
        }
    ],
    "current_theme": "theme-default"
}
```

### **POST /api/theme**
Set application theme.

**Request:**
```json
{
    "theme": "theme-dark"
}
```

**Response:**
```json
{
    "success": true,
    "theme": "theme-dark",
    "message": "Theme updated successfully"
}
```

## 🔧 **Settings Management**

### **GET /settings**
Get application settings.

**Response:**
```json
{
    "settings": {
        "default_format": "csv",
        "max_file_size": "100MB",
        "auto_save": true,
        "theme": "theme-default",
        "language": "en"
    }
}
```

### **POST /settings**
Update application settings.

**Request:**
```json
{
    "default_format": "parquet",
    "auto_save": false
}
```

## 📊 **Error Handling**

### **Error Response Format**
```json
{
    "success": false,
    "error": "Error message",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "filename",
        "message": "Filename is required"
    }
}
```

### **Common Error Codes**
- `VALIDATION_ERROR`: Input validation failed
- `FILE_NOT_FOUND`: Requested file not found
- `FORMAT_NOT_SUPPORTED`: Unsupported file format
- `ANALYSIS_FAILED`: Analysis operation failed
- `CONVERSION_FAILED`: Format conversion failed
- `DOWNLOAD_FAILED`: Data download failed
- `PERMISSION_DENIED`: Insufficient permissions
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded

## 📈 **Rate Limiting**

Currently, REDLINE does not implement rate limiting. Future versions will include configurable rate limiting for API endpoints.

## 🔍 **Query Parameters**

### **Pagination**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100, max: 1000)

### **Filtering**
- `format`: Filter by file format
- `date_from`: Filter by modification date
- `date_to`: Filter by modification date
- `size_min`: Minimum file size
- `size_max`: Maximum file size

### **Sorting**
- `sort`: Sort field
- `order`: Sort order (`asc` or `desc`)

## 📝 **Examples**

### **Complete Workflow Example**

```python
import requests

# 1. Check system status
response = requests.get('http://localhost:8082/api/status')
print(response.json())

# 2. Upload a file
with open('data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8082/api/upload', files=files)
    print(response.json())

# 3. Load data
data = {
    'filename': 'data.csv',
    'format': 'csv'
}
response = requests.post('http://localhost:8082/data/load', json=data)
data_id = response.json()['data_id']

# 4. Run analysis
analysis = {
    'data_id': data_id,
    'analysis_type': 'financial'
}
response = requests.post('http://localhost:8082/analysis/analyze', json=analysis)
print(response.json())

# 5. Convert format
conversion = {
    'input_format': 'csv',
    'output_format': 'parquet',
    'input_file': 'data.csv',
    'output_file': 'data.parquet'
}
response = requests.post('http://localhost:8082/converter/convert', json=conversion)
print(response.json())
```

## 🚀 **SDK Examples**

### **Python SDK**
```python
from redline_api import RedlineClient

client = RedlineClient('http://localhost:8082')

# Upload and analyze data
file_id = client.upload_file('data.csv')
analysis = client.analyze_data(file_id, 'financial')
results = client.get_analysis_results(analysis['analysis_id'])
```

### **JavaScript SDK**
```javascript
import { RedlineClient } from 'redline-js-sdk';

const client = new RedlineClient('http://localhost:8082');

// Upload and analyze data
const fileId = await client.uploadFile('data.csv');
const analysis = await client.analyzeData(fileId, 'financial');
const results = await client.getAnalysisResults(analysis.analysis_id);
```

## 📚 **Additional Resources**

- **Web Interface**: http://localhost:8082
- **API Documentation**: http://localhost:8082/help
- **Status Page**: http://localhost:8082/status
- **Health Check**: http://localhost:8082/health

## 🔄 **Version History**

- **v1.0.0**: Initial API release
- **v1.1.0** (Current): Added batch operations, background tasks, API key management, dashboard, and enhanced analysis capabilities
- **v1.2.0**: Enhanced analysis capabilities (planned)
- **v1.3.0**: Added theme management (planned)
- **v1.4.0**: Improved error handling (planned)

---

**REDLINE API: Comprehensive, fast, and easy to use.** 🚀
