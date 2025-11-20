# Massive.com Rate Limits Guide

## Overview

Yes, **Massive.com has rate limits** that vary by subscription tier. Understanding and properly configuring these limits is crucial for reliable data downloads.

## Rate Limits by Tier

### Free Tier
- **Limit**: 5 requests per minute
- **Delay between requests**: 12 seconds minimum
- **Use case**: Testing, low-volume downloads

### Paid Subscriptions
- **Recommended limit**: Under 100 requests per second
- **Actual limit**: Monitored to ensure fair access
- **Use case**: Production applications, bulk downloads

### Enterprise
- **Limit**: Custom based on agreement
- **Contact**: Massive.com sales for details

## Current REDLINE Implementation

The `MassiveDownloader` uses a **conservative default** of:
- **10 requests per minute** (6 seconds between requests)
- This ensures compatibility with Free Tier while allowing faster downloads on paid plans

### Default Configuration

```python
from redline.downloaders.massive_downloader import MassiveDownloader

downloader = MassiveDownloader(api_key=api_key)
# Default: 6 seconds between requests (10 requests/minute)
```

## Adjusting Rate Limits

### For Free Tier (5 requests/minute)

```python
downloader = MassiveDownloader(api_key=api_key)
downloader.rate_limit_delay = 12.0  # 12 seconds = 5 requests/minute
```

### For Paid Tier (Aggressive)

```python
downloader = MassiveDownloader(api_key=api_key)
downloader.rate_limit_delay = 0.1  # 0.1 seconds = 10 requests/second (600/minute)
# Stay under 100 requests/second to avoid throttling
```

### For Paid Tier (Conservative)

```python
downloader = MassiveDownloader(api_key=api_key)
downloader.rate_limit_delay = 1.0  # 1 second = 60 requests/minute
```

## Automatic Rate Limit Handling

The downloader automatically:

1. **Enforces delays** between requests via `_apply_rate_limit()`
2. **Detects 429 errors** (Too Many Requests)
3. **Implements backoff** - waits 60 seconds and retries once
4. **Logs warnings** when rate limits are hit

### Example Error Handling

```python
# If rate limit is exceeded, the downloader will:
# 1. Log a warning
# 2. Wait 60 seconds
# 3. Retry the request once
# 4. Return empty DataFrame if still failing
```

## Best Practices

### 1. Start Conservative

Begin with the default (10 requests/minute) and increase gradually:

```python
# Start here
downloader.rate_limit_delay = 6.0  # 10/minute

# If no errors, try faster
downloader.rate_limit_delay = 1.0  # 60/minute

# For paid tier, can go faster
downloader.rate_limit_delay = 0.1  # 600/minute (stay under 100/second)
```

### 2. Monitor for 429 Errors

Check logs for rate limit warnings:

```python
import logging
logging.basicConfig(level=logging.WARNING)

# Watch for: "Rate limit exceeded, backing off for 60 seconds"
```

### 3. Batch Downloads

For bulk downloads, use the built-in batch methods:

```python
# Multi-source downloader handles rate limiting automatically
from redline.downloaders.multi_source import MultiSourceDownloader

downloader = MultiSourceDownloader(massive_api_key=api_key)
results = downloader.download_multiple_tickers(tickers, start_date, end_date)
```

### 4. Use Multi-Source Fallback

If you hit rate limits, the multi-source downloader will automatically fall back to other sources:

```python
# Priority: Massive.com → Yahoo → Stooq
# If Massive.com rate limited, falls back to Yahoo
downloader = MultiSourceDownloader(massive_api_key=api_key)
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
```

## Rate Limit Calculation

Calculate delay based on desired requests per minute:

```python
# Formula: delay = 60.0 / requests_per_minute

# 5 requests/minute (Free Tier)
delay = 60.0 / 5  # = 12.0 seconds

# 60 requests/minute
delay = 60.0 / 60  # = 1.0 second

# 600 requests/minute (10/second)
delay = 60.0 / 600  # = 0.1 seconds
```

## Testing Rate Limits

Test your rate limit configuration:

```python
import time
from redline.downloaders.massive_downloader import MassiveDownloader

api_key = "your_key"
downloader = MassiveDownloader(api_key=api_key)

# Test with different delays
for delay in [12.0, 6.0, 1.0, 0.1]:
    downloader.rate_limit_delay = delay
    print(f"Testing {delay}s delay ({60/delay:.1f} requests/minute)...")
    
    start = time.time()
    data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-01-31')
    elapsed = time.time() - start
    
    if not data.empty:
        print(f"  ✅ Success in {elapsed:.2f}s")
    else:
        print(f"  ❌ Failed or rate limited")
```

## Troubleshooting

### Error: "Rate limit exceeded"

**Solution**: Increase `rate_limit_delay`:
```python
downloader.rate_limit_delay = 12.0  # More conservative
```

### Slow Downloads

**Solution**: If you have a paid plan, decrease delay:
```python
downloader.rate_limit_delay = 0.1  # Faster (stay under 100/second)
```

### Inconsistent Behavior

**Solution**: Check your subscription tier and adjust accordingly:
- Free Tier: Use 12 seconds delay
- Paid Tier: Can use 0.1-1.0 seconds delay

## Summary

- **Free Tier**: 5 requests/minute → Use 12 second delay
- **Paid Tier**: < 100 requests/second → Use 0.1-1.0 second delay
- **Default**: 10 requests/minute → 6 second delay (safe for all tiers)
- **Automatic**: Handles 429 errors with 60-second backoff
- **Multi-Source**: Falls back to other sources if rate limited

## References

- [Massive.com Knowledge Base](https://massive.com/knowledge-base/article/what-is-the-request-limit-for-polygons-restful-apis)
- [Massive.com API Documentation](https://massive.com/docs)

