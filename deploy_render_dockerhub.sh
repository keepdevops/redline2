#!/bin/bash

# Deploy Redline to Render using Docker Hub Image
# This script guides you through deploying keepdevops/redline:latest to Render

set -e

echo "🚀 REDLINE - Render Deployment (Docker Hub)"
echo "==========================================="
echo ""

echo "📦 Docker Hub Image: keepdevops/redline:latest"
echo ""

echo "📋 Deployment Steps:"
echo ""
echo "1. Go to Render Dashboard: https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Select 'Deploy an existing image from a registry'"
echo "4. Enter Image URL: keepdevops/redline:latest"
echo "5. Click 'Connect'"
echo ""
echo "6. Configure Service:"
echo "   • Name: redline-backend (or your preferred name)"
echo "   • Region: Choose closest to users"
echo "   • Plan: Starter ($7/month) or Free"
echo ""
echo "7. Docker Command (auto-filled, but verify):"
echo "   gunicorn --bind 0.0.0.0:\$PORT --workers 1 --threads 4 --timeout 120 --worker-class gthread --access-logfile - --error-logfile - web_app:create_app()"
echo ""
echo "8. Add Environment Variables (see RENDER_DOCKER_HUB_SETUP.md for full list)"
echo ""
echo "9. Click 'Create Web Service'"
echo ""
echo "✅ Alternative: Use render.yaml"
echo ""
echo "If you have render.yaml in your repo:"
echo "1. Push render.yaml to GitHub"
echo "2. In Render, connect your GitHub repository"
echo "3. Render will auto-detect render.yaml and use it"
echo ""
echo "📝 Current render.yaml configuration:"
echo "   • Image: keepdevops/redline:latest"
echo "   • Command: Gunicorn with optimized settings"
echo "   • Plan: Starter"
echo ""
echo "🔄 To Update Image:"
echo "   1. Push new image to Docker Hub: docker push keepdevops/redline:latest"
echo "   2. In Render Dashboard → Settings → Docker Image"
echo "   3. Update tag or click 'Redeploy'"
echo ""
echo "🌐 After Deployment:"
echo "   • Service URL: https://redline-backend.onrender.com"
echo "   • Custom Domain: https://app.redfindat.com (after DNS setup)"
echo ""



