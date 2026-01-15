# REDLINE Docker Containerization Guide

This guide covers containerizing REDLINE for scalable deployment using Docker and Docker Compose.

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Make (optional, for convenience commands)

### Local Development

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services:**
   ```bash
   make up
   # Or manually:
   docker-compose up -d
   ```

3. **Access the application:**
   - Web UI: http://localhost:5000
   - Flower (Celery monitoring): http://localhost:5555
   - Redis: localhost:6379
   - PostgreSQL: localhost:5432

4. **View logs:**
   ```bash
   make logs
   # Or for specific service:
   make logs-web
   make logs-celery
   ```

5. **Stop services:**
   ```bash
   make down
   ```

## Docker Images

### Web Application (`Dockerfile`)

Multi-stage build for the Flask web application:
- Base: Python 3.11-slim
- Non-root user: `redline`
- Port: 5000
- Health check included
- Optimized for production

**Build:**
```bash
docker build -t redline-web:latest .
```

**Run:**
```bash
docker run -p 5000:5000 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_KEY=your-key \
  redline-web:latest
```

### Celery Worker (`Dockerfile.celery`)

For async task processing:
- Same base as web
- Non-root user: `celery`
- Configured for Celery workers/beat

**Build:**
```bash
docker build -f Dockerfile.celery -t redline-celery:latest .
```

## Docker Compose Services

### Services Overview

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| `web` | Flask web application | 5000 | `/health` |
| `celery-worker` | Async task processing | - | Celery ping |
| `celery-beat` | Scheduled tasks | - | - |
| `flower` | Celery monitoring UI | 5555 | - |
| `redis` | Celery broker & cache | 6379 | Redis ping |
| `postgres` | Local database (dev only) | 5432 | pg_isready |

### Development Setup

```bash
# Start all services
docker-compose up -d

# Start with logs visible
docker-compose up

# Rebuild after code changes
docker-compose build web
docker-compose up -d web
```

### Production Setup

For production, use the production override:

```bash
# Build production images
make prod-build

# Start in production mode
make prod-up

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Note:** In production, remove the local `postgres` service and use Supabase instead.

## Environment Variables

Key environment variables (see `.env.example`):

### Required
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key
- `SECRET_KEY` - Flask secret key

### Optional
- `REDIS_URL` - Redis connection string
- `CELERY_BROKER_URL` - Celery broker URL
- `STRIPE_SECRET_KEY` - Stripe API key
- `AWS_ACCESS_KEY_ID` - Object storage access key
- `AWS_SECRET_ACCESS_KEY` - Object storage secret key
- `AWS_ENDPOINT_URL` - Object storage endpoint (Wasabi/S3)

## Volume Mounts

Development volumes:
- `./data/uploads` → `/app/data/uploads` - User uploads
- `./data/cache` → `/app/data/cache` - Cache files
- `./logs` → `/app/logs` - Application logs

## Health Checks

All services include health checks:

```bash
# Check all services
make health

# Manual checks
curl http://localhost:5000/health
docker-compose exec redis redis-cli ping
docker-compose exec postgres pg_isready -U redline
```

## Database Initialization

The database schema is automatically initialized when the `postgres` container starts (via `supabase_schema.sql`).

To manually initialize:
```bash
make init-db
```

## Scaling

### Horizontal Scaling (Production)

```yaml
# In docker-compose.prod.yml
services:
  web:
    deploy:
      replicas: 3  # Run 3 web instances
  
  celery-worker:
    deploy:
      replicas: 5  # Run 5 worker instances
```

### Vertical Scaling

Adjust resource limits in `docker-compose.prod.yml`:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Deployment to Render

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: redline-web
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class gevent web:create_app()[0]
       envVars:
         - key: SUPABASE_URL
           sync: false
         - key: SUPABASE_KEY
           sync: false
   ```

2. **Set environment variables in Render dashboard**

3. **Deploy:** Render will build and deploy automatically

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Check container status
docker-compose ps

# Restart service
docker-compose restart web
```

### Database connection issues
```bash
# Verify postgres is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U redline -d redline -c "SELECT 1;"
```

### Redis connection issues
```bash
# Test Redis
docker-compose exec redis redis-cli ping

# Check Celery connection
docker-compose exec celery-worker celery -A background.tasks inspect active
```

### Out of memory
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

## Useful Commands

```bash
# View all Make targets
make help

# Shell into container
make shell
make shell-celery

# Run tests
make test

# Clean everything
make clean

# Rebuild specific service
docker-compose build web
docker-compose up -d web
```

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use secrets management** - In production, use Render/Cloud secrets
3. **Monitor resource usage** - Set appropriate limits
4. **Use health checks** - Monitor service health
5. **Keep images updated** - Regularly update base images
6. **Use multi-stage builds** - Reduce final image size
7. **Run as non-root** - Security best practice
8. **Separate dev/prod configs** - Use compose overrides

## Next Steps

- Set up CI/CD pipeline
- Configure monitoring (Sentry, etc.)
- Set up backup strategies
- Configure auto-scaling
- Set up SSL/TLS certificates
