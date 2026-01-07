-- Create processing_jobs table for Modal job tracking
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS public.processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    job_type VARCHAR NOT NULL,  -- 'csv_to_parquet', 'aggregate', 'clean', 'download'
    status VARCHAR DEFAULT 'queued',  -- 'queued', 'processing', 'completed', 'failed'
    input_s3_path VARCHAR NOT NULL,
    output_s3_path VARCHAR,
    modal_call_id VARCHAR,  -- Modal function call ID
    file_size_bytes BIGINT,
    row_count BIGINT,
    processing_hours DECIMAL(10,4),
    error_message TEXT,
    metadata JSONB,  -- Additional job parameters
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON public.processing_jobs(created_at);

-- Enable Row Level Security
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
DROP POLICY IF EXISTS "Users can manage own jobs" ON public.processing_jobs;
CREATE POLICY "Users can manage own jobs" ON public.processing_jobs
    USING (auth.uid() = user_id);

COMMENT ON TABLE public.processing_jobs IS 'Tracks Modal processing jobs for data conversions and analytics';
