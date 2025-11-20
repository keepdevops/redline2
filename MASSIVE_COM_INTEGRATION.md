# Massive.com API Integration Guide for REDLINE

## Overview

Massive.com provides comprehensive financial market data including stocks, options, indices, currencies, and futures. This guide explains how to integrate Massive.com's API feeds into REDLINE to enhance data capabilities.

## Massive.com API Features

### Data Access Methods
1. **RESTful APIs** - JSON/CSV formats for historical and real-time data
2. **WebSocket APIs** - Real-time streaming data
3. **Flat Files** - CSV downloads via S3-compatible interface
4. **SQL Query Interface** - Direct SQL access to data

### Available Data Types
- Stock aggregates (OHLC)
- Trades and quotes
- Fundamental data
- Options data
- Indices
- Currencies
- Futures
- Dark pool data
- OTC market data

## Integration Approaches

### Approach 1: Generic API Downloader (Quick Setup)

Use REDLINE's existing `GenericAPIDownloader` for rapid integration:

#### Configuration Example

```json
{
  "name": "Massive.com",
  "base_url": "https://api.massive.com/v1",
  "endpoint": "stocks/aggregates",
  "api_key": "YOUR_MASSIVE_API_KEY",
  "api_key_param": "api_key",
  "ticker_param": "ticker",
  "start_date_param": "start_date",
  "end_date_param": "end_date",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "data",
  "column_mapping": {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "date": "date"
  },
  "rate_limit_per_minute": 60,
  "timeout": 30,
  "headers": {
    "Authorization": "Bearer YOUR_MASSIVE_API_KEY"
  }
}
```

#### Usage in REDLINE

1. **Via Web UI:**
   - Go to Settings → API Keys
   - Add custom API configuration
   - Select "Massive.com" as source in Download tab

2. **Via Python API:**
```python
from redline.downloaders.generic_api_downloader import GenericAPIDownloader

# Load configuration
import json
with open('massive_config.json', 'r') as f:
    config = json.load(f)

downloader = GenericAPIDownloader(config)
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
```

### Approach 2: Dedicated Massive.com Downloader (Recommended)

Create a specialized downloader leveraging Massive.com's Python client library:

#### Implementation

```python
#!/usr/bin/env python3
"""
REDLINE Massive.com Downloader
Uses Massive.com Python client library for optimized data access.
"""

import logging
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from .base_downloader import BaseDownloader

try:
    from massive import Client
    MASSIVE_AVAILABLE = True
except ImportError:
    MASSIVE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)

class MassiveDownloader(BaseDownloader):
    """Massive.com data downloader using official Python client."""
    
    def __init__(self, api_key: str, output_dir: str = "data"):
        """Initialize Massive.com downloader."""
        if not MASSIVE_AVAILABLE:
            raise ImportError(
                "Massive.com client library not installed. "
                "Install with: pip install massive-client"
            )
        
        super().__init__("Massive.com", "https://api.massive.com")
        self.output_dir = output_dir
        self.api_key = api_key
        
        # Initialize Massive.com client
        self.client = Client(api_key=api_key)
        
        # Rate limiting (adjust based on your plan)
        self.rate_limit_delay = 1.0  # 1 second between requests
        
    def download_single_ticker(self, ticker: str, start_date: str = None, 
                              end_date: str = None) -> pd.DataFrame:
        """
        Download historical data for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            self._apply_rate_limit()
            
            # Convert dates to datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            # Fetch aggregates (OHLCV data)
            response = self.client.stocks.aggregates(
                ticker=ticker,
                start_date=start_dt,
                end_date=end_dt
            )
            
            if not response or 'data' not in response:
                logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(response['data'])
            
            # Standardize column names
            df = self._standardize_columns(df, ticker)
            
            return self.standardize_data(df, ticker, 'massive')
            
        except Exception as e:
            logger.error(f"Error downloading {ticker} from Massive.com: {str(e)}")
            return pd.DataFrame()
    
    def download_trades(self, ticker: str, start_date: str = None, 
                       end_date: str = None) -> pd.DataFrame:
        """Download trade-level data."""
        try:
            self._apply_rate_limit()
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            response = self.client.stocks.trades(
                ticker=ticker,
                start_date=start_dt,
                end_date=end_dt
            )
            
            if not response or 'data' not in response:
                return pd.DataFrame()
            
            return pd.DataFrame(response['data'])
            
        except Exception as e:
            logger.error(f"Error downloading trades for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def download_quotes(self, ticker: str, start_date: str = None, 
                        end_date: str = None) -> pd.DataFrame:
        """Download quote-level data."""
        try:
            self._apply_rate_limit()
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            response = self.client.stocks.quotes(
                ticker=ticker,
                start_date=start_dt,
                end_date=end_dt
            )
            
            if not response or 'data' not in response:
                return pd.DataFrame()
            
            return pd.DataFrame(response['data'])
            
        except Exception as e:
            logger.error(f"Error downloading quotes for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def download_fundamentals(self, ticker: str) -> pd.DataFrame:
        """Download fundamental data."""
        try:
            self._apply_rate_limit()
            
            response = self.client.stocks.fundamentals(ticker=ticker)
            
            if not response:
                return pd.DataFrame()
            
            # Convert to DataFrame (may need flattening)
            return pd.DataFrame([response])
            
        except Exception as e:
            logger.error(f"Error downloading fundamentals for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _standardize_columns(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Standardize column names to REDLINE format."""
        column_mapping = {
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            't': 'date',
            'timestamp': 'date'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure ticker column
        if 'ticker' not in df.columns:
            df['ticker'] = ticker
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
```

### Approach 3: WebSocket Real-Time Data

For real-time streaming data, integrate Massive.com's WebSocket API:

```python
#!/usr/bin/env python3
"""
REDLINE Massive.com WebSocket Integration
Real-time data streaming from Massive.com.
"""

import asyncio
import websockets
import json
import pandas as pd
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class MassiveWebSocketClient:
    """WebSocket client for Massive.com real-time data."""
    
    def __init__(self, api_key: str, callback: Optional[Callable] = None):
        """Initialize WebSocket client."""
        self.api_key = api_key
        self.callback = callback
        self.ws_url = "wss://api.massive.com/v1/stream"
        self.connected = False
        
    async def connect(self, tickers: list):
        """Connect and subscribe to tickers."""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with websockets.connect(
            self.ws_url,
            extra_headers=headers
        ) as websocket:
            self.connected = True
            
            # Subscribe to tickers
            subscribe_msg = {
                "action": "subscribe",
                "tickers": tickers
            }
            await websocket.send(json.dumps(subscribe_msg))
            
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                await self._handle_message(data)
    
    async def _handle_message(self, data: dict):
        """Handle incoming WebSocket messages."""
        if self.callback:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            await self.callback(df)
        else:
            logger.info(f"Received data: {data}")
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self.connected = False
```

### Approach 4: SQL Query Interface

For advanced queries, use Massive.com's SQL interface:

```python
#!/usr/bin/env python3
"""
REDLINE Massive.com SQL Interface
Direct SQL queries to Massive.com data.
"""

import pandas as pd
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MassiveSQLClient:
    """SQL query interface for Massive.com."""
    
    def __init__(self, api_key: str):
        """Initialize SQL client."""
        self.api_key = api_key
        self.base_url = "https://api.massive.com/v1/sql"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query against Massive.com data.
        
        Example queries:
        - SELECT * FROM stocks WHERE ticker='AAPL' AND date >= '2024-01-01'
        - SELECT ticker, AVG(close) as avg_close FROM stocks GROUP BY ticker
        """
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": sql},
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'data' in result:
                return pd.DataFrame(result['data'])
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"SQL query failed: {str(e)}")
            return pd.DataFrame()
```

## Integration Steps

### Step 1: Install Massive.com Client Library

```bash
pip install massive-client
```

Or add to `requirements.txt`:
```
massive-client>=1.0.0
```

### Step 2: Get API Key

1. Sign up at [massive.com](https://massive.com)
2. Navigate to API Keys section
3. Generate a new API key
4. Store securely in REDLINE's API key management

### Step 3: Configure in REDLINE

#### Option A: Environment Variable
```bash
export MASSIVE_API_KEY="your_api_key_here"
```

#### Option B: REDLINE Settings
- Go to Settings → API Keys
- Add new API key
- Name: "Massive.com"
- Key: `your_api_key_here`
- Source: "massive"

#### Option C: Configuration File
Add to `redline/config/api_keys.json`:
```json
{
  "massive": {
    "api_key": "your_api_key_here",
    "rate_limit_per_minute": 60,
    "timeout": 30
  }
}
```

### Step 4: Add to Multi-Source Downloader

Update `redline/downloaders/multi_source.py`:

```python
from .massive_downloader import MassiveDownloader

class MultiSourceDownloader(BaseDownloader):
    def __init__(self, output_dir: str = "data"):
        super().__init__("Multi-Source", None)
        self.output_dir = output_dir
        
        # Get API key from config
        api_key = self._get_massive_api_key()
        
        # Initialize downloaders
        self.downloaders = {
            'yahoo': YahooDownloader(output_dir),
            'stooq': StooqDownloader(output_dir),
            'massive': MassiveDownloader(api_key, output_dir) if api_key else None
        }
        
        # Update priority (Massive.com first if available)
        self.source_priority = ['massive', 'yahoo', 'stooq']
```

### Step 5: Update Web Routes

Add Massive.com to download routes in `redline/web/routes/download_single.py`:

```python
elif source == 'massive':
    from redline.downloaders.massive_downloader import MassiveDownloader
    api_key = data.get('api_key') or os.environ.get('MASSIVE_API_KEY')
    if not api_key:
        return jsonify({'error': 'Massive.com API key required'}), 400
    downloader = MassiveDownloader(api_key=api_key)
    result = downloader.download_single_ticker(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date
    )
```

## Advanced Features

### Bulk Data Downloads

Massive.com supports bulk downloads via S3-compatible interface:

```python
def download_bulk_data(self, date: str, output_dir: str):
    """Download bulk data files for a specific date."""
    s3_url = f"https://data.massive.com/{date}/stocks.csv"
    
    # Use boto3 or requests to download
    response = requests.get(s3_url, headers={"Authorization": f"Bearer {self.api_key}"})
    
    # Save to file
    filepath = os.path.join(output_dir, f"massive_stocks_{date}.csv")
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    return filepath
```

### Data Caching

Implement caching to reduce API calls:

```python
from functools import lru_cache
import hashlib

class CachedMassiveDownloader(MassiveDownloader):
    """Massive.com downloader with caching."""
    
    @lru_cache(maxsize=1000)
    def download_single_ticker(self, ticker: str, start_date: str = None, 
                               end_date: str = None) -> pd.DataFrame:
        """Download with caching."""
        cache_key = f"{ticker}_{start_date}_{end_date}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Download from API
        data = super().download_single_ticker(ticker, start_date, end_date)
        
        # Cache result
        self._save_to_cache(cache_key, data)
        
        return data
```

## Benefits of Massive.com Integration

1. **Comprehensive Coverage**: All U.S. exchanges, dark pools, OTC markets
2. **Real-Time Data**: WebSocket support for live streaming
3. **Multiple Formats**: REST, WebSocket, SQL, Flat Files
4. **High Quality**: Clean, standardized data
5. **Scalability**: Handle large datasets efficiently
6. **Flexibility**: SQL interface for custom queries

## Rate Limits

Yes, Massive.com has rate limits that vary by subscription tier:

- **Free Tier**: 5 requests/minute (12 seconds between requests)
- **Paid Subscriptions**: Recommended to stay under 100 requests/second to avoid throttling
- **Enterprise**: Custom limits based on agreement

### Current Implementation

The REDLINE downloader uses a conservative default of **10 requests/minute** (6 seconds between requests) to ensure compatibility across all tiers. You can adjust this based on your plan:

```python
# For Free Tier (5 requests/minute)
downloader = MassiveDownloader(api_key=api_key)
downloader.rate_limit_delay = 12.0  # 12 seconds between requests

# For Paid Tier (can be more aggressive)
downloader.rate_limit_delay = 0.1  # 10 requests/second (600/minute)
```

### Automatic Rate Limiting

The downloader automatically:
- Enforces delays between requests via `_apply_rate_limit()`
- Handles rate limit errors (429 status codes)
- Provides backoff on rate limit exceeded errors

## Error Handling

Implement robust error handling:

```python
def download_single_ticker(self, ticker: str, start_date: str = None, 
                          end_date: str = None) -> pd.DataFrame:
    try:
        # API call
        ...
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit exceeded, backing off")
            time.sleep(60)
            return self.download_single_ticker(ticker, start_date, end_date)
        elif e.response.status_code == 401:
            logger.error("Invalid API key")
            raise ValueError("Invalid Massive.com API key")
        else:
            raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return pd.DataFrame()
```

## Testing

Create test script:

```python
#!/usr/bin/env python3
"""Test Massive.com integration."""

from redline.downloaders.massive_downloader import MassiveDownloader
import os

def test_massive_downloader():
    api_key = os.environ.get('MASSIVE_API_KEY')
    if not api_key:
        print("Set MASSIVE_API_KEY environment variable")
        return
    
    downloader = MassiveDownloader(api_key=api_key)
    
    # Test single ticker
    data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
    print(f"Downloaded {len(data)} rows for AAPL")
    print(data.head())
    
    # Test multiple tickers
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    results = downloader.download_multiple_tickers(tickers, '2024-01-01', '2024-12-31')
    print(f"Downloaded {len(results)} tickers")

if __name__ == '__main__':
    test_massive_downloader()
```

## Next Steps

1. **Install client library**: `pip install massive-client`
2. **Get API key**: Sign up at massive.com
3. **Choose integration approach**: Generic or dedicated downloader
4. **Configure in REDLINE**: Add API key to settings
5. **Test integration**: Run test script
6. **Add to multi-source**: Include in fallback chain
7. **Monitor usage**: Track API calls and rate limits

## Resources

- [Massive.com Documentation](https://massive.com/docs)
- [Python Client Library](https://github.com/massive-com/client-python)
- [API Reference](https://massive.com/docs/rest)
- [WebSocket Guide](https://massive.com/docs/websocket)
- [SQL Interface](https://massive.com/docs/sql)

