#!/bin/bash
# Quick Deploy Script - Minimal steps for fast deployment

set -e

PROJECT_ID="moa-robo"
SERVICE_NAME="moa-computer-use"
REGION="asia-northeast3"

echo "🚀 Quick deploying to Cloud Run..."
echo ""

# Build and deploy in one command
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --project=${PROJECT_ID}

# Get URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project=${PROJECT_ID})

echo ""
echo "✅ Deployed successfully!"
echo "🔗 URL: ${SERVICE_URL}"
echo ""
echo "⚠️  Don't forget to:"
echo "1. Set environment variables in Cloud Run console"
echo "2. Update Google OAuth redirect URI"
