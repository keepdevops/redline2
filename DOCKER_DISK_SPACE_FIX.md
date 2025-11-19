# Docker Disk Space Fix

## Problem
Error: `OSError: [Errno 28] No space left on device: '/app/data/users'`

This occurs when Docker containers run out of disk space, even if the host system has space available.

## Quick Fix: Clean Up Docker

### Option 1: Clean Up Unused Docker Resources (Recommended)

```bash
# Remove unused volumes, networks, images, and build cache
docker system prune -a --volumes

# This will free up space but may remove:
# - Unused images
# - Stopped containers
# - Unused volumes (21.58GB reclaimable)
# - Build cache
```

### Option 2: Clean Up Only Volumes (Safest)

```bash
# Remove only unused volumes (21.58GB available)
docker volume prune

# Or remove specific unused volumes
docker volume ls
docker volume rm <volume-name>
```

### Option 3: Clean Up Build Cache

```bash
# Remove build cache (370MB available)
docker builder prune -a
```

## Check Current Disk Usage

```bash
# Check Docker disk usage
docker system df

# Check specific container disk usage
docker ps
docker exec <container-id> df -h
```

## Permanent Solutions

### Solution 1: Use S3/Cloud Storage (Recommended for Production)

Instead of storing data in Docker volumes, use S3/R2 cloud storage:

1. **Add to `.env` or environment variables:**
   ```bash
   USE_S3_STORAGE=true
   S3_BUCKET=your-bucket-name
   S3_ACCESS_KEY=your-access-key
   S3_SECRET_KEY=your-secret-key
   S3_REGION=us-east-1
   # For Cloudflare R2:
   S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
   ```

2. **Restart the container:**
   ```bash
   docker-compose restart
   ```

### Solution 2: Mount Host Directory (For Development)

Mount a host directory instead of using Docker volumes:

1. **Edit `docker-compose.yml`:**
   ```yaml
   services:
     web:
       volumes:
         - ./data:/app/data  # Mount host directory
   ```

2. **Restart:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Solution 3: Increase Docker Disk Space

**macOS (Docker Desktop):**
1. Open Docker Desktop
2. Settings → Resources → Advanced
3. Increase Disk image size (default: 64GB)
4. Apply & Restart

**Linux:**
- Increase Docker root directory space
- Move Docker data directory to larger partition

## Verify Fix

After cleanup, verify:

```bash
# Check available space
docker system df

# Check if container can start
docker-compose up -d

# Check logs
docker-compose logs -f web
```

## Prevention

1. **Use S3 storage** for production (no local disk usage)
2. **Regular cleanup:**
   ```bash
   # Add to cron or run weekly
   docker system prune -f --volumes
   ```
3. **Monitor disk usage:**
   ```bash
   docker system df
   ```
4. **Set up alerts** for disk space in production

## Error Handling

The code now includes better error handling for disk space issues. If space is exhausted, you'll see a clear error message suggesting to:
- Free up disk space
- Configure S3 storage

## Related Files

- `redline/storage/user_storage.py` - Storage initialization with error handling
- `docker-compose.yml` - Docker volume configuration
- `.env` - Environment variables for S3 storage

