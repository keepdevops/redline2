-- VarioSync Complete Supabase PostgreSQL Schema
-- Run this in Supabase SQL Editor after creating your project

-- ============================================
-- 1. User Hours Tracking (Main table)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_hours (
  user_id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email VARCHAR NOT NULL,
  hours_remaining DOUBLE PRECISION DEFAULT 0,
  total_hours_purchased DOUBLE PRECISION DEFAULT 0,
  total_hours_used DOUBLE PRECISION DEFAULT 0,
  last_deduction_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.user_hours ENABLE ROW LEVEL SECURITY;

-- Users can read their own hours
CREATE POLICY "Users can view own hours" ON public.user_hours
  FOR SELECT USING (auth.uid() = user_id);

-- Service role can manage all (for backend hour deduction)
CREATE POLICY "Service role full access hours" ON public.user_hours
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 2. Usage Sessions (Track active sessions)
-- ============================================
CREATE TABLE IF NOT EXISTS public.usage_sessions (
  session_id VARCHAR PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  total_hours DOUBLE PRECISION,
  total_seconds DOUBLE PRECISION,
  status VARCHAR DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_sessions_user ON public.usage_sessions(user_id);
CREATE INDEX idx_usage_sessions_start ON public.usage_sessions(start_time);

ALTER TABLE public.usage_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sessions" ON public.usage_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access sessions" ON public.usage_sessions
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 3. Usage History (Hour deduction log)
-- ============================================
CREATE TABLE IF NOT EXISTS public.usage_history (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  session_id VARCHAR,
  hours_deducted DOUBLE PRECISION NOT NULL,
  deduction_time TIMESTAMP NOT NULL,
  hours_remaining_before DOUBLE PRECISION,
  hours_remaining_after DOUBLE PRECISION,
  api_endpoint VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_history_user ON public.usage_history(user_id);
CREATE INDEX idx_usage_history_time ON public.usage_history(deduction_time);

ALTER TABLE public.usage_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own usage history" ON public.usage_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access usage history" ON public.usage_history
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 4. Payment History (Stripe transactions)
-- ============================================
CREATE TABLE IF NOT EXISTS public.payment_history (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  stripe_session_id VARCHAR,
  payment_id VARCHAR,
  hours_purchased DOUBLE PRECISION NOT NULL,
  amount_paid DOUBLE PRECISION NOT NULL,
  currency VARCHAR DEFAULT 'usd',
  payment_status VARCHAR,
  payment_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payment_history_user ON public.payment_history(user_id);
CREATE INDEX idx_payment_history_date ON public.payment_history(payment_date);

ALTER TABLE public.payment_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own payment history" ON public.payment_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access payment history" ON public.payment_history
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 5. Access Logs (API endpoint tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS public.access_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  session_id VARCHAR,
  endpoint VARCHAR NOT NULL,
  method VARCHAR NOT NULL,
  ip_address VARCHAR,
  user_agent VARCHAR,
  response_status INTEGER,
  response_time_ms INTEGER,
  access_time TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_access_logs_user ON public.access_logs(user_id);
CREATE INDEX idx_access_logs_time ON public.access_logs(access_time);
CREATE INDEX idx_access_logs_endpoint ON public.access_logs(endpoint);

ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own access logs" ON public.access_logs
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access logs" ON public.access_logs
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 6. User Files (File metadata)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_files (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  filename VARCHAR NOT NULL,
  original_filename VARCHAR,
  file_type VARCHAR,
  format VARCHAR,
  size_bytes BIGINT,
  supabase_url VARCHAR,
  uploaded_at TIMESTAMP DEFAULT NOW(),
  converted_from VARCHAR,
  metadata JSONB
);

CREATE INDEX idx_user_files_user ON public.user_files(user_id);
CREATE INDEX idx_user_files_uploaded ON public.user_files(uploaded_at);

ALTER TABLE public.user_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own files" ON public.user_files
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access files" ON public.user_files
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 7. Converted Files (Conversion tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS public.converted_files (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  original_file_id BIGINT REFERENCES public.user_files(id),
  output_format VARCHAR NOT NULL,
  output_filename VARCHAR NOT NULL,
  size_bytes BIGINT,
  supabase_url VARCHAR,
  converted_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

CREATE INDEX idx_converted_files_user ON public.converted_files(user_id);
CREATE INDEX idx_converted_files_original ON public.converted_files(original_file_id);

ALTER TABLE public.converted_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own converted files" ON public.converted_files
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access converted files" ON public.converted_files
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 8. User Data Tables (Data table metadata)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_data_tables (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  table_name VARCHAR NOT NULL,
  ticker VARCHAR,
  format VARCHAR,
  row_count INTEGER,
  columns TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  last_accessed TIMESTAMP,
  metadata JSONB,
  UNIQUE(user_id, table_name)
);

CREATE INDEX idx_user_data_tables_user ON public.user_data_tables(user_id);
CREATE INDEX idx_user_data_tables_accessed ON public.user_data_tables(last_accessed);

ALTER TABLE public.user_data_tables ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data tables" ON public.user_data_tables
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access data tables" ON public.user_data_tables
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- Triggers
-- ============================================

-- Update updated_at timestamp for user_hours
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_hours_updated_at
  BEFORE UPDATE ON public.user_hours
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- ============================================
-- Storage Buckets (Run separately in Storage UI)
-- ============================================
-- Create these buckets in Supabase Storage UI:
-- 1. user-files (private)
-- 2. user-data (private)

-- Then set RLS policies for storage (run in SQL Editor):

-- User Files Bucket Policy
INSERT INTO storage.buckets (id, name, public)
VALUES ('user-files', 'user-files', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Users can access own files" ON storage.objects
  FOR ALL
  USING (
    bucket_id = 'user-files'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- User Data Bucket Policy
INSERT INTO storage.buckets (id, name, public)
VALUES ('user-data', 'user-data', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Users can access own data" ON storage.objects
  FOR ALL
  USING (
    bucket_id = 'user-data'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- ============================================
-- Complete!
-- ============================================
-- Next steps:
-- 1. Copy your Supabase credentials to .env
-- 2. Update Python code to use Supabase PostgreSQL
-- 3. Remove DuckDB dependencies
