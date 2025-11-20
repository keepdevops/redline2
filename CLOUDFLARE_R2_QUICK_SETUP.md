# Cloudflare R2 Storage Quick Setup Guide
**Complete guide for setting up R2 storage and API keys**

---

## 🎯 Overview

Cloudflare R2 is S3-compatible object storage with **no egress fees**. Perfect for storing user files in REDLINE.

**Benefits:**
- ✅ **No egress fees** (unlike AWS S3)
- ✅ **S3-compatible API** (works with existing code)
- ✅ **Free tier**: 10GB storage free
- ✅ **Low cost**: $0.015/GB/month after free tier

---

## 📋 Step-by-Step Setup

### Step 1: Create R2 Bucket

1. **Go to Cloudflare Dashboard**
   - https://dash.cloudflare.com
   - Click **"R2"** in left sidebar
   - Or: **Workers & Pages** → **R2**

2. **Create Bucket**
   - Click **"Create bucket"**
   - **Bucket name**: `redline-data` (or your preferred name)
   - **Location**: Choose closest region (or default)
   - Click **"Create bucket"**

3. **Verify Bucket Created**
   - Bucket should appear in R2 dashboard
   - Note the bucket name for later

---

### Step 2: Get R2 API Credentials

1. **Navigate to API Tokens**
   - In R2 dashboard, click **"Manage R2 API Tokens"**
   - Or go to: https://dash.cloudflare.com → R2 → Manage R2 API Tokens

2. **Create API Token**
   - Click **"Create API token"**
   - **Token name**: `redline-storage` (descriptive name)
   - **Permissions**: 
     - ✅ **Object Read & Write** (for file operations)
   - **TTL**: Leave empty (no expiration) or set expiration date
   - Click **"Create API Token"**

3. **Save Credentials** ⚠️ **IMPORTANT**
   - **Access Key ID**: Copy and save securely
   - **Secret Access Key**: Copy and save securely
   - **⚠️ Secret shown only once!** Save immediately
   - Format:
     ```
     Access Key ID:     abc123def456...
     Secret Access Key: xyz789uvw012...
     ```

---

### Step 3: Get R2 Endpoint URL

1. **Find Account ID**
   - Go to Cloudflare Dashboard → Overview (right sidebar)
   - Copy your **Account ID**
   - Format: `abc123def456...` (alphanumeric)

2. **Construct Endpoint URL**
   ```
   https://<account-id>.r2.cloudflarestorage.com
   ```
   
   **Example:**
   ```
   https://abc123def456.r2.cloudflarestorage.com
   ```

3. **Save Endpoint URL**
   - You'll need this for configuration

---

### Step 4: Configure REDLINE for R2

#### For Render (Production)

1. **Go to Render Dashboard**
   - https://dashboard.render.com
   - Select your service
   - Go to **Environment** tab

2. **Add R2 Environment Variables**
   - Click **"Add Environment Variable"**
   - Add each variable:

   ```bash
   USE_S3_STORAGE=true
   S3_BUCKET=redline-data
   S3_ACCESS_KEY=<your-R2-access-key-id>
   S3_SECRET_KEY=<your-R2-secret-access-key>
   S3_REGION=auto
   S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
   ```

3. **Important Notes:**
   - Variable names say "S3" but we're using R2
   - R2 is S3-compatible, so boto3 works with endpoint URL
   - `S3_REGION=auto` (R2 doesn't use regions like AWS)
   - `S3_ENDPOINT_URL` is **REQUIRED** for R2

4. **Save Changes**
   - Render will auto-redeploy
   - Wait for deployment to complete

#### For Local Development (.env file)

```bash
# .env file
USE_S3_STORAGE=true
S3_BUCKET=redline-data
S3_ACCESS_KEY=abc123def456...
S3_SECRET_KEY=xyz789uvw012...
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

---

### Step 5: Test R2 Connection

1. **Deploy to Render** (if not already)
   - Service should redeploy with new environment variables

2. **Test File Upload**
   - Go to REDLINE web interface
   - Upload a test file
   - Check R2 Dashboard → Your bucket
   - File should appear in bucket

3. **Test File Download**
   - Download the file you just uploaded
   - Verify it works correctly

4. **Check Logs**
   - Render Dashboard → Logs
   - Look for R2/S3 connection messages
   - No errors about credentials or connection

---

## 🔑 API Keys Reference

### What You Need

| Item | Description | Example |
|------|-------------|---------|
| **Access Key ID** | R2 API access key | `abc123def456...` |
| **Secret Access Key** | R2 API secret key | `xyz789uvw012...` |
| **Bucket Name** | R2 bucket name | `redline-data` |
| **Account ID** | Cloudflare account ID | `abc123def456...` |
| **Endpoint URL** | R2 endpoint URL | `https://<account-id>.r2.cloudflarestorage.com` |

### Where to Find Them

1. **Access Key ID & Secret Access Key**
   - R2 Dashboard → Manage R2 API Tokens
   - Create new token or view existing
   - **Secret shown only once!**

2. **Bucket Name**
   - R2 Dashboard → Your bucket
   - Name you created (e.g., `redline-data`)

3. **Account ID**
   - Cloudflare Dashboard → Overview (right sidebar)
   - Copy Account ID

4. **Endpoint URL**
   - Format: `https://<account-id>.r2.cloudflarestorage.com`
   - Replace `<account-id>` with your Account ID

---

## 🔐 Security Best Practices

### API Token Security

1. **Rotate Regularly**
   - Create new tokens periodically
   - Revoke old tokens
   - Update environment variables

2. **Least Privilege**
   - Only grant necessary permissions
   - Use separate tokens for different purposes
   - Don't use admin tokens for app access

3. **Secure Storage**
   - Store credentials in Render environment variables
   - Never commit to git
   - Use secrets management if available

4. **Monitor Usage**
   - Check R2 Dashboard for unusual activity
   - Review API token usage
   - Set up alerts if available

---

## 📊 R2 vs S3 Configuration

### Comparison

| Setting | AWS S3 | Cloudflare R2 |
|---------|--------|---------------|
| **Endpoint URL** | Not needed (default) | **Required**: `https://<account-id>.r2.cloudflarestorage.com` |
| **Region** | `us-east-1`, etc. | `auto` (R2 doesn't use regions) |
| **Access Key** | AWS Access Key ID | R2 Access Key ID |
| **Secret Key** | AWS Secret Access Key | R2 Secret Access Key |
| **Bucket** | S3 bucket name | R2 bucket name |
| **Egress Fees** | $0.09/GB | **FREE** ✅ |

### Why R2 is Better

- ✅ **No egress fees** - Save money on data transfer
- ✅ **Lower storage costs** - $0.015/GB vs S3's $0.023/GB
- ✅ **S3-compatible** - Works with existing code
- ✅ **Free tier** - 10GB free storage

---

## 💰 Pricing

### R2 Pricing (as of 2024)

- **Storage**: $0.015/GB/month
- **Class A Operations** (writes): $4.50 per million
- **Class B Operations** (reads): $0.36 per million
- **Egress**: **FREE** (unlimited) ✅

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

---

## 🚨 Troubleshooting

### Issue 1: "Invalid Credentials" Error

**Symptoms:**
- Logs show: "Invalid credentials" or "Access Denied"
- File uploads fail

**Solution:**
1. Verify Access Key ID is correct
2. Verify Secret Access Key matches
3. Check for typos or extra spaces
4. Ensure token has correct permissions (Read & Write)
5. Verify token hasn't expired

### Issue 2: "Endpoint Not Found" Error

**Symptoms:**
- Logs show: "Endpoint not found" or connection errors
- Can't connect to R2

**Solution:**
1. Verify endpoint URL format: `https://<account-id>.r2.cloudflarestorage.com`
2. Check Account ID is correct
3. Ensure no typos in endpoint URL
4. Verify R2 is enabled in your Cloudflare account

### Issue 3: "Bucket Not Found" Error

**Symptoms:**
- Logs show: "Bucket not found"
- Can't access bucket

**Solution:**
1. Verify bucket name matches exactly (case-sensitive)
2. Check bucket exists in R2 Dashboard
3. Verify bucket is in same account
4. Check API token has access to bucket

### Issue 4: Files Not Appearing in Bucket

**Symptoms:**
- Upload seems successful but file not in bucket

**Solution:**
1. Check R2 Dashboard → Your bucket
2. Verify file path/prefix is correct
3. Check logs for upload errors
4. Verify API token has write permissions
5. Check bucket region matches (if specified)

---

## ✅ Setup Checklist

### Pre-Setup
- [ ] Cloudflare account created
- [ ] R2 access enabled (may need to enable in account)

### R2 Setup
- [ ] R2 bucket created (`redline-data`)
- [ ] API token created with Read & Write permissions
- [ ] Access Key ID saved securely
- [ ] Secret Access Key saved securely
- [ ] Account ID obtained
- [ ] Endpoint URL constructed

### Configuration
- [ ] Environment variables added to Render
- [ ] `USE_S3_STORAGE=true` set
- [ ] `S3_BUCKET` set to bucket name
- [ ] `S3_ACCESS_KEY` set to Access Key ID
- [ ] `S3_SECRET_KEY` set to Secret Access Key
- [ ] `S3_REGION=auto` set
- [ ] `S3_ENDPOINT_URL` set to endpoint URL

### Testing
- [ ] Service redeployed successfully
- [ ] Test file upload works
- [ ] Test file download works
- [ ] Files appear in R2 bucket
- [ ] No errors in logs

---

## 📝 Environment Variables Template

### Complete Template

```bash
# Enable R2 Storage
USE_S3_STORAGE=true

# R2 Bucket Configuration
S3_BUCKET=redline-data
S3_ACCESS_KEY=<your-R2-access-key-id>
S3_SECRET_KEY=<your-R2-secret-access-key>
S3_REGION=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

### For Render Dashboard

Add these one by one in Render Dashboard → Environment:

1. `USE_S3_STORAGE` = `true`
2. `S3_BUCKET` = `redline-data`
3. `S3_ACCESS_KEY` = `<your-access-key-id>`
4. `S3_SECRET_KEY` = `<your-secret-access-key>`
5. `S3_REGION` = `auto`
6. `S3_ENDPOINT_URL` = `https://<account-id>.r2.cloudflarestorage.com`

---

## 🔗 Quick Links

- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **R2 Dashboard**: https://dash.cloudflare.com → R2
- **R2 API Tokens**: https://dash.cloudflare.com → R2 → Manage R2 API Tokens
- **Account ID**: Cloudflare Dashboard → Overview (right sidebar)
- **R2 Documentation**: https://developers.cloudflare.com/r2/

---

## 🎯 Quick Start (5 Minutes)

1. **Create R2 Bucket**
   - Cloudflare Dashboard → R2 → Create bucket
   - Name: `redline-data`

2. **Get API Credentials**
   - R2 → Manage R2 API Tokens → Create token
   - Save Access Key ID and Secret Access Key

3. **Get Account ID**
   - Dashboard → Overview → Copy Account ID

4. **Add to Render**
   - Render Dashboard → Environment
   - Add all 6 environment variables

5. **Test**
   - Upload a file
   - Check R2 bucket

**Done!** ✅

---

**Report Generated:** November 19, 2025  
**Version:** 2.1.0
