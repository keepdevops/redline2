#!/bin/bash

# Deploy Splash Page to Cloudflare Pages
# This is the RECOMMENDED approach since redfindat.com is on Cloudflare

set -e

echo "🚀 REDFINDAT Splash Page - Cloudflare Pages Deployment"
echo "======================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "splash/index.html" ]; then
    echo "❌ Error: splash/index.html not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "✅ Splash page found: splash/index.html"
echo ""

echo "📋 Deployment Steps for Cloudflare Pages:"
echo ""
echo "1. Go to Cloudflare Dashboard: https://dash.cloudflare.com"
echo "2. Click 'Workers & Pages' → 'Pages'"
echo "3. Click 'Create a project'"
echo "4. Connect your GitHub repository"
echo "5. Configure the project:"
echo "   • Project name: redfindat-splash"
echo "   • Production branch: main (or your default branch)"
echo "   • Framework preset: None"
echo "   • Build command: (leave empty)"
echo "   • Build output directory: splash"
echo ""
echo "6. Click 'Save and Deploy'"
echo ""
echo "7. After deployment, you'll get a URL like:"
echo "   https://redfindat-splash.pages.dev"
echo ""
echo "8. Configure Custom Domain:"
echo "   • In your Pages project, click 'Custom domains'"
echo "   • Click 'Set up a custom domain'"
echo "   • Enter: redfindat.com"
echo "   • Cloudflare will automatically configure DNS"
echo ""
echo "9. Update DNS (if needed):"
echo "   • Cloudflare Dashboard → DNS → Records"
echo "   • Ensure CNAME '@' points to: redfindat-splash.pages.dev"
echo "   • Ensure CNAME 'app' points to: your-render-service.onrender.com"
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
echo "   • Splash page: https://redfindat.com"
echo "   • App: https://app.redfindat.com"
echo ""
echo "💡 Benefits of Cloudflare Pages:"
echo "   • FREE hosting"
echo "   • Fast global CDN"
echo "   • Automatic SSL"
echo "   • Easy custom domain setup"
echo "   • Perfect for static sites"
echo ""

