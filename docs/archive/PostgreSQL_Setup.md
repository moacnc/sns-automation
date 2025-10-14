# PostgreSQL / AlloyDB 설정 가이드

## 1. PostgreSQL 데이터베이스 설정

### 1.1 로컬 PostgreSQL 설치

#### macOS (Homebrew)
```bash
# PostgreSQL 설치
brew install postgresql@15

# PostgreSQL 서비스 시작
brew services start postgresql@15

# PostgreSQL 버전 확인
psql --version
```

#### Linux (Ubuntu/Debian)
```bash
# PostgreSQL 설치
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 버전 확인
psql --version
```

#### Windows
- [PostgreSQL 공식 사이트](https://www.postgresql.org/download/windows/)에서 설치 프로그램 다운로드
- 설치 중 비밀번호 설정 필수

### 1.2 데이터베이스 생성

```bash
# PostgreSQL 접속 (기본 사용자: postgres)
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE instagram_automation;

# 사용자 생성 (선택사항)
CREATE USER instagram_user WITH PASSWORD 'your_secure_password';

# 권한 부여
GRANT ALL PRIVILEGES ON DATABASE instagram_automation TO instagram_user;

# 종료
\q
```

### 1.3 환경변수 설정

`.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일 편집:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_SSLMODE=prefer
```

---

## 2. AlloyDB 설정 (Google Cloud)

### 2.1 AlloyDB 클러스터 생성

```bash
# gcloud CLI 설치 확인
gcloud --version

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# AlloyDB 클러스터 생성
gcloud alloydb clusters create instagram-cluster \
    --region=asia-northeast3 \
    --password=YOUR_SECURE_PASSWORD
```

### 2.2 AlloyDB 인스턴스 생성

```bash
gcloud alloydb instances create instagram-primary \
    --cluster=instagram-cluster \
    --region=asia-northeast3 \
    --instance-type=PRIMARY \
    --cpu-count=2
```

### 2.3 데이터베이스 생성

```bash
# AlloyDB에 연결 (Cloud SQL Proxy 또는 Private IP)
psql "host=ALLOYDB_IP port=5432 user=postgres dbname=postgres sslmode=require"

# 데이터베이스 생성
CREATE DATABASE instagram_automation;

# 종료
\q
```

### 2.4 AlloyDB 연결 설정

#### 방법 1: Private IP (권장)
VPC 네트워크 내에서 직접 연결

`.env` 설정:
```bash
DB_HOST=10.x.x.x  # AlloyDB Private IP
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=your_alloydb_password
DB_SSLMODE=require
```

#### 방법 2: AlloyDB Auth Proxy
```bash
# AlloyDB Auth Proxy 다운로드
curl -o alloydb-auth-proxy https://storage.googleapis.com/alloydb-auth-proxy/v0.3.0/alloydb-auth-proxy.linux.amd64
chmod +x alloydb-auth-proxy

# Proxy 실행
./alloydb-auth-proxy \
  --address 0.0.0.0 \
  --port 5432 \
  projects/PROJECT_ID/locations/REGION/clusters/CLUSTER_ID/instances/INSTANCE_ID
```

`.env` 설정:
```bash
DB_HOST=localhost  # Proxy 사용 시
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=your_alloydb_password
DB_SSLMODE=require
```

---

## 3. 테이블 스키마

데이터베이스 핸들러가 자동으로 생성하지만, 수동으로 생성하려면:

```sql
-- 세션 테이블
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    device_id VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50),
    total_interactions INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_follows INTEGER DEFAULT 0,
    total_unfollows INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_sessions_username ON sessions(username);
CREATE INDEX idx_sessions_start_time ON sessions(start_time DESC);

-- 인터랙션 테이블
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    target_user VARCHAR(255),
    target_post VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_interactions_session ON interactions(session_id);
CREATE INDEX idx_interactions_timestamp ON interactions(timestamp DESC);

-- 통계 테이블
CREATE TABLE statistics (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    total_likes INTEGER DEFAULT 0,
    total_follows INTEGER DEFAULT 0,
    total_unfollows INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    sessions_count INTEGER DEFAULT 0,
    success_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, date)
);

-- 인덱스
CREATE INDEX idx_statistics_username_date ON statistics(username, date DESC);
```

---

## 4. 연결 테스트

### 4.1 psql로 직접 테스트
```bash
# 로컬
psql -h localhost -p 5432 -U postgres -d instagram_automation

# AlloyDB
psql "host=ALLOYDB_IP port=5432 user=postgres dbname=instagram_automation sslmode=require"
```

### 4.2 Python 코드로 테스트
```python
from src.utils.db_handler import DatabaseHandler

# 환경변수에서 자동 로드
db = DatabaseHandler()

# 또는 직접 설정
config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'instagram_automation',
    'user': 'postgres',
    'password': 'your_password'
}
db = DatabaseHandler(config)

# 테스트 세션 생성
import uuid
session_id = str(uuid.uuid4())
db.create_session(session_id, "test_user", "device123")

# 통계 확인
stats = db.get_session_stats(session_id)
print(stats)

db.close()
```

---

## 5. 보안 고려사항

### 5.1 비밀번호 관리
- ✅ 환경변수로 관리 (`.env` 파일)
- ✅ `.env` 파일은 Git에 커밋 금지 (`.gitignore`)
- ✅ 강력한 비밀번호 사용 (최소 16자, 특수문자 포함)

### 5.2 SSL/TLS 연결
- AlloyDB는 `DB_SSLMODE=require` 필수
- 프로덕션 환경에서는 SSL 인증서 검증 권장

### 5.3 네트워크 보안
- AlloyDB는 Private IP 사용 권장
- VPC 방화벽 규칙 설정
- 특정 IP만 접근 허용

### 5.4 접근 권한
- 최소 권한 원칙 적용
- 애플리케이션 전용 사용자 생성
- 읽기 전용 사용자 별도 생성 (분석용)

---

## 6. 백업 및 복구

### 6.1 수동 백업
```bash
# 로컬 PostgreSQL
pg_dump -U postgres -d instagram_automation > backup_$(date +%Y%m%d).sql

# 복구
psql -U postgres -d instagram_automation < backup_20251003.sql
```

### 6.2 AlloyDB 자동 백업
```bash
# AlloyDB 백업 설정
gcloud alloydb backups create backup-name \
    --cluster=instagram-cluster \
    --region=asia-northeast3
```

---

## 7. 모니터링

### 7.1 연결 상태 확인
```sql
-- 활성 연결 수
SELECT count(*) FROM pg_stat_activity;

-- 연결 상세 정보
SELECT * FROM pg_stat_activity WHERE datname = 'instagram_automation';
```

### 7.2 테이블 크기 확인
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 8. 문제 해결

### 8.1 연결 실패
```bash
# PostgreSQL 서비스 상태 확인
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# 포트 확인
lsof -i :5432
```

### 8.2 권한 오류
```sql
-- 권한 확인
\du

-- 권한 재부여
GRANT ALL PRIVILEGES ON DATABASE instagram_automation TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

### 8.3 AlloyDB 연결 오류
- Private IP 확인
- VPC 네트워크 연결 확인
- 방화벽 규칙 확인
- SSL 모드 설정 확인

---

## 참고 자료

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [AlloyDB 공식 문서](https://cloud.google.com/alloydb/docs)
- [psycopg2 문서](https://www.psycopg.org/docs/)
