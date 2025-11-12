#!/bin/bash
# Deploy REDLINE to Google Cloud Run

set -e

echo "☁️  REDLINE Google Cloud Run Deployment"
echo "========================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found."
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please login to Google Cloud:"
    gcloud auth login
fi

# Get project ID
echo ""
read -p "Enter your GCP Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID is required!"
    exit 1
fi

gcloud config set project $PROJECT_ID

# Get region
echo ""
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

# Set environment variables
echo ""
echo "🔧 Configuring environment variables..."
ENV_VARS="FLASK_ENV=production,FLASK_APP=web_app.py,PORT=8080,HOST=0.0.0.0"

# Generate secret key
read -p "Generate new SECRET_KEY? (y/n): " GEN_KEY
if [ "$GEN_KEY" = "y" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
fi

# Deploy
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy redline \
    --image keepdevops/redline:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars $ENV_VARS \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Your Cloud Run URL:"
gcloud run services describe redline --region $REGION --format="value(status.url)"
echo ""
echo "🔍 Test your deployment:"
SERVICE_URL=$(gcloud run services describe redline --region $REGION --format="value(status.url)")
echo "   curl $SERVICE_URL/health"
echo ""

