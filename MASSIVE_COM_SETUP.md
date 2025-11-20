# Massive.com Integration Setup Guide

## Quick Start

This guide will help you set up Massive.com API integration in REDLINE using all three integration approaches.

## Prerequisites

1. **Massive.com Account**: Sign up at [massive.com](https://massive.com)
2. **API Key**: Get your API key from the Massive.com dashboard
3. **Python Client (Optional)**: For dedicated downloader approach
   ```bash
   pip install massive-client
   ```

## Integration Approaches

### Option 1: Generic API Downloader (Quick Setup)

Use REDLINE's existing `GenericAPIDownloader` - no code changes needed!

#### Step 1: Create Configuration File

Copy the example configuration:
```bash
cp config/massive_com_config.json config/custom_apis.json
```

#### Step 2: Update API Key

Edit `config/custom_apis.json` and replace `YOUR_MASSive_API_KEY_HERE` with your actual API key.

#### Step 3: Use in REDLINE

1. Go to **Download** tab in REDLINE web UI
2. Select **Custom API** as source
3. Choose **Massive.com** from the dropdown
4. Enter ticker and date range
5. Click **Download**

### Option 2: Dedicated Massive.com Downloader

A specialized downloader is already implemented in `redline/downloaders/massive_downloader.py`.

#### Step 1: Set Environment Variable

```bash
export MASSIVE_API_KEY="your_api_key_here"
```

Or add to `.env` file:
```
MASSIVE_API_KEY=your_api_key_here
```

#### Step 2: Use in REDLINE

1. Go to **Download** tab
2. Select **Massive.com** as source
3. Enter ticker and date range
4. Click **Download**

#### Step 3: Use in Python Code

```python
from redline.downloaders.massive_downloader import MassiveDownloader
import os

# Initialize downloader
api_key = os.environ.get('MASSIVE_API_KEY')
downloader = MassiveDownloader(api_key=api_key)

# Download data
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
print(data.head())

# Download trades
trades = downloader.download_trades('AAPL', '2024-01-01', '2024-12-31')

# Download quotes
quotes = downloader.download_quotes('AAPL', '2024-01-01', '2024-12-31')

# Download fundamentals
fundamentals = downloader.download_fundamentals('AAPL')

# SQL queries
sql = "SELECT * FROM stocks WHERE ticker='AAPL' AND date >= '2024-01-01'"
results = downloader.query_sql(sql)
```

### Option 3: Multi-Source Integration

Massive.com is automatically integrated into the multi-source downloader with fallback.

#### Step 1: Set Environment Variable

```bash
export MASSIVE_API_KEY="your_api_key_here"
```

#### Step 2: Use Multi-Source Downloader

```python
from redline.downloaders.multi_source import MultiSourceDownloader
import os

# Initialize with Massive.com API key
api_key = os.environ.get('MASSIVE_API_KEY')
downloader = MultiSourceDownloader(massive_api_key=api_key)

# Download with automatic fallback
# Priority: Massive.com → Yahoo → Stooq
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')

# Check which source was used
print(f"Data source: {data['data_source'].iloc[0] if 'data_source' in data.columns else 'unknown'}")

# Get source statistics
stats = downloader.get_source_statistics()
print(f"Source stats: {stats}")

# Get success rates
success_rates = downloader.get_source_success_rates()
print(f"Success rates: {success_rates}")

# Get recommended source
recommended = downloader.recommend_source()
print(f"Recommended source: {recommended}")
```

#### Step 3: Use in Web UI

The multi-source downloader is used automatically when you select "Auto" or "Multi-Source" as the download source.

## Configuration Options

### Rate Limiting

Massive.com rate limits vary by plan:
- **Free Tier**: 60 requests/minute
- **Professional**: 300 requests/minute
- **Enterprise**: Custom limits

The downloader automatically handles rate limiting. You can adjust the delay:

```python
downloader = MassiveDownloader(api_key=api_key)
downloader.rate_limit_delay = 0.5  # 2 requests/second (120/minute)
```

### Client Library vs REST API

The downloader automatically uses the official Python client library if available, otherwise falls back to REST API:

```python
# Force REST API (no client library needed)
downloader = MassiveDownloader(api_key=api_key, use_client_library=False)
```

## Testing

### Test Single Download

```python
from redline.downloaders.massive_downloader import MassiveDownloader
import os

api_key = os.environ.get('MASSIVE_API_KEY')
if not api_key:
    print("Set MASSIVE_API_KEY environment variable")
    exit(1)

downloader = MassiveDownloader(api_key=api_key)

# Test download
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
print(f"Downloaded {len(data)} rows")
print(data.head())
```

### Test Multi-Source

```python
from redline.downloaders.multi_source import MultiSourceDownloader
import os

api_key = os.environ.get('MASSIVE_API_KEY')
downloader = MultiSourceDownloader(massive_api_key=api_key)

# Test with fallback
tickers = ['AAPL', 'MSFT', 'GOOGL']
results = downloader.download_multiple_tickers(tickers, '2024-01-01', '2024-12-31')

for ticker, data in results.items():
    source = data['data_source'].iloc[0] if 'data_source' in data.columns else 'unknown'
    print(f"{ticker}: {len(data)} rows from {source}")
```

## Troubleshooting

### Error: "Massive.com API key is required"

**Solution**: Set the `MASSIVE_API_KEY` environment variable or provide it in the request.

### Error: "Massive.com client library not available"

**Solution**: Install the client library (optional):
```bash
pip install massive-client
```

Or use REST API mode:
```python
downloader = MassiveDownloader(api_key=api_key, use_client_library=False)
```

### Error: "Rate limit exceeded"

**Solution**: The downloader automatically handles rate limiting. If you're still hitting limits:
1. Check your Massive.com plan limits
2. Increase `rate_limit_delay` in the downloader
3. Use batch downloads with delays between requests

### No Data Returned

**Possible causes**:
1. Invalid ticker symbol
2. Date range outside available data
3. API key doesn't have access to requested data

**Solution**: Check the logs for detailed error messages.

## Advanced Features

### SQL Queries

Execute custom SQL queries against Massive.com data:

```python
downloader = MassiveDownloader(api_key=api_key)

# Example: Get average close price by ticker
sql = """
SELECT ticker, AVG(close) as avg_close, COUNT(*) as days
FROM stocks
WHERE date >= '2024-01-01' AND date <= '2024-12-31'
GROUP BY ticker
ORDER BY avg_close DESC
LIMIT 10
"""
results = downloader.query_sql(sql)
print(results)
```

### Custom Data Types

Download different data types:

```python
# Trades
trades = downloader.download_trades('AAPL', '2024-01-01', '2024-12-31')

# Quotes
quotes = downloader.download_quotes('AAPL', '2024-01-01', '2024-12-31')

# Fundamentals
fundamentals = downloader.download_fundamentals('AAPL')
```

## Next Steps

1. **Get API Key**: Sign up at [massive.com](https://massive.com)
2. **Choose Approach**: Generic API (quick) or Dedicated Downloader (recommended)
3. **Set Environment Variable**: `export MASSIVE_API_KEY="your_key"`
4. **Test Integration**: Run test scripts
5. **Use in Production**: Integrate into your workflows

## Resources

- [Massive.com Documentation](https://massive.com/docs)
- [Python Client Library](https://github.com/massive-com/client-python)
- [API Reference](https://massive.com/docs/rest)
- [Integration Guide](../MASSIVE_COM_INTEGRATION.md)

