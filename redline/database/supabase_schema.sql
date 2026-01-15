-- REDLINE Supabase Database Schema
-- Production-ready schema for scalable time-series data processing SaaS
-- Supports multi-tenant architecture with Row Level Security (RLS)

-- ============================================================================
-- 1. User Profile (extends auth.users)
-- ============================================================================
create table if not exists profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    display_name text,
    avatar_url text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- RLS: users can only read/update their own profile
alter table profiles enable row level security;

create policy "Users can view own profile" 
    on profiles for select 
    using (auth.uid() = id);

create policy "Users can update own profile" 
    on profiles for update 
    using (auth.uid() = id);

-- Auto-create profile on user signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, email, display_name)
    values (new.id, new.email, new.raw_user_meta_data->>'display_name');
    return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- ============================================================================
-- 2. Subscription Plans (static, admin-managed)
-- ============================================================================
create table if not exists subscription_plans (
    id serial primary key,
    name text not null,               -- "5 Hours Pack", "10 Hours Pack", etc.
    hours numeric not null,
    price_usd numeric not null,
    stripe_price_id text unique,      -- Stripe Price ID for Checkout
    is_active boolean default true,
    sort_order integer default 0,
    created_at timestamptz default now()
);

-- No RLS — public read access (or admin only)
-- Insert default plans
insert into subscription_plans (name, hours, price_usd, stripe_price_id, sort_order) values
    ('5 Hours Pack', 5, 25.00, null, 1),
    ('10 Hours Pack', 10, 45.00, null, 2),
    ('20 Hours Pack', 20, 80.00, null, 3),
    ('50 Hours Pack', 50, 180.00, null, 4)
on conflict do nothing;

-- ============================================================================
-- 3. User Subscriptions (current subscription state + remaining hours)
-- ============================================================================
create table if not exists user_subscriptions (
    id serial primary key,
    user_id uuid not null references profiles(id) on delete cascade,
    plan_id integer references subscription_plans(id),
    status text not null default 'active',  -- 'active', 'trialing', 'canceled', 'past_due'
    remaining_hours numeric not null default 0,
    current_period_start timestamptz,
    current_period_end timestamptz,
    stripe_subscription_id text,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    unique(user_id)
);

alter table user_subscriptions enable row level security;

create policy "Users see own subscription" 
    on user_subscriptions
    for all 
    using (auth.uid() = user_id) 
    with check (auth.uid() = user_id);

-- Index for fast lookups
create index if not exists idx_user_subscriptions_user_id on user_subscriptions(user_id);

-- ============================================================================
-- 4. Stripe Customer Mapping
-- ============================================================================
create table if not exists stripe_customers (
    user_id uuid primary key references profiles(id) on delete cascade,
    stripe_customer_id text not null unique,
    created_at timestamptz default now()
);

alter table stripe_customers enable row level security;

create policy "Users see own Stripe customer" 
    on stripe_customers
    using (auth.uid() = user_id);

-- ============================================================================
-- 5. Stripe Payments (audit log of successful payments)
-- ============================================================================
create table if not exists stripe_payments (
    id bigserial primary key,
    user_id uuid not null references profiles(id) on delete cascade,
    stripe_invoice_id text unique,
    stripe_payment_intent_id text,
    amount_usd numeric not null,
    hours_granted numeric not null,
    status text not null,  -- 'pending', 'succeeded', 'failed', 'refunded'
    created_at timestamptz default now()
);

alter table stripe_payments enable row level security;

create policy "Users see own payments" 
    on stripe_payments
    using (auth.uid() = user_id);

create index if not exists idx_stripe_payments_user_id on stripe_payments(user_id);
create index if not exists idx_stripe_payments_invoice_id on stripe_payments(stripe_invoice_id);

-- ============================================================================
-- 6. Time-Series Collections (logical groupings/folders)
-- ============================================================================
create table if not exists time_series_collections (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    name text not null,
    description text,
    tags jsonb,                             -- ["stocks", "crypto", "sensors"]
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

alter table time_series_collections enable row level security;

create policy "Users own their collections" 
    on time_series_collections
    for all
    using (auth.uid() = user_id) 
    with check (auth.uid() = user_id);

create index if not exists idx_ts_collections_user_id on time_series_collections(user_id);

-- ============================================================================
-- 7. Time-Series Metadata (one row per series_id)
-- ============================================================================
create table if not exists time_series_metadata (
    id uuid primary key default gen_random_uuid(),
    collection_id uuid references time_series_collections(id) on delete cascade,
    series_id text not null,                -- AAPL, SENSOR-001, etc.
    name text,
    description text,
    measurement_keys jsonb not null,        -- ["temperature", "humidity"] or ["open", "close", "vol"]
    first_timestamp timestamptz,
    last_timestamp timestamptz,
    row_count bigint,
    source_format text,
    storage_key text,                       -- S3/Wasabi key for Parquet file
    storage_bucket text,                    -- S3/Wasabi bucket name
    last_updated timestamptz default now(),
    unique (collection_id, series_id)
);

alter table time_series_metadata enable row level security;

create policy "Users own their series metadata" 
    on time_series_metadata
    for all
    using (
        exists (
            select 1 from time_series_collections c
            where c.id = collection_id and c.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from time_series_collections c
            where c.id = collection_id and c.user_id = auth.uid()
        )
    );

-- Performance indexes
create index if not exists idx_ts_metadata_collection_id on time_series_metadata(collection_id);
create index if not exists idx_ts_metadata_series_id on time_series_metadata(series_id);
create index if not exists idx_ts_metadata_user_collection on time_series_metadata(collection_id, series_id);

-- ============================================================================
-- 8. API Downloader Configurations (saved configs per user)
-- ============================================================================
create table if not exists api_downloader_configs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    name text not null,
    config_json jsonb not null,             -- entire apiDownloaderConfig object
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

alter table api_downloader_configs enable row level security;

create policy "Users own their downloader configs" 
    on api_downloader_configs
    for all
    using (auth.uid() = user_id) 
    with check (auth.uid() = user_id);

create index if not exists idx_api_configs_user_id on api_downloader_configs(user_id);

-- ============================================================================
-- 9. Analysis / ML Configurations
-- ============================================================================
create table if not exists analysis_configs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    name text not null,
    config_json jsonb not null,             -- analysisConfig + mlConfig combined
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

alter table analysis_configs enable row level security;

create policy "Users own their analysis configs" 
    on analysis_configs
    for all
    using (auth.uid() = user_id) 
    with check (auth.uid() = user_id);

create index if not exists idx_analysis_configs_user_id on analysis_configs(user_id);

-- ============================================================================
-- 10. Usage Logs (granular usage tracking for billing reconciliation)
-- ============================================================================
create table if not exists usage_logs (
    id bigserial primary key,
    user_id uuid not null references profiles(id) on delete cascade,
    event_type text not null,               -- download, analysis, ml_train, query, etc.
    duration_hours numeric not null,
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    success boolean default true,
    metadata jsonb,                         -- {"series_ids": [...], "query": "...", "ticker": "AAPL"}
    created_at timestamptz default now()
);

alter table usage_logs enable row level security;

create policy "Users see own usage" 
    on usage_logs
    using (auth.uid() = user_id);

-- Performance indexes
create index if not exists idx_usage_logs_user_started on usage_logs(user_id, started_at);
create index if not exists idx_usage_logs_event_type on usage_logs(event_type);
create index if not exists idx_usage_logs_created_at on usage_logs(created_at);

-- ============================================================================
-- 11. Audit Logs (optional high-level audit trail for compliance)
-- ============================================================================
create table if not exists audit_logs (
    id bigserial primary key,
    user_id uuid references profiles(id) on delete set null,
    action text not null,                   -- create, update, delete, download, etc.
    entity_type text not null,              -- collection, series, config, etc.
    entity_id uuid,
    timestamp timestamptz default now(),
    details jsonb                           -- Additional context
);

-- RLS: Users can see their own audit logs, admins see all
alter table audit_logs enable row level security;

create policy "Users see own audit logs" 
    on audit_logs
    using (auth.uid() = user_id);

create index if not exists idx_audit_logs_user_timestamp on audit_logs(user_id, timestamp);
create index if not exists idx_audit_logs_entity on audit_logs(entity_type, entity_id);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to deduct hours atomically (prevents race conditions)
create or replace function deduct_hours(p_user_id uuid, p_hours numeric)
returns boolean as $$
declare
    v_remaining numeric;
begin
    update user_subscriptions
    set remaining_hours = greatest(remaining_hours - p_hours, 0),
        updated_at = now()
    where user_id = p_user_id
    returning remaining_hours into v_remaining;
    
    -- Return true if user has sufficient hours, false otherwise
    return coalesce(v_remaining, 0) >= 0;
end;
$$ language plpgsql security definer;

-- Function to add hours (for Stripe webhook)
create or replace function add_hours(p_user_id uuid, p_hours numeric)
returns void as $$
begin
    insert into user_subscriptions (user_id, remaining_hours, status)
    values (p_user_id, p_hours, 'active')
    on conflict (user_id) 
    do update set 
        remaining_hours = user_subscriptions.remaining_hours + p_hours,
        updated_at = now();
end;
$$ language plpgsql security definer;

-- Function to check if user has sufficient hours
create or replace function check_usage_hours(p_user_id uuid, p_required_hours numeric default 0.01)
returns boolean as $$
declare
    v_remaining numeric;
begin
    select remaining_hours into v_remaining
    from user_subscriptions
    where user_id = p_user_id;
    
    return coalesce(v_remaining, 0) >= p_required_hours;
end;
$$ language plpgsql security definer;

-- Function to get user's remaining hours
create or replace function get_remaining_hours(p_user_id uuid)
returns numeric as $$
declare
    v_hours numeric;
begin
    select remaining_hours into v_hours
    from user_subscriptions
    where user_id = p_user_id;
    
    return coalesce(v_hours, 0);
end;
$$ language plpgsql security definer;

-- ============================================================================
-- Triggers for updated_at timestamps
-- ============================================================================

-- Auto-update updated_at on profiles
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger update_profiles_updated_at
    before update on profiles
    for each row execute procedure update_updated_at_column();

create trigger update_user_subscriptions_updated_at
    before update on user_subscriptions
    for each row execute procedure update_updated_at_column();

create trigger update_time_series_collections_updated_at
    before update on time_series_collections
    for each row execute procedure update_updated_at_column();

create trigger update_api_downloader_configs_updated_at
    before update on api_downloader_configs
    for each row execute procedure update_updated_at_column();

create trigger update_analysis_configs_updated_at
    before update on analysis_configs
    for each row execute procedure update_updated_at_column();

-- ============================================================================
-- Realtime Subscriptions (optional, for live updates)
-- ============================================================================

-- Enable realtime on user_subscriptions (for live remaining hours display)
alter publication supabase_realtime add table user_subscriptions;

-- Enable realtime on usage_logs (for admin dashboard)
alter publication supabase_realtime add table usage_logs;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

comment on table profiles is 'Extended user information (extends auth.users)';
comment on table subscription_plans is 'Predefined subscription packages (5h, 10h, 20h, 50h packs)';
comment on table user_subscriptions is 'Current subscription state + remaining hours for each user';
comment on table stripe_customers is 'Mapping between Supabase user and Stripe customer';
comment on table stripe_payments is 'Audit log of successful payments + granted hours';
comment on table time_series_collections is 'Logical groupings of time-series data owned by a user';
comment on table time_series_metadata is 'Metadata about each individual time-series (schema, source, stats)';
comment on table api_downloader_configs is 'Per-user saved API download configurations';
comment on table analysis_configs is 'Saved analysis / ML configurations per user';
comment on table usage_logs is 'Granular usage tracking (for billing reconciliation & debugging)';
comment on table audit_logs is 'Optional high-level audit trail (optional for compliance)';
