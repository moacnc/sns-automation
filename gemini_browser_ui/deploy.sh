#!/bin/bash
set -e

# ============================================
# Cloud Run Deployment Script (Optimized)
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="moa-robo"
SERVICE_NAME="moa-computer-use"
REGION="asia-northeast3"  # Seoul region

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  MOA Computer Use - Cloud Run Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if gcloud is installed
echo -e "${YELLOW}[1/3] Checking gcloud CLI...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI found${NC}"
echo ""

# Set GCP project
echo -e "${YELLOW}[2/3] Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}✅ Project set to: ${PROJECT_ID}${NC}"
echo ""

# Load environment variables from .env file
ENV_ARGS=""
if [ -f "../.env" ]; then
    echo -e "${YELLOW}📋 Loading environment variables from ../.env...${NC}"

    ENV_VARS=""

    # Extract environment variables (exclude placeholders and local-only vars)
    if grep -q "GEMINI_API_KEY" ../.env; then
        GEMINI_KEY=$(grep "GEMINI_API_KEY" ../.env | cut -d '=' -f2 | tr -d '\r' | xargs)
        if [ ! -z "$GEMINI_KEY" ] && [ "$GEMINI_KEY" != "your-gemini-api-key-here" ]; then
            ENV_VARS="${ENV_VARS}GEMINI_API_KEY=${GEMINI_KEY},"
        fi
    fi

    if grep -q "GOOGLE_CLIENT_ID" ../.env; then
        CLIENT_ID=$(grep "GOOGLE_CLIENT_ID" ../.env | cut -d '=' -f2 | tr -d '\r' | xargs)
        if [ ! -z "$CLIENT_ID" ] && [ "$CLIENT_ID" != "your-client-id.apps.googleusercontent.com" ]; then
            ENV_VARS="${ENV_VARS}GOOGLE_CLIENT_ID=${CLIENT_ID},"
        fi
    fi

    if grep -q "GOOGLE_CLIENT_SECRET" ../.env; then
        CLIENT_SECRET=$(grep "GOOGLE_CLIENT_SECRET" ../.env | cut -d '=' -f2 | tr -d '\r' | xargs)
        if [ ! -z "$CLIENT_SECRET" ] && [ "$CLIENT_SECRET" != "your-client-secret" ]; then
            ENV_VARS="${ENV_VARS}GOOGLE_CLIENT_SECRET=${CLIENT_SECRET},"
        fi
    fi

    if grep -q "FLASK_SECRET_KEY" ../.env; then
        FLASK_SECRET=$(grep "FLASK_SECRET_KEY" ../.env | cut -d '=' -f2 | tr -d '\r' | xargs)
        if [ ! -z "$FLASK_SECRET" ]; then
            ENV_VARS="${ENV_VARS}FLASK_SECRET_KEY=${FLASK_SECRET},"
        fi
    fi

    # Add required Cloud Run environment variables
    ENV_VARS="${ENV_VARS}HEADLESS=true,"
    ENV_VARS="${ENV_VARS}ENVIRONMENT=production"

    # Remove trailing comma if exists
    ENV_VARS=$(echo "$ENV_VARS" | sed 's/,$//')

    if [ ! -z "$ENV_VARS" ]; then
        ENV_ARGS="--set-env-vars=${ENV_VARS}"
        echo -e "${GREEN}✅ Environment variables loaded${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    ENV_ARGS="--set-env-vars=HEADLESS=true,ENVIRONMENT=production"
fi
echo ""

# Deploy to Cloud Run with automatic build
# This uses Cloud Build automatically - no separate docker build needed!
echo -e "${YELLOW}[3/3] Building and deploying to Cloud Run...${NC}"
echo -e "${BLUE}⏱️  This will take 2-4 minutes (automatic build + deploy)${NC}"
echo ""

gcloud run deploy ${SERVICE_NAME} \
    --source=. \
    --region=${REGION} \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0 \
    ${ENV_ARGS} \
    --project=${PROJECT_ID}

echo ""
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)' \
    --project=${PROJECT_ID})

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  🎉 Deployment Successful!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Service URL:${NC} ${SERVICE_URL}"
echo -e "${BLUE}Region:${NC} ${REGION}"
echo -e "${BLUE}Project:${NC} ${PROJECT_ID}"
echo ""
echo -e "${YELLOW}📝 Important: Update OAuth Redirect URI${NC}"
echo "Add this to Google Cloud Console OAuth settings:"
echo "   ${SERVICE_URL}/auth/google/callback"
echo ""
echo -e "${YELLOW}🔧 View logs:${NC}"
echo "   gcloud run services logs tail ${SERVICE_NAME} --region=${REGION}"
echo ""
echo -e "${YELLOW}🌐 Visit your app:${NC}"
echo "   ${SERVICE_URL}"
echo ""
