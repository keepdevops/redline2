# REDLINE Refactoring Roadmap

## ✅ Completed

1. **JSON Template Refactoring**
   - ✅ Generalized from OHLCV to all time-series data
   - ✅ Updated schema to support arbitrary measurements
   - ✅ Maintained backward compatibility

2. **Supabase Database Schema**
   - ✅ Complete PostgreSQL schema with RLS
   - ✅ Pydantic models for type safety
   - ✅ Python client wrapper
   - ✅ Migration utilities

3. **Docker Containerization**
   - ✅ Multi-stage Dockerfiles
   - ✅ Docker Compose for development
   - ✅ Production configurations
   - ✅ Health checks and monitoring

## 🚀 Next Steps (Priority Order)

### Phase 1: Core Integration (Week 1-2)

#### 1.1 Integrate Supabase Client into Flask Routes
**Priority: HIGH** | **Effort: Medium**

- [ ] Update Flask app initialization to use Supabase client
- [ ] Add authentication middleware using Supabase Auth
- [ ] Replace local config storage with Supabase tables
- [ ] Update user profile routes to use Supabase
- [ ] Add usage hour checking before operations

**Files to modify:**
- `web/__init__.py` - Initialize Supabase client
- `web/routes/main_auth.py` - Supabase Auth integration
- `web/routes/settings_*.py` - Use Supabase for configs
- Create `web/middleware/auth.py` - Auth middleware

**Example:**
```python
from redline.database.supabase_client import SupabaseClient

def create_app():
    app = Flask(__name__)
    app.supabase = SupabaseClient()
    # ... rest of setup
```

#### 1.2 Update Celery Tasks for Supabase
**Priority: HIGH** | **Effort: Medium**

- [ ] Add usage hour deduction to all Celery tasks
- [ ] Log usage to `usage_logs` table
- [ ] Check hours before task execution
- [ ] Update task implementations to use Supabase

**Files to modify:**
- `background/tasks.py` - Add hour checking/deduction
- `background/tasks/download_tasks.py` - Integrate Supabase
- `background/tasks/analysis_tasks.py` - Integrate Supabase
- `background/tasks/conversion_tasks.py` - Integrate Supabase

**Example:**
```python
@celery_app.task
def process_data_download(user_id, ticker, ...):
    # Check hours
    if not supabase_client.check_usage_hours(user_id, 0.05).has_sufficient_hours:
        raise InsufficientHoursError()
    
    start_time = datetime.utcnow()
    try:
        result = download_impl(...)
        # Deduct hours
        supabase_client.deduct_hours(user_id, 0.05)
        # Log usage
        supabase_client.log_usage(user_id, 'download', 0.05, start_time)
        return result
    except Exception as e:
        # Log failure
        supabase_client.log_usage(user_id, 'download', 0.05, start_time, success=False)
        raise
```

#### 1.3 Create Storage Service Abstraction
**Priority: HIGH** | **Effort: Low**

- [ ] Create `storage/s3_storage.py` wrapper for Wasabi/S3
- [ ] Abstract storage operations (upload, download, delete)
- [ ] Support both local (dev) and S3 (prod) backends
- [ ] Update time-series metadata with storage keys

**Files to create:**
- `storage/object_storage.py` - Storage abstraction
- `storage/wasabi_storage.py` - Wasabi implementation

**Example:**
```python
class ObjectStorage:
    def upload_parquet(self, file_path, key):
        # Upload to Wasabi/S3
        pass
    
    def get_presigned_url(self, key, expires=3600):
        # Generate presigned URL
        pass
```

### Phase 2: Stripe Integration (Week 2-3)

#### 2.1 Stripe Webhook Handler
**Priority: HIGH** | **Effort: Medium**

- [ ] Create Stripe webhook route
- [ ] Handle `invoice.paid` events
- [ ] Map Stripe customers to Supabase users
- [ ] Add hours to user subscriptions
- [ ] Log payments to `stripe_payments` table

**Files to create:**
- `web/routes/stripe_webhook.py` - Webhook handler

**Files to modify:**
- `web/routes/main.py` - Register webhook blueprint

#### 2.2 Payment UI Integration
**Priority: MEDIUM** | **Effort: Low**

- [ ] Update payment routes to use Supabase plans
- [ ] Display remaining hours in UI
- [ ] Add low-hours warnings
- [ ] Integrate Stripe Checkout

**Files to modify:**
- `web/routes/payments_*.py` - Use Supabase
- `web/templates/payments_*.html` - Show hours

#### 2.3 Usage Tracking Dashboard
**Priority: MEDIUM** | **Effort: Medium**

- [ ] Create usage analytics endpoint
- [ ] Display usage logs in UI
- [ ] Show hourly consumption trends
- [ ] Add usage predictions

**Files to create:**
- `web/routes/usage_analytics.py`
- `web/templates/usage_dashboard.html`

### Phase 3: Modal Integration (Week 3-4)

#### 3.1 Set Up Modal Functions
**Priority: MEDIUM** | **Effort: High**

- [ ] Create Modal app configuration
- [ ] Move heavy compute tasks to Modal
- [ ] Set up DuckDB queries in Modal
- [ ] Configure secrets management

**Files to create:**
- `modal_app.py` - Modal application
- `modal_functions/download.py` - Download function
- `modal_functions/analysis.py` - Analysis function

**Example:**
```python
import modal

app = modal.App("redline")

@app.function(cpu=4, memory=8192, secrets=["API_KEYS"])
def download_ticker(config, ticker):
    # Heavy download/processing
    pass
```

#### 3.2 Update Celery Tasks to Use Modal
**Priority: MEDIUM** | **Effort: Medium**

- [ ] Replace heavy operations with Modal calls
- [ ] Handle Modal async responses
- [ ] Add error handling and retries
- [ ] Update progress callbacks

**Files to modify:**
- `background/tasks/download_tasks.py` - Use Modal
- `background/tasks/analysis_tasks.py` - Use Modal

### Phase 4: Object Storage Integration (Week 4-5)

#### 4.1 Migrate File Operations to Wasabi/S3
**Priority: MEDIUM** | **Effort: Medium**

- [ ] Update download tasks to store in S3
- [ ] Update analysis to read from S3
- [ ] Implement presigned URLs for downloads
- [ ] Add lifecycle policies

**Files to modify:**
- `downloaders/*.py` - Store in S3
- `core/data_loader.py` - Read from S3
- `storage/s3_operations.py` - Update implementation

#### 4.2 DuckDB HTTPFS Integration
**Priority: LOW** | **Effort: Low**

- [ ] Configure DuckDB to query Parquet from S3
- [ ] Use HTTPFS extension
- [ ] Optimize query performance
- [ ] Add caching layer

**Files to modify:**
- `core/data_loader.py` - Use HTTPFS
- `database/operations.py` - S3 queries

### Phase 5: Testing & Migration (Week 5-6)

#### 5.1 Unit Tests
**Priority: HIGH** | **Effort: Medium**

- [ ] Test Supabase client operations
- [ ] Test Celery task integration
- [ ] Test Stripe webhook handling
- [ ] Test storage operations

**Files to create:**
- `tests/test_supabase.py`
- `tests/test_celery_tasks.py`
- `tests/test_stripe.py`
- `tests/test_storage.py`

#### 5.2 Integration Tests
**Priority: MEDIUM** | **Effort: High**

- [ ] End-to-end download flow
- [ ] End-to-end analysis flow
- [ ] Payment flow testing
- [ ] Multi-user scenarios

#### 5.3 Data Migration Scripts
**Priority: MEDIUM** | **Effort: Medium**

- [ ] Migrate existing user configs
- [ ] Migrate time-series metadata
- [ ] Migrate files to S3
- [ ] Verify data integrity

**Files to create:**
- `scripts/migrate_users.py`
- `scripts/migrate_data.py`
- `scripts/migrate_files_to_s3.py`

### Phase 6: Production Deployment (Week 6-7)

#### 6.1 Render Deployment
**Priority: HIGH** | **Effort: Low**

- [ ] Create `render.yaml`
- [ ] Configure environment variables
- [ ] Set up auto-deploy from Git
- [ ] Configure health checks

**Files to create:**
- `render.yaml`

#### 6.2 Monitoring & Observability
**Priority: HIGH** | **Effort: Medium**

- [ ] Set up Sentry for error tracking
- [ ] Configure logging aggregation
- [ ] Set up metrics collection
- [ ] Create dashboards

#### 6.3 Performance Optimization
**Priority: MEDIUM** | **Effort: Medium**

- [ ] Optimize database queries
- [ ] Add Redis caching
- [ ] Optimize Celery task routing
- [ ] Load testing

## 📋 Immediate Next Steps (This Week)

1. **Set up Supabase project** (30 min)
   - Create project at supabase.com
   - Run `supabase_schema.sql`
   - Get API keys

2. **Integrate Supabase client** (2-3 hours)
   - Add to Flask app initialization
   - Create auth middleware
   - Update one route as proof of concept

3. **Update one Celery task** (2 hours)
   - Add hour checking to download task
   - Add usage logging
   - Test end-to-end

4. **Set up local development** (1 hour)
   - Run `docker-compose up`
   - Verify all services start
   - Test basic functionality

## 🎯 Success Metrics

- [ ] All routes use Supabase for data
- [ ] All tasks check/deduct hours
- [ ] Stripe payments add hours automatically
- [ ] Files stored in S3/Wasabi
- [ ] Heavy tasks run in Modal
- [ ] Zero downtime deployments
- [ ] <200ms API response times
- [ ] 99.9% uptime

## 📚 Resources

- [Supabase Docs](https://supabase.com/docs)
- [Celery Docs](https://docs.celeryq.dev/)
- [Modal Docs](https://modal.com/docs)
- [Wasabi Docs](https://wasabi.com/api-docs/)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

## 🔄 Iterative Approach

Start small, test frequently:
1. Integrate one feature at a time
2. Test locally with Docker Compose
3. Deploy to staging environment
4. Monitor and iterate
5. Deploy to production

## 💡 Tips

- Use feature flags for gradual rollout
- Keep local development simple (local postgres)
- Use Supabase in production only
- Monitor costs (Modal, Wasabi, Supabase)
- Set up alerts for low hours/errors
