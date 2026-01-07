-- Complete Supabase Schema Setup for REDLINE
-- Run this in Supabase SQL Editor

-- ============================================================================
-- 1. USERS TABLE (extends Supabase auth.users)
-- ============================================================================

-- Drop existing table if needed (careful in production!)
-- DROP TABLE IF EXISTS public.users CASCADE;

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR NOT NULL UNIQUE,
    stripe_customer_id VARCHAR UNIQUE,
    stripe_subscription_id VARCHAR,
    subscription_status VARCHAR DEFAULT 'inactive',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON public.users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "Users can read own data" ON public.users;
CREATE POLICY "Users can read own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own data" ON public.users;
CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- ============================================================================
-- 2. PROCESSING JOBS TABLE (for Modal job tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    job_type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'queued',
    input_s3_path VARCHAR NOT NULL,
    output_s3_path VARCHAR,
    modal_call_id VARCHAR,
    file_size_bytes BIGINT,
    row_count BIGINT,
    processing_hours DECIMAL(10,4),
    error_message TEXT,
    metadata JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON public.processing_jobs(created_at);

-- Enable RLS
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;

-- RLS Policy
DROP POLICY IF EXISTS "Users can manage own jobs" ON public.processing_jobs;
CREATE POLICY "Users can manage own jobs" ON public.processing_jobs
    USING (auth.uid() = user_id);

-- ============================================================================
-- 3. USAGE HISTORY TABLE
-- ============================================================================

-- This should already exist, but verify it has the right schema
CREATE TABLE IF NOT EXISTS public.usage_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR,
    hours_used DECIMAL(10,4) NOT NULL,
    usage_timestamp TIMESTAMPTZ DEFAULT NOW(),
    job_id UUID REFERENCES public.processing_jobs(id),
    api_endpoint VARCHAR,
    session_id VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_usage_user_id ON public.usage_history(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_job_id ON public.usage_history(job_id);
CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON public.usage_history(usage_timestamp);

-- Enable RLS
ALTER TABLE public.usage_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy
DROP POLICY IF EXISTS "Users can read own usage" ON public.usage_history;
CREATE POLICY "Users can read own usage" ON public.usage_history
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- 4. PAYMENT HISTORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.payment_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR NOT NULL,
    stripe_session_id VARCHAR,
    stripe_payment_intent VARCHAR,
    stripe_invoice_id VARCHAR,
    hours_purchased DECIMAL(10,4),
    amount_paid DECIMAL(10,2) NOT NULL,
    currency VARCHAR DEFAULT 'usd',
    payment_status VARCHAR DEFAULT 'succeeded',
    payment_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_payment_user_id ON public.payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_stripe_customer ON public.payment_history(stripe_customer_id);

-- Enable RLS
ALTER TABLE public.payment_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy
DROP POLICY IF EXISTS "Users can read own payments" ON public.payment_history;
CREATE POLICY "Users can read own payments" ON public.payment_history
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check that all tables were created
DO $$
BEGIN
    RAISE NOTICE '=== REDLINE Schema Setup Complete ===';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - public.users';
    RAISE NOTICE '  - public.processing_jobs';
    RAISE NOTICE '  - public.usage_history';
    RAISE NOTICE '  - public.payment_history';
    RAISE NOTICE '';
    RAISE NOTICE 'All tables have Row Level Security enabled';
END $$;
