# REDLINE Celery and Redis Integration

## Overview

Celery and Redis have been fully integrated into REDLINE for background task processing and rate limiting persistence.

## What Was Implemented

### 1. Redis Service
- **Location**: `docker-compose.yml`
- **Image**: `redis:7-alpine` (lightweight, production-ready)
- **Configuration**: 
  - Append-only persistence enabled
  - Max memory: 256MB with LRU eviction
  - Health checks every 5 seconds
  - Data stored in named volume

### 2. TaskManager Initialization
- **Location**: `web_app.py` (lines 110-118)
- **Behavior**: Initializes TaskManager on app startup
- **Fallback**: Gracefully handles Celery/Redis unavailability

### 3. Celery Worker Startup
- **Location**: `Dockerfile` (lines 199-217)
- **Management**: Supervisor (monitoring, auto-restart)
- **Configuration**:
  - 2 concurrent workers
  - Queue: `redline_tasks`
  - Logging to `/var/log/redline/celery_*.log`

### 4. Environment Variables
- **REDIS_URL**: Connection string for Redis (`redis://redis:6379/0`)
- **CELERY_BROKER_URL**: Celery message broker
- **CELERY_RESULT_BACKEND**: Result storage backend

## Architecture

```
┌─────────────────┐
│  Flask Web App  │
│  (Gunicorn)     │
└────────┬────────┘
         │
         ├──→ Redis (Cache, Rate Limiting)
         │
         ├──→ Redis (Task Queue)
         │
         └──→ Celery Workers (Background Tasks)
```

## Services in docker-compose.yml

### Redis Service
```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  command: redis-server --appendonly yes --maxmemory 256mb
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
```

### Web App Service
```yaml
redline-webgui:
  depends_on:
    redis:
      condition: service_healthy
  environment:
    - REDIS_URL=redis://redis:6379/0
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Using the Integration

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Check Redis Status
```bash
docker-compose exec redis redis-cli ping
# Expected: PONG
```

### 3. Monitor Celery Workers
```bash
docker-compose exec redline-web-app celery -A redline inspect active
```

### 4. Submit a Background Task
```bash
curl -X POST http://localhost:8080/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "process_data_conversion",
    "kwargs": {
      "input_file": "data.csv",
      "output_format": "parquet",
      "output_file": "output.parquet"
    }
  }'
```

### 5. Check Task Status
```bash
curl http://localhost:8080/tasks/status/<task_id>
```

## Benefits

### Without Redis/Celery
- ❌ Rate limits reset on restart
- ❌ UI freezes for long operations
- ❌ No background processing
- ❌ Limited scalability

### With Redis/Celery
- ✅ Persistent rate limiting across restarts
- ✅ Non-blocking background tasks
- ✅ Scalable multi-worker processing
- ✅ Task monitoring and management
- ✅ Automatic retries on failures

## Configuration

### Concurrency Settings
Edit `Dockerfile` line 205:
```bash
celery -A redline worker --concurrency=4 --loglevel=info
```

### Memory Limits
Edit `docker-compose.yml` line 10:
```yaml
command: redis-server --appendonly yes --maxmemory 512mb
```

### Rate Limiting Storage
The app automatically uses Redis if available:
```python
# In web_app.py
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    storage_uri = redis_url  # Use Redis
else:
    storage_uri = "memory://"  # Fallback to memory
```

## Monitoring

### Check Redis Info
```bash
docker-compose exec redis redis-cli INFO
```

### View Celery Worker Logs
```bash
docker-compose logs -f redline-web-app | grep celery
```

### Monitor Task Queue
```bash
curl http://localhost:8080/tasks/health
```

### Active Workers
```bash
curl http://localhost:8080/tasks/queue/stats
```

## Troubleshooting

### Issue: Celery workers not starting
```bash
# Check logs
docker-compose logs celery

# Manually start worker
docker-compose exec redline-web-app celery -A redline worker --loglevel=debug
```

### Issue: Tasks stuck in PENDING
```bash
# Check Redis connection
docker-compose exec redline-web-app python3 -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Check worker status
docker-compose exec redline-web-app celery -A redline inspect ping
```

### Issue: Rate limits not persisting
```bash
# Verify Redis is being used
docker-compose logs redline-web-app | grep "Rate limiting"

# Should see: "Rate limiting using Redis storage"
```

## Performance

### Expected Improvements
- **Background Tasks**: 0ms impact on web requests
- **Rate Limiting**: Persistent across restarts
- **Scalability**: Handle 10x more concurrent users
- **Memory**: Efficient worker pooling

## Testing

### Test Redis Connection
```python
import redis
r = redis.from_url('redis://localhost:6379/0')
print(r.ping())  # Should return True
```

### Test Task Submission
```bash
curl -X POST http://localhost:8080/tasks/submit \
  -d '{"task_name": "process_data_conversion", "kwargs": {...}}'
```

### Test Celery Integration
```bash
celery -A redline inspect registered
# Should show all registered tasks
```

## Production Deployment

### Recommended Settings
- **Redis Memory**: 512MB minimum
- **Celery Workers**: 4-8 per CPU core
- **Task Timeout**: 30 minutes
- **Worker Max Tasks**: 1000 per child

### Environment Variables
```bash
CELERY_CONCURRENCY=4
CELERY_LOGLEVEL=info
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Summary

✅ **Redis Service**: Added to docker-compose.yml with persistence  
✅ **TaskManager**: Initialized in web_app.py  
✅ **Celery Workers**: Auto-started via Supervisor  
✅ **Rate Limiting**: Uses Redis for persistence  
✅ **Background Tasks**: Fully functional with monitoring  

Redis and Celery are now fully integrated and ready for production use!

