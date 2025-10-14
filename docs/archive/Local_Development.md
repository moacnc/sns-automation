# 로컬 개발 환경 가이드

## 빠른 시작 (Quick Start)

### 1. 자동 설정 (권장)

```bash
# 한 번에 모든 설정 완료
./scripts/setup_dev.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- ✅ Docker 및 Python 확인
- ✅ Python 가상환경 생성
- ✅ 패키지 설치
- ✅ 환경변수 파일 생성
- ✅ PostgreSQL 시작
- ✅ 데이터베이스 연결 테스트

### 2. 수동 설정

```bash
# 1. 가상환경 생성
python3 -m venv gramaddict-env
source gramaddict-env/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.development .env

# 4. PostgreSQL 시작
cd docker
docker-compose up -d postgres
cd ..

# 5. 마이그레이션
python3 scripts/db_migrate.py
```

---

## 개발 도구 사용법

### Makefile 사용 (간편)

```bash
# 도움말
make help

# 개발 환경 설정
make setup

# PostgreSQL 시작/중지
make start
make stop
make restart

# 로그 확인
make logs

# DB 접속
make psql

# 마이그레이션
make migrate

# DB 연결 테스트
make test-db

# 시스템 상태 확인
make check
```

### 개발 스크립트 사용

```bash
# 모든 명령어 확인
./scripts/dev.sh help

# PostgreSQL 관리
./scripts/dev.sh start      # 시작
./scripts/dev.sh stop       # 중지
./scripts/dev.sh restart    # 재시작
./scripts/dev.sh logs       # 로그 확인

# 데이터베이스
./scripts/dev.sh psql       # PostgreSQL 접속
./scripts/dev.sh migrate    # 마이그레이션
./scripts/dev.sh test-db    # 연결 테스트
./scripts/dev.sh clean      # 초기화 (주의!)

# 도구
./scripts/dev.sh pgadmin    # pgAdmin 시작
./scripts/dev.sh check      # 상태 확인
```

---

## Docker Compose 구성

### 서비스 구성

1. **postgres** - PostgreSQL 15 데이터베이스
   - 포트: 5432
   - 데이터베이스: instagram_automation
   - 사용자: postgres
   - 비밀번호: devpassword123

2. **pgadmin** - 데이터베이스 관리 도구 (선택사항)
   - 포트: 5050
   - 이메일: admin@localhost.com
   - 비밀번호: admin123

### 기본 명령어

```bash
cd docker

# PostgreSQL만 시작
docker-compose up -d postgres

# PostgreSQL + pgAdmin 시작
docker-compose --profile dev up -d

# 중지
docker-compose down

# 로그 확인
docker-compose logs -f postgres

# 데이터 포함 완전 삭제
docker-compose down -v
```

---

## pgAdmin 사용법

### 1. pgAdmin 시작

```bash
make pgadmin
# 또는
./scripts/dev.sh pgadmin
# 또는
cd docker && docker-compose --profile dev up -d
```

### 2. 브라우저 접속

```
URL: http://localhost:5050
Email: admin@localhost.com
Password: admin123
```

### 3. PostgreSQL 서버 연결

1. 좌측 "Servers" 우클릭 → "Register" → "Server"
2. General 탭:
   - Name: Instagram Automation (또는 원하는 이름)
3. Connection 탭:
   - Host: postgres (또는 host.docker.internal)
   - Port: 5432
   - Maintenance database: postgres
   - Username: postgres
   - Password: devpassword123
4. Save

---

## 데이터베이스 직접 접속

### psql 사용

```bash
# 컨테이너 내부에서 접속
make psql

# 또는 직접 접속
docker exec -it instagram-automation-db psql -U postgres -d instagram_automation
```

### 자주 사용하는 SQL 명령어

```sql
-- 테이블 목록
\dt

-- 테이블 구조 확인
\d sessions
\d interactions
\d statistics

-- 데이터 조회
SELECT * FROM sessions ORDER BY start_time DESC LIMIT 10;
SELECT * FROM interactions WHERE session_id = 'SESSION_ID';

-- 통계
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM interactions;

-- 사용자별 통계
SELECT username, COUNT(*) as session_count
FROM sessions
GROUP BY username;

-- 종료
\q
```

---

## 개발 워크플로우

### 일반적인 개발 순서

```bash
# 1. 개발 환경 시작
make start

# 2. 가상환경 활성화
source gramaddict-env/bin/activate

# 3. 코드 수정
# (에디터로 코드 편집)

# 4. 테스트
python3 src/main.py --check-device

# 5. 실행
python3 src/main.py --config config/accounts/myaccount.yml

# 6. 로그 확인
make logs

# 7. DB 확인
make psql

# 8. 종료
make stop
```

### 데이터베이스 스키마 변경 시

```bash
# 1. db_handler.py 수정

# 2. 기존 DB 초기화 (개발 환경)
make clean

# 3. 마이그레이션 실행
make migrate

# 4. 테스트
make test-db
```

---

## 문제 해결

### PostgreSQL이 시작되지 않음

```bash
# 로그 확인
make logs

# 포트 충돌 확인
lsof -i :5432

# 컨테이너 완전 삭제 후 재시작
cd docker
docker-compose down -v
docker-compose up -d postgres
```

### 데이터베이스 연결 실패

```bash
# 연결 테스트
make test-db

# .env 파일 확인
cat .env

# PostgreSQL 상태 확인
docker ps | grep postgres
```

### 패키지 설치 오류

```bash
# 가상환경 재생성
rm -rf gramaddict-env
python3 -m venv gramaddict-env
source gramaddict-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 마이그레이션 오류

```bash
# DB 완전 초기화
make clean

# 마이그레이션 재실행
make migrate
```

---

## 환경변수 설정

### 로컬 개발 (.env.development)

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=devpassword123
DB_SSLMODE=disable
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### 커스텀 설정 (.env)

```bash
# .env.development 복사
cp .env.development .env

# 필요한 값 수정
vi .env
```

---

## 유용한 팁

### 1. 빠른 재시작

```bash
# PostgreSQL 재시작
make restart
```

### 2. 실시간 로그 모니터링

```bash
# 터미널 1: PostgreSQL 로그
make logs

# 터미널 2: 애플리케이션 로그
tail -f logs/custom/app_*.log
```

### 3. 데이터베이스 백업

```bash
# 백업
docker exec instagram-automation-db pg_dump -U postgres instagram_automation > backup.sql

# 복구
cat backup.sql | docker exec -i instagram-automation-db psql -U postgres -d instagram_automation
```

### 4. 성능 모니터링

```bash
# PostgreSQL 연결 수 확인
make psql
SELECT count(*) FROM pg_stat_activity;

# 테이블 크기 확인
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 다음 단계

1. ✅ 로컬 환경 설정 완료
2. ⏩ Android 디바이스 연결 ([README.md](../README.md) 참고)
3. ⏩ 계정 설정 파일 생성
4. ⏩ 테스트 실행
5. ⏩ 실제 개발 시작

---

## 참고 자료

- [README.md](../README.md) - 전체 설치 가이드
- [PostgreSQL_Setup.md](PostgreSQL_Setup.md) - PostgreSQL 상세 설정
- [개발문서.md](개발문서.md) - 프로젝트 아키텍처
