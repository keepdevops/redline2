# Massive.com WebSocket Integration Guide

## WebSocket Feeds

Massive.com provides two WebSocket feeds:

### 1. Delayed Feed (15-minute delay)
- **URL**: `wss://delayed.massive.com/stocks`
- **Delay**: 15 minutes
- **Access**: Available on free tier
- **Use case**: Testing, development, non-time-sensitive applications

### 2. Real-Time Feed
- **URL**: `wss://socket.massive.com`
- **Delay**: Real-time (no delay)
- **Access**: May require paid subscription
- **Use case**: Production applications, live trading

## Testing with wscat

### Test Delayed Feed (15-minute)

```bash
# Connect to delayed feed
wscat -c wss://delayed.massive.com/stocks

# After connecting, send subscription message:
{"action": "subscribe", "tickers": ["AAPL", "MSFT"]}
```

### Test Real-Time Feed

```bash
# Connect to real-time feed (may require authentication)
wscat -c wss://socket.massive.com \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Integration in REDLINE

### Using the WebSocket Client

```python
from redline.downloaders.massive_websocket import MassiveWebSocketClient
import asyncio

# Initialize client (15-minute delayed feed)
client = MassiveWebSocketClient(
    api_key="your_api_key",
    use_delayed=True,  # Use delayed feed
    callback=handle_data  # Optional callback
)

# Connect and subscribe
async def main():
    await client.connect(['AAPL', 'MSFT', 'GOOGL'])

# Run
asyncio.run(main())
```

### Using from Downloader

```python
from redline.downloaders.massive_downloader import MassiveDownloader

downloader = MassiveDownloader(api_key="your_api_key")

# Get WebSocket client
ws_client = downloader.get_websocket_client(use_delayed=True)

# Connect
await ws_client.connect(['AAPL', 'MSFT'])
```

### Callback Example

```python
import pandas as pd

def handle_data(df: pd.DataFrame):
    """Handle incoming WebSocket data."""
    print(f"Received {len(df)} data points")
    print(df.head())
    
    # Process data (save, analyze, etc.)
    # df contains: ticker, price, volume, timestamp, etc.

# Initialize with callback
client = MassiveWebSocketClient(
    api_key="your_api_key",
    use_delayed=True,
    callback=handle_data
)

await client.connect(['AAPL'])
```

## WebSocket Message Format

### Subscribe Message
```json
{
  "action": "subscribe",
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

### Unsubscribe Message
```json
{
  "action": "unsubscribe",
  "tickers": ["AAPL"]
}
```

### Incoming Data Format
```json
{
  "ticker": "AAPL",
  "price": 150.25,
  "volume": 1000000,
  "timestamp": "2024-01-01T10:00:00Z",
  "exchange": "NASDAQ"
}
```

## Authentication

Both feeds require authentication via `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits

- **Delayed Feed**: Generally more lenient rate limits
- **Real-Time Feed**: May have stricter limits based on subscription

## Best Practices

1. **Use Delayed Feed for Testing**: Start with delayed feed to avoid rate limits
2. **Handle Reconnections**: Implement automatic reconnection logic
3. **Error Handling**: Handle connection errors gracefully
4. **Data Validation**: Validate incoming data before processing
5. **Resource Cleanup**: Always disconnect when done

## Example: Complete WebSocket Integration

```python
import asyncio
from redline.downloaders.massive_websocket import MassiveWebSocketClient
import pandas as pd

class DataStreamer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.data_buffer = []
        
    async def handle_data(self, df: pd.DataFrame):
        """Process incoming data."""
        self.data_buffer.append(df)
        print(f"Received data: {df.to_string()}")
        
        # Save to file, update UI, etc.
        
    async def stream(self, tickers: List[str], duration: int = 60):
        """Stream data for specified duration."""
        client = MassiveWebSocketClient(
            api_key=self.api_key,
            use_delayed=True,  # Use 15-minute delayed feed
            callback=self.handle_data
        )
        
        try:
            await client.run(tickers, duration=duration)
        except KeyboardInterrupt:
            print("Streaming stopped by user")
        finally:
            await client.disconnect()
            
        return pd.concat(self.data_buffer, ignore_index=True)

# Usage
streamer = DataStreamer(api_key="your_key")
data = await streamer.stream(['AAPL', 'MSFT'], duration=300)  # 5 minutes
```

## Troubleshooting

### Connection Refused

**Solution**: Check API key and subscription tier
```bash
# Test with wscat first
wscat -c wss://delayed.massive.com/stocks
```

### No Data Received

**Possible causes**:
1. Market is closed
2. Invalid ticker symbols
3. Subscription doesn't include real-time feed

**Solution**: Verify tickers and subscription

### Authentication Errors

**Solution**: Ensure API key is valid and has WebSocket access
```python
# Test API key first with REST API
downloader = MassiveDownloader(api_key="your_key")
data = downloader.download_single_ticker('AAPL')
```

## Next Steps

1. **Test Connection**: Use `wscat` to verify WebSocket access
2. **Integrate Client**: Use `MassiveWebSocketClient` in your code
3. **Handle Data**: Implement callback to process streaming data
4. **Deploy**: Add to REDLINE for real-time data streaming

## Resources

- [Massive.com WebSocket Docs](https://massive.com/docs/websocket)
- [WebSocket Testing with wscat](https://github.com/websockets/wscat)

