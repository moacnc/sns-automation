# Instagram Automation System - Makefile
# 편리한 개발 명령어 모음

.PHONY: help setup start stop restart logs psql migrate test-db clean pgadmin check install run

# 기본 타겟
help:
	@echo "Instagram Automation - 개발 명령어"
	@echo ""
	@echo "사용법: make [명령어]"
	@echo ""
	@echo "설정:"
	@echo "  setup         - 개발 환경 초기 설정"
	@echo "  install       - Python 패키지 설치"
	@echo ""
	@echo "데이터베이스:"
	@echo "  start         - PostgreSQL 시작"
	@echo "  stop          - PostgreSQL 중지"
	@echo "  restart       - PostgreSQL 재시작"
	@echo "  logs          - PostgreSQL 로그"
	@echo "  psql          - PostgreSQL 접속"
	@echo "  migrate       - 마이그레이션 실행"
	@echo "  test-db       - DB 연결 테스트"
	@echo "  clean         - DB 초기화 (주의!)"
	@echo "  pgadmin       - pgAdmin 시작"
	@echo ""
	@echo "실행:"
	@echo "  run           - 프로그램 실행"
	@echo "  check         - 시스템 상태 확인"
	@echo ""

# 개발 환경 설정
setup:
	@bash scripts/setup_dev.sh

# Python 패키지 설치
install:
	@echo "Python 패키지 설치 중..."
	@source gramaddict-env/bin/activate && pip install -r requirements.txt
	@echo "✓ 설치 완료"

# PostgreSQL 시작
start:
	@bash scripts/dev.sh start

# PostgreSQL 중지
stop:
	@bash scripts/dev.sh stop

# PostgreSQL 재시작
restart:
	@bash scripts/dev.sh restart

# PostgreSQL 로그
logs:
	@bash scripts/dev.sh logs

# PostgreSQL 접속
psql:
	@bash scripts/dev.sh psql

# 마이그레이션
migrate:
	@bash scripts/dev.sh migrate

# DB 연결 테스트
test-db:
	@bash scripts/dev.sh test-db

# DB 초기화
clean:
	@bash scripts/dev.sh clean

# pgAdmin 시작
pgadmin:
	@bash scripts/dev.sh pgadmin

# 시스템 상태 확인
check:
	@bash scripts/dev.sh check

# 프로그램 실행
run:
	@echo "설정 파일을 지정하세요:"
	@echo "  make run CONFIG=config/accounts/myaccount.yml"

# 설정 파일 지정 실행
run-config:
	@source gramaddict-env/bin/activate && python3 src/main.py --config $(CONFIG)
