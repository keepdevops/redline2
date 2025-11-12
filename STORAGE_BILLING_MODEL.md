# Storage Billing Model - Current State & Options

## Current Implementation Status

### ❌ **Storage Billing NOT Implemented**
Currently, **data storage is FREE** for all users. There is no billing, tracking, or limits for storage usage.

### Current Storage Architecture

1. **Local Storage (Default)**
   - **Cost**: FREE to users
   - **Who Pays**: Redline (server disk space costs)
   - **Location**: `data/users/{hashed_license_key}/`
   - **No limits**: Unlimited storage per user

2. **S3 Cloud Storage (Optional)**
   - **Cost**: FREE to users (currently)
   - **Who Pays**: **Redline** (uses Redline's AWS account)
   - **Configuration**: Redline's S3 credentials in environment
   - **No user billing**: Users don't pay Amazon directly

## Current Billing Model

### What Users Pay For:
- ✅ **Access Time (Hours)**: Users purchase hours via Stripe
- ✅ **Usage Tracking**: Hours deducted during API usage
- ❌ **Storage**: NOT charged (completely free)

### What Redline Pays For:
- Server disk space (local storage)
- AWS S3 costs (if S3 enabled)
- Infrastructure costs

## Storage Billing Options

### Option 1: Redline Charges Users (Recommended)
**Model**: Redline bills users for storage, Redline pays AWS

**How it works**:
- Redline tracks storage usage per user
- Redline charges users monthly via Stripe
- Redline pays AWS S3 costs
- Redline keeps the margin

**Pros**:
- ✅ Redline controls pricing
- ✅ Single billing relationship
- ✅ Can bundle with access hours
- ✅ Redline keeps profit margin

**Cons**:
- ❌ Redline responsible for AWS costs
- ❌ Need to track usage accurately

**Implementation**:
```python
# Track storage usage
storage_gb = user_storage.get_storage_stats(license_key)['total_size_mb'] / 1024

# Calculate cost (e.g., $0.10/GB/month)
monthly_cost = storage_gb * 0.10

# Charge via Stripe subscription
```

### Option 2: Users Pay Amazon Directly
**Model**: Users provide their own S3 credentials

**How it works**:
- Users provide their own AWS credentials
- Files stored in user's S3 bucket
- Users pay Amazon directly
- Redline doesn't handle storage billing

**Pros**:
- ✅ No storage costs for Redline
- ✅ Users control their own data
- ✅ Users get AWS pricing directly

**Cons**:
- ❌ More complex setup for users
- ❌ Users need AWS accounts
- ❌ Less control for Redline

**Implementation**:
```python
# User provides S3 credentials
user_s3_config = {
    'bucket': user_provided_bucket,
    'access_key': user_provided_key,
    'secret_key': user_provided_secret
}

# Store in user's bucket
user_storage.save_file(..., s3_config=user_s3_config)
```

### Option 3: Hybrid Model
**Model**: Free tier + paid storage

**How it works**:
- Free tier: 1 GB included
- Paid tier: Additional storage billed by Redline
- Users can also use their own S3

**Pros**:
- ✅ Flexible for users
- ✅ Redline can monetize storage
- ✅ Users can bring their own storage

**Cons**:
- ❌ More complex to implement
- ❌ Need to track free tier usage

## Recommended Implementation

### Phase 1: Add Storage Tracking (Current)
✅ **DONE**: Storage usage tracking implemented
- `get_storage_stats()` tracks usage per user
- No billing yet

### Phase 2: Add Storage Limits
**TODO**: Implement storage limits per license tier
```python
STORAGE_LIMITS = {
    'free': 1_000_000_000,  # 1 GB
    'standard': 10_000_000_000,  # 10 GB
    'professional': 100_000_000_000,  # 100 GB
    'enterprise': -1  # Unlimited
}
```

### Phase 3: Add Storage Billing
**TODO**: Charge users for storage via Stripe
```python
# Monthly storage billing
storage_gb = usage_mb / 1024
cost_per_gb = 0.10  # $0.10/GB/month
monthly_charge = storage_gb * cost_per_gb

# Create Stripe subscription item
stripe.SubscriptionItem.create(
    subscription=subscription_id,
    price=storage_price_id,
    quantity=int(storage_gb)
)
```

## Cost Breakdown

### AWS S3 Costs (What Redline Would Pay)
- **Storage**: ~$0.023/GB/month (Standard)
- **Requests**: ~$0.005/1000 requests
- **Data Transfer**: ~$0.09/GB (outbound)

### Recommended Pricing (What Redline Charges)
- **Free Tier**: 1 GB included
- **Standard**: $0.10/GB/month (4x markup)
- **Professional**: $0.08/GB/month (bulk discount)
- **Enterprise**: Custom pricing

### Profit Margin
- **Cost**: ~$0.023/GB/month (AWS)
- **Charge**: ~$0.10/GB/month (users)
- **Margin**: ~$0.077/GB/month (77% margin)

## Implementation Priority

### High Priority (Do First)
1. ✅ Storage usage tracking (DONE)
2. ⏳ Storage limits per license tier
3. ⏳ Storage billing integration

### Medium Priority
4. ⏳ Storage usage alerts
5. ⏳ Storage cleanup policies
6. ⏳ Storage analytics dashboard

### Low Priority
7. ⏳ User-provided S3 credentials
8. ⏳ Storage migration tools
9. ⏳ Storage tier management

## Current Answer to User's Question

**Q: Is user being charged for data storage by redline or amazon directly or by a third party?**

**A: Currently, NO ONE charges users for storage.**
- ❌ Redline does NOT charge for storage
- ❌ Amazon does NOT charge users (Redline's account)
- ❌ No third party charges for storage
- ✅ Storage is completely FREE

**Future**: Redline will charge users for storage (Option 1 recommended), and Redline will pay AWS costs.

## Next Steps

1. **Decide on billing model** (Option 1 recommended)
2. **Implement storage limits** per license tier
3. **Add Stripe billing** for storage usage
4. **Add storage alerts** when approaching limits
5. **Add storage dashboard** for users to see usage

