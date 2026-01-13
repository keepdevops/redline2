#!/bin/bash
# Quick Supabase Setup Script for VarioSync

set -e

echo "🔧 VarioSync Supabase Setup"
echo "============================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Supabase credentials!"
    echo "   See SUPABASE_SETUP.md for detailed instructions"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Check if Supabase variables are set
if grep -q "your-project-id" .env 2>/dev/null; then
    echo "⚠️  WARNING: .env file still contains placeholder values"
    echo "   Please update .env with your actual Supabase credentials"
    echo ""
fi

echo "📋 Next steps:"
echo "1. Get your Supabase credentials from https://app.supabase.com"
echo "2. Edit .env and add your SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, and SUPABASE_JWT_SECRET"
echo "3. Run the SQL schema in Supabase SQL Editor (setup_supabase_schema.sql)"
echo "4. Restart the container: docker-compose restart variosync-web"
echo ""
echo "📖 For detailed instructions, see SUPABASE_SETUP.md"
