#!/bin/bash
# Deploy REDLINE to multiple platforms
# Usage: ./deploy_all_platforms.sh [platform]

set -e

PLATFORM=${1:-""}

echo "🚀 REDLINE Multi-Platform Deployment"
echo "===================================="
echo ""

if [ -z "$PLATFORM" ]; then
    echo "Available platforms:"
    echo "  1) railway  - Railway.app (Recommended)"
    echo "  2) render   - Render.com (Best free tier)"
    echo "  3) fly      - Fly.io (Global edge)"
    echo "  4) cloudrun - Google Cloud Run (Serverless)"
    echo "  5) digitalocean - DigitalOcean App Platform"
    echo ""
    read -p "Select platform [1-5]: " CHOICE
    
    case $CHOICE in
        1) PLATFORM="railway" ;;
        2) PLATFORM="render" ;;
        3) PLATFORM="fly" ;;
        4) PLATFORM="cloudrun" ;;
        5) PLATFORM="digitalocean" ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

case $PLATFORM in
    railway)
        echo "🚂 Deploying to Railway..."
        if [ -f "./deploy_backend_railway.sh" ]; then
            ./deploy_backend_railway.sh
        else
            echo "❌ deploy_backend_railway.sh not found"
            echo "Run: railway up --docker-image keepdevops/redline:latest"
        fi
        ;;
    render)
        echo "🎨 Deploying to Render..."
        echo ""
        echo "Option 1: Via Dashboard"
        echo "  1. Go to https://render.com"
        echo "  2. New → Web Service"
        echo "  3. Connect Docker image: keepdevops/redline:latest"
        echo "  4. Set environment variables"
        echo ""
        echo "Option 2: Via Git (if you have render.yaml)"
        echo "  1. Push to Git"
        echo "  2. Connect repo in Render dashboard"
        echo "  3. Render will use render.yaml automatically"
        ;;
    fly)
        echo "✈️  Deploying to Fly.io..."
        if [ -f "./deploy_fly.sh" ]; then
            ./deploy_fly.sh
        else
            echo "❌ deploy_fly.sh not found"
            echo "Run: flyctl launch --image keepdevops/redline:latest"
        fi
        ;;
    cloudrun)
        echo "☁️  Deploying to Google Cloud Run..."
        if [ -f "./deploy_cloudrun.sh" ]; then
            ./deploy_cloudrun.sh
        else
            echo "❌ deploy_cloudrun.sh not found"
            echo "Run: gcloud run deploy redline --image keepdevops/redline:latest"
        fi
        ;;
    digitalocean)
        echo "🌊 Deploying to DigitalOcean..."
        echo ""
        echo "Via Dashboard:"
        echo "  1. Go to https://cloud.digitalocean.com/apps"
        echo "  2. Create App → Docker Hub"
        echo "  3. Image: keepdevops/redline:latest"
        echo "  4. Set environment variables"
        echo "  5. Deploy"
        ;;
    *)
        echo "❌ Unknown platform: $PLATFORM"
        echo "Available: railway, render, fly, cloudrun, digitalocean"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment process initiated!"
echo ""

