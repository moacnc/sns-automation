#!/bin/bash
# 개발 편의 스크립트 - 자주 사용하는 명령어 모음

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function show_help() {
    echo -e "${BLUE}Instagram Automation - 개발 도구${NC}"
    echo ""
    echo "사용법: ./scripts/dev.sh [명령어]"
    echo ""
    echo "명령어:"
    echo "  setup       - 개발 환경 초기 설정"
    echo "  start       - PostgreSQL 시작"
    echo "  stop        - PostgreSQL 중지"
    echo "  restart     - PostgreSQL 재시작"
    echo "  logs        - PostgreSQL 로그 확인"
    echo "  psql        - PostgreSQL 접속"
    echo "  migrate     - 데이터베이스 마이그레이션"
    echo "  test-db     - 데이터베이스 연결 테스트"
    echo "  clean       - 데이터베이스 초기화 (주의!)"
    echo "  pgadmin     - pgAdmin 시작 (포트 5050)"
    echo "  check       - 시스템 상태 확인"
    echo "  help        - 도움말 표시"
    echo ""
}

function setup() {
    echo -e "${YELLOW}개발 환경 설정 시작...${NC}"
    bash "$SCRIPT_DIR/setup_dev.sh"
}

function start_db() {
    echo -e "${YELLOW}PostgreSQL 시작...${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose up -d postgres
    echo -e "${GREEN}✓ PostgreSQL 시작 완료${NC}"
    echo "접속 정보: localhost:5432 (DB: instagram_automation, User: postgres)"
}

function stop_db() {
    echo -e "${YELLOW}PostgreSQL 중지...${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose down
    echo -e "${GREEN}✓ PostgreSQL 중지 완료${NC}"
}

function restart_db() {
    echo -e "${YELLOW}PostgreSQL 재시작...${NC}"
    stop_db
    sleep 2
    start_db
}

function show_logs() {
    echo -e "${YELLOW}PostgreSQL 로그:${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose logs -f postgres
}

function psql_connect() {
    echo -e "${YELLOW}PostgreSQL 접속...${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose exec postgres psql -U postgres -d instagram_automation
}

function migrate() {
    echo -e "${YELLOW}데이터베이스 마이그레이션...${NC}"
    cd "$PROJECT_ROOT"
    source gramaddict-env/bin/activate 2>/dev/null || true
    python3 scripts/db_migrate.py
}

function test_db() {
    echo -e "${YELLOW}데이터베이스 연결 테스트...${NC}"
    cd "$PROJECT_ROOT"
    source gramaddict-env/bin/activate 2>/dev/null || true
    python3 << 'EOF'
from src.utils.db_handler import DatabaseHandler
try:
    db = DatabaseHandler()
    print("✓ 연결 성공!")
    db.close()
except Exception as e:
    print(f"✗ 연결 실패: {e}")
    exit(1)
EOF
}

function clean_db() {
    echo -e "${YELLOW}⚠️  데이터베이스 초기화 (모든 데이터 삭제)${NC}"
    read -p "정말 진행하시겠습니까? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        cd "$PROJECT_ROOT/docker"
        docker-compose down -v
        echo -e "${GREEN}✓ 데이터 삭제 완료${NC}"
        docker-compose up -d postgres
        echo -e "${GREEN}✓ PostgreSQL 재시작 완료${NC}"
        sleep 3
        cd "$PROJECT_ROOT"
        python3 scripts/db_migrate.py
    else
        echo "취소되었습니다."
    fi
}

function start_pgadmin() {
    echo -e "${YELLOW}pgAdmin 시작...${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose --profile dev up -d
    echo -e "${GREEN}✓ pgAdmin 시작 완료${NC}"
    echo ""
    echo "접속 정보:"
    echo "  URL: http://localhost:5050"
    echo "  Email: admin@localhost.com"
    echo "  Password: admin123"
    echo ""
    echo "PostgreSQL 서버 연결:"
    echo "  Host: postgres (또는 host.docker.internal)"
    echo "  Port: 5432"
    echo "  Database: instagram_automation"
    echo "  Username: postgres"
    echo "  Password: devpassword123"
}

function check_status() {
    echo -e "${BLUE}시스템 상태 확인${NC}"
    echo ""

    # Docker 확인
    echo -e "${YELLOW}[Docker]${NC}"
    if command -v docker &> /dev/null; then
        echo "✓ Docker 설치됨: $(docker --version | cut -d' ' -f3 | tr -d ',')"
    else
        echo "✗ Docker 미설치"
    fi

    # PostgreSQL 컨테이너 확인
    echo ""
    echo -e "${YELLOW}[PostgreSQL]${NC}"
    cd "$PROJECT_ROOT/docker"
    if docker-compose ps postgres | grep -q "Up"; then
        echo "✓ PostgreSQL 실행 중"
    else
        echo "✗ PostgreSQL 중지됨"
    fi

    # Python 확인
    echo ""
    echo -e "${YELLOW}[Python]${NC}"
    if command -v python3 &> /dev/null; then
        echo "✓ Python: $(python3 --version)"
    else
        echo "✗ Python3 미설치"
    fi

    # 가상환경 확인
    if [ -d "$PROJECT_ROOT/gramaddict-env" ]; then
        echo "✓ 가상환경 존재함"
    else
        echo "✗ 가상환경 없음 (./scripts/dev.sh setup 실행)"
    fi

    # ADB 확인
    echo ""
    echo -e "${YELLOW}[ADB]${NC}"
    if command -v adb &> /dev/null; then
        echo "✓ ADB 설치됨: $(adb version | head -n1)"
    else
        echo "✗ ADB 미설치"
    fi

    # 환경변수 파일 확인
    echo ""
    echo -e "${YELLOW}[설정 파일]${NC}"
    cd "$PROJECT_ROOT"
    if [ -f ".env" ]; then
        echo "✓ .env 파일 존재"
    else
        echo "✗ .env 파일 없음"
    fi
}

# 메인 로직
case "$1" in
    setup)
        setup
        ;;
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    logs)
        show_logs
        ;;
    psql)
        psql_connect
        ;;
    migrate)
        migrate
        ;;
    test-db)
        test_db
        ;;
    clean)
        clean_db
        ;;
    pgadmin)
        start_pgadmin
        ;;
    check)
        check_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
