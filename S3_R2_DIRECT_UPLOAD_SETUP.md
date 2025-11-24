# S3/R2 Direct Upload Setup for Subscription Service

## Overview

This setup enables direct file uploads to S3 (AWS) or R2 (Cloudflare) storage, bypassing container storage and M3 Apple Silicon security restrictions. Perfect for subscription-based services.

## Benefits

- ✅ **Bypasses M3 Security**: No container file upload restrictions
- ✅ **Scalable**: Unlimited storage capacity
- ✅ **Cost-Effective**: Pay only for what you use
- ✅ **Fast**: Direct browser uploads via presigned URLs
- ✅ **Reliable**: S3/R2's 99.999999999% durability

## Setup Steps

### 1. Choose Storage Provider

**Option A: Cloudflare R2 (Recommended)**
- Free egress (no bandwidth charges)
- S3-compatible API
- Lower cost than AWS S3
- Perfect for subscription services

**Option B: AWS S3**
- Industry standard
- Global availability
- More expensive for high bandwidth

### 2. Create Bucket

#### Cloudflare R2:
1. Go to Cloudflare Dashboard → R2
2. Click "Create bucket"
3. Name: `redline-data` (or your choice)
4. Note your Account ID

#### AWS S3:
1. Go to AWS Console → S3
2. Create bucket
3. Name: `redline-data` (or your choice)
4. Choose region (e.g., `us-east-1`)

### 3. Get API Credentials

#### Cloudflare R2:
1. Go to R2 → Manage R2 API Tokens
2. Create API Token
3. Permissions: Object Read & Write
4. Save:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL: `https://<account-id>.r2.cloudflarestorage.com`

#### AWS S3:
1. Go to IAM → Users → Create User
2. Attach policy: `AmazonS3FullAccess` (or custom)
3. Create Access Key
4. Save:
   - Access Key ID
   - Secret Access Key
   - Region (e.g., `us-east-1`)

### 4. Configure Environment Variables

Add to `.env` or your deployment environment:

```bash
# Enable S3/R2 storage
USE_S3_STORAGE=true

# Bucket configuration
S3_BUCKET=redline-data

# Credentials
S3_ACCESS_KEY=<your-access-key-id>
S3_SECRET_KEY=<your-secret-access-key>

# Region (use 'auto' for R2, or specific region for S3)
S3_REGION=auto

# Endpoint URL (REQUIRED for R2, optional for S3)
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

### 5. Restart Container

```bash
docker-compose -f docker-compose-dev.yml restart
```

## API Endpoints

### Check Configuration
```bash
GET /s3-upload/check-config
```

Response:
```json
{
  "s3_available": true,
  "use_s3_storage": true,
  "has_credentials": true,
  "bucket_configured": true,
  "storage_type": "R2",
  "connection_test": "success"
}
```

### Get Presigned URL (Direct Browser Upload)
```bash
POST /s3-upload/presigned-url
Content-Type: application/json

{
  "filename": "data.csv",
  "file_type": "csv",
  "license_key": "RL-XXX"
}
```

Response:
```json
{
  "success": true,
  "presigned_url": "https://...",
  "s3_key": "users/abc123/files/data.csv",
  "bucket": "redline-data",
  "expires_in": 3600,
  "upload_url": "https://...",
  "method": "PUT"
}
```

### Direct Upload (Server-Side)
```bash
POST /s3-upload/direct-upload
Content-Type: multipart/form-data
X-License-Key: RL-XXX

file: <file data>
```

Response:
```json
{
  "success": true,
  "message": "File uploaded to S3/R2 successfully",
  "filename": "data.csv",
  "s3_key": "users/abc123/files/data.csv",
  "file_url": "https://...",
  "size": 1024
}
```

### Standard Upload (Auto-Detects S3/R2)
```bash
POST /data/load-multiple/upload
Content-Type: multipart/form-data
X-License-Key: RL-XXX

file: <file data>
```

If S3/R2 is configured, uploads directly to cloud storage.
Otherwise, falls back to local container storage.

## Frontend Integration

### Using Presigned URLs (Recommended)

```javascript
// 1. Get presigned URL
const response = await fetch('/s3-upload/presigned-url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-License-Key': licenseKey
  },
  body: JSON.stringify({
    filename: file.name,
    file_type: 'csv'
  })
});

const { presigned_url } = await response.json();

// 2. Upload directly to S3/R2
await fetch(presigned_url, {
  method: 'PUT',
  body: file,
  headers: {
    'Content-Type': file.type
  }
});

// 3. File is now in S3/R2!
```

### Using Direct Upload

```javascript
const formData = new FormData();
formData.append('file', file);

const response = await fetch('/s3-upload/direct-upload', {
  method: 'POST',
  headers: {
    'X-License-Key': licenseKey
  },
  body: formData
});

const result = await response.json();
// File uploaded to S3/R2
```

## File Organization

Files are organized by user (license key):

```
bucket/
└── users/
    ├── {hash1}/          # User 1
    │   └── files/
    │       ├── file1.csv
    │       └── file2.json
    └── {hash2}/          # User 2
        └── files/
            └── file1.parquet
```

## Security

- ✅ License keys are hashed before use in paths
- ✅ Users can only access their own files
- ✅ Presigned URLs expire after 1 hour
- ✅ All uploads require valid license key

## Cost Estimation

### Cloudflare R2:
- Storage: $0.015/GB/month
- Egress: FREE (unlimited)
- Operations: $4.50 per million Class A operations

### AWS S3:
- Storage: $0.023/GB/month (Standard)
- Egress: $0.09/GB (first 10TB)
- Operations: $0.005 per 1,000 PUT requests

**For 1000 users with 1GB each:**
- R2: ~$15/month
- S3: ~$23/month + egress costs

## Troubleshooting

### "S3/R2 not configured"
- Check `USE_S3_STORAGE=true` is set
- Verify `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` are set
- For R2, ensure `S3_ENDPOINT_URL` is set

### "Connection test failed"
- Verify credentials are correct
- Check bucket name matches
- For R2, verify endpoint URL format: `https://<account-id>.r2.cloudflarestorage.com`

### "Upload failed"
- Check bucket permissions
- Verify API token has Object Read & Write permissions
- Check file size limits (default: 100MB)

## Migration from Local Storage

If you have existing files in local storage:

1. Enable S3/R2 storage
2. Files will upload to cloud automatically
3. Old local files remain (can be deleted after verification)
4. New uploads go directly to S3/R2

## Next Steps

1. ✅ Set up S3/R2 bucket
2. ✅ Configure environment variables
3. ✅ Test upload with `/s3-upload/check-config`
4. ✅ Update frontend to use presigned URLs
5. ✅ Monitor storage usage and costs

## Support

- R2 Setup: See `CLOUDFLARE_R2_SETUP.md`
- S3 Setup: See AWS S3 documentation
- API Reference: See endpoint documentation above

