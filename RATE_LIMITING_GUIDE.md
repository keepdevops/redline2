# REDLINE Rate Limiting Guide

## Overview

Rate limiting has been implemented in REDLINE to protect the API from abuse and ensure fair usage. Rate limits prevent excessive API usage that could degrade performance for all users.

## What Was Implemented

### 1. Global Rate Limiting
- **Location**: `web_app.py`
- **Default Limits**: 200 requests per day, 50 requests per hour per IP
- **Storage**: In-memory (resets on server restart)
- **Headers**: Enabled (shows remaining limits to clients)

### 2. Endpoint-Specific Limits

| Endpoint | Rate Limit | Purpose |
|----------|-----------|---------|
| `/api/upload` | 10 per minute | Prevent excessive file uploads |
| `/api/convert` | 20 per hour | Limit format conversions |
| `/api/download/<ticker>` | 30 per hour | Control data downloads |
| `/data/load` | 30 per minute | Limit data loading operations |
| `/data/filter` | 60 per minute | Allow frequent filtering |

### 3. Graceful Degradation
- If Flask-Limiter is not installed, rate limiting is disabled
- Application continues to work without rate limiting
- Warning message logged if limiter is unavailable

## How It Works

### 1. IP-Based Limiting
- Rate limits are applied per IP address
- Each client has their own rate limit quota
- Limits are independent across different clients

### 2. Time Windows
- **Per day**: Resets at midnight UTC
- **Per hour**: Rolling 1-hour window
- **Per minute**: Rolling 60-second window

### 3. Rate Limit Headers
Every response includes rate limit information:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
```

## Usage Examples

### Example 1: Understanding Rate Limit Headers

When you make a request, check the response headers:

```python
import requests

response = requests.get('http://localhost:8080/api/status')

print(f"Limit: {response.headers.get('X-RateLimit-Limit')}")
print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
print(f"Reset at: {response.headers.get('X-RateLimit-Reset')}")
```

### Example 2: Handling Rate Limit Errors

```python
import requests
import time

def make_request():
    try:
        response = requests.post('http://localhost:8080/api/convert', json={...})
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded. Retry after {retry_after} seconds")
            time.sleep(retry_after)
            return make_request()  # Retry
        else:
            return {'error': 'Request failed'}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
```

### Example 3: Checking Your Rate Limit Status

```python
import requests

def check_rate_limit():
    response = requests.get('http://localhost:8080/api/status')
    
    headers = response.headers
    
    limit = headers.get('X-RateLimit-Limit', 'Unknown')
    remaining = headers.get('X-RateLimit-Remaining', 'Unknown')
    
    print(f"You can make {remaining} more requests")
    print(f"Total limit: {limit} per day")
    
    if int(remaining) < 10:
        print("⚠ Warning: Approaching rate limit!")
```

## Rate Limit Responses

### Success (200 OK)
```json
{
  "status": "running",
  "version": "1.0.0",
  ...
}
```

### Rate Limit Exceeded (429 Too Many Requests)
```json
{
  "error": "Rate limit exceeded: 50 per hour",
  "retry_after": 3600
}
```

## Configuration

### Adjust Rate Limits

Edit `web_app.py` to change global limits:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # ← Change these
    storage_uri="memory://",
    headers_enabled=True
)
```

### Adjust Endpoint Limits

Edit specific endpoints in route files:

```python
# redline/web/routes/api.py
@api_bp.route('/upload', methods=['POST'])
@rate_limit("10 per minute")  # ← Change this
def upload_file():
    ...
```

## Benefits

### 1. Prevents Abuse
- Stops excessive API usage
- Protects server resources
- Ensures fair usage for all users

### 2. Improved Stability
- Prevents server overload
- Reduces memory usage
- Better response times

### 3. Better User Experience
- Predictable performance
- Fair resource allocation
- Clear error messages

## Testing

Run the test script to verify rate limiting:

```bash
python test_rate_limiting.py
```

Expected output:
```
============================================================
REDLINE Rate Limiting Test
============================================================

✓ Connected to server (status: 200)
✓ Rate limit headers detected
✓ Server is handling concurrent requests
✓ All tests passed!
```

## Production Considerations

### 1. Use Redis Storage (Recommended)

For production, use Redis instead of in-memory storage:

```python
from redis import Redis

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379",  # ← Redis storage
    headers_enabled=True
)
```

### 2. Custom Key Functions

For user-based rate limiting:

```python
from flask_limiter.util import get_remote_address

def get_user_identifier():
    """Get user identifier from session or token."""
    if 'user_id' in session:
        return str(session['user_id'])
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_user_identifier,  # ← Custom key function
    ...
)
```

### 3. Whitelisting IPs

```python
from flask_limiter import Limiter

def key_func():
    ip = get_remote_address()
    whitelist = ['127.0.0.1', '10.0.0.1']
    if ip in whitelist:
        return None  # No rate limit
    return ip

limiter = Limiter(app=app, key_func=key_func, ...)
```

## Monitoring

### View Rate Limit Statistics

Check logs for rate limit events:

```bash
tail -f redline_web.log | grep "Rate limit"
```

### Monitor Redis (if using)

```bash
redis-cli
> KEYS *:limiter:*
> GET rate_limit:192.168.1.1:day
```

## Troubleshooting

### Issue: Rate Limits Not Working

1. Check if Flask-Limiter is installed:
```bash
pip list | grep flask-limiter
```

2. Check application logs:
```bash
grep "rate limiting" redline_web.log
```

3. Verify limiter is initialized:
```python
# Check web_app.py for: limiter = Limiter(...)
```

### Issue: Too Restrictive

Adjust limits in route files:

```python
@rate_limit("100 per minute")  # ← Increase limit
def my_endpoint():
    ...
```

### Issue: Headers Not Showing

Check if headers are enabled:

```python
limiter = Limiter(
    ...
    headers_enabled=True  # ← Must be True
)
```

## Best Practices

### 1. Set Reasonable Limits
- Too strict: Frustrates legitimate users
- Too loose: Doesn't prevent abuse
- **Recommended**: Start conservative, adjust based on usage

### 2. Use Appropriate Time Windows
- Frequent operations (filtering): Per minute
- Moderate operations (loading): Per minute
- Heavy operations (conversion): Per hour

### 3. Provide Clear Error Messages
```python
if response.status_code == 429:
    error = response.json()
    print(f"Rate limit exceeded: {error['error']}")
    print(f"Retry after: {error['retry_after']} seconds")
```

## Summary

✅ **Automatic Rate Limiting**: Enabled by default  
✅ **Configurable Limits**: Adjust per endpoint  
✅ **Graceful Degradation**: Works without Flask-Limiter  
✅ **Rate Limit Headers**: Shows remaining quota  
✅ **Production Ready**: Supports Redis for scaling  

Rate limiting is now fully integrated into REDLINE and protects the API from abuse while ensuring fair usage for all users!
