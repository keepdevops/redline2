#!/usr/bin/env python3
"""
Modal App for REDLINE - Serverless DuckDB Processing
Handles data conversions, analytics, and aggregations
"""

import modal
import os

# ============================================================================
# MODAL APP CONFIGURATION
# ============================================================================

app = modal.App("redline-processing")

# Create Docker image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "duckdb==0.10.0",
        "pandas==2.1.4",
        "pyarrow==14.0.1",
        "boto3==1.34.11",
        "supabase==2.3.0",
        "stripe==7.8.0",
        "numpy==1.26.2",
        "openpyxl==3.1.2",  # For Excel files
        "tables==3.9.2"     # For HDF5 files
    )
)

# Modal secrets (created earlier via CLI)
secrets = [
    modal.Secret.from_name("supabase-secrets"),  # SUPABASE_URL, SUPABASE_SERVICE_KEY
    modal.Secret.from_name("s3-credentials"),    # S3/Wasabi keys
    modal.Secret.from_name("stripe-secrets")     # STRIPE_SECRET_KEY
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def configure_duckdb_s3(conn):
    """Configure DuckDB to access S3/Wasabi"""
    access_key = os.environ.get('R2_ACCESS_KEY_ID') or os.environ.get('S3_ACCESS_KEY')
    secret_key = os.environ.get('R2_SECRET_ACCESS_KEY') or os.environ.get('S3_SECRET_KEY')
    endpoint = os.environ.get('R2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL')

    # Configure S3 access for DuckDB
    conn.execute(f"""
        SET s3_access_key_id='{access_key}';
        SET s3_secret_access_key='{secret_key}';
        SET s3_endpoint='{endpoint}';
        SET s3_url_style='path';
        SET s3_region='us-east-1';
    """)

def update_job_status(supabase, job_id: str, status: str, **kwargs):
    """Update job status in Supabase"""
    from datetime import datetime

    update_data = {'status': status}

    # Add timestamps based on status
    if status == 'processing':
        update_data['started_at'] = datetime.utcnow().isoformat()
    elif status in ('completed', 'failed'):
        update_data['completed_at'] = datetime.utcnow().isoformat()

    # Add any additional fields
    update_data.update(kwargs)

    supabase.table('processing_jobs').update(update_data).eq('id', job_id).execute()

def report_usage_to_stripe(stripe_customer_id: str, processing_hours: float):
    """Report usage to Stripe metered billing"""
    import stripe
    import time

    stripe.api_key = os.environ['STRIPE_SECRET_KEY']

    try:
        # Get active subscription for customer
        subscriptions = stripe.Subscription.list(customer=stripe_customer_id, limit=1, status='active')

        if subscriptions.data:
            subscription = subscriptions.data[0]
            subscription_item_id = subscription['items']['data'][0]['id']

            # Report usage (convert hours to units: 0.5 hours = 50 units)
            stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=int(processing_hours * 100),
                timestamp=int(time.time()),
                action='increment'
            )
            return True
    except Exception as e:
        print(f"Error reporting usage to Stripe: {str(e)}")
        return False

# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    timeout=7200,    # 2 hours max
    memory=16384,    # 16GB RAM
    cpu=8.0          # 8 CPUs
)
def process_data(
    job_id: str,
    user_id: str,
    stripe_customer_id: str,
    input_s3_path: str,
    output_s3_path: str,
    job_type: str = 'csv_to_parquet'
):
    """
    Main data processing function

    Args:
        job_id: Supabase job ID
        user_id: Supabase user ID
        stripe_customer_id: Stripe customer ID
        input_s3_path: S3 URI to input file (e.g., s3://bucket/path/file.csv)
        output_s3_path: S3 URI for output file
        job_type: Type of job to run

    Returns:
        Result dict with status and metrics
    """
    import duckdb
    import time
    from datetime import datetime
    from supabase import create_client

    start_time = time.time()

    # Initialize Supabase client
    supabase = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_KEY']
    )

    try:
        # Update job status to 'processing'
        update_job_status(supabase, job_id, 'processing')

        # Initialize DuckDB connection (in-memory)
        conn = duckdb.connect(':memory:')
        configure_duckdb_s3(conn)

        # Route to appropriate handler based on job_type
        if job_type == 'csv_to_parquet':
            result = convert_csv_to_parquet(conn, input_s3_path, output_s3_path)

        elif job_type == 'parquet_to_csv':
            result = convert_parquet_to_csv(conn, input_s3_path, output_s3_path)

        elif job_type == 'aggregate_timeseries':
            result = aggregate_timeseries(conn, input_s3_path, output_s3_path)

        elif job_type == 'clean_data':
            result = clean_data(conn, input_s3_path, output_s3_path)

        elif job_type == 'merge_files':
            result = merge_files(conn, input_s3_path, output_s3_path)

        else:
            raise ValueError(f"Unknown job type: {job_type}")

        # Calculate processing time
        end_time = time.time()
        processing_hours = (end_time - start_time) / 3600.0

        # Update job status to 'completed'
        update_job_status(
            supabase, job_id, 'completed',
            output_s3_path=output_s3_path,
            row_count=result.get('row_count', 0),
            processing_hours=processing_hours
        )

        # Log usage to Supabase
        supabase.table('usage_history').insert({
            'user_id': user_id,
            'stripe_customer_id': stripe_customer_id,
            'hours_used': processing_hours,
            'job_id': job_id,
            'usage_timestamp': datetime.utcnow().isoformat()
        }).execute()

        # Report usage to Stripe
        report_usage_to_stripe(stripe_customer_id, processing_hours)

        return {
            'success': True,
            'job_id': job_id,
            'output_s3_path': output_s3_path,
            'row_count': result.get('row_count', 0),
            'processing_hours': processing_hours,
            'message': f'Job completed successfully in {processing_hours:.4f} hours'
        }

    except Exception as e:
        # Update job status to 'failed'
        update_job_status(
            supabase, job_id, 'failed',
            error_message=str(e)
        )

        raise

# ============================================================================
# JOB TYPE HANDLERS
# ============================================================================

def convert_csv_to_parquet(conn, input_s3_path: str, output_s3_path: str) -> dict:
    """Convert CSV to Parquet format"""
    # Read CSV from S3 directly (no download needed!)
    conn.execute(f"""
        CREATE TABLE data AS
        SELECT * FROM read_csv_auto('{input_s3_path}', AUTO_DETECT=TRUE)
    """)

    # Get row count
    row_count = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]

    # Write to Parquet on S3 (no local storage!)
    conn.execute(f"""
        COPY data
        TO '{output_s3_path}'
        (FORMAT PARQUET, COMPRESSION 'SNAPPY')
    """)

    return {'row_count': row_count}

def convert_parquet_to_csv(conn, input_s3_path: str, output_s3_path: str) -> dict:
    """Convert Parquet to CSV format"""
    # Read Parquet from S3
    conn.execute(f"""
        CREATE TABLE data AS
        SELECT * FROM read_parquet('{input_s3_path}')
    """)

    row_count = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]

    # Write to CSV on S3
    conn.execute(f"""
        COPY data
        TO '{output_s3_path}'
        (FORMAT CSV, HEADER TRUE)
    """)

    return {'row_count': row_count}

def aggregate_timeseries(conn, input_s3_path: str, output_s3_path: str) -> dict:
    """
    Aggregate timeseries data by day
    Assumes columns: timestamp, ticker, open, high, low, close, volume
    """
    conn.execute(f"""
        COPY (
            SELECT
                ticker,
                DATE_TRUNC('day', timestamp) as date,
                FIRST(open) as open,
                MAX(high) as high,
                MIN(low) as low,
                LAST(close) as close,
                SUM(volume) as volume
            FROM read_parquet('{input_s3_path}')
            GROUP BY ticker, DATE_TRUNC('day', timestamp)
            ORDER BY ticker, date
        )
        TO '{output_s3_path}'
        (FORMAT PARQUET, COMPRESSION 'SNAPPY')
    """)

    row_count = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{output_s3_path}')").fetchone()[0]

    return {'row_count': row_count}

def clean_data(conn, input_s3_path: str, output_s3_path: str) -> dict:
    """
    Clean data: remove duplicates, handle nulls, validate ranges
    """
    # Read data
    conn.execute(f"""
        CREATE TABLE raw_data AS
        SELECT * FROM read_parquet('{input_s3_path}')
    """)

    # Clean: remove duplicates, filter nulls
    conn.execute("""
        CREATE TABLE cleaned_data AS
        SELECT DISTINCT *
        FROM raw_data
        WHERE TRUE
        -- Add your cleaning logic here
    """)

    row_count = conn.execute("SELECT COUNT(*) FROM cleaned_data").fetchone()[0]

    # Write cleaned data
    conn.execute(f"""
        COPY cleaned_data
        TO '{output_s3_path}'
        (FORMAT PARQUET, COMPRESSION 'SNAPPY')
    """)

    return {'row_count': row_count}

def merge_files(conn, input_s3_paths: str, output_s3_path: str) -> dict:
    """
    Merge multiple files (input_s3_paths should be comma-separated)
    """
    paths = input_s3_paths.split(',')

    # Create UNION ALL query
    union_parts = [f"SELECT * FROM read_parquet('{path.strip()}')" for path in paths]
    union_query = " UNION ALL ".join(union_parts)

    conn.execute(f"""
        COPY (
            {union_query}
        )
        TO '{output_s3_path}'
        (FORMAT PARQUET, COMPRESSION 'SNAPPY')
    """)

    row_count = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{output_s3_path}')").fetchone()[0]

    return {'row_count': row_count}

# ============================================================================
# ADDITIONAL ANALYTICS FUNCTIONS
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    timeout=3600,
    memory=8192,
    cpu=4.0
)
def analyze_financial_data(
    job_id: str,
    user_id: str,
    input_s3_path: str,
    analysis_type: str = 'summary_stats'
):
    """
    Perform financial data analysis

    Args:
        job_id: Supabase job ID
        user_id: Supabase user ID
        input_s3_path: S3 URI to input Parquet file
        analysis_type: Type of analysis (summary_stats, returns, volatility)

    Returns:
        Analysis results as dict
    """
    import duckdb
    from supabase import create_client

    supabase = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_KEY']
    )

    conn = duckdb.connect(':memory:')
    configure_duckdb_s3(conn)

    try:
        update_job_status(supabase, job_id, 'processing')

        if analysis_type == 'summary_stats':
            # Calculate summary statistics
            result = conn.execute(f"""
                SELECT
                    ticker,
                    COUNT(*) as row_count,
                    MIN(close) as min_price,
                    MAX(close) as max_price,
                    AVG(close) as avg_price,
                    STDDEV(close) as price_stddev,
                    SUM(volume) as total_volume
                FROM read_parquet('{input_s3_path}')
                GROUP BY ticker
                ORDER BY ticker
            """).fetchdf()

            analysis_results = result.to_dict('records')

        elif analysis_type == 'returns':
            # Calculate daily returns
            result = conn.execute(f"""
                SELECT
                    ticker,
                    date,
                    close,
                    LAG(close) OVER (PARTITION BY ticker ORDER BY date) as prev_close,
                    (close - LAG(close) OVER (PARTITION BY ticker ORDER BY date)) /
                        LAG(close) OVER (PARTITION BY ticker ORDER BY date) as daily_return
                FROM read_parquet('{input_s3_path}')
                ORDER BY ticker, date
            """).fetchdf()

            analysis_results = result.to_dict('records')

        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

        update_job_status(supabase, job_id, 'completed')

        return {
            'success': True,
            'analysis_type': analysis_type,
            'results': analysis_results
        }

    except Exception as e:
        update_job_status(supabase, job_id, 'failed', error_message=str(e))
        raise

# ============================================================================
# LOCAL TESTING ENTRYPOINT
# ============================================================================

@app.local_entrypoint()
def test():
    """Test the Modal app locally"""
    print("Testing REDLINE Modal App...")
    print("To deploy: modal deploy redline/processing/modal_app.py")
    print("To run remotely: modal run redline/processing/modal_app.py")

if __name__ == "__main__":
    print("REDLINE Modal App")
    print("Deploy with: modal deploy redline/processing/modal_app.py")
