#!/bin/bash

# Deploy Splash Page to Render
# This script helps you deploy the splash page to Render as a static site

set -e

echo "🚀 REDFINDAT Splash Page - Render Deployment"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "splash/index.html" ]; then
    echo "❌ Error: splash/index.html not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "✅ Splash page found: splash/index.html"
echo ""

echo "📋 Deployment Steps for Render:"
echo ""
echo "1. Go to Render Dashboard: https://dashboard.render.com"
echo "2. Click 'New +' → 'Static Site'"
echo "3. Connect your GitHub repository"
echo "4. Configure the service:"
echo "   • Name: redfindat-splash"
echo "   • Branch: main (or your default branch)"
echo "   • Root Directory: (leave empty)"
echo "   • Build Command: (leave empty)"
echo "   • Publish Directory: splash"
echo ""
echo "5. Click 'Create Static Site'"
echo ""
echo "6. After deployment, you'll get a URL like:"
echo "   https://redfindat-splash.onrender.com"
echo ""
echo "7. Configure Custom Domain (optional):"
echo "   • In Render dashboard, go to your static site"
echo "   • Click 'Settings' → 'Custom Domains'"
echo "   • Add: redfindat.com"
echo "   • Update DNS: CNAME @ → redfindat-splash.onrender.com"
echo ""
echo "📝 Files to deploy:"
echo "   • splash/index.html (main page)"
if [ -f "splash/redfindat-movie.mp4" ]; then
    echo "   • splash/redfindat-movie.mp4 (video)"
else
    echo "   ⚠️  splash/redfindat-movie.mp4 (not found - video won't display)"
fi
echo ""
echo "✅ Ready to deploy!"
echo ""
echo "🌐 After deployment:"
echo "   • Splash page: https://redfindat.com (if DNS configured)"
echo "   • App: https://app.redfindat.com"
echo ""

