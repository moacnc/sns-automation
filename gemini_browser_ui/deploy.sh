#!/bin/bash
set -e

# ============================================
# Cloud Run Deployment Script
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
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  MOA Computer Use - Cloud Run Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if required tools are installed
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Set GCP project
echo -e "${YELLOW}[2/7] Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}✅ Project set to: ${PROJECT_ID}${NC}"
echo ""

# Enable required APIs
echo -e "${YELLOW}[3/7] Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project=${PROJECT_ID}
echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Build Docker image using Cloud Build (faster than local build)
echo -e "${YELLOW}[4/7] Building Docker image with Cloud Build...${NC}"
echo "This may take 3-5 minutes..."
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}
echo -e "${GREEN}✅ Docker image built: ${IMAGE_NAME}${NC}"
echo ""

# Check if .env file exists for environment variables
ENV_ARGS=""
if [ -f "../.env" ]; then
    echo -e "${YELLOW}[5/7] Loading environment variables from ../.env...${NC}"

    # Important: PORT is automatically set by Cloud Run - do not include it
    ENV_VARS=""

    # Add required variables (exclude PORT, DB settings, local-only vars)
    if grep -q "GEMINI_API_KEY" ../.env; then
        GEMINI_KEY=$(grep "GEMINI_API_KEY" ../.env | cut -d '=' -f2 | tr -d '\r')
        if [ ! -z "$GEMINI_KEY" ] && [ "$GEMINI_KEY" != "your-gemini-api-key-here" ]; then
            ENV_VARS="${ENV_VARS}GEMINI_API_KEY=${GEMINI_KEY},"
        fi
    fi

    if grep -q "GOOGLE_CLIENT_ID" ../.env; then
        CLIENT_ID=$(grep "GOOGLE_CLIENT_ID" ../.env | cut -d '=' -f2 | tr -d '\r')
        if [ ! -z "$CLIENT_ID" ] && [ "$CLIENT_ID" != "your-client-id.apps.googleusercontent.com" ]; then
            ENV_VARS="${ENV_VARS}GOOGLE_CLIENT_ID=${CLIENT_ID},"
        fi
    fi

    if grep -q "GOOGLE_CLIENT_SECRET" ../.env; then
        CLIENT_SECRET=$(grep "GOOGLE_CLIENT_SECRET" ../.env | cut -d '=' -f2 | tr -d '\r')
        if [ ! -z "$CLIENT_SECRET" ] && [ "$CLIENT_SECRET" != "your-client-secret" ]; then
            ENV_VARS="${ENV_VARS}GOOGLE_CLIENT_SECRET=${CLIENT_SECRET},"
        fi
    fi

    if grep -q "FLASK_SECRET_KEY" ../.env; then
        FLASK_SECRET=$(grep "FLASK_SECRET_KEY" ../.env | cut -d '=' -f2 | tr -d '\r')
        if [ ! -z "$FLASK_SECRET" ]; then
            ENV_VARS="${ENV_VARS}FLASK_SECRET_KEY=${FLASK_SECRET},"
        fi
    fi

    # Add HEADLESS=true for Cloud Run
    ENV_VARS="${ENV_VARS}HEADLESS=true"

    # Remove trailing comma if exists
    ENV_VARS=$(echo "$ENV_VARS" | sed 's/,$//')

    if [ ! -z "$ENV_VARS" ]; then
        ENV_ARGS="--set-env-vars ${ENV_VARS}"
        echo -e "${GREEN}✅ Environment variables loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  No valid environment variables found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found - using default settings${NC}"
    echo -e "${YELLOW}   You'll need to set environment variables manually after deployment${NC}"
fi
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}[6/7] Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    ${ENV_ARGS} \
    --project=${PROJECT_ID}

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""

# Get service URL
echo -e "${YELLOW}[7/7] Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --format 'value(status.url)' \
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
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Update Google OAuth Redirect URI:"
echo "   ${SERVICE_URL}/auth/google/callback"
echo ""
echo "2. Update .env file with production URL:"
echo "   OAUTH_REDIRECT_URI=${SERVICE_URL}/auth/google/callback"
echo ""
echo "3. Visit your application:"
echo "   ${SERVICE_URL}"
echo ""
echo -e "${YELLOW}🔧 Manage your service:${NC}"
echo "   https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo ""
