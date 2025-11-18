# How to Shutdown Render Deployment

## Quick Methods

### Method 1: Suspend Service (Recommended)

**Best for**: Temporarily stopping service, saving costs

1. Go to https://dashboard.render.com
2. Click on your service name
3. Go to **Settings** tab (left sidebar)
4. Scroll to **"Suspend Service"** section
5. Click **"Suspend Service"** button
6. Confirm suspension

**Result:**
- ✅ Service stops immediately
- ✅ No charges while suspended
- ✅ Can restart anytime
- ✅ All data preserved

### Method 2: Delete Service (Permanent)

**Best for**: Completely removing service

1. Go to https://dashboard.render.com
2. Click on your service name
3. Go to **Settings** tab
4. Scroll to bottom → **"Delete Service"** (red section)
5. Click **"Delete Service"** button
6. Type service name to confirm
7. Click **"Delete"**

**Result:**
- ⚠️ Service permanently deleted
- ⚠️ Cannot be undone
- ⚠️ All data removed
- ✅ Billing stops immediately

### Method 3: Quick Suspend (Fastest)

1. Go to https://dashboard.render.com
2. Find your service in the list
3. Click **three dots (⋮)** next to service name
4. Select **"Suspend"**

## Comparison

| Method | Reversible | Data Saved | Charges | Use Case |
|--------|------------|------------|---------|----------|
| **Suspend** | ✅ Yes | ✅ Yes | ❌ No | Temporary stop |
| **Delete** | ❌ No | ❌ No | ❌ No | Permanent removal |

## Restarting After Suspend

1. Go to Render Dashboard
2. Find your suspended service
3. Click **"Resume"** or **"Restart"** button
4. Service will start again (takes 1-2 minutes)

## Important Notes

### Before Suspending/Deleting

- **Backup Data**: If using local storage, data is preserved. If using R2, data is safe.
- **Environment Variables**: Saved with service (not lost on suspend)
- **Custom Domain**: Disconnected on suspend, reconnects on resume

### After Suspending

- Service URL becomes unavailable
- Custom domain stops working
- No charges accrue
- Can resume anytime

### After Deleting

- Service completely removed
- Cannot recover
- Must recreate from scratch if needed
- Environment variables lost

## Troubleshooting

### Can't Find Suspend/Delete Button?

1. Make sure you're the service owner
2. Check you're in **Settings** tab
3. Scroll to bottom of settings page

### Service Won't Suspend?

1. Check if service is already stopped
2. Wait a few minutes and try again
3. Contact Render support if issue persists

### Need to Keep Data?

- **Suspend**: Data is preserved
- **Delete**: Export data first (if using database, export before deleting)

## Cost Savings

**Suspend Service:**
- $0/month while suspended
- Resume anytime
- No data loss

**Delete Service:**
- Immediate cost savings
- No recurring charges
- Must recreate to use again

## Quick Commands (If Using Render CLI)

If you have Render CLI installed:

```bash
# List services
render services list

# Suspend service
render services suspend <service-id>

# Delete service
render services delete <service-id>
```

**Note**: Render CLI requires authentication. Install from: https://render.com/docs/cli

---

**Dashboard**: https://dashboard.render.com  
**Support**: https://render.com/docs/support

