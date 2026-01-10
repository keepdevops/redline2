# Docker Configuration Updates for JWT Authentication Migration

## Summary

Updated all Docker configuration files to reflect the migration from license_key-based authentication to JWT token-based authentication with Stripe subscriptions.

---

## Files Updated

### 1. `Dockerfile.webgui.bytecode` ✅
**Changes**:
- Updated environment variable comments to reflect JWT authentication requirements
- Added comprehensive documentation for Supabase authentication variables
- Updated Stripe configuration documentation
- Removed any references to license server

**New Required Environment Variables**:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT secret for token validation
- `STRIPE_SECRET_KEY` - Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook signing secret
- `STRIPE_PRICE_ID_METERED` - Stripe metered billing price ID

**Optional Variables**:
- `USE_S3_STORAGE` - Enable S3/R2 storage
- `S3_ENDPOINT_URL` - S3/R2 endpoint URL
- `S3_BUCKET` - S3/R2 bucket name
- `S3_ACCESS_KEY` - S3/R2 access key
- `S3_SECRET_KEY` - S3/R2 secret key
- `S3_REGION` - S3 region (default: us-east-1)

---

### 2. `docker-compose.yml` ✅
**Changes**:
- Added Supabase authentication environment variables
- Updated Stripe configuration variables
- Added `STRIPE_PRICE_ID_METERED` (was missing)
- Added optional S3/R2 storage configuration
- Removed deprecated `HOURS_PER_DOLLAR` and `PAYMENT_CURRENCY` (now handled by Stripe)

**Environment Variables Added**:
```yaml
# Supabase Authentication (JWT) - REQUIRED
- SUPABASE_URL=${SUPABASE_URL:-}
- SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-}
- SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET:-}

# Stripe Subscription Configuration - REQUIRED
- STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}
- STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-}
- STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET:-}
- STRIPE_PRICE_ID_METERED=${STRIPE_PRICE_ID_METERED:-}

# Optional - Cloud Storage (S3/R2)
- USE_S3_STORAGE=${USE_S3_STORAGE:-false}
- S3_ENDPOINT_URL=${S3_ENDPOINT_URL:-}
- S3_BUCKET=${S3_BUCKET:-}
- S3_ACCESS_KEY=${S3_ACCESS_KEY:-}
- S3_SECRET_KEY=${S3_SECRET_KEY:-}
- S3_REGION=${S3_REGION:-us-east-1}
```

---

### 3. `docker.env.template` ✅
**Changes**:
- Added new section for Supabase Authentication configuration
- Added new section for Stripe Subscription configuration
- Added new section for Cloud Storage (S3/R2) configuration
- All variables documented with descriptions

**New Sections**:
1. **Authentication Configuration (JWT with Supabase)**
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `SUPABASE_JWT_SECRET`

2. **Stripe Subscription Configuration**
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_ID_METERED`

3. **Cloud Storage Configuration (Optional - S3/R2)**
   - `USE_S3_STORAGE`
   - `S3_ENDPOINT_URL`
   - `S3_BUCKET`
   - `S3_ACCESS_KEY`
   - `S3_SECRET_KEY`
   - `S3_REGION`

---

### 4. `Dockerfile.license-server` ✅
**Changes**:
- Added deprecation notice at the top
- Documented that this Dockerfile is no longer used
- Noted that VarioSync now uses JWT authentication

**Status**: Deprecated - kept for reference only

---

## Deployment Instructions

### 1. Create Environment File
```bash
cp docker.env.template docker.env
# Edit docker.env with your actual values
```

### 2. Set Required Variables
Ensure all required environment variables are set:
- Supabase credentials (URL, service key, JWT secret)
- Stripe credentials (secret key, publishable key, webhook secret, price ID)

### 3. Build Docker Image
```bash
docker build -f Dockerfile.webgui.bytecode -t keepdevops/variosync1:latest .
```

### 4. Run with Docker Compose
```bash
docker-compose up -d
```

### 5. Verify Deployment
```bash
docker logs variosync-web
# Check for any missing environment variable warnings
```

---

## Environment Variable Checklist

### Required for Production ✅
- [ ] `SUPABASE_URL` - Set to your Supabase project URL
- [ ] `SUPABASE_SERVICE_KEY` - Set to your Supabase service role key
- [ ] `SUPABASE_JWT_SECRET` - Set to your Supabase JWT secret
- [ ] `STRIPE_SECRET_KEY` - Set to your Stripe secret key (live mode)
- [ ] `STRIPE_PUBLISHABLE_KEY` - Set to your Stripe publishable key (live mode)
- [ ] `STRIPE_WEBHOOK_SECRET` - Set to your Stripe webhook signing secret
- [ ] `STRIPE_PRICE_ID_METERED` - Set to your Stripe metered price ID

### Cloud Storage (S3/R2) 📦
**For Cloudflare R2:**
- [ ] `USE_S3_STORAGE` - Set to 'true' (default: true)
- [ ] `S3_ENDPOINT_URL` - Set to `https://<account-id>.r2.cloudflarestorage.com`
- [ ] `S3_BUCKET` - Set to your R2 bucket name
- [ ] `S3_ACCESS_KEY` - Set to your R2 API Token
- [ ] `S3_SECRET_KEY` - Set to your R2 API Secret
- [ ] `S3_REGION` - Set to 'auto' (R2 doesn't use regions)

**For AWS S3:**
- [ ] `USE_S3_STORAGE` - Set to 'true' (default: true)
- [ ] `S3_ENDPOINT_URL` - Leave empty or use standard S3 endpoint
- [ ] `S3_BUCKET` - Set to your S3 bucket name
- [ ] `S3_ACCESS_KEY` - Set to your AWS Access Key ID
- [ ] `S3_SECRET_KEY` - Set to your AWS Secret Access Key
- [ ] `S3_REGION` - Set to your AWS region (e.g., us-east-1)

---

## Verification

### Check Environment Variables
```bash
docker exec variosync-web env | grep -E "SUPABASE|STRIPE|S3"
```

### Check Application Logs
```bash
docker logs variosync-web 2>&1 | grep -i "supabase\|stripe\|jwt\|auth"
```

### Test Authentication
1. Access the web interface at `http://localhost:8080`
2. Try to register a new user
3. Verify JWT token is created
4. Verify Stripe customer is created

---

## Migration Notes

### Removed Variables
- ❌ `LICENSE_SERVER_URL` - No longer needed
- ❌ `REQUIRE_LICENSE_SERVER` - No longer needed
- ❌ `HOURS_PER_DOLLAR` - Now handled by Stripe
- ❌ `PAYMENT_CURRENCY` - Now handled by Stripe

### New Variables
- ✅ `SUPABASE_URL` - Required for authentication
- ✅ `SUPABASE_SERVICE_KEY` - Required for authentication
- ✅ `SUPABASE_JWT_SECRET` - Required for JWT validation
- ✅ `STRIPE_PRICE_ID_METERED` - Required for subscriptions

---

## Troubleshooting

### Missing Environment Variables
If you see errors about missing environment variables:
1. Check `docker.env` file exists and is properly formatted
2. Verify variables are set in `docker-compose.yml`
3. Check container logs: `docker logs variosync-web`

### Authentication Failures
If authentication is not working:
1. Verify `SUPABASE_URL` is correct
2. Verify `SUPABASE_JWT_SECRET` matches Supabase project settings
3. Check Supabase project is active and configured
4. Verify JWT secret is correct in Supabase dashboard

### Stripe Issues
If Stripe integration is not working:
1. Verify all Stripe keys are set (secret, publishable, webhook secret)
2. Verify `STRIPE_PRICE_ID_METERED` is correct
3. Check Stripe webhook endpoint is configured
4. Verify webhook secret matches Stripe dashboard

### Cloud Storage (R2/S3) Issues
If cloud storage is not working:

**For Cloudflare R2:**
1. Verify `S3_ENDPOINT_URL` is set to `https://<account-id>.r2.cloudflarestorage.com`
2. Verify R2 API Token and Secret are correct (from Cloudflare dashboard)
3. Verify bucket name is correct
4. Set `S3_REGION` to 'auto'
5. Check R2 bucket permissions and CORS settings

**For AWS S3:**
1. Verify AWS credentials are correct (Access Key ID and Secret Access Key)
2. Verify bucket name is correct
3. Verify `S3_REGION` matches your bucket region
4. Check S3 bucket permissions and policies
5. Verify IAM user has necessary S3 permissions

---

## Status

✅ **All Docker files updated and ready for production deployment**

**Last Updated**: [Current Date]  
**Migration Status**: Complete
