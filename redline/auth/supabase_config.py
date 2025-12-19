"""Supabase client configuration"""
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

# Client for user-facing operations (uses anon key with RLS)
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin client for backend operations (bypasses RLS)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
