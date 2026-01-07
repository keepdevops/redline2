# VarioSync System Design Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Database Schema](#database-schema)
7. [Authentication & Authorization](#authentication--authorization)
8. [Payment System](#payment-system)
9. [Storage Architecture](#storage-architecture)
10. [API Design](#api-design)
11. [Deployment Architecture](#deployment-architecture)
12. [Security Architecture](#security-architecture)
13. [Scalability & Performance](#scalability--performance)
14. [Integration Points](#integration-points)
15. [Monitoring & Logging](#monitoring--logging)

---

## System Overview

**VarioSync** is a professional financial data analysis platform that provides:
- Multi-source financial data downloading (Yahoo Finance, Stooq, Massive.com, Alpha Vantage, Finnhub)
- Data format conversion and processing (CSV, JSON, Parquet, Feather, DuckDB, H5, NPZ)
- Advanced data analysis (financial, statistical, correlation, ML)
- Web-based and desktop GUI interfaces
- Multi-user SaaS platform with usage-based billing

### Key Characteristics
- **Multi-tenant SaaS**: User isolation with Supabase authentication
- **Usage-based billing**: Time-based access control (hours purchased via Stripe)
- **Serverless processing**: Modal for heavy data processing tasks
- **Cloud storage**: Wasabi S3 for user file storage
- **Production-ready**: Gunicorn WSGI server, Docker deployment, health checks

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (React/JS)  │  Desktop GUI (Tkinter)  │  CLI     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer (Flask)                    │
├─────────────────────────────────────────────────────────────────┤
│  Web Routes  │  API Routes  │  Authentication  │  Middleware │
│  - Main      │  - Data      │  - JWT Validation │  - Rate     │
│  - Download  │  - Analysis  │  - Hours Check   │    Limiting │
│  - Converter │  - ML        │  - Usage Tracking │  - CORS     │
│  - Settings  │  - Files     │                   │             │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Business   │    │   Data Processing │    │   External   │
│   Logic      │    │   Services        │    │   Services   │
├──────────────┤    ├──────────────────┤    ├──────────────┤
│ - Downloaders│    │ - Format Converter│    │ - Supabase   │
│ - Analyzers  │    │ - Data Cleaner    │    │ - Stripe     │
│ - Converters │    │ - Schema Validator│    │ - Modal       │
│              │    │ - DuckDB Service  │    │ - Wasabi S3  │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Storage Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Supabase)  │  Wasabi S3  │  Local File System     │
│  - Users                │  - User Files│  - Downloads            │
│  - Hours                │  - Uploads  │  - Temp Files          │
│  - Sessions             │             │                         │
│  - Usage History        │             │                         │
│  - Payments             │             │                         │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Patterns
- **Layered Architecture**: Clear separation between presentation, business logic, and data layers
- **Microservices**: Serverless functions (Modal) for heavy processing
- **RESTful API**: Standard HTTP endpoints for all operations
- **Event-Driven**: Webhook-based payment processing
- **Multi-tenancy**: User isolation at database and storage levels

---

## Core Components

### 1. Web Application (`web_app.py`)
**Purpose**: Main Flask application entry point

**Responsibilities**:
- Flask app initialization and configuration
- Blueprint registration
- Middleware setup (authentication, rate limiting, usage tracking)
- Error handling
- Health check endpoint

**Key Features**:
- Gunicorn-compatible for production
- JWT-based authentication middleware
- Usage tracking middleware (deducts hours every 30 seconds)
- Rate limiting (200/day, 50/hour default)
- CORS support
- Response compression

### 2. Authentication System (`redline/auth/`)

#### SupabaseAuthService (`supabase_auth.py`)
**Purpose**: User authentication and hours management

**Key Methods**:
- `register()`: Create new user account
- `login()`: Authenticate user, return JWT tokens
- `validate_jwt()`: Verify JWT token, extract user info
- `get_user_hours()`: Retrieve remaining hours
- `deduct_hours()`: Deduct hours from balance
- `add_hours()`: Add purchased hours

**Integration**: 
- Supabase Auth for user management
- PostgreSQL `user_hours` table for balance tracking

#### UsageTracker (`usage_tracker.py`)
**Purpose**: Track user sessions and usage time

**Features**:
- Session management (start/end)
- Time-based hour deduction (configurable interval, default 30s)
- Thread-safe session tracking
- Last deduction time tracking per user

### 3. Downloader System (`redline/downloaders/`)

#### BaseDownloader (`base_downloader.py`)
**Abstract base class** for all data downloaders

**Features**:
- Rate limiting with thread-safe locks
- Retry logic (3 attempts with exponential backoff)
- Connection pooling (requests.Session)
- Data standardization (OHLCV format)
- Statistics tracking
- Batch processing support

**Concrete Implementations**:
- `YahooDownloader`: Yahoo Finance API (yfinance library)
- `StooqDownloader`: Stooq.com historical data
- `MassiveDownloader`: Massive.com REST API + WebSocket (15-min delayed + real-time)
- `AlphaVantageDownloader`: Alpha Vantage API
- `FinnhubDownloader`: Finnhub API
- `CSVDownloader`: Local CSV file import
- `MultiSourceDownloader`: Fallback mechanism across sources

**Data Flow**:
```
User Request → Downloader → API Call → Raw Data → Standardization → DataFrame → Save
```

### 4. Format Converter (`redline/core/format_converter.py`)
**Purpose**: Convert between data formats

**Supported Formats**:
- **Input**: CSV, JSON, Parquet, Feather, Excel, DuckDB, H5, NPZ, Arrow
- **Output**: CSV, JSON, Parquet, Feather, Excel, DuckDB, H5, NPZ, Arrow

**Features**:
- Batch conversion with column alignment
- Column reordering
- Data cleaning (duplicates, missing values)
- Schema validation
- Memory-efficient processing

**Libraries Used**:
- Pandas (primary)
- Polars (high-performance alternative)
- PyArrow (Arrow format)
- TensorFlow (H5, NPZ formats)
- DuckDB (via Modal serverless)

### 5. Analysis Engine (`redline/web/routes/analysis*.py`)

**Analysis Types**:
- **Financial Analysis** (`analysis_financial.py`): OHLCV metrics, returns, volatility
- **Statistical Analysis** (`analysis_statistical.py`): Mean, median, std dev, min/max
- **Correlation Analysis** (`analysis_correlation.py`): Asset relationships, correlation matrices
- **ML Analysis** (`analysis_ml.py`): Predictive models, clustering
- **Visualization** (`analysis_visualization.py`): Charts, graphs

**Features**:
- Smart column detection (case-insensitive, pattern matching)
- Flexible column naming support
- Multi-file analysis
- Export capabilities (JSON, CSV)

### 6. Data Management (`redline/web/routes/data*.py`)

**Components**:
- **Data Loading** (`data_loading*.py`): Single/multiple file loading
- **Data Browsing** (`data_browsing.py`): Pagination, virtual scrolling
- **Data Filtering** (`data_filtering*.py`): SQL-like queries, column filtering
- **Data Cleaning** (`data_filtering_clean.py`): Remove empty rows/columns

**Performance Optimizations**:
- Virtual scrolling for 10M+ rows
- Lazy loading
- Pagination (1000 rows per page)
- Memory-efficient processing

### 7. Converter System (`redline/web/routes/converter*.py`)

**Components**:
- **Single Conversion** (`converter_single.py`): One file at a time
- **Batch Conversion** (`converter_batch.py`): Multiple files with column alignment
- **File Browsing** (`converter_browsing*.py`): Select files for conversion
- **Merge Operations** (`converter_merge.py`): Combine multiple files
- **Cleanup** (`converter_cleanup.py`): Remove duplicates, fill missing values

### 8. Payment System (`redline/payment/`, `redline/web/routes/payments*.py`)

#### PaymentConfig (`payment/config.py`)
**Configuration**:
- Stripe API keys
- Pricing: 0.2 hours per dollar (configurable)
- Hour packages: 5h ($25), 10h ($45), 20h ($80), 50h ($180)

#### Payment Flow
```
1. User selects hours package
2. Create Stripe checkout session (payments_checkout.py)
3. User completes payment on Stripe
4. Stripe webhook → payments_webhook.py
5. Verify webhook signature
6. Add hours to user_hours table (supabase_auth.add_hours())
7. Log payment to payment_history table
```

**Security**:
- Webhook signature verification
- Metadata validation (user_id, hours)
- Idempotent operations

### 9. Storage System (`redline/storage/`)

#### SupabaseStorageService (`supabase_storage.py`)
**Purpose**: File storage in Supabase Storage

**Operations**:
- `upload_file()`: Upload to user-specific path
- `download_file()`: Download user files
- `list_files()`: List user's files
- `delete_file()`: Remove files

**Structure**: `{user_id}/files/{filename}`

#### UserStorage (`user_storage.py`)
**Purpose**: Local file system management

**Features**:
- User-specific directories
- File metadata tracking
- Cleanup operations

#### S3 Integration (`redline/web/routes/s3_upload.py`)
**Purpose**: Direct upload to Wasabi S3

**Features**:
- Pre-signed URLs for direct upload
- Bucket management
- File organization by user

### 10. Database Layer (`redline/database/`)

#### Models (`models.py`)
**SQLAlchemy ORM Models**:

1. **User**: User profile (linked to Supabase auth.users)
   - `user_id` (UUID, PK)
   - `email`, `name`, `company`
   - Relationships: hours, sessions, usage_history, payments, access_logs

2. **UserHours**: Hours balance tracking
   - `user_id` (FK to User)
   - `hours_remaining`, `total_hours_purchased`, `total_hours_used`
   - `last_deduction_at`

3. **UsageSession**: Active sessions
   - `session_id` (PK)
   - `user_id`, `start_time`, `end_time`
   - `total_hours`, `total_seconds`, `status`

4. **UsageHistory**: Hour deduction audit log
   - `user_id`, `session_id`
   - `hours_deducted`, `deduction_time`
   - `hours_remaining_before/after`, `api_endpoint`

5. **PaymentHistory**: Stripe payment transactions
   - `user_id`, `stripe_session_id`, `payment_id`
   - `hours_purchased`, `amount_paid`, `currency`
   - `payment_status`, `payment_date`

6. **AccessLog**: API access logs
   - `user_id`, `session_id`
   - `endpoint`, `method`, `ip_address`, `user_agent`
   - `response_status`, `response_time_ms`, `access_time`

#### UsageStorage (`usage_storage.py`)
**Purpose**: Persistent storage operations

**Methods**:
- `log_session_start()`: Create new session
- `log_session_end()`: End session, calculate hours
- `log_hour_deduction()`: Audit log for deductions
- `log_payment()`: Record payment transactions
- `log_access()`: API access logging

**Backend**: Supabase PostgreSQL (via Supabase client)

#### Database Connector (`optimized_connector.py`)
**Purpose**: Optimized database connections

**Features**:
- Connection pooling
- Query optimization
- Transaction management

### 11. Serverless Processing (`modal_processing/`, `redline/clients/modal_client.py`)

#### Modal Client (`modal_client.py`)
**Purpose**: Interface to Modal serverless functions

**Available Functions**:
- `process_csv()`: Process CSV/Parquet/Excel files
- `convert_format()`: Format conversion
- `generate_chart_data()`: Chart data generation
- `run_query()`: SQL queries on DuckDB
- `get_metadata()`: File metadata extraction

**Benefits**:
- Offloads heavy processing from main server
- Scalable compute resources
- Cost-effective (pay per use)

### 12. API Routes (`redline/web/routes/api*.py`)

**API Endpoints**:
- `/api/data/*`: Data operations (load, filter, browse)
- `/api/analysis/*`: Analysis operations
- `/api/convert/*`: Format conversion
- `/api/download/*`: Data downloading
- `/api/files/*`: File management
- `/api/keys/*`: API key management
- `/api/metadata/*`: File metadata
- `/api/themes/*`: UI theme management

**Response Format**:
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

---

## Data Flow

### 1. User Registration Flow
```
User → POST /api/register → SupabaseAuthService.register()
  → Supabase Auth API (create user)
  → Initialize user_hours table (0 hours)
  → Return JWT tokens
```

### 2. User Login Flow
```
User → POST /api/login → SupabaseAuthService.login()
  → Supabase Auth API (authenticate)
  → Return JWT tokens
  → Client stores tokens
```

### 3. Data Download Flow
```
User → POST /download/single → Downloader (Yahoo/Stooq/etc.)
  → API Call → Raw Data
  → Standardize Format (OHLCV)
  → Save to Local/S3
  → Return File Metadata
```

### 4. Data Analysis Flow
```
User → POST /analysis/financial → Load Data (from file/S3)
  → Apply Analysis (financial metrics)
  → Generate Results
  → Return JSON Response
```

### 5. Format Conversion Flow
```
User → POST /converter/convert → Load Source File
  → FormatConverter.convert_format()
  → Save to Target Format
  → Return Conversion Status
```

### 6. Payment Flow
```
User → POST /payments/create-checkout → Create Stripe Session
  → Redirect to Stripe Checkout
  → User Completes Payment
  → Stripe Webhook → /payments/webhook
  → Verify Signature → Add Hours → Log Payment
```

### 7. Usage Tracking Flow
```
Every Request → Middleware (before_request)
  → Check JWT Token
  → Check Hours Remaining
  → Process Request
  → Track Usage (every 30s)
  → Deduct Hours (if interval elapsed)
  → Log Access
```

---

## Technology Stack

### Backend
- **Python 3.11+**: Core language
- **Flask 3.1.2**: Web framework
- **Gunicorn 23.0.0**: Production WSGI server
- **SQLAlchemy 2.0.25**: ORM
- **Alembic 1.13.1**: Database migrations
- **Flask-Limiter 4.0.0**: Rate limiting
- **Flask-Compress 1.23**: Response compression
- **Flask-CORS 6.0.1**: CORS support

### Data Processing
- **Pandas 2.3.3**: Data manipulation
- **NumPy 2.3.5**: Numerical computing
- **Polars 1.35.2**: High-performance DataFrame
- **PyArrow 22.0.0**: Arrow format support
- **DuckDB**: Analytical database (via Modal)
- **TensorFlow 2.20.0**: ML formats (H5, NPZ)

### Data Sources
- **yfinance 0.2.40**: Yahoo Finance
- **requests 2.32.5**: HTTP client
- **curl-cffi 0.7.0**: HTTP/2 support for yfinance
- **massive 2.0.1**: Massive.com client

### Authentication & Backend Services
- **Supabase 2.10.1**: Auth + PostgreSQL + Storage
- **Stripe 14.0.1**: Payment processing
- **psycopg2-binary 2.9.9**: PostgreSQL adapter

### Serverless
- **Modal 0.63.0**: Serverless compute platform

### Cloud Storage
- **boto3 1.41.2**: AWS S3/Wasabi client

### Frontend
- **HTML/CSS/JavaScript**: Vanilla JS (no framework)
- **Templates**: Jinja2
- **Static Assets**: Minified CSS/JS

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Gunicorn**: Production server (2 workers × 4 threads)

---

## Database Schema

### PostgreSQL (Supabase)

#### Tables

**users**
```sql
- user_id (UUID, PK) - Links to auth.users.id
- email (String, UNIQUE)
- name (String)
- company (String)
- created_at (DateTime)
- updated_at (DateTime)
```

**user_hours**
```sql
- id (BigInteger, PK, Auto)
- user_id (UUID, FK → users.user_id, UNIQUE)
- hours_remaining (Float, default 0.0)
- total_hours_purchased (Float, default 0.0)
- total_hours_used (Float, default 0.0)
- last_deduction_at (DateTime)
- created_at (DateTime)
- updated_at (DateTime)
```

**usage_sessions**
```sql
- session_id (String, PK)
- user_id (UUID, FK → users.user_id)
- start_time (DateTime)
- end_time (DateTime)
- total_hours (Float)
- total_seconds (Float)
- status (String, default 'active')
- created_at (DateTime)
```

**usage_history**
```sql
- id (BigInteger, PK, Auto)
- user_id (UUID, FK → users.user_id)
- session_id (String)
- hours_deducted (Float)
- deduction_time (DateTime)
- hours_remaining_before (Float)
- hours_remaining_after (Float)
- api_endpoint (String)
- created_at (DateTime)
```

**payment_history**
```sql
- id (BigInteger, PK, Auto)
- user_id (UUID, FK → users.user_id)
- stripe_session_id (String)
- payment_id (String)
- hours_purchased (Float)
- amount_paid (Float)
- currency (String, default 'usd')
- payment_status (String)
- payment_date (DateTime)
- created_at (DateTime)
```

**access_logs**
```sql
- id (BigInteger, PK, Auto)
- user_id (UUID, FK → users.user_id)
- session_id (String)
- endpoint (String)
- method (String)
- ip_address (String)
- user_agent (String)
- response_status (Integer)
- response_time_ms (Integer)
- access_time (DateTime)
- created_at (DateTime)
```

#### Indexes
- `idx_user_hours_user` on `user_hours.user_id`
- `idx_usage_sessions_user` on `usage_sessions.user_id`
- `idx_usage_sessions_start` on `usage_sessions.start_time`
- `idx_usage_history_user` on `usage_history.user_id`
- `idx_usage_history_time` on `usage_history.deduction_time`
- `idx_payment_history_user` on `payment_history.user_id`
- `idx_payment_history_date` on `payment_history.payment_date`
- `idx_access_logs_user` on `access_logs.user_id`
- `idx_access_logs_time` on `access_logs.access_time`
- `idx_access_logs_endpoint` on `access_logs.endpoint`

---

## Authentication & Authorization

### Authentication Flow

1. **Registration**
   - User provides email, password, name, company
   - Supabase Auth creates user account
   - `user_hours` record initialized with 0 hours
   - JWT tokens returned

2. **Login**
   - User provides email, password
   - Supabase Auth validates credentials
   - JWT tokens (access + refresh) returned
   - Client stores tokens

3. **Request Authentication**
   - Client sends `Authorization: Bearer <token>` header
   - Middleware validates JWT via Supabase
   - User info extracted and stored in `g.user_id`, `g.email`
   - Request proceeds if valid

### Authorization

**Public Endpoints** (no auth required):
- `/` (index)
- `/register`, `/login`
- `/health`
- `/static/*`
- `/payments/webhook` (Stripe signature verified separately)

**Protected Endpoints** (require valid JWT):
- All `/api/*` endpoints
- All `/data/*` endpoints
- All `/analysis/*` endpoints
- All `/download/*` endpoints
- All `/converter/*` endpoints
- All `/settings/*` endpoints

**Hours Check**:
- After JWT validation, check `user_hours.hours_remaining`
- If `hours_remaining <= 0`, return 403 Forbidden
- Configurable via `ENFORCE_PAYMENT` env var

### Session Management

- **Session Tracking**: `UsageTracker` manages sessions
- **Session ID**: Generated UUID, stored in `g.session_id`
- **Session Duration**: Tracked from first request to last
- **Hour Deduction**: Every 30 seconds (configurable via `USAGE_CHECK_INTERVAL`)

---

## Payment System

### Architecture

```
User → Stripe Checkout → Payment → Webhook → Add Hours → Log Payment
```

### Components

1. **PaymentConfig** (`redline/payment/config.py`)
   - Pricing: 0.2 hours per dollar (configurable)
   - Hour packages: 5h ($25), 10h ($45), 20h ($80), 50h ($180)
   - Stripe API keys

2. **Checkout Creation** (`payments_checkout.py`)
   - Create Stripe checkout session
   - Include user_id and hours in metadata
   - Return checkout URL

3. **Webhook Handler** (`payments_webhook.py`)
   - Verify Stripe webhook signature
   - Handle `checkout.session.completed` event
   - Extract user_id and hours from metadata
   - Call `supabase_auth.add_hours()`
   - Log payment to `payment_history` table

### Security

- **Webhook Signature Verification**: Prevents unauthorized requests
- **Metadata Validation**: Ensures user_id and hours are present
- **Idempotent Operations**: Safe to retry webhook events

### Hour Management

- **Purchase**: Hours added via Stripe webhook
- **Usage**: Hours deducted every 30 seconds during active sessions
- **Balance Check**: Before each request (if `ENFORCE_PAYMENT=true`)
- **Audit Trail**: All deductions logged to `usage_history`

---

## Storage Architecture

### Storage Backends

1. **Supabase Storage**
   - **Purpose**: User file storage
   - **Structure**: `{user_id}/files/{filename}`
   - **Operations**: Upload, download, list, delete
   - **Access**: Via Supabase Storage API

2. **Wasabi S3**
   - **Purpose**: Alternative/complementary storage
   - **Structure**: User-specific buckets or prefixes
   - **Operations**: Pre-signed URLs for direct upload
   - **Access**: Via boto3 client

3. **Local File System**
   - **Purpose**: Temporary files, downloads, cache
   - **Structure**: `data/uploads/`, `data/downloaded/`, `data/converted/`
   - **Operations**: Standard file I/O
   - **Access**: Direct file system access

### File Organization

```
data/
├── uploads/          # User-uploaded files
├── downloaded/       # Downloaded data files
├── converted/        # Converted files
├── users/            # User-specific directories
│   └── {user_id}/
│       ├── files/    # User files
│       └── analysis/ # Analysis results
└── usage_data.duckdb # Usage tracking database
```

### Storage Selection

- **User Files**: Supabase Storage (primary) or Wasabi S3
- **Temporary Files**: Local file system
- **Downloads**: Local file system (can be moved to cloud)
- **Analysis Results**: Local or cloud (user preference)

---

## API Design

### RESTful Endpoints

#### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/status` - Check authentication status

#### Data Management
- `POST /data/load` - Load data file
- `GET /data/browse` - Browse data with pagination
- `POST /data/filter` - Apply filters
- `GET /data/metadata` - Get file metadata

#### Analysis
- `POST /analysis/financial` - Financial analysis
- `POST /analysis/statistical` - Statistical analysis
- `POST /analysis/correlation` - Correlation analysis
- `POST /analysis/ml` - ML analysis

#### Download
- `POST /download/single` - Download single ticker
- `POST /download/batch` - Download multiple tickers
- `GET /download/history` - Download history

#### Converter
- `POST /converter/convert` - Convert file format
- `POST /converter/batch` - Batch conversion
- `POST /converter/merge` - Merge files

#### Files
- `GET /api/files` - List user files
- `POST /api/files/upload` - Upload file
- `DELETE /api/files/{file_id}` - Delete file

#### Payments
- `POST /payments/create-checkout` - Create Stripe checkout
- `GET /payments/balance` - Get hours balance
- `POST /payments/webhook` - Stripe webhook handler

### Response Format

**Success Response**:
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

### Rate Limiting

- **Default**: 200 requests/day, 50 requests/hour
- **Health Endpoint**: 10,000 requests/hour
- **Balance Endpoint**: 1,000 requests/hour
- **Files List**: 500 requests/hour

---

## Deployment Architecture

### Docker Deployment

#### Dockerfile Structure
```dockerfile
# Multi-stage build
FROM python:3.11-slim as base
# Install dependencies
# Copy application code
# Create non-root user
# Expose port 8080
# Run with Gunicorn
```

#### Docker Compose
```yaml
services:
  web:
    build: .
    ports: ["8080:8080"]
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "http://localhost:8080/health"]
      interval: 30s
```

### Production Configuration

**Gunicorn**:
- Workers: 2 (configurable via `WORKERS`)
- Threads per worker: 4
- Total capacity: 8 concurrent requests
- Timeout: 120 seconds
- Max requests: 1000 (with jitter)

**Environment Variables**:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Environment (production/development)
- `SECRET_KEY`: Flask secret key
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Supabase service key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
- `ENFORCE_PAYMENT`: Enable/disable payment enforcement
- `USAGE_CHECK_INTERVAL`: Seconds between hour deductions (default: 30)

### Deployment Options

1. **Docker**: Pre-built images (AMD64, ARM64)
2. **PyPI**: `pip install redline-financial`
3. **Source**: Clone repository, install dependencies
4. **Executables**: Standalone binaries (Windows, macOS, Linux)

---

## Security Architecture

### Authentication Security

1. **JWT Tokens**
   - Signed by Supabase Auth
   - Short-lived access tokens
   - Refresh tokens for renewal
   - Validated on every request

2. **Password Security**
   - Handled by Supabase Auth
   - Hashing and salting (bcrypt)
   - Password strength requirements

### Authorization Security

1. **Hours Enforcement**
   - Check before each request
   - Prevents usage without payment
   - Configurable enforcement

2. **User Isolation**
   - User-specific file paths
   - Database row-level security (Supabase RLS)
   - Storage bucket isolation

### API Security

1. **Rate Limiting**
   - Prevents abuse
   - Per-IP limits
   - Configurable thresholds

2. **CORS**
   - Configured origins
   - Prevents unauthorized cross-origin requests

3. **Input Validation**
   - File size limits (100MB)
   - File type validation
   - SQL injection prevention (parameterized queries)

### Payment Security

1. **Webhook Verification**
   - Stripe signature verification
   - Prevents fake webhook calls
   - Idempotent processing

2. **Metadata Validation**
   - Verify user_id and hours
   - Prevent manipulation

### Data Security

1. **File Storage**
   - User-specific paths
   - Access control via Supabase Storage policies
   - Encryption at rest (Supabase/Wasabi)

2. **Database Security**
   - Row-level security (Supabase RLS)
   - Connection encryption (SSL/TLS)
   - Parameterized queries

### Infrastructure Security

1. **Docker**
   - Non-root user in container
   - Minimal base image (python:3.11-slim)
   - No unnecessary packages

2. **Secrets Management**
   - Environment variables
   - `.env` file (not committed)
   - Supabase service key (admin access)

---

## Scalability & Performance

### Performance Optimizations

1. **Data Processing**
   - Virtual scrolling for large datasets (10M+ rows)
   - Pagination (1000 rows per page)
   - Lazy loading
   - Format optimization (Parquet 10x smaller than CSV)

2. **Server Performance**
   - Gunicorn with multiple workers/threads
   - Connection pooling (database, HTTP)
   - Response compression
   - Static file caching

3. **Database Performance**
   - Indexes on frequently queried columns
   - Connection pooling
   - Query optimization

4. **Storage Performance**
   - CDN for static assets
   - Pre-signed URLs for direct S3 uploads
   - Batch operations

### Scalability Strategies

1. **Horizontal Scaling**
   - Stateless application (JWT tokens)
   - Multiple Gunicorn workers
   - Load balancer support

2. **Serverless Processing**
   - Modal for heavy computations
   - Offloads CPU-intensive tasks
   - Auto-scaling

3. **Database Scaling**
   - Supabase PostgreSQL (managed)
   - Connection pooling
   - Read replicas (if needed)

4. **Storage Scaling**
   - Wasabi S3 (unlimited storage)
   - CDN for static files
   - File lifecycle management

### Performance Benchmarks

| Dataset Size | Memory Usage | Load Time | Format |
|--------------|--------------|-----------|--------|
| 100K rows    | ~50MB        | 2-3s      | Any    |
| 1M rows      | ~200MB       | 5-10s     | Parquet/DuckDB |
| 10M rows     | ~1GB         | 30-60s    | Parquet/DuckDB |

---

## Integration Points

### External Services

1. **Supabase**
   - **Auth**: User authentication, JWT tokens
   - **PostgreSQL**: User data, hours, sessions, payments, logs
   - **Storage**: User file storage

2. **Stripe**
   - **Checkout**: Payment processing
   - **Webhooks**: Payment completion events

3. **Modal**
   - **Serverless Functions**: DuckDB processing, format conversion
   - **Auto-scaling**: Handles variable workloads

4. **Wasabi S3**
   - **Object Storage**: User file storage (alternative to Supabase Storage)
   - **CDN**: Fast file delivery

5. **Data Sources**
   - **Yahoo Finance**: Free financial data
   - **Stooq.com**: Historical data
   - **Massive.com**: Professional data (REST + WebSocket)
   - **Alpha Vantage**: API-based data
   - **Finnhub**: API-based data

### Integration Patterns

1. **REST APIs**: All external services accessed via REST
2. **Webhooks**: Stripe payment events
3. **WebSockets**: Massive.com real-time data
4. **SDKs**: Supabase, Stripe, Modal Python SDKs

---

## Monitoring & Logging

### Logging

**Log Levels**:
- `INFO`: General operations
- `DEBUG`: Detailed debugging
- `WARNING`: Non-critical issues
- `ERROR`: Errors requiring attention

**Log Destinations**:
- File: `variosync_web.log`
- Console: Standard output
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Monitoring

1. **Health Checks**
   - Endpoint: `/health`
   - Returns: `{"status": "healthy", "service": "redline-web"}`
   - Used by: Docker health checks, load balancers

2. **Usage Tracking**
   - All API access logged to `access_logs`
   - Hour deductions logged to `usage_history`
   - Session tracking in `usage_sessions`

3. **Error Tracking**
   - Errors logged with stack traces
   - User context included (user_id, endpoint)
   - Response status codes tracked

### Metrics

**Tracked Metrics**:
- Request count (per endpoint)
- Response times (per endpoint)
- Error rates
- User sessions
- Hour usage
- Payment transactions

**Storage**:
- Database tables (`access_logs`, `usage_history`)
- Can be exported for analysis

---

## Conclusion

VarioSync is a comprehensive, production-ready financial data analysis platform with:

- **Multi-tenant SaaS architecture** with user isolation
- **Usage-based billing** via Stripe integration
- **Scalable processing** with serverless functions (Modal)
- **Multiple data sources** with fallback mechanisms
- **Production deployment** with Docker and Gunicorn
- **Security** with JWT authentication, rate limiting, and input validation
- **Performance optimizations** for large datasets

The system is designed for scalability, security, and maintainability, with clear separation of concerns and well-defined interfaces between components.


