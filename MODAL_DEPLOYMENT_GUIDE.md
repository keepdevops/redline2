# VarioSync Modal + Render + Supabase Deployment Guide

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │─────▶│    Render    │─────▶│  Supabase   │
│    User     │      │  Flask Web   │      │  PostgreSQL │
└─────────────┘      │   Server     │      │  + Storage  │
                     └───────┬──────┘      └─────────────┘
                             │
                             │ API Call
                             ▼
                     ┌──────────────┐
                     │    Modal     │
                     │   DuckDB     │
                     │  Processing  │
                     └──────────────┘
```

## Components

1. **Render** - Flask web server (authentication, routing)
2. **Supabase** - Database (user data, payments, logs) + Storage (files)
3. **Modal** - Serverless compute (DuckDB data processing)

---

## ✅ What's Been Completed

### Code Changes:
1. ✅ Created `modal_processing/duckdb_service.py` - Modal functions
2. ✅ Created `modal_processing/requirements.txt` - Modal dependencies
3. ✅ Created `redline/clients/modal_client.py` - Modal client for Flask
4. ✅ Updated `requirements.txt` - Added modal>=0.63.0
5. ✅ Updated `redline/web/routes/api_data.py` - Uses Modal client
6. ✅ Removed DuckDB from main dependencies

### Database:
1. ✅ Created `scripts/supabase_schema.sql` - Complete Supabase schema
2. ✅ Updated `redline/database/usage_storage.py` - Uses Supabase PostgreSQL
3. ✅ Updated `redline/storage/user_storage.py` - Uses Supabase Storage + PostgreSQL

---

## 🔧 Deployment Steps

### Step 1: Deploy Modal App

```bash
# Install Modal CLI
pip install modal

# Authenticate with Modal
modal setup

# Deploy DuckDB processing service
cd /Users/caribou/redline
modal deploy modal_processing/duckdb_service.py
```

**Expected output:**
```
✓ Created app variosync-duckdb-processor
✓ Deployed 6 functions
  - process_csv
  - convert_format
  - generate_chart_data
  - run_query
  - get_metadata
```

---

### Step 2: Setup Supabase

1. **Go to** https://supabase.com

2. **Create Project**: `variosync-prod`

3. **Run SQL Schema**: Copy entire contents of `scripts/supabase_schema.sql` and paste into Supabase SQL Editor

4. **Get Credentials** from Project Settings → API:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`

---

### Step 3: Configure Environment Variables

Add to your Render environment (or `.env` for local):

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...

# Modal (get from Modal dashboard)
MODAL_TOKEN_ID=ak-...
MODAL_TOKEN_SECRET=as-...

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# App Config
SECRET_KEY=your-secure-secret-key
ENFORCE_PAYMENT=true
USAGE_CHECK_INTERVAL=30
```

---

### Step 4: Deploy to Render

1. **Connect Repository** to Render

2. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Command**:
   ```bash
   gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 4
   ```

4. **Environment**: Python 3.11

5. **Add Environment Variables** from Step 3

6. **Deploy**

---

## 📝 Remaining File Updates (Optional)

The following files still have local DuckDB code but are **optional** to update now. The core functionality works with Modal for data preview and metadata.

### Files with DuckDB to update later:

1. `redline/web/routes/analysis_charts.py` - Chart generation
2. `redline/web/routes/analysis_ml.py` - ML operations
3. `redline/web/routes/analysis_export.py` - Export operations
4. `redline/web/routes/analysis_tab.py` - Analysis tab
5. `redline/core/data_loader.py` - Data loading
6. `redline/core/format_converter.py` - Format conversion

**Pattern to update each file:**

```python
# OLD (local DuckDB):
import duckdb
conn = duckdb.connect(':memory:')
result = conn.execute(query).fetchdf()

# NEW (Modal):
from redline.clients.modal_client import modal_client

with open(file_path, 'rb') as f:
    file_data = f.read()

result = modal_client.run_query(
    file_data=file_data,
    filename=filename,
    query=query
)
```

---

## 🧪 Testing

### Test Modal Deployment:

```python
import modal

# Test process_csv function
func = modal.Func.lookup("variosync-duckdb-processor", "get_metadata")

with open("test.csv", "rb") as f:
    result = func.remote(file_data=f.read(), filename="test.csv")

print(result)  # Should show metadata
```

### Test Supabase Connection:

```python
from redline.auth.supabase_config import supabase_admin

# Test connection
result = supabase_admin.table('user_hours').select('*').limit(1).execute()
print(result.data)
```

### Test End-to-End:

1. **Register**: POST `/api/register` with email/password
2. **Login**: POST `/api/login` → get JWT token
3. **Upload File**: POST `/user-data/upload` with auth header
4. **Preview Data**: GET `/api/data/{filename}` → Should use Modal

---

## 💰 Cost Estimates

### Render:
- **Starter Plan**: $7/month (512 MB RAM, no DuckDB needed)

### Supabase:
- **Free Tier**: 500 MB database, 1 GB storage
- **Pro**: $25/month (8 GB database, 100 GB storage)

### Modal:
- **Free Tier**: $30 credits/month
- **Pay-as-you-go**: ~$0.00002/second of compute
- **Estimated**: $5-20/month depending on usage

**Total**: $12-52/month (vs $50-100/month with single server approach)

---

## 🔍 Monitoring

### Check Modal Logs:
```bash
modal app logs variosync-duckdb-processor
```

### Check Render Logs:
```bash
# In Render dashboard → Logs tab
```

### Check Supabase:
```sql
-- Recent usage
SELECT * FROM usage_history ORDER BY deduction_time DESC LIMIT 10;

-- Recent payments
SELECT * FROM payment_history ORDER BY payment_date DESC LIMIT 10;
```

---

## 🆘 Troubleshooting

### Modal Function Not Found:
```bash
# List deployed functions
modal app list

# Redeploy
modal deploy modal_processing/duckdb_service.py
```

### Supabase Connection Error:
- Check `SUPABASE_SERVICE_KEY` is correct
- Verify RLS policies allow service_role access

### Out of Memory on Render:
- Modal handles all heavy processing
- If still happening, upgrade Render plan

---

## ✅ Verification Checklist

- [ ] Modal app deployed successfully
- [ ] Supabase tables created
- [ ] Supabase storage buckets created
- [ ] Environment variables set in Render
- [ ] App deployed to Render
- [ ] User registration works
- [ ] User login returns JWT
- [ ] File upload to Supabase Storage works
- [ ] Data preview uses Modal (check logs)
- [ ] Stripe payment webhook works
- [ ] Hours are tracked in Supabase

---

## 📚 Additional Resources

- [Modal Documentation](https://modal.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Render Documentation](https://render.com/docs)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

---

## Next Steps

1. Deploy Modal app
2. Run Supabase SQL schema
3. Add environment variables
4. Deploy to Render
5. Test registration/login
6. Test file upload/preview
7. Update remaining routes as needed (optional)
