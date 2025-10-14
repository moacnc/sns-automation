# 프로젝트 아키텍처 - Instagram 자동화 시스템

## 📋 프로젝트 개요

### 목표
1. **해시태그 스토리 자동 리스토리** (필터링 포함)
2. **프로필 정보 수집 및 DM 발송**

### 기술 스택
- **Base Framework**: GramAddict (Instagram UI 자동화)
- **AI Layer**: OpenAI Agents SDK
- **Database**: PostgreSQL/AlloyDB
- **Language**: Python 3.9
- **Automation**: ADB (Android Debug Bridge)

---

## 🏗️ 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                   User Interface Layer                        │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ CLI Commands   │  │ Web Dashboard    │  │ Scheduler    │ │
│  │ (future)       │  │ (future)         │  │              │ │
│  └────────────────┘  └──────────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  AI Agent Layer (OpenAI SDK)                  │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────────┐│
│  │ Content      │ │ Profile      │ │ DM Composer           ││
│  │ Filter       │ │ Scraper      │ │ Agent                 ││
│  │ Agent        │ │ Agent        │ │                       ││
│  └──────────────┘ └──────────────┘ └───────────────────────┘│
│  ┌──────────────┐ ┌──────────────┐                          │
│  │ Config       │ │ Planning     │                          │
│  │ Generator    │ │ Agent        │                          │
│  └──────────────┘ └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              Task Management Layer                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            SmartTaskManager                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ Story        │  │ Profile      │  │ DM          │ │  │
│  │  │ Restory      │  │ Collection   │  │ Sender      │ │  │
│  │  │ Manager      │  │ Manager      │  │ Manager     │ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│           GramAddict Integration Layer                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              GramAddictSessionRunner                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ Story        │  │ Profile      │  │ DM          │ │  │
│  │  │ Actions      │  │ Scraping     │  │ Sending     │ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                 Instagram App (Android)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  UIAutomator → Instagram Native UI                    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Session      │  │ Profile      │  │ DM              │   │
│  │ Logs         │  │ Data         │  │ Tracking        │   │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL)    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 핵심 기능별 설계

### 기능 1: 해시태그 스토리 자동 리스토리

#### 워크플로우

```
1. 사용자 입력
   ↓
   - 타겟 해시태그: ["맛집", "카페", "여행"]
   - 불량 단어 리스트: ["욕설", "광고", "스팸"]
   - 일일 리스토리 한도: 20개

2. SmartTaskManager
   ↓
   - ConfigGeneratorAgent: 설정 생성
   - ContentFilterAgent: 필터링 규칙 적용

3. GramAddict Runner
   ↓
   - Instagram 앱 실행
   - 해시태그 검색: "#맛집"
   - 스토리 목록 조회

4. ContentFilterAgent
   ↓
   - 각 스토리 텍스트 분석
   - 불량 단어 검사
   - 이미지 내용 분석 (OpenAI Vision API)

5. 필터링 결과
   ↓
   - ✅ 안전: 리스토리 실행
   - ❌ 위험: 건너뛰기 + 로그 기록

6. 리스토리 실행
   ↓
   - GramAddict: UI 자동화
   - 스토리 클릭 → 공유 버튼 → 내 스토리에 추가

7. 결과 저장
   ↓
   - DB에 세션 기록
   - 리스토리 카운트
   - 필터링된 항목 기록
```

#### 필요 모듈

1. **ContentFilterAgent** (신규 개발)
   ```python
   class ContentFilterAgent:
       def check_text(text: str, bad_words: List[str]) -> bool
       def check_image(image_path: str) -> Dict[str, Any]
       def apply_filter_policy(content: Dict) -> FilterResult
   ```

2. **StoryRestoryManager** (신규 개발)
   ```python
   class StoryRestoryManager:
       def search_hashtag_stories(hashtag: str) -> List[Story]
       def collect_story_content(story: Story) -> StoryContent
       def restory(story: Story) -> RestoryResult
   ```

3. **Database Schema** (확장 필요)
   ```sql
   CREATE TABLE restory_sessions (
       session_id UUID PRIMARY KEY,
       username VARCHAR(255),
       target_hashtags TEXT[],
       total_viewed INT,
       total_restoried INT,
       total_filtered INT,
       created_at TIMESTAMP
   );

   CREATE TABLE filtered_stories (
       id SERIAL PRIMARY KEY,
       session_id UUID REFERENCES restory_sessions,
       story_url TEXT,
       filter_reason VARCHAR(255),
       bad_words_found TEXT[],
       created_at TIMESTAMP
   );
   ```

---

### 기능 2: 프로필 정보 수집 및 DM 발송

#### 워크플로우

```
1. 사용자 입력
   ↓
   - 검색 조건: {"niche": "fashion", "follower_range": (10k, 100k)}
   - DM 템플릿: "collaboration_proposal"
   - 일일 DM 한도: 30개

2. ProfileScraperAgent
   ↓
   - Instagram 검색: 해시태그, 위치, 추천
   - 프로필 목록 수집
   - 조건 필터링 (팔로워 수, 참여율)

3. 각 프로필 상세 정보 수집
   ↓
   - 팔로워 수, 팔로잉 수
   - 포스팅 수
   - 최근 게시물 (10개)
   - 평균 좋아요/댓글 수
   - 참여율 계산: (likes + comments) / followers * 100

4. DB에 프로필 데이터 저장
   ↓
   - profile_data 테이블에 저장
   - 중복 프로필 체크

5. DMComposerAgent
   ↓
   - 프로필 데이터 분석
   - 개인화 메시지 생성 (OpenAI GPT)
   - 템플릿 적용

6. DM 발송
   ↓
   - GramAddict: DM 발송 자동화
   - 속도 제어 (60초 대기)
   - 실패 시 재시도 (3회)

7. 결과 저장
   ↓
   - DM 발송 기록
   - 성공/실패 상태
   - 응답 추적 (future)
```

#### 필요 모듈

1. **ProfileScraperAgent** (신규 개발)
   ```python
   class ProfileScraperAgent:
       def search_profiles(criteria: Dict) -> List[str]
       def collect_profile_info(username: str) -> ProfileData
       def calculate_engagement_rate(profile: ProfileData) -> float
       def filter_by_criteria(profiles: List, criteria: Dict) -> List
   ```

2. **DMComposerAgent** (신규 개발)
   ```python
   class DMComposerAgent:
       def compose_personalized_dm(
           profile_data: ProfileData,
           template_name: str,
           brand_info: Dict
       ) -> str

       def load_template(name: str) -> str
       def apply_ab_testing() -> str
   ```

3. **DMSenderManager** (신규 개발)
   ```python
   class DMSenderManager:
       def send_dm(username: str, message: str) -> DMResult
       def batch_send(targets: List[str], messages: List[str]) -> List[DMResult]
       def track_response(dm_id: str) -> ResponseStatus
   ```

4. **Database Schema** (확장 필요)
   ```sql
   CREATE TABLE profile_data (
       id SERIAL PRIMARY KEY,
       username VARCHAR(255) UNIQUE,
       followers INT,
       following INT,
       posts_count INT,
       engagement_rate FLOAT,
       bio TEXT,
       last_updated TIMESTAMP,
       created_at TIMESTAMP
   );

   CREATE TABLE dm_campaigns (
       campaign_id UUID PRIMARY KEY,
       campaign_name VARCHAR(255),
       target_criteria JSONB,
       template_name VARCHAR(255),
       daily_limit INT,
       created_at TIMESTAMP
   );

   CREATE TABLE dm_sent (
       id SERIAL PRIMARY KEY,
       campaign_id UUID REFERENCES dm_campaigns,
       target_username VARCHAR(255),
       message TEXT,
       status VARCHAR(50),  -- sent, failed, responded
       error_message TEXT,
       sent_at TIMESTAMP,
       responded_at TIMESTAMP
   );
   ```

---

## 🔧 기술적 고려사항

### 1. Instagram API 제한 회피

**문제**: Instagram은 비공식 자동화를 감지하고 제재함

**해결책**:
- **인간 행동 패턴 모방**
  - 랜덤 딜레이: 30-90초 사이
  - 스크롤 속도 조절
  - 클릭 위치 랜덤화

- **안전한 한도 설정**
  - 리스토리: 하루 20-30개
  - DM: 하루 30-50개 (계정 나이에 따라)
  - 프로필 조회: 시간당 50개

- **IP 로테이션** (고급)
  - VPN/프록시 사용
  - 디바이스 ID 로테이션

### 2. 필터링 정확도

**문제**: 불량 단어 필터링이 오탐/미탐 발생

**해결책**:
- **다층 필터링**
  - Level 1: 정규식 기반 단어 매칭
  - Level 2: OpenAI Moderation API
  - Level 3: GPT-4 Vision (이미지 분석)

- **화이트리스트/블랙리스트**
  - 안전 확인된 사용자: 화이트리스트
  - 반복 위반 사용자: 블랙리스트

- **사용자 피드백 루프**
  - 잘못 필터링된 항목 보고
  - AI 모델 재학습

### 3. 성능 최적화

**문제**: 대량 프로필 수집 시 느린 속도

**해결책**:
- **비동기 처리**
  ```python
  async def collect_profiles_async(usernames: List[str]):
      tasks = [collect_profile_info(u) for u in usernames]
      results = await asyncio.gather(*tasks)
      return results
  ```

- **캐싱**
  - Redis 캐시: 프로필 데이터 24시간
  - DB 인덱싱: username, followers

- **배치 처리**
  - 10개씩 묶어서 처리
  - 실패 시 개별 재시도

### 4. 데이터 보안

**문제**: 민감한 데이터 (DM 내용, 프로필 정보) 보호

**해결책**:
- **암호화**
  - DM 메시지: AES-256 암호화
  - API Key: 환경변수 + AWS Secrets Manager

- **접근 제어**
  - PostgreSQL 역할 기반 권한
  - VPN 내부망 접근만 허용

- **로그 관리**
  - 민감 정보 마스킹
  - 로그 보관 기간: 30일

---

## 📊 데이터 모델

### ER Diagram

```
┌─────────────────┐
│  users          │
├─────────────────┤
│ id (PK)         │
│ username        │
│ device_id       │
│ created_at      │
└─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐       ┌──────────────────┐
│ sessions        │       │ profile_data     │
├─────────────────┤       ├──────────────────┤
│ session_id (PK) │       │ id (PK)          │
│ user_id (FK)    │       │ username (UQ)    │
│ session_type    │       │ followers        │
│ status          │       │ engagement_rate  │
│ started_at      │       │ last_updated     │
│ ended_at        │       └──────────────────┘
└─────────────────┘                │
        │                           │
        │ 1:N                       │ 1:N
        ▼                           ▼
┌─────────────────┐       ┌──────────────────┐
│ restory_logs    │       │ dm_campaigns     │
├─────────────────┤       ├──────────────────┤
│ id (PK)         │       │ campaign_id (PK) │
│ session_id (FK) │       │ name             │
│ story_url       │       │ target_criteria  │
│ action          │       │ daily_limit      │
│ created_at      │       └──────────────────┘
└─────────────────┘                │
                                   │ 1:N
                                   ▼
                          ┌──────────────────┐
                          │ dm_sent          │
                          ├──────────────────┤
                          │ id (PK)          │
                          │ campaign_id (FK) │
                          │ target_username  │
                          │ message (암호화)  │
                          │ status           │
                          │ sent_at          │
                          └──────────────────┘
```

---

## 🚀 구현 계획

### Phase 1: 기반 구조 (완료 ✅)
- [x] GramAddict 통합
- [x] OpenAI Agents SDK 통합
- [x] ConfigGeneratorAgent
- [x] PlanningAgent
- [x] SmartTaskManager
- [x] Database 연동

### Phase 2: 스토리 리스토리 기능 (2-3주)
- [ ] ContentFilterAgent 개발
  - [ ] 텍스트 필터링 (정규식 + OpenAI Moderation)
  - [ ] 이미지 필터링 (GPT-4 Vision)
  - [ ] 필터링 정책 엔진

- [ ] StoryRestoryManager 개발
  - [ ] 해시태그 검색 기능
  - [ ] 스토리 내용 수집
  - [ ] 리스토리 자동화

- [ ] Database Schema 확장
  - [ ] restory_sessions 테이블
  - [ ] filtered_stories 테이블

- [ ] 테스트 및 검증
  - [ ] 필터링 정확도 테스트
  - [ ] 리스토리 성공률 측정

### Phase 3: 프로필 수집 및 DM 기능 (3-4주)
- [ ] ProfileScraperAgent 개발
  - [ ] 프로필 검색 기능
  - [ ] 상세 정보 수집
  - [ ] 참여율 계산

- [ ] DMComposerAgent 개발
  - [ ] 템플릿 시스템
  - [ ] 개인화 메시지 생성 (GPT)
  - [ ] A/B 테스팅

- [ ] DMSenderManager 개발
  - [ ] DM 발송 자동화
  - [ ] 배치 처리
  - [ ] 응답 추적

- [ ] Database Schema 확장
  - [ ] profile_data 테이블
  - [ ] dm_campaigns 테이블
  - [ ] dm_sent 테이블

- [ ] 테스트 및 검증
  - [ ] 프로필 수집 정확도
  - [ ] DM 발송 성공률
  - [ ] 응답률 추적

### Phase 4: 고급 기능 (4-6주)
- [ ] 스케줄링 시스템
  - [ ] Cron 기반 자동 실행
  - [ ] 시간대별 작업 분산

- [ ] 모니터링 및 알림
  - [ ] 실시간 세션 모니터링
  - [ ] 에러 알림 (Slack, Email)
  - [ ] 성과 대시보드

- [ ] 웹 대시보드
  - [ ] React 기반 UI
  - [ ] 실시간 통계
  - [ ] 설정 관리 인터페이스

---

## 📈 성공 지표

### 리스토리 기능
- **목표 리스토리 수**: 하루 20개
- **필터링 정확도**: 95% 이상
- **제재 회피율**: 99% 이상

### DM 발송 기능
- **일일 DM 발송**: 30개
- **응답률**: 5% 이상
- **발송 성공률**: 98% 이상

### 시스템 안정성
- **가동 시간**: 99.5% 이상
- **에러율**: 1% 이하
- **평균 응답 시간**: 30초 이내

---

## ⚠️ 리스크 및 대응

### 1. Instagram 제재
**리스크**: 계정 일시 정지 또는 영구 차단

**대응**:
- 테스트 계정 사용
- 보수적인 작업 속도
- 인간 행동 패턴 모방
- 즉시 중단 메커니즘

### 2. AI 비용
**리스크**: OpenAI API 비용 증가

**대응**:
- gpt-4o-mini 사용 (저렴)
- 캐싱으로 중복 호출 방지
- 월 예산 설정 및 모니터링

### 3. 데이터 보안
**리스크**: 민감 정보 유출

**대응**:
- 암호화 (AES-256)
- VPN 접근 제한
- 정기 보안 감사

---

## 📝 참고 자료

- [GramAddict 문서](https://github.com/GramAddict/GramAddict)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/ko/)
- [Instagram API 제한 가이드](https://developers.facebook.com/docs/instagram-api/overview)
- [프로젝트 통합 계획](../OPENAI_AGENTS_INTEGRATION.md)

---

**작성일**: 2025-10-10
**버전**: 1.0
**상태**: 설계 완료, Phase 2 개발 대기 중
