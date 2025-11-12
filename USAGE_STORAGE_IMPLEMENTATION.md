# User Access Data Storage Implementation

## Overview

Added persistent storage for all user access data, usage history, and payment records using DuckDB (same database system already in use for data storage).

## Storage Solution

### Database: DuckDB
- **File**: `data/usage_data.duckdb`
- **Why DuckDB**: Already in use, file-based, fast, SQL-compatible
- **Location**: Stored in `data/` directory (persistent via Docker volumes)

## Database Schema

### 1. `usage_sessions` Table
Tracks active and completed usage sessions:
```sql
- session_id (VARCHAR, PRIMARY KEY)
- license_key (VARCHAR, NOT NULL)
- user_id (VARCHAR)
- start_time (TIMESTAMP, NOT NULL)
- end_time (TIMESTAMP)
- total_hours (DOUBLE)
- total_seconds (DOUBLE)
- api_endpoints (TEXT[])
- status (VARCHAR, DEFAULT 'active')
- created_at (TIMESTAMP)
```

### 2. `usage_history` Table
Detailed log of every hour deduction:
```sql
- id (INTEGER, PRIMARY KEY)
- license_key (VARCHAR, NOT NULL)
- session_id (VARCHAR)
- hours_deducted (DOUBLE, NOT NULL)
- deduction_time (TIMESTAMP, NOT NULL)
- hours_remaining_before (DOUBLE)
- hours_remaining_after (DOUBLE)
- api_endpoint (VARCHAR)
- created_at (TIMESTAMP)
```

### 3. `payment_history` Table
All payment transactions:
```sql
- id (INTEGER, PRIMARY KEY)
- license_key (VARCHAR, NOT NULL)
- stripe_session_id (VARCHAR)
- payment_id (VARCHAR)
- hours_purchased (DOUBLE, NOT NULL)
- amount_paid (DOUBLE, NOT NULL)
- currency (VARCHAR, DEFAULT 'usd')
- payment_status (VARCHAR)
- payment_date (TIMESTAMP, NOT NULL)
- created_at (TIMESTAMP)
```

### 4. `access_logs` Table
Detailed API access tracking:
```sql
- id (INTEGER, PRIMARY KEY)
- license_key (VARCHAR, NOT NULL)
- session_id (VARCHAR)
- endpoint (VARCHAR, NOT NULL)
- method (VARCHAR, NOT NULL)
- ip_address (VARCHAR)
- user_agent (VARCHAR)
- response_status (INTEGER)
- response_time_ms (INTEGER)
- access_time (TIMESTAMP, NOT NULL)
- created_at (TIMESTAMP)
```

## Indexes

All tables have indexes on:
- `license_key` (for fast lookups)
- Time-based columns (for date range queries)

## What Gets Stored

### Automatically Stored:
1. **Session Start/End**: Every usage session
2. **Hour Deductions**: Every time hours are deducted
3. **Payments**: Every Stripe payment (checkout + webhook)
4. **API Access**: Every API request with license key

### Data Retention:
- All data is stored permanently
- Can query historical data
- Supports analytics and reporting

## API Endpoints

### Get Usage History
```bash
GET /payments/history?license_key=RL-XXX&type=all
# Returns: usage_history, payment_history, session_history, stats
```

### Get Balance (with stats)
```bash
GET /payments/balance?license_key=RL-XXX
# Returns: hours_remaining + usage_stats (last 30 days)
```

## Usage Statistics

The system tracks:
- Total API calls per license
- Total hours used
- Most used endpoints
- Payment history
- Session history

## Integration Points

### 1. Usage Tracker
- Logs session start/end
- Logs hour deductions with before/after balances

### 2. Payment Routes
- Logs all payments (checkout + webhook)
- Includes Stripe session IDs and payment IDs

### 3. Web App Middleware
- Logs every API access
- Tracks IP, user agent, response time

## Benefits

1. **Audit Trail**: Complete history of all access
2. **Analytics**: Usage patterns and statistics
3. **Billing Support**: Payment history for accounting
4. **Debugging**: Track down issues with specific sessions
5. **Compliance**: Maintain records for legal/accounting

## Performance

- DuckDB is optimized for analytics queries
- Indexes ensure fast lookups by license key
- File-based storage (no separate database server needed)
- Thread-safe operations with locks

## Data Location

- **Development**: `./data/usage_data.duckdb`
- **Docker**: `/app/data/usage_data.duckdb` (persistent via volume)
- **Backup**: Include in regular backups

## Query Examples

### Get all usage for a license
```python
from redline.database.usage_storage import usage_storage
history = usage_storage.get_usage_history('RL-XXX', limit=100)
```

### Get payment history
```python
payments = usage_storage.get_payment_history('RL-XXX', limit=50)
```

### Get access statistics
```python
stats = usage_storage.get_access_stats('RL-XXX', days=30)
```

## Files Created

- `redline/database/usage_storage.py` - Storage module with all database operations

## Files Modified

- `redline/auth/usage_tracker.py` - Added storage logging
- `redline/web/routes/payments.py` - Added payment logging and history endpoint
- `web_app.py` - Added access logging
- `redline/web/static/js/payments.js` - Added history display

## Next Steps

1. **Backup Strategy**: Include `usage_data.duckdb` in backups
2. **Data Retention Policy**: Consider archiving old data (optional)
3. **Analytics Dashboard**: Build admin dashboard using stored data
4. **Export Features**: Add CSV/JSON export for accounting

