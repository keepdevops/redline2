# Next Steps - Quick Start Guide

## 🎯 What to Do Right Now

### Step 1: Set Up Supabase (15 minutes)

1. **Create Supabase Project**
   ```bash
   # Go to https://supabase.com
   # Create new project
   # Note your project URL and anon key
   ```

2. **Run Database Schema**
   ```bash
   # In Supabase Dashboard:
   # SQL Editor > New Query > Paste database/supabase_schema.sql > Run
   ```

3. **Set Environment Variables**
   ```bash
   # Create .env file (copy from .env.example)
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your-anon-key"
   ```

### Step 2: Test Local Setup (10 minutes)

```bash
# Start all services
make up

# Check health
make health

# View logs
make logs-web
```

### Step 3: Integrate Supabase Client (30 minutes)

**File: `web/__init__.py`**
```python
from redline.database.supabase_client import SupabaseClient

def create_app():
    app = Flask(__name__)
    
    # Initialize Supabase
    try:
        app.supabase = SupabaseClient()
        app.logger.info("Supabase client initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize Supabase: {e}")
        app.supabase = None
    
    # ... rest of setup
```

**Test it:**
```python
# In a route
from flask import current_app

@app.route('/test-supabase')
def test_supabase():
    if current_app.supabase:
        hours = current_app.supabase.get_remaining_hours(user_id)
        return jsonify({'hours': hours})
    return jsonify({'error': 'Supabase not configured'})
```

### Step 4: Add Usage Checking to One Task (30 minutes)

**File: `background/tasks/download_tasks.py`**
```python
from redline.database.supabase_client import get_supabase_client
from datetime import datetime

def process_data_download_impl(user_id, ticker, start_date, end_date, 
                               source='yahoo', options=None, progress_callback=None):
    supabase = get_supabase_client()
    start_time = datetime.utcnow()
    
    # Check hours
    if not supabase.check_usage_hours(user_id, 0.05).has_sufficient_hours:
        raise ValueError("Insufficient hours")
    
    try:
        # Existing download logic
        result = download_data(ticker, start_date, end_date, source)
        
        # Deduct hours
        duration = (datetime.utcnow() - start_time).total_seconds() / 3600
        supabase.deduct_hours(user_id, duration)
        
        # Log usage
        supabase.log_usage(
            user_id=user_id,
            event_type='download',
            duration_hours=duration,
            started_at=start_time,
            success=True,
            metadata={'ticker': ticker, 'source': source}
        )
        
        return result
    except Exception as e:
        # Log failure
        duration = (datetime.utcnow() - start_time).total_seconds() / 3600
        supabase.log_usage(
            user_id=user_id,
            event_type='download',
            duration_hours=duration,
            started_at=start_time,
            success=False,
            metadata={'error': str(e)}
        )
        raise
```

## 📝 Checklist

- [ ] Supabase project created
- [ ] Database schema executed
- [ ] Environment variables set
- [ ] Docker Compose running
- [ ] Supabase client integrated in Flask
- [ ] One route using Supabase
- [ ] One Celery task checking hours
- [ ] Usage logging working

## 🚀 After Basics Work

1. **Stripe Webhook** - Handle payments
2. **Storage Migration** - Move to S3/Wasabi
3. **Modal Integration** - Heavy compute tasks
4. **Full Testing** - End-to-end tests
5. **Production Deploy** - Render.com

## 📖 Detailed Guides

- `ROADMAP.md` - Complete refactoring plan
- `database/README_SUPABASE.md` - Supabase setup
- `DOCKER.md` - Containerization guide

## 🆘 Troubleshooting

**Supabase connection fails:**
- Check `SUPABASE_URL` and `SUPABASE_KEY`
- Verify network connectivity
- Check Supabase project status

**Docker won't start:**
- Check ports aren't in use
- Verify Docker is running
- Check `docker-compose logs`

**Hours not deducting:**
- Check user has subscription record
- Verify RLS policies allow access
- Check Supabase logs

## 💬 Need Help?

- Check existing code examples
- Review Supabase docs
- Test in isolation first
- Use Docker Compose for local testing
