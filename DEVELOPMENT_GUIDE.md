# Instagram 자동화 시스템 - 개발 가이드

**버전**: 3.0 (통합)
**최종 수정**: 2025-10-10
**목표**: 해시태그 스토리 리스토리 + 프로필 정보 수집 및 DM 발송

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [빠른 시작 (15분)](#2-빠른-시작-15분)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [핵심 기능 구현](#4-핵심-기능-구현)
5. [개발 환경 설정](#5-개발-환경-설정)
6. [AI Agents 사용법](#6-ai-agents-사용법)
7. [데이터베이스 설정](#7-데이터베이스-설정)
8. [안전성 및 리스크 관리](#8-안전성-및-리스크-관리)
9. [구현 로드맵](#9-구현-로드맵)
10. [문제 해결](#10-문제-해결)

---

## 1. 프로젝트 개요

### 1.1 목표

본 시스템은 두 가지 핵심 기능을 제공합니다:

#### ✅ 기능 1: 해시태그 스토리 자동 리스토리 (필터링)
- 내 계정으로 로그인
- 특정 해시태그 스토리 검색
- **불량 단어 필터링** (욕설, 광고, 부적절한 내용)
- 안전한 스토리만 자동 리스토리

#### ✅ 기능 2: 프로필 정보 수집 및 DM 발송
- 특정 프로필 검색 (조건 기반)
- 프로필 정보 자동 수집:
  - 팔로워/팔로잉/포스팅 수
  - 최근 게시물 및 댓글
  - 참여율(Engagement Rate)
- **AI 기반 맞춤형 DM** 자동 발송

### 1.2 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| **AI Layer** | OpenAI Agents SDK | 콘텐츠 필터링, DM 생성, 작업 계획 |
| **Base Framework** | GramAddict 3.x | Instagram UI 자동화 |
| **Core Engine** | UIAutomator2 | Android UI 제어 |
| **Programming** | Python 3.9-3.11 | 메인 언어 |
| **Database** | PostgreSQL/AlloyDB | 세션 로그, 프로필 데이터 |
| **Device Control** | ADB | Android 디바이스 연결 |
| **Logging** | Loguru | 구조화된 로깅 |

### 1.3 개발 전략

**3단계 순차적 접근**:
1. **Stage 1** (현재): GramAddict 기반 - 안전하고 빠른 구현 ✅
2. **Stage 2** (필요시): 네이티브 프레임워크 - 고급 기능
3. **Stage 3** (필요시): Appium 통합 - 크로스 플랫폼

---

## 2. 빠른 시작 (15분)

### Step 1: 자동 설정 (권장)

```bash
# 한 번에 모든 설정 완료
./scripts/setup_dev.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- ✅ Python 가상환경 생성
- ✅ 패키지 설치 (GramAddict, OpenAI SDK 등)
- ✅ 환경변수 파일 생성
- ✅ PostgreSQL 시작 (Docker)
- ✅ 데이터베이스 연결 테스트

### Step 2: 환경변수 설정

`.env` 파일에 API Key 추가:

```bash
# OpenAI API Key (필수)
OPENAI_API_KEY=sk-your-api-key-here

# PostgreSQL (자동 설정됨)
DB_HOST=127.0.0.1
DB_PORT=5434
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=devpassword123
```

### Step 3: Android 디바이스 연결

```bash
# 디바이스 연결 확인
adb devices

# 출력 예시:
# List of devices attached
# R3CN70D9ZBY    device
```

### Step 4: 첫 실행 테스트

```bash
# 가상환경 활성화
source gramaddict-env/bin/activate

# Instagram 실행 테스트
python -m src.main --config config/accounts/example.yml
```

**✅ 15분 만에 설정 완료!**

---

## 3. 시스템 아키텍처

### 3.1 전체 구조

```
┌──────────────────────────────────────────────────────────────┐
│                   User Interface Layer                        │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ CLI        │  │ Scheduler    │  │ Web Dashboard (TBD) │ │
│  └────────────┘  └──────────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              AI Agent Layer (OpenAI Agents SDK)               │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐  │
│  │ ContentFilter  │ │ ProfileScraper │ │ DMComposer      │  │
│  │ Agent          │ │ Agent          │ │ Agent           │  │
│  └────────────────┘ └────────────────┘ └─────────────────┘  │
│  ┌────────────────┐ ┌────────────────┐                      │
│  │ ConfigGen      │ │ Planning       │                      │
│  │ Agent (✅)     │ │ Agent (✅)     │                      │
│  └────────────────┘ └────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              Task Management Layer                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │               SmartTaskManager (✅)                    │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │  │
│  │  │ Story        │ │ Profile      │ │ DM           │  │  │
│  │  │ Restory Mgr  │ │ Collection   │ │ Sender Mgr   │  │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│           GramAddict Integration Layer                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          GramAddictSessionRunner (✅)                  │  │
│  │  - Interaction Engine (좋아요, 팔로우, 스토리 등)     │  │
│  │  - Safety Features (계정 제재 방지)                   │  │
│  │  - Human-like Behavior (인간 행동 패턴)               │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  UIAutomator2 → ADB → Android Device + Instagram App         │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              Data Storage (PostgreSQL/AlloyDB)                │
│  sessions | profile_data | dm_campaigns | restory_logs       │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 주요 컴포넌트

#### ✅ 구현 완료
1. **SmartTaskManager**: AI 강화 작업 관리자
2. **ConfigGeneratorAgent**: 자연어 → YAML 설정 변환
3. **PlanningAgent**: 계정 통계 분석 및 계획 생성
4. **GramAddictSessionRunner**: GramAddict 실행 래퍼
5. **DatabaseHandler**: PostgreSQL 연동 (재연결 로직 포함)
6. **SessionLock**: 동시성 제어

#### 🚧 개발 필요
7. **ContentFilterAgent**: 스토리 필터링 (텍스트 + 이미지)
8. **ProfileScraperAgent**: 프로필 정보 수집
9. **DMComposerAgent**: AI 기반 DM 생성
10. **StoryRestoryManager**: 스토리 리스토리 관리
11. **DMSenderManager**: DM 발송 관리

---

## 4. 핵심 기능 구현

### 4.1 기능 1: 해시태그 스토리 리스토리

#### 워크플로우

```
1. 사용자 입력
   ↓
   타겟 해시태그: ["맛집", "카페"]
   불량 단어: ["욕설", "광고"]
   일일 한도: 20개

2. SmartTaskManager
   ↓
   AI로 설정 생성 + 필터링 규칙 적용

3. GramAddict
   ↓
   Instagram 실행 → 해시태그 검색 → 스토리 목록 조회

4. ContentFilterAgent (개발 필요)
   ↓
   텍스트 필터링 (정규식 + OpenAI Moderation)
   이미지 필터링 (GPT-4 Vision)

5. 필터링 결과
   ↓
   ✅ 안전 → 리스토리
   ❌ 위험 → 건너뛰기 + 로그

6. 결과 저장
   ↓
   DB에 세션 기록
```

#### 사용 예제

```python
from src.wrapper.smart_task_manager import SmartTaskManager

# 자연어로 설정 생성
tm = SmartTaskManager.from_prompt(
    """
    해시태그 스토리 리스토리 작업
    - 해시태그: #맛집, #서울카페
    - 하루 20개 리스토리
    - 불량 단어 필터링
    - 매우 안전한 속도
    """,
    username="my_account"
)

# 불량 단어 리스트
config_overrides = {
    "content-filter": {
        "enabled": True,
        "bad-words": ["욕설", "광고", "스팸"],
        "filter-action": "skip"
    }
}

# AI 계획 생성 및 실행
plan = tm.get_intelligent_plan(
    goals={
        "daily_restories": 20,
        "target_hashtags": ["맛집", "서울카페"]
    }
)

result = tm.run_with_plan(plan, config_overrides=config_overrides)

if result.succeeded:
    stats = tm.get_session_stats(result.session_id)
    print(f"리스토리: {stats.get('total_restories')}")
    print(f"필터링: {stats.get('filtered_count')}")
```

### 4.2 기능 2: 프로필 수집 및 DM 발송

#### 워크플로우

```
1. 사용자 입력
   ↓
   검색 조건: {"niche": "fashion", "follower_range": (10k, 100k)}
   DM 템플릿: "collaboration_proposal"

2. ProfileScraperAgent (개발 필요)
   ↓
   Instagram 검색 → 프로필 목록 수집 → 조건 필터링

3. 상세 정보 수집
   ↓
   팔로워/팔로잉/포스팅 수
   최근 게시물 분석
   참여율 계산

4. DB 저장
   ↓
   profile_data 테이블

5. DMComposerAgent (개발 필요)
   ↓
   프로필 데이터 분석 → 개인화 메시지 생성 (GPT)

6. DM 발송
   ↓
   GramAddict로 자동 발송 (60초 대기)

7. 결과 저장
   ↓
   dm_sent 테이블
```

#### 사용 예제

```python
from src.agents.profile_scraper_agent import ProfileScraperAgent
from src.agents.dm_composer_agent import DMComposerAgent
from src.wrapper.smart_task_manager import SmartTaskManager

# Agents 초기화
scraper = ProfileScraperAgent()
dm_agent = DMComposerAgent()

tm = SmartTaskManager.from_prompt(
    """
    패션 인플루언서 DM 발송
    - 팔로워 10k-100k
    - 하루 30명
    - 개인화 메시지
    """,
    username="my_brand"
)

# 프로필 검색
profiles = scraper.search_profiles(
    criteria={
        "niche": "fashion",
        "follower_range": (10000, 100000),
        "engagement_rate_min": 3.0
    },
    limit=30
)

# 각 프로필에 DM 발송
for username in profiles:
    # 정보 수집
    profile = scraper.collect_profile_info(username)

    # AI 메시지 생성
    message = dm_agent.compose_personalized_dm(
        profile_data=profile,
        template_name="collaboration"
    )

    # DM 발송
    result = tm.send_dm(username, message)

    if result.succeeded:
        print(f"✅ DM 발송: {username}")

    time.sleep(60)  # 안전한 속도
```

---

## 5. 개발 환경 설정

### 5.1 필수 요구사항

| 항목 | 요구사항 |
|------|----------|
| **OS** | macOS, Linux, Windows |
| **Python** | 3.9 - 3.11 (3.10+ 비권장) |
| **Android** | Android 5.0+, Instagram 앱 설치 |
| **ADB** | Android Debug Bridge |
| **PostgreSQL** | 12+ (Docker 또는 로컬) |
| **OpenAI API** | API Key 필수 |

### 5.2 프로젝트 구조

```
instagram-automation/
├── config/
│   ├── accounts/                    # 계정별 YAML 설정
│   │   ├── example.yml
│   │   └── my_account.yml
│   ├── global_config.yml            # 전역 설정
│   └── generated/                   # 동적 생성 설정 (gitignore)
├── src/
│   ├── agents/                      # 🤖 OpenAI Agents
│   │   ├── config_agent.py          # ✅ 설정 생성
│   │   ├── planning_agent.py        # ✅ 작업 계획
│   │   ├── agent_manager.py         # ✅ Agent 통합
│   │   ├── content_filter_agent.py  # 🚧 필터링 (개발 필요)
│   │   ├── profile_scraper_agent.py # 🚧 프로필 수집
│   │   └── dm_composer_agent.py     # 🚧 DM 생성
│   ├── wrapper/
│   │   ├── task_manager.py          # ✅ GramAddict 래퍼
│   │   ├── smart_task_manager.py    # ✅ AI 강화 TaskManager
│   │   ├── log_parser.py            # ✅ 로그 파싱
│   │   ├── story_restory_manager.py # 🚧 스토리 관리
│   │   └── dm_sender_manager.py     # 🚧 DM 관리
│   ├── utils/
│   │   ├── logger.py                # ✅ 로깅
│   │   ├── db_handler.py            # ✅ PostgreSQL
│   │   └── session_lock.py          # ✅ 동시성 제어
│   ├── gramaddict_adapter/          # ✅ GramAddict 통합
│   └── main.py                      # 메인 진입점
├── logs/
│   ├── gramaddict/                  # GramAddict 로그
│   └── custom/                      # 커스텀 로그
├── tests/                           # 테스트
├── docs/                            # 문서
├── scripts/
│   ├── setup_dev.sh                 # 자동 설정
│   └── dev.sh                       # 개발 도구
├── docker/
│   └── docker-compose.yml           # PostgreSQL 컨테이너
├── .env                             # 환경변수 (gitignore)
├── requirements.txt
└── README.md
```

### 5.3 개발 도구 사용

#### Makefile (권장)

```bash
# 설정
make setup

# PostgreSQL 관리
make start       # 시작
make stop        # 중지
make logs        # 로그 확인

# 데이터베이스
make psql        # DB 접속
make migrate     # 마이그레이션
make test-db     # 연결 테스트

# 테스트
pytest           # 전체 테스트
pytest --cov     # 커버리지 포함
```

#### 개발 스크립트

```bash
./scripts/dev.sh help       # 도움말
./scripts/dev.sh start      # PostgreSQL 시작
./scripts/dev.sh psql       # DB 접속
./scripts/dev.sh check      # 시스템 상태 확인
```

---

## 6. AI Agents 사용법

### 6.1 기존 Agents (✅ 사용 가능)

#### ConfigGeneratorAgent

```python
from src.agents.config_agent import ConfigGeneratorAgent

agent = ConfigGeneratorAgent()

# 자연어 → YAML 설정
config = agent.generate(
    "여행 블로거, 하루 30개 좋아요, 안전 모드",
    username="travel_account"
)

# 파일로 저장
agent.generate_and_save(
    "여행 블로거, 하루 30개 좋아요",
    username="travel_account",
    output_path="config/accounts/travel.yml"
)
```

#### PlanningAgent

```python
from src.agents.planning_agent import PlanningAgent
from src.utils.db_handler import DatabaseHandler

db = DatabaseHandler()
agent = PlanningAgent(db_handler=db)

# 계정 데이터 기반 계획 생성
plan = agent.plan_daily_tasks(
    username="my_account",
    goals={"followers": 50, "timeframe": "1 week"}
)

print(f"추천 일일 좋아요: {plan['plan']['daily_likes']}")
print(f"추천 해시태그: {plan['plan']['recommended_hashtags']}")
print(f"신뢰도: {plan['confidence']:.1%}")
```

#### AgentManager (통합)

```python
from src.agents.agent_manager import AgentManager

mgr = AgentManager(db_handler=db)

# 설정 + 계획 동시 생성
result = mgr.get_config_with_plan(
    prompt="패션 계정, 하루 40개 좋아요",
    username="fashion",
    goals={"followers": 100, "timeframe": "1 week"}
)

config = result['config']
plan = result['plan']
```

### 6.2 새로운 Agents (🚧 개발 필요)

#### ContentFilterAgent (Phase 2)

```python
# 예정된 API
from src.agents.content_filter_agent import ContentFilterAgent

filter_agent = ContentFilterAgent()

# 텍스트 필터링
is_safe = filter_agent.check_text(
    text="스토리 내용",
    bad_words=["욕설", "광고"]
)

# 이미지 필터링 (GPT-4 Vision)
is_safe_img = filter_agent.check_image(
    image_path="story.jpg",
    detect=["adult_content", "violence"]
)
```

#### ProfileScraperAgent (Phase 3)

```python
# 예정된 API
from src.agents.profile_scraper_agent import ProfileScraperAgent

scraper = ProfileScraperAgent()

# 프로필 검색
profiles = scraper.search_profiles(
    criteria={"niche": "fashion", "follower_range": (10000, 100000)},
    limit=50
)

# 상세 정보 수집
profile = scraper.collect_profile_info(
    username="target",
    collect_fields=["followers", "posts", "engagement_rate"]
)
```

#### DMComposerAgent (Phase 3)

```python
# 예정된 API
from src.agents.dm_composer_agent import DMComposerAgent

dm_agent = DMComposerAgent()

# 개인화 메시지 생성
message = dm_agent.compose_personalized_dm(
    profile_data=profile,
    template_name="collaboration_proposal",
    brand_info={"name": "My Brand"}
)
```

---

## 7. 데이터베이스 설정

### 7.1 로컬 PostgreSQL (Docker 권장)

#### 자동 설정

```bash
# 한 번에 시작
make start

# 또는
./scripts/dev.sh start
```

#### 수동 설정

```bash
# PostgreSQL 시작
cd docker
docker-compose up -d postgres

# 연결 테스트
python scripts/db_test.py
```

### 7.2 데이터베이스 스키마

#### 기존 스키마 (✅ 구현됨)

```sql
-- 세션 로그
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    username VARCHAR(255),
    device_id VARCHAR(255),
    status VARCHAR(50),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 상호작용 로그
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    action_type VARCHAR(50),
    target VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 새로운 스키마 (🚧 Phase 2/3)

```sql
-- 리스토리 세션
CREATE TABLE restory_sessions (
    session_id UUID PRIMARY KEY,
    username VARCHAR(255),
    target_hashtags TEXT[],
    total_viewed INT DEFAULT 0,
    total_restoried INT DEFAULT 0,
    total_filtered INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 필터링된 스토리
CREATE TABLE filtered_stories (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES restory_sessions,
    story_url TEXT,
    filter_reason VARCHAR(255),
    bad_words_found TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- 프로필 데이터
CREATE TABLE profile_data (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    followers INT,
    following INT,
    posts_count INT,
    engagement_rate FLOAT,
    bio TEXT,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- DM 캠페인
CREATE TABLE dm_campaigns (
    campaign_id UUID PRIMARY KEY,
    campaign_name VARCHAR(255),
    target_criteria JSONB,
    template_name VARCHAR(255),
    daily_limit INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- DM 발송 기록
CREATE TABLE dm_sent (
    id SERIAL PRIMARY KEY,
    campaign_id UUID REFERENCES dm_campaigns,
    target_username VARCHAR(255),
    message TEXT,  -- 암호화 필요
    status VARCHAR(50),  -- sent, failed, responded
    error_message TEXT,
    sent_at TIMESTAMP,
    responded_at TIMESTAMP
);
```

### 7.3 DB 접속 및 쿼리

```bash
# PostgreSQL 접속
make psql

# 또는
psql -h 127.0.0.1 -p 5434 -U postgres -d instagram_automation

# 세션 조회
SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10;

# 통계
SELECT username, COUNT(*) as sessions
FROM sessions
GROUP BY username;
```

---

## 8. 안전성 및 리스크 관리

### 8.1 Instagram 제재 방지 ⚠️ 최고 우선순위

#### GramAddict 내장 안전 기능 (✅)
- ✅ 검증된 인간 행동 패턴
- ✅ 랜덤 딜레이 (3-7초)
- ✅ 자연스러운 스크롤
- ✅ 작업 빈도 자동 제한

#### 추가 대응 방안

```yaml
# config/accounts/my_account.yml

# 안전한 한도 설정
limits:
  likes-per-day: 30-50         # 신규 계정: 30, 오래된 계정: 50
  follows-per-day: 20-30
  unfollows-per-day: 20-30
  restories-per-day: 20        # 새 기능
  dms-per-day: 30              # 새 기능

# 작업 시간대 분산 (새벽 작업 금지)
working-hours:
  - 09:00-11:00
  - 14:00-16:00
  - 19:00-21:00

# 느린 속도 (안전)
speed-multiplier: 1.8-2.0
```

#### 신규 계정 워밍업

```
Week 1: 수동 사용 (자동화 금지)
Week 2: 하루 10개 좋아요
Week 3: 하루 20개 좋아요
Week 4: 하루 30-50개 좋아요 (정상)
```

### 8.2 UI 변경 대응

#### GramAddict 커뮤니티 대응 (✅)
- ✅ GitHub Issues 구독
- ✅ 정기 업데이트: `pip install --upgrade gramaddict`
- ✅ 버전 고정 옵션 (안정성 우선 시)

#### 롤백 전략

```bash
# 특정 버전 고정
pip install gramaddict==3.2.12

# requirements.txt에 명시
gramaddict==3.2.12
```

### 8.3 데이터 보안

#### 환경변수 관리

```bash
# .env 파일 (절대 커밋하지 말 것)
OPENAI_API_KEY=sk-...
DB_PASSWORD=...
INSTAGRAM_USERNAME=...  # 자동 로그인용 (선택)
```

#### 민감 정보 암호화

```python
from cryptography.fernet import Fernet

# DM 메시지 암호화
def encrypt_message(message: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

# 복호화
def decrypt_message(encrypted: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
```

---

## 9. 구현 로드맵

### ✅ Phase 1: 기반 구조 (완료)

- [x] GramAddict 통합
- [x] OpenAI Agents SDK 통합
- [x] ConfigGeneratorAgent
- [x] PlanningAgent
- [x] SmartTaskManager
- [x] DatabaseHandler (재연결 로직)
- [x] SessionLock (동시성 제어)
- [x] 로그 파싱 개선
- [x] 유닛 테스트

### 🚧 Phase 2: 스토리 리스토리 기능 (2-3주)

**주차별 계획**:

#### 1주차
- [ ] ContentFilterAgent 개발
  - [ ] 텍스트 필터링 (정규식)
  - [ ] OpenAI Moderation API 통합
  - [ ] 불량 단어 DB 구축

#### 2주차
- [ ] GPT-4 Vision 이미지 분석
- [ ] StoryRestoryManager 개발
  - [ ] 해시태그 검색
  - [ ] 스토리 내용 수집
  - [ ] 리스토리 자동화

#### 3주차
- [ ] DB 스키마 확장 (restory_sessions, filtered_stories)
- [ ] 테스트 및 검증
  - [ ] 필터링 정확도 측정
  - [ ] 리스토리 성공률 측정
- [ ] 문서화

### 🚧 Phase 3: 프로필 수집 및 DM (3-4주)

**주차별 계획**:

#### 1-2주차
- [ ] ProfileScraperAgent 개발
  - [ ] 프로필 검색 (해시태그, 위치)
  - [ ] 상세 정보 수집
  - [ ] 참여율 계산 알고리즘

#### 2-3주차
- [ ] DMComposerAgent 개발
  - [ ] 템플릿 시스템
  - [ ] GPT 기반 개인화
  - [ ] A/B 테스팅

#### 3-4주차
- [ ] DMSenderManager 개발
  - [ ] DM 발송 자동화
  - [ ] 배치 처리
  - [ ] 응답 추적
- [ ] DB 스키마 확장 (profile_data, dm_campaigns, dm_sent)
- [ ] 테스트 및 검증

### 📅 Phase 4: 고급 기능 (4-6주, 선택)

- [ ] 스케줄링 시스템
- [ ] 실시간 모니터링
- [ ] 웹 대시보드 (React)
- [ ] 추가 AI Agents (SafetyMonitor, LogAnalysis)

---

## 10. 문제 해결

### 10.1 ADB 연결 문제

```bash
# ADB 서버 재시작
adb kill-server
adb start-server
adb devices

# Wi-Fi ADB 사용 (USB 불안정 시)
adb tcpip 5555
adb connect <DEVICE_IP>:5555
```

### 10.2 Python 버전 오류

```bash
# Python 3.9-3.11 확인
python --version

# 가상환경 재생성
rm -rf gramaddict-env
python3.9 -m venv gramaddict-env
source gramaddict-env/bin/activate
pip install -r requirements.txt
```

### 10.3 OpenAI API 오류

```bash
# API Key 확인
echo $OPENAI_API_KEY

# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 비용 체크
# https://platform.openai.com/usage
```

### 10.4 PostgreSQL 연결 오류

```bash
# Docker 컨테이너 확인
docker ps

# 로그 확인
docker logs instagram-postgres

# 재시작
make restart

# 연결 테스트
python scripts/db_test.py
```

### 10.5 GramAddict 실행 오류

```bash
# 로그 확인
tail -f logs/gramaddict/<SESSION_ID>/gramaddict.log

# Instagram 앱 버전 확인 (너무 최신이면 미지원 가능)
adb shell dumpsys package com.instagram.android | grep versionName

# GramAddict 업데이트
pip install --upgrade gramaddict
```

---

## 📚 추가 리소스

### 문서
- [README.md](README.md) - 프로젝트 개요
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 개선 사항
- [OPENAI_AGENTS_INTEGRATION.md](OPENAI_AGENTS_INTEGRATION.md) - AI 통합 계획

### 아카이브된 문서 (참고용)
- [docs/archive/개발문서.md](docs/archive/개발문서.md) - 초기 개발 문서
- [docs/archive/Local_Development.md](docs/archive/Local_Development.md) - 로컬 개발 가이드
- [docs/archive/PostgreSQL_Setup.md](docs/archive/PostgreSQL_Setup.md) - DB 설정 상세
- [docs/archive/AGENTS_USAGE_GUIDE.md](docs/archive/AGENTS_USAGE_GUIDE.md) - Agents 상세 가이드
- [docs/archive/PROJECT_ARCHITECTURE.md](docs/archive/PROJECT_ARCHITECTURE.md) - 아키텍처 상세

### 외부 링크
- [GramAddict 공식 문서](https://docs.gramaddict.org/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/ko/)
- [Android ADB 가이드](https://developer.android.com/studio/command-line/adb)

---

## ✅ 체크리스트

개발 시작 전 확인:

- [ ] Android 디바이스 준비 (Android 5.0+, Instagram 설치)
- [ ] ADB 연결 확인 (`adb devices`)
- [ ] Python 3.9-3.11 설치
- [ ] OpenAI API Key 발급 및 설정
- [ ] PostgreSQL 실행 (Docker 또는 로컬)
- [ ] 테스트 계정 준비 (제재되어도 괜찮은 계정)
- [ ] `.env` 파일 설정
- [ ] `./scripts/setup_dev.sh` 실행
- [ ] 첫 실행 테스트 완료

---

**작성일**: 2025-10-10
**버전**: 3.0 (통합)
**상태**: Phase 1 완료, Phase 2/3 진행 중
**다음 업데이트**: Phase 2 완료 후

---

## 🎯 결론

이 문서 하나로 프로젝트의 **모든 것**을 파악할 수 있습니다:

1. **빠른 시작**: 15분 안에 설정 완료
2. **아키텍처**: 전체 시스템 구조 이해
3. **핵심 기능**: 2가지 목표 구현 방법
4. **AI Agents**: 기존 + 개발 필요 Agent 파악
5. **데이터베이스**: 스키마 및 사용법
6. **안전성**: 리스크 관리 전략
7. **로드맵**: Phase별 구현 계획
8. **문제 해결**: 일반적인 오류 대응

**다음 단계**: Phase 2 (스토리 리스토리) 또는 Phase 3 (프로필 수집 + DM) 개발 시작! 🚀
