#!/bin/bash
# Docker Test Runner Script
# Usage: ./docker-test.sh [phase]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Instagram Automation - Docker Test Runner${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    echo "Please install docker-compose first"
    exit 1
fi

# Build Docker image
echo -e "${YELLOW}[1/3] Building Docker image...${NC}"
docker-compose build instagram-automation

echo ""
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Start container
echo -e "${YELLOW}[2/3] Starting Docker container...${NC}"
docker-compose up -d instagram-automation

echo ""
echo -e "${GREEN}✓ Container started${NC}"
echo ""

# Run tests based on phase argument
PHASE=${1:-all}

echo -e "${YELLOW}[3/3] Running tests (Phase: $PHASE)...${NC}"
echo ""

case $PHASE in
  1)
    echo -e "${BLUE}Running Phase 1 Tests...${NC}"
    docker-compose exec instagram-automation python3 tests/phase1_infrastructure/test_device_connection.py
    ;;
  2)
    echo -e "${BLUE}Running Phase 2 Tests...${NC}"
    docker-compose exec instagram-automation python3 tests/phase2_navigation/test_tab_navigation.py
    docker-compose exec instagram-automation python3 tests/phase2_navigation/test_search_user.py
    ;;
  3)
    echo -e "${BLUE}Running Phase 3 Tests...${NC}"
    docker-compose exec instagram-automation python3 tests/phase3_vision/test_profile_ocr.py
    docker-compose exec instagram-automation python3 tests/phase3_vision/test_content_filter.py
    ;;
  4)
    echo -e "${BLUE}Running Phase 4 Tests...${NC}"
    docker-compose exec instagram-automation python3 tests/phase4_integration/test_profile_scraping.py
    ;;
  all)
    echo -e "${BLUE}Running All Tests (Phase 1-4)...${NC}"
    docker-compose exec instagram-automation python3 tests/phase1_infrastructure/test_device_connection.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase1_infrastructure/test_instagram_launch.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase2_navigation/test_tab_navigation.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase2_navigation/test_search_user.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase3_vision/test_profile_ocr.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase3_vision/test_content_filter.py
    echo ""
    docker-compose exec instagram-automation python3 tests/phase4_integration/test_profile_scraping.py
    ;;
  shell)
    echo -e "${BLUE}Opening interactive shell...${NC}"
    docker-compose exec instagram-automation /bin/bash
    exit 0
    ;;
  *)
    echo -e "${RED}Unknown phase: $PHASE${NC}"
    echo "Usage: ./docker-test.sh [1|2|3|4|all|shell]"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Tests completed!${NC}"
echo -e "${GREEN}================================${NC}"
