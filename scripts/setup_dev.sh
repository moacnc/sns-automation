#!/bin/bash
# 로컬 개발 환경 자동 설정 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "========================================"
echo "Instagram Automation - 로컬 개발 환경 설정"
echo "========================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "프로젝트 디렉토리: $PROJECT_ROOT"
echo ""

# 1. Docker 설치 확인
echo -e "${YELLOW}[1/7] Docker 설치 확인...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker가 설치되어 있지 않습니다.${NC}"
    echo "Docker 설치: https://www.docker.com/get-started"
    exit 1
fi
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose가 설치되어 있지 않습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 설치 확인 완료${NC}"
echo ""

# 2. Python 버전 확인
echo -e "${YELLOW}[2/7] Python 버전 확인...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$PYTHON_VERSION" == "3.10" ]] || [[ "$PYTHON_VERSION" > "3.9" ]]; then
    echo -e "${YELLOW}⚠ Python ${PYTHON_VERSION} 감지. Python 3.6-3.9 권장${NC}"
fi
echo -e "${GREEN}✓ Python $(python3 --version) 확인 완료${NC}"
echo ""

# 3. 가상환경 생성
echo -e "${YELLOW}[3/7] Python 가상환경 생성...${NC}"
if [ ! -d "gramaddict-env" ]; then
    python3 -m venv gramaddict-env
    echo -e "${GREEN}✓ 가상환경 생성 완료${NC}"
else
    echo -e "${GREEN}✓ 가상환경이 이미 존재합니다${NC}"
fi
echo ""

# 4. 가상환경 활성화 및 의존성 설치
echo -e "${YELLOW}[4/7] Python 패키지 설치...${NC}"
source gramaddict-env/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ 패키지 설치 완료${NC}"
echo ""

# 5. 환경변수 파일 생성
echo -e "${YELLOW}[5/7] 환경변수 파일 설정...${NC}"
if [ ! -f ".env" ]; then
    cp .env.development .env
    echo -e "${GREEN}✓ .env 파일 생성 완료 (.env.development 복사)${NC}"
else
    echo -e "${YELLOW}⚠ .env 파일이 이미 존재합니다. 건너뜁니다.${NC}"
fi
echo ""

# 6. Docker Compose로 PostgreSQL 시작
echo -e "${YELLOW}[6/7] PostgreSQL 데이터베이스 시작...${NC}"
cd docker
docker-compose down > /dev/null 2>&1 || true
docker-compose up -d postgres
echo "PostgreSQL 시작 대기 중..."
sleep 5

# PostgreSQL 연결 대기
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL 시작 완료${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ PostgreSQL 시작 실패 (타임아웃)${NC}"
        exit 1
    fi
    sleep 1
done
cd ..
echo ""

# 7. 데이터베이스 연결 테스트
echo -e "${YELLOW}[7/7] 데이터베이스 연결 테스트...${NC}"
python3 << 'EOF'
import sys
try:
    from src.utils.db_handler import DatabaseHandler
    db = DatabaseHandler()
    print("✓ 데이터베이스 연결 성공!")
    db.close()
except Exception as e:
    print(f"✗ 데이터베이스 연결 실패: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 데이터베이스 연결 테스트 완료${NC}"
else
    echo -e "${RED}✗ 데이터베이스 연결 테스트 실패${NC}"
    exit 1
fi
echo ""

# 완료 메시지
echo -e "${GREEN}========================================"
echo "✓ 로컬 개발 환경 설정 완료!"
echo "========================================${NC}"
echo ""
echo "다음 명령어로 시작하세요:"
echo ""
echo -e "${YELLOW}  # 가상환경 활성화${NC}"
echo "  source gramaddict-env/bin/activate"
echo ""
echo -e "${YELLOW}  # 디바이스 연결 확인${NC}"
echo "  python3 src/main.py --check-device"
echo ""
echo -e "${YELLOW}  # 프로그램 실행${NC}"
echo "  python3 src/main.py --config config/accounts/myaccount.yml"
echo ""
echo -e "${YELLOW}  # pgAdmin 접속 (선택사항)${NC}"
echo "  docker-compose --profile dev up -d"
echo "  http://localhost:5050"
echo "  (Email: admin@localhost.com, Password: admin123)"
echo ""
echo -e "${YELLOW}  # PostgreSQL 중지${NC}"
echo "  cd docker && docker-compose down"
echo ""
