# Cloudflare R2 Storage Setup for REDLINE

## Overview

This guide covers setting up Cloudflare R2 (object storage) for REDLINE file storage. R2 is S3-compatible, so it works with existing boto3 code using a custom endpoint URL.

## Why Cloudflare R2?

- ✅ **No Egress Fees**: Free data transfer (unlike AWS S3)
- ✅ **Lower Storage Costs**: $0.015/GB/month (vs S3's $0.023/GB)
- ✅ **S3-Compatible**: Works with existing boto3 code
- ✅ **Integrated with Cloudflare**: Same ecosystem as DNS/CDN
- ✅ **Free Tier**: First 10GB storage free

## Prerequisites

1. **Cloudflare Account**
   - Domain `redfindat.com` registered with Cloudflare
   - Access to Cloudflare Dashboard

2. **R2 Access**
   - R2 is available in Cloudflare Dashboard
   - May require enabling R2 in your account

## Step 1: Create R2 Bucket

### In Cloudflare Dashboard

1. **Navigate to R2**
   - Go to https://dash.cloudflare.com
   - Select your account
   - Click **R2** in left sidebar
   - If not visible, click **"Workers & Pages"** → **R2**

2. **Create Bucket**
   - Click **"Create bucket"**
   - **Bucket name**: `redline-data` (or your preferred name)
   - **Location**: Choose closest region (or default)
   - Click **"Create bucket"**

3. **Verify Bucket Created**
   - Bucket should appear in R2 dashboard
   - Note the bucket name for configuration

## Step 2: Get R2 API Credentials

### Create API Token

1. **Navigate to R2 API Tokens**
   - In R2 dashboard, click **"Manage R2 API Tokens"**
   - Or go to: https://dash.cloudflare.com → R2 → Manage R2 API Tokens

2. **Create API Token**
   - Click **"Create API token"**
   - **Token name**: `redline-storage` (or descriptive name)
   - **Permissions**: 
     - ✅ **Object Read & Write** (for file operations)
   - **TTL**: Leave empty (no expiration) or set expiration date
   - Click **"Create API Token"**

3. **Save Credentials**
   - **Access Key ID**: Copy and save securely
   - **Secret Access Key**: Copy and save securely (shown only once!)
   - **Important**: Save these immediately - secret won't be shown again

### Get R2 Endpoint URL

1. **Find Account ID**
   - Go to Cloudflare Dashboard → Overview
   - Copy your **Account ID**

2. **Construct Endpoint URL**
   ```
   https://<account-id>.r2.cloudflarestorage.com
   ```
   
   Example:
   ```
   https://abc123def456.r2.cloudflarestorage.com
   ```

## Step 3: Configure REDLINE for R2

### Environment Variables

Add these to Render environment variables:

```bash
# Enable S3-compatible storage (R2 uses S3 API)
USE_S3_STORAGE=true

# R2 Bucket Configuration
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY_ID>
S3_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

**Important Notes:**
- Variable names say "S3" but we're using R2
- R2 is S3-compatible, so boto3 works with endpoint URL
- `S3_REGION=auto` (R2 doesn't use regions like AWS)
- `S3_ENDPOINT_URL` is **REQUIRED** for R2

### Code Changes

The code has been updated to support R2 endpoint URLs:

**File**: `redline/storage/user_storage.py`

- Added `S3_ENDPOINT_URL` environment variable support
- Automatically detects R2 vs S3 based on endpoint URL
- Works with existing boto3 code

## Step 4: Test R2 Connection

### Test from Application

1. **Deploy to Render** with R2 environment variables
2. **Upload a test file** via web interface
3. **Check R2 Dashboard** - file should appear in bucket
4. **Download file** - verify it works

### Test with Python (Optional)

```python
import boto3
import os

# R2 Configuration
s3_client = boto3.client(
    's3',
    endpoint_url='https://<account-id>.r2.cloudflarestorage.com',
    aws_access_key_id='<R2_ACCESS_KEY>',
    aws_secret_access_key='<R2_SECRET_KEY>',
    region_name='auto'
)

# Test upload
s3_client.put_object(
    Bucket='redline-data',
    Key='test.txt',
    Body=b'Hello R2!'
)

# Test download
response = s3_client.get_object(Bucket='redline-data', Key='test.txt')
print(response['Body'].read())
```

## R2 vs S3 Configuration Comparison

| Setting | AWS S3 | Cloudflare R2 |
|---------|--------|---------------|
| **Endpoint URL** | Not needed (default) | Required: `https://<account-id>.r2.cloudflarestorage.com` |
| **Region** | `us-east-1`, etc. | `auto` (R2 doesn't use regions) |
| **Access Key** | AWS Access Key ID | R2 Access Key ID |
| **Secret Key** | AWS Secret Access Key | R2 Secret Access Key |
| **Bucket** | S3 bucket name | R2 bucket name |

## Storage Structure in R2

### File Organization

```
redline-data/
└── users/
    └── {hashed_license_key}/
        └── files/
            ├── file1.csv
            ├── file2.parquet
            └── ...
```

### Prefix Pattern

- **User files**: `users/{hash}/files/{filename}`
- **Hash**: First 16 characters of SHA256(license_key)

## Cost Calculation

### R2 Pricing (as of 2024)

- **Storage**: $0.015/GB/month
- **Class A Operations** (writes): $4.50 per million
- **Class B Operations** (reads): $0.36 per million
- **Egress**: **FREE** (unlimited)

### Free Tier

- **10GB storage** free per month
- **1 million Class A operations** free per month
- **10 million Class B operations** free per month

### Cost Example

**Scenario**: 100GB storage, 50GB egress/month

**R2 Costs:**
- Storage: 100GB × $0.015 = $1.50/month
- Egress: $0 (FREE)
- **Total: $1.50/month**

**AWS S3 Costs (for comparison):**
- Storage: 100GB × $0.023 = $2.30/month
- Egress: 50GB × $0.09 = $4.50/month
- **Total: $6.80/month**

**Savings with R2: $5.30/month (78% cheaper)**

## Security Best Practices

### API Token Security

1. **Rotate Regularly**
   - Create new tokens periodically
   - Revoke old tokens

2. **Least Privilege**
   - Only grant necessary permissions
   - Use separate tokens for different purposes

3. **Secure Storage**
   - Store credentials in Render environment variables
   - Never commit to git
   - Use secrets management if available

### Bucket Security

1. **Private by Default**
   - R2 buckets are private by default
   - Files require authentication to access

2. **Public Access** (if needed)
   - Can enable public access for specific files
   - Use Cloudflare CDN for public files

## Monitoring R2 Usage

### Cloudflare Dashboard

1. **View Usage**
   - Go to R2 → Your bucket
   - View storage usage
   - Check operation counts

2. **Set Alerts**
   - Configure usage alerts
   - Monitor costs
   - Set budget limits

### Application Monitoring

1. **Track Storage Usage**
   - Use `get_storage_stats()` per user
   - Monitor total storage across users
   - Alert if approaching limits

## Troubleshooting

### Connection Errors

1. **Check Endpoint URL**
   - Verify endpoint URL is correct
   - Format: `https://<account-id>.r2.cloudflarestorage.com`
   - Ensure account ID is correct

2. **Verify Credentials**
   - Check Access Key ID is correct
   - Verify Secret Access Key matches
   - Ensure token has correct permissions

3. **Check Network**
   - Verify Render can reach R2 endpoint
   - Check firewall rules
   - Test from application logs

### Upload Failures

1. **Check Bucket Name**
   - Verify bucket exists in R2 dashboard
   - Ensure bucket name matches configuration

2. **Check Permissions**
   - Verify API token has write permissions
   - Check bucket access settings

3. **Check File Size**
   - R2 supports large files
   - Check application file size limits

## Migration from S3 to R2

### If Currently Using S3

1. **Create R2 Bucket**
   - Follow Step 1 above

2. **Get R2 Credentials**
   - Follow Step 2 above

3. **Update Environment Variables**
   - Change `S3_ENDPOINT_URL` to R2 endpoint
   - Update `S3_ACCESS_KEY` and `S3_SECRET_KEY`
   - Keep `S3_BUCKET` as R2 bucket name

4. **Migrate Data** (if needed)
   - Use R2 import tool
   - Or copy files via application

5. **Test and Verify**
   - Test file uploads
   - Verify file downloads
   - Check data integrity

## Quick Reference

### R2 Dashboard URLs

- **R2 Overview**: https://dash.cloudflare.com → R2
- **API Tokens**: https://dash.cloudflare.com → R2 → Manage R2 API Tokens
- **Bucket Details**: https://dash.cloudflare.com → R2 → Your bucket

### Environment Variables Template

```bash
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=<R2_ACCESS_KEY_ID>
S3_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

### Test Commands

```bash
# Test R2 connection (Python)
python3 -c "
import boto3
s3 = boto3.client('s3',
    endpoint_url='https://<account-id>.r2.cloudflarestorage.com',
    aws_access_key_id='<KEY>',
    aws_secret_access_key='<SECRET>',
    region_name='auto'
)
print(s3.list_buckets())
"
```

## Next Steps

After R2 is configured:

1. ✅ Test file upload via application
2. ✅ Verify files appear in R2 bucket
3. ✅ Test file download
4. ✅ Monitor storage usage
5. ✅ Set up usage alerts

---

**R2 Bucket**: redline-data  
**Endpoint**: https://<account-id>.r2.cloudflarestorage.com  
**Storage Type**: S3-compatible object storage

