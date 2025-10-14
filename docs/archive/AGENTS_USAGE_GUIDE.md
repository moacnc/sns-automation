# OpenAI Agents 사용 가이드

OpenAI Agents SDK가 통합되어 AI 기반 Instagram 자동화 작업을 수행할 수 있습니다.

## 📌 프로젝트 목표

본 시스템은 두 가지 핵심 기능을 제공합니다:

### 1. 해시태그 스토리 자동 리스토리 (필터링)
- 내 계정으로 로그인
- 특정 해시태그가 포함된 스토리 검색
- 불량 단어 필터링 (욕설, 부적절한 내용 등)
- 필터링된 스토리를 자동으로 리그램 또는 리스토리

### 2. 프로필 정보 수집 및 DM 발송
- 특정 프로필 검색
- 프로필 정보 자동 수집:
  - 팔로워 수
  - 팔로잉 수
  - 포스팅 수
  - 최근 게시물 정보
  - 댓글 및 반응 데이터
- 수집된 정보 기반 맞춤형 DM 자동 발송

---

## 목차

1. [설정](#설정)
2. [프로젝트별 사용법](#프로젝트별-사용법)
   - [해시태그 스토리 리스토리](#1-해시태그-스토리-자동-리스토리)
   - [프로필 정보 수집 및 DM](#2-프로필-정보-수집-및-dm-발송)
3. [Agent 종류](#agent-종류)
4. [고급 사용법](#고급-사용법)
5. [예제](#예제)
6. [문제 해결](#문제-해결)

---

## 설정

### 1. OpenAI API Key 발급

1. https://platform.openai.com/api-keys 방문
2. "Create new secret key" 클릭
3. API key 복사 (sk-로 시작)

### 2. 환경 변수 설정

`.env` 파일에 추가:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

또는 쉘에서 export:

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 패키지 확인

```bash
pip install openai-agents openai
```

requirements.txt에 이미 포함되어 있습니다.

---

## 프로젝트별 사용법

### 1. 해시태그 스토리 자동 리스토리

**목표**: 특정 해시태그 스토리를 찾아서 불량 단어를 필터링한 후 자동 리스토리

#### Step 1: 자연어로 설정 생성

```python
from src.wrapper.smart_task_manager import SmartTaskManager

# 자연어로 리스토리 작업 설정
tm = SmartTaskManager.from_prompt(
    """
    해시태그 스토리 자동 리스토리 작업
    - 타겟 해시태그: #맛집, #서울카페, #여행
    - 불량 단어 필터링: 욕설, 광고성 단어
    - 하루 최대 리스토리: 20개
    - 안전 모드 (천천히)
    """,
    username="my_account"
)
```

#### Step 2: 불량 단어 필터링 설정

```python
# 필터링할 불량 단어 리스트
bad_words = [
    "욕설1", "욕설2", "광고",
    "스팸", "도박", "성인"
]

# 설정에 필터 추가
config_overrides = {
    "content-filter": {
        "enabled": True,
        "bad-words": bad_words,
        "filter-action": "skip"  # skip 또는 report
    }
}
```

#### Step 3: 리스토리 실행

```python
# AI 계획 생성
plan = tm.get_intelligent_plan(
    goals={
        "daily_restories": 20,
        "target_hashtags": ["맛집", "서울카페", "여행"],
        "timeframe": "1 day"
    }
)

# 필터링과 함께 실행
result = tm.run_with_plan(
    plan=plan,
    config_overrides=config_overrides
)

if result.succeeded:
    print(f"✅ 리스토리 완료: {result.session_id}")
    stats = tm.get_session_stats(result.session_id)
    print(f"총 리스토리: {stats.get('total_restories')}")
    print(f"필터링됨: {stats.get('filtered_count')}")
else:
    print(f"❌ 실패: {result.errors}")
```

#### 실전 예제: 완전 자동화

```python
#!/usr/bin/env python
"""
해시태그 스토리 자동 리스토리 시스템
"""

from src.wrapper.smart_task_manager import SmartTaskManager
from src.utils.logger import get_logger

logger = get_logger()

# 1. 설정
BAD_WORDS = [
    "욕설", "광고", "스팸", "도박",
    "성인", "19금", "불법"
]

TARGET_HASHTAGS = [
    "맛집", "서울카페", "여행",
    "데일리룩", "ootd", "fashion"
]

# 2. TaskManager 생성
tm = SmartTaskManager.from_prompt(
    f"""
    해시태그 스토리 리스토리 자동화
    - 해시태그: {', '.join(TARGET_HASHTAGS)}
    - 하루 20개 리스토리
    - 불량 단어 필터링 활성화
    - 매우 안전한 속도
    """,
    username="my_restory_account",
    save_config=True
)

# 3. AI 계획 생성
plan = tm.get_intelligent_plan(
    goals={
        "daily_restories": 20,
        "target_hashtags": TARGET_HASHTAGS
    }
)

logger.info(f"AI 추천 리스토리 수: {plan['plan']['daily_restories']}")
logger.info(f"추천 해시태그: {plan['plan']['recommended_hashtags']}")

# 4. 필터링 설정 적용
config_overrides = {
    "content-filter": {
        "enabled": True,
        "bad-words": BAD_WORDS,
        "filter-action": "skip"
    },
    "hashtag-story-repost": {
        "hashtags": TARGET_HASHTAGS,
        "amount": 20
    }
}

# 5. 실행
result = tm.run_with_plan(
    plan=plan,
    config_overrides=config_overrides
)

# 6. 결과 확인
if result.succeeded:
    stats = tm.get_session_stats(result.session_id)
    logger.info("=" * 60)
    logger.info("리스토리 세션 완료")
    logger.info("=" * 60)
    logger.info(f"총 리스토리: {stats.get('total_restories', 0)}")
    logger.info(f"필터링됨: {stats.get('filtered_count', 0)}")
    logger.info(f"건너뜀: {stats.get('skipped_count', 0)}")
else:
    logger.error(f"세션 실패: {result.errors}")

tm.close()
```

---

### 2. 프로필 정보 수집 및 DM 발송

**목표**: 특정 프로필의 정보를 수집하고 맞춤형 DM 발송

#### Step 1: 프로필 정보 수집 설정

```python
from src.wrapper.smart_task_manager import SmartTaskManager

# 자연어로 프로필 수집 작업 설정
tm = SmartTaskManager.from_prompt(
    """
    프로필 정보 수집 및 DM 발송
    - 타겟: 패션 인플루언서 (팔로워 10k-100k)
    - 수집 정보: 팔로워, 포스팅, 최근 댓글
    - 하루 30명에게 DM 발송
    - 개인화된 메시지
    """,
    username="my_account"
)
```

#### Step 2: 타겟 프로필 정의

```python
# 타겟 프로필 리스트
target_profiles = [
    "fashion_influencer_1",
    "beauty_blogger_2",
    "lifestyle_creator_3"
]

# 또는 검색 조건으로 자동 수집
search_criteria = {
    "niche": "fashion",
    "follower_range": (10000, 100000),
    "engagement_rate": ">3%",
    "location": "Seoul"
}
```

#### Step 3: 프로필 정보 수집

```python
from src.agents.profile_scraper_agent import ProfileScraperAgent

# ProfileScraperAgent 사용 (AI 기반)
scraper = ProfileScraperAgent()

profile_data = scraper.collect_profile_info(
    username="target_profile",
    collect_fields=[
        "followers",
        "following",
        "posts_count",
        "recent_posts",
        "comments",
        "engagement_rate"
    ]
)

print(f"팔로워: {profile_data['followers']}")
print(f"포스팅: {profile_data['posts_count']}")
print(f"참여율: {profile_data['engagement_rate']}")
```

#### Step 4: AI 기반 맞춤형 DM 생성 및 발송

```python
from src.agents.dm_composer_agent import DMComposerAgent

# DMComposerAgent 사용 (AI가 개인화 메시지 생성)
dm_agent = DMComposerAgent()

# 프로필 데이터 기반 맞춤형 메시지 생성
message = dm_agent.compose_personalized_dm(
    profile_data=profile_data,
    template="""
    안녕하세요 {username}님!

    {follower_count}명의 팔로워와 함께하시는 모습이 정말 멋지네요.
    특히 최근 {recent_post_topic}에 대한 포스팅이 인상 깊었습니다.

    저희 {my_brand}와 협업 기회에 대해 이야기 나누고 싶습니다.
    관심 있으시면 답장 부탁드립니다!

    감사합니다.
    """
)

# DM 발송
result = tm.send_dm(
    username=profile_data['username'],
    message=message,
    attachments=None  # 필요시 이미지/비디오 첨부
)

if result.succeeded:
    print(f"✅ DM 발송 성공: {profile_data['username']}")
else:
    print(f"❌ DM 발송 실패: {result.error}")
```

#### 실전 예제: 대량 프로필 수집 및 DM 자동화

```python
#!/usr/bin/env python
"""
프로필 정보 수집 및 자동 DM 발송 시스템
"""

from src.wrapper.smart_task_manager import SmartTaskManager
from src.agents.profile_scraper_agent import ProfileScraperAgent
from src.agents.dm_composer_agent import DMComposerAgent
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

logger = get_logger()

# 1. 타겟 프로필 검색 조건
SEARCH_CRITERIA = {
    "niche": "fashion",
    "follower_range": (10000, 100000),
    "engagement_rate_min": 3.0,
    "location": "Seoul"
}

# 2. TaskManager 및 Agents 초기화
tm = SmartTaskManager.from_prompt(
    """
    패션 인플루언서 대상 협업 제안 DM 발송
    - 타겟: 팔로워 10k-100k, 서울 지역
    - 하루 30명 DM 발송
    - 개인화된 메시지
    - 안전한 속도
    """,
    username="my_brand_account"
)

scraper = ProfileScraperAgent()
dm_agent = DMComposerAgent()
db = DatabaseHandler()

# 3. 타겟 프로필 검색 및 수집
logger.info("타겟 프로필 검색 중...")

target_profiles = scraper.search_profiles(
    criteria=SEARCH_CRITERIA,
    limit=100  # 최대 100명 검색
)

logger.info(f"발견된 프로필: {len(target_profiles)}명")

# 4. 각 프로필 정보 수집 및 DM 발송
sent_count = 0
max_daily_dms = 30

for profile_username in target_profiles:
    if sent_count >= max_daily_dms:
        logger.info("일일 DM 한도 도달")
        break

    try:
        # 4.1 프로필 정보 수집
        logger.info(f"프로필 수집: {profile_username}")

        profile_data = scraper.collect_profile_info(
            username=profile_username,
            collect_fields=[
                "followers", "following", "posts_count",
                "recent_posts", "engagement_rate", "bio"
            ]
        )

        # 4.2 DB에 프로필 정보 저장
        db.save_profile_data(profile_data)

        # 4.3 조건 확인 (재검증)
        if not (10000 <= profile_data['followers'] <= 100000):
            logger.info(f"팔로워 범위 미충족, 건너뜀: {profile_username}")
            continue

        # 4.4 AI가 개인화 메시지 생성
        logger.info(f"맞춤형 DM 생성 중: {profile_username}")

        message = dm_agent.compose_personalized_dm(
            profile_data=profile_data,
            template_name="collaboration_proposal",  # 미리 정의된 템플릿
            brand_info={
                "name": "My Fashion Brand",
                "niche": "sustainable fashion",
                "collaboration_type": "sponsored post"
            }
        )

        # 4.5 DM 발송
        logger.info(f"DM 발송 중: {profile_username}")

        result = tm.send_dm(
            username=profile_username,
            message=message
        )

        if result.succeeded:
            logger.info(f"✅ DM 발송 성공: {profile_username}")

            # DB에 발송 기록 저장
            db.log_dm_sent(
                target_username=profile_username,
                message=message,
                status="sent"
            )

            sent_count += 1
        else:
            logger.error(f"❌ DM 발송 실패: {profile_username}")
            db.log_dm_sent(
                target_username=profile_username,
                message=message,
                status="failed",
                error=result.error
            )

        # 안전한 속도 유지 (Instagram 제재 방지)
        import time
        time.sleep(60)  # 각 DM 발송 후 1분 대기

    except Exception as e:
        logger.error(f"프로필 처리 실패 ({profile_username}): {e}")
        continue

# 6. 결과 리포트
logger.info("=" * 60)
logger.info("DM 발송 세션 완료")
logger.info("=" * 60)
logger.info(f"총 발송: {sent_count}/{max_daily_dms}")
logger.info(f"검색된 프로필: {len(target_profiles)}")

tm.close()
db.close()
```

---

## Agent 종류

### 기존 Agents

#### 1. ConfigGeneratorAgent
- **역할**: 자연어 프롬프트 → GramAddict YAML 설정 변환
- **파일**: `src/agents/config_agent.py`
- **특징**:
  - 안전 우선 접근
  - 해시태그 자동 선택
  - 작업 시간대 추천

#### 2. PlanningAgent
- **역할**: 계정 통계 분석 → 최적 작업 계획 생성
- **파일**: `src/agents/planning_agent.py`
- **특징**:
  - 과거 세션 데이터 분석
  - 성공률 계산
  - 목표 기반 추천

#### 3. AgentManager
- **역할**: 여러 Agent 오케스트레이션
- **파일**: `src/agents/agent_manager.py`
- **특징**:
  - ConfigGeneratorAgent + PlanningAgent 통합
  - 설정과 계획을 결합한 워크플로우

### 새로운 Agents (프로젝트 목표용)

#### 4. ContentFilterAgent ⚠️ (개발 필요)
- **역할**: 스토리 및 포스트 내용 필터링
- **파일**: `src/agents/content_filter_agent.py` (예정)
- **기능**:
  - 불량 단어 감지 (욕설, 광고, 스팸)
  - 이미지 내용 분석 (AI 기반)
  - 필터링 정책 적용
- **사용 예**:
  ```python
  from src.agents.content_filter_agent import ContentFilterAgent

  filter_agent = ContentFilterAgent()

  # 텍스트 필터링
  is_safe = filter_agent.check_text(
      text="스토리 텍스트 내용",
      bad_words=["욕설", "광고"]
  )

  # 이미지 필터링 (AI 비전)
  is_safe_image = filter_agent.check_image(
      image_path="story_image.jpg",
      detect=["adult_content", "violence", "spam"]
  )
  ```

#### 5. ProfileScraperAgent ⚠️ (개발 필요)
- **역할**: 프로필 정보 자동 수집
- **파일**: `src/agents/profile_scraper_agent.py` (예정)
- **기능**:
  - 프로필 검색 (조건 기반)
  - 팔로워/팔로잉/포스팅 수 수집
  - 최근 게시물 및 댓글 분석
  - 참여율(Engagement Rate) 계산
- **사용 예**:
  ```python
  from src.agents.profile_scraper_agent import ProfileScraperAgent

  scraper = ProfileScraperAgent()

  # 프로필 정보 수집
  profile = scraper.collect_profile_info(
      username="target_profile",
      collect_fields=["followers", "posts", "comments"]
  )

  # 검색 조건으로 프로필 찾기
  profiles = scraper.search_profiles(
      criteria={
          "niche": "fashion",
          "follower_range": (10000, 100000)
      },
      limit=50
  )
  ```

#### 6. DMComposerAgent ⚠️ (개발 필요)
- **역할**: AI 기반 맞춤형 DM 메시지 생성
- **파일**: `src/agents/dm_composer_agent.py` (예정)
- **기능**:
  - 프로필 데이터 기반 개인화
  - 템플릿 기반 메시지 생성
  - A/B 테스팅 지원
  - 자연스러운 톤 유지
- **사용 예**:
  ```python
  from src.agents.dm_composer_agent import DMComposerAgent

  dm_agent = DMComposerAgent()

  # 개인화 메시지 생성
  message = dm_agent.compose_personalized_dm(
      profile_data={
          "username": "target",
          "followers": 50000,
          "recent_post_topic": "fashion"
      },
      template_name="collaboration_proposal"
  )
  ```

---

## 고급 사용법

### 스케줄링 자동화

```python
import schedule
import time
from src.wrapper.smart_task_manager import SmartTaskManager

def daily_restory_job():
    """매일 오전 10시 리스토리 작업"""
    tm = SmartTaskManager.from_prompt(
        "해시태그 리스토리 20개, 불량 단어 필터링",
        username="my_account"
    )

    plan = tm.get_intelligent_plan()
    result = tm.run_with_plan(plan)
    tm.close()

def daily_dm_job():
    """매일 오후 3시 DM 발송 작업"""
    # DM 발송 로직
    pass

# 스케줄 설정
schedule.every().day.at("10:00").do(daily_restory_job)
schedule.every().day.at("15:00").do(daily_dm_job)

# 스케줄러 실행
while True:
    schedule.run_pending()
    time.sleep(60)
```

### 데이터베이스 연동

```python
from src.utils.db_handler import DatabaseHandler

db = DatabaseHandler()

# 프로필 데이터 저장
db.save_profile_data({
    "username": "target_profile",
    "followers": 50000,
    "posts_count": 1200,
    "engagement_rate": 4.5
})

# DM 발송 기록 저장
db.log_dm_sent(
    target_username="target_profile",
    message="협업 제안 메시지",
    status="sent"
)

# 통계 조회
stats = db.get_dm_statistics(days=7)
print(f"7일간 발송된 DM: {stats['total_sent']}")
```

---

## 예제

### 예제 1: 해시태그 스토리 필터링 및 리스토리

```python
#!/usr/bin/env python
"""해시태그 스토리 자동 리스토리 (불량 단어 필터링)"""

from src.wrapper.smart_task_manager import SmartTaskManager
from src.agents.content_filter_agent import ContentFilterAgent

# 1. 필터 설정
bad_words = ["욕설", "광고", "스팸"]
filter_agent = ContentFilterAgent(bad_words=bad_words)

# 2. TaskManager 생성
tm = SmartTaskManager.from_prompt(
    "해시태그: #맛집, #카페, 하루 20개 리스토리, 필터링",
    username="my_account"
)

# 3. 실행
plan = tm.get_intelligent_plan()
result = tm.run_with_plan(plan)

print(f"리스토리: {result.stats['restories']}")
print(f"필터링: {result.stats['filtered']}")
```

### 예제 2: 프로필 수집 및 맞춤형 DM

```python
#!/usr/bin/env python
"""프로필 정보 수집 및 개인화 DM 발송"""

from src.agents.profile_scraper_agent import ProfileScraperAgent
from src.agents.dm_composer_agent import DMComposerAgent

scraper = ProfileScraperAgent()
dm_agent = DMComposerAgent()

# 1. 프로필 검색
profiles = scraper.search_profiles(
    criteria={"niche": "fashion", "follower_range": (10000, 100000)},
    limit=30
)

# 2. 각 프로필에 DM 발송
for profile in profiles:
    # 정보 수집
    data = scraper.collect_profile_info(profile['username'])

    # 개인화 메시지 생성
    message = dm_agent.compose_personalized_dm(
        profile_data=data,
        template_name="collaboration"
    )

    # DM 발송
    send_dm(profile['username'], message)

    time.sleep(60)  # 안전한 속도
```

---

## 문제 해결

### 문제: `ImportError: openai-agents required`

**해결**:
```bash
pip install openai-agents openai
```

### 문제: `ValueError: OPENAI_API_KEY required`

**해결**:
1. `.env` 파일에 `OPENAI_API_KEY=sk-...` 추가
2. 또는: `export OPENAI_API_KEY=sk-...`

### 문제: 필터링이 작동하지 않음

**해결**:
1. `ContentFilterAgent` 초기화 확인
2. 불량 단어 리스트 검토
3. 로그 확인: `logs/content_filter.log`

### 문제: DM 발송 실패

**원인**: Instagram 일일 DM 한도 초과

**해결**:
- 신규 계정: 하루 20-30개
- 오래된 계정: 하루 50-100개
- 속도 조절: 각 DM 사이 1-2분 대기

### 문제: 프로필 정보 수집 오류

**원인**: 프라이빗 계정 또는 차단됨

**해결**:
1. 공개 계정만 타겟팅
2. IP 로테이션 고려
3. 속도 줄이기 (시간당 30-50개)

---

## 다음 단계

### 개발 필요 모듈

1. **ContentFilterAgent** - 스토리/포스트 내용 필터링
2. **ProfileScraperAgent** - 프로필 정보 자동 수집
3. **DMComposerAgent** - AI 기반 맞춤형 DM 생성

### 통합 계획

이 모듈들은 `OPENAI_AGENTS_INTEGRATION.md`에 정의된 아키텍처를 따라 개발될 예정입니다.

---

## 추가 리소스

- [OpenAI Agents SDK 문서](https://openai.github.io/openai-agents-python/ko/)
- [프로젝트 통합 계획](../OPENAI_AGENTS_INTEGRATION.md)
- [GramAddict 문서](https://github.com/GramAddict/GramAddict)

---

## 지원

문제 발생 시:
1. GitHub Issues에 보고
2. 로그 파일 확인 (`logs/`)
3. 테스트 실행: `python -m src.agents.agent_manager`

---

**⚠️ 중요 안내**:
- ContentFilterAgent, ProfileScraperAgent, DMComposerAgent는 아직 개발 중입니다.
- 현재는 ConfigGeneratorAgent와 PlanningAgent만 사용 가능합니다.
- 새로운 Agent 개발이 필요하면 프로젝트 팀에 문의하세요.
