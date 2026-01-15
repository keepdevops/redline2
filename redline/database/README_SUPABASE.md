# REDLINE Supabase Database Schema

This directory contains the database schema and utilities for migrating REDLINE from a monolithic local architecture to a scalable cloud-native SaaS using Supabase.

## Files

- **`supabase_schema.sql`** - Complete PostgreSQL schema with tables, RLS policies, functions, and triggers
- **`supabase_models.py`** - Pydantic models matching the database schema for type safety
- **`supabase_client.py`** - Python client wrapper for Supabase operations
- **`migration_utils.py`** - Utilities for migrating data from local DuckDB to Supabase

## Quick Start

### 1. Set Up Supabase Project

1. Create a new project at [supabase.com](https://supabase.com)
2. Get your project URL and anon/service key from Settings > API
3. Set environment variables:
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your-anon-or-service-key"
   ```

### 2. Run Database Migration

Execute the SQL schema in your Supabase SQL editor:

```bash
# Option 1: Via Supabase Dashboard
# Go to SQL Editor > New Query > Paste supabase_schema.sql > Run

# Option 2: Via Supabase CLI
supabase db reset
supabase db push
```

### 3. Install Python Dependencies

```bash
pip install supabase pydantic python-dotenv
```

### 4. Use the Client in Your Code

```python
from redline.database.supabase_client import SupabaseClient
import os

# Initialize client
client = SupabaseClient(
    url=os.getenv('SUPABASE_URL'),
    key=os.getenv('SUPABASE_KEY')
)

# Check user's remaining hours
user_id = "user-uuid-here"
usage_check = client.check_usage_hours(user_id, required_hours=0.1)
if usage_check.has_sufficient_hours:
    # Proceed with operation
    pass

# Deduct hours after operation
result = client.deduct_hours(user_id, hours=0.05)
print(f"Remaining hours: {result.remaining_hours}")
```

## Database Schema Overview

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `profiles` | Extended user info | id, email, display_name |
| `subscription_plans` | Predefined packages | name, hours, price_usd, stripe_price_id |
| `user_subscriptions` | User subscription state | user_id, remaining_hours, status |
| `stripe_customers` | Stripe customer mapping | user_id, stripe_customer_id |
| `stripe_payments` | Payment audit log | user_id, amount_usd, hours_granted |
| `time_series_collections` | Logical groupings | user_id, name, tags |
| `time_series_metadata` | Series metadata | collection_id, series_id, measurement_keys |
| `api_downloader_configs` | Saved API configs | user_id, name, config_json |
| `analysis_configs` | Saved ML configs | user_id, name, config_json |
| `usage_logs` | Usage tracking | user_id, event_type, duration_hours |
| `audit_logs` | Audit trail | user_id, action, entity_type |

### Row Level Security (RLS)

All tables have RLS enabled to ensure:
- Users can only access their own data
- Multi-tenant isolation
- Secure by default

### Helper Functions

- `deduct_hours(user_id, hours)` - Atomically deduct hours (prevents race conditions)
- `add_hours(user_id, hours)` - Add hours to subscription
- `check_usage_hours(user_id, required_hours)` - Check if user has sufficient hours
- `get_remaining_hours(user_id)` - Get user's remaining hours

## Migration from Local DuckDB

```python
from redline.database.migration_utils import MigrationHelper, create_initial_subscription
from redline.database.supabase_client import SupabaseClient

# Initialize
client = SupabaseClient()
helper = MigrationHelper(client, duckdb_path="local_data.duckdb")

# Create initial subscription for user
user_id = "user-uuid"
create_initial_subscription(user_id, client, initial_hours=5.0)

# Migrate configurations
local_configs = {
    'api_downloaders': {
        'yahoo': {...},
        'alpha_vantage': {...}
    }
}
helper.migrate_user_configs(user_id, local_configs)

# Migrate time-series metadata
series_data = [
    {
        'series_id': 'AAPL',
        'measurement_keys': ['open', 'high', 'low', 'close', 'vol'],
        'format': 'yahoo',
        'row_count': 1000
    }
]
helper.migrate_time_series_metadata(user_id, "My Stocks", series_data)
```

## Integration with Stripe Webhooks

```python
from redline.database.supabase_client import SupabaseClient
import stripe

client = SupabaseClient()

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    event = stripe.Webhook.construct_event(
        request.data, request.headers['Stripe-Signature'], 
        os.getenv('STRIPE_WEBHOOK_SECRET')
    )
    
    if event.type == 'invoice.paid':
        invoice = event.data.object
        customer_id = invoice.customer
        
        # Get Supabase user_id from Stripe customer_id
        stripe_customer = client.client.table('stripe_customers')\
            .select('user_id')\
            .eq('stripe_customer_id', customer_id)\
            .single()\
            .execute()
        
        user_id = stripe_customer.data['user_id']
        amount_usd = invoice.amount_paid / 100
        
        # Calculate hours (from payment config: hours_per_dollar = 0.2)
        hours = amount_usd * 0.2
        
        # Add hours to subscription
        client.add_hours(user_id, hours)
        
        # Log payment
        client.client.table('stripe_payments').insert({
            'user_id': user_id,
            'stripe_invoice_id': invoice.id,
            'amount_usd': amount_usd,
            'hours_granted': hours,
            'status': 'succeeded'
        }).execute()
    
    return jsonify(success=True)
```

## Usage Tracking

```python
from datetime import datetime

# Log usage for billing reconciliation
start_time = datetime.utcnow()

# ... perform operation (download, analysis, etc.) ...

duration_hours = (datetime.utcnow() - start_time).total_seconds() / 3600

client.log_usage(
    user_id=user_id,
    event_type='download',
    duration_hours=duration_hours,
    started_at=start_time,
    success=True,
    metadata={
        'ticker': 'AAPL',
        'source': 'yahoo',
        'rows_downloaded': 1000
    }
)
```

## Best Practices

1. **Always check hours before operations**: Use `check_usage_hours()` before expensive operations
2. **Log all usage**: Track every operation for billing reconciliation
3. **Use transactions**: The `deduct_hours()` function is atomic, but wrap related operations in transactions when possible
4. **Handle errors gracefully**: Supabase operations can fail, always have fallbacks
5. **Monitor usage**: Query `usage_logs` regularly to understand usage patterns

## Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key

# Optional (for Stripe integration)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Next Steps

1. **Deploy to Render**: Set up Flask app with Supabase integration
2. **Set up Celery**: For async task processing
3. **Configure Wasabi/S3**: For object storage of Parquet files
4. **Set up Modal**: For compute-intensive tasks
5. **Configure Stripe**: Set up webhooks and payment flows

See the main refactoring guide for complete architecture details.
