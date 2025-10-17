# Instagram Automation Development Roadmap

## 📋 목표 (tests/todo.md 기반)

1. **Instagram의 모든 동작과 좌표를 완전히 모듈화**
2. **시나리오 기반 AI Agent 자동화**
   - Agent가 필요한 모듈만 선택하여 실행
   - 데이터 수집 → 분석 → 저장 → 행동의 자동화된 워크플로우

---

## 🎯 현재 상태 (Phase 1-5 완료)

### ✅ 완료된 기능 및 검증된 좌표

| Phase | 기능 | 구현 위치 | 검증된 좌표 |
|-------|------|-----------|------------|
| **Phase 1** | 디바이스 연결, Instagram 실행 | `navigation.py` | - |
| **Phase 2** | 탭 네비게이션, 사용자 검색 | `navigation.py` | `nav_home(108, 2045)`, `nav_search(324, 2045)` |
| **Phase 3** | 팔로우, OCR, 콘텐츠 필터링 | `navigation.py`, `vision_analyzer.py` | `follow_button(257, 630)` |
| **Phase 4** | 프로필 스크래핑, 고급 분석 | `profile_scraper.py`, `vision_analyzer.py` | - |
| **Phase 5** | DM 전송 (개인화 메시지) | `dm_sender.py` | `message_button(372, 290)`, `send_button(668, 1420)` |

### 📦 기존 모듈 및 테스트 결과

```
✅ 성공한 기능 (tests/ 참조)
├── navigation.py
│   ├── connect() - 디바이스 연결
│   ├── launch_instagram() - 앱 실행
│   ├── goto_search() - 검색 탭 이동 (324, 2045)
│   ├── search_username() - 사용자 검색
│   └── follow_user() - 팔로우 (257, 630)
│
├── vision_analyzer.py
│   ├── analyze_profile_screenshot() - 프로필 OCR
│   ├── analyze_profile_advanced() - 성향 분석
│   └── analyze_grid_posts() - 그리드 분석
│
├── profile_scraper.py
│   └── scrape_profile() - 통합 프로필 스크래핑
│
├── dm_sender.py
│   ├── _generate_message() - GPT-4o 메시지 생성
│   └── _send_dm_to_current_profile() - DM 전송
│       ├── 메시지 버튼: (372, 290)
│       └── 전송 버튼: (668, 1420)
│
└── story_restory.py (테스트 필요)
```

### 📍 검증된 좌표 목록 (1080x2400 기준)

**Phase 1-5 테스트에서 확인된 좌표:**

```python
# Navigation Bar (하단)
NAV_HOME = (108, 2045)        # Phase 2 ✅
NAV_SEARCH = (324, 2045)      # Phase 2 ✅
NAV_PROFILE = (972, 2045)     # 추정

# Profile Actions
PROFILE_FOLLOW_BUTTON = (257, 630)      # Phase 3 ✅ (UI Automator 확인)
PROFILE_MESSAGE_BUTTON = (372, 290)     # Phase 5 ✅
PROFILE_FOLLOWING_BUTTON = (132, 290)   # Phase 3 추정

# DM Screen
DM_SEND_BUTTON = (668, 1420)  # Phase 5 ✅

# Search
SEARCH_INPUT = (530, 168)     # Phase 2 추정
SEARCH_FIRST_RESULT = (540, 522)  # Phase 2 추정
```

**아직 테스트되지 않은 기능:**
- 해시태그 검색
- 포스팅 저장 (이미지 + 텍스트)
- 팔로워 리스트 크롤링
- 좋아요, 댓글
- 스토리 리스토리

---

## 🗺️ 개발 로드맵

### 📌 Phase 6: Core Module Refactoring (핵심 모듈 리팩토링)

**목표**: Phase 1-5의 검증된 동작들을 재사용 가능한 독립 함수로 분리

> **용어 설명**: "Atomic Actions" = 더 이상 나눌 수 없는 최소 단위 동작
> 예: `follow_user()`, `send_dm()`, `like_post()` 등

---

#### 6.1 Device Config System (디바이스 고정 및 좌표 관리)
**우선순위**: 🔴 높음

**현재 문제**:
```python
# navigation.py에 좌표가 하드코딩됨
self._adb_tap(324, 2045)  # 검색 탭
self._adb_tap(257, 630)   # 팔로우 버튼
```

**해결 방안**:
```python
# 1. 디바이스 자동 인식
DeviceConfig.detect_device()
# → Serial: R39M30H71LK
# → Model: SM-N981N
# → Resolution: 1080x2400

# 2. 설정 파일 자동 생성
# src/config/devices/R39M30H71LK_SM-N981N.json
{
  "device_info": {...},
  "coordinates": {
    "nav_search": [324, 2045],     # Phase 2 검증됨
    "profile_follow": [257, 630],   # Phase 3 검증됨
    "dm_send": [668, 1420]          # Phase 5 검증됨
  }
}

# 3. 간편한 사용
from src.config.device_config import get_coord

x, y = get_coord("nav_search")
self._adb_tap(x, y)
```

**작업 항목**:
- [x] `DeviceConfig` 클래스 구현 ✅
- [ ] Phase 1-5의 검증된 좌표를 설정 파일로 마이그레이션
- [ ] 기존 하드코딩 좌표를 `get_coord()` 사용으로 변경
- [ ] 좌표 검증 도구 (UI Automator 활용)

**참조할 파일**:
- `tests/phase2_navigation/` - 검색 탭 좌표
- `tests/phase3_vision/test_follow_user.py` - 팔로우 버튼 좌표
- `tests/phase5_dm/test_dm_send.py` - DM 버튼 좌표

**예상 소요 시간**: 2-3일

---

#### 6.2 Atomic Actions (원자적 동작 모듈)
**우선순위**: 🔴 높음

**목표**: Phase 1-5에서 검증된 동작들을 독립 함수로 추출

**Phase 1-5 기반 Atomic Actions 목록**:

```python
# src/actions/atomic_actions.py
class AtomicActions:
    """
    Phase 1-5에서 검증된 동작들을 모듈화
    """

    # === Phase 1: Infrastructure ===
    def connect_device(self) -> bool:
        """디바이스 연결 (tests/phase1_infrastructure/)"""

    def wake_and_unlock_screen(self) -> bool:
        """화면 깨우기 + 잠금 해제 (navigation.py)"""

    def launch_instagram(self) -> bool:
        """Instagram 앱 실행 (navigation.py)"""

    # === Phase 2: Navigation ===
    def goto_home(self) -> bool:
        """홈 탭 이동 (tests/phase2_navigation/)"""

    def goto_search(self) -> bool:
        """검색 탭 이동 (tests/phase2_navigation/)"""
        # 좌표: (324, 2045) ✅ 검증됨

    def search_username(self, username: str) -> bool:
        """사용자 검색 (tests/phase2_navigation/)"""

    # === Phase 3: Vision & Actions ===
    def follow_user(self) -> bool:
        """팔로우 (tests/phase3_vision/test_follow_user.py)"""
        # 좌표: (257, 630) ✅ UI Automator로 검증됨

    def check_follow_status(self) -> str:
        """팔로우 상태 확인 (navigation.py)"""
        # return: "follow" | "following" | "requested"

    def screenshot(self, path: str) -> bool:
        """스크린샷 촬영 (navigation.py)"""

    # === Phase 4: Profile Scraping ===
    def scrape_profile_basic(self, username: str) -> dict:
        """기본 프로필 정보 (tests/phase4_integration/)"""
        # follower_count, posts_count, bio 등

    def analyze_profile_advanced(self, screenshot_path: str) -> dict:
        """고급 프로필 분석 (vision_analyzer.py)"""
        # account_type, influencer_tier, collaboration_potential

    def analyze_grid_posts(self, screenshot_path: str) -> dict:
        """그리드 포스팅 분석 (vision_analyzer.py)"""

    # === Phase 5: DM Send ===
    def send_dm(self, username: str, message: str) -> bool:
        """DM 전송 (tests/phase5_dm/)"""
        # 메시지 버튼: (372, 290) ✅
        # 전송 버튼: (668, 1420) ✅

    def generate_personalized_message(self, username: str, profile: dict, template: str) -> str:
        """개인화 메시지 생성 (dm_sender.py)"""
        # GPT-4o 사용

    # === 아직 구현 안 된 동작들 (Phase 6+) ===
    def search_hashtag(self, hashtag: str) -> bool:
        """해시태그 검색 (TODO)"""

    def like_post(self) -> bool:
        """게시물 좋아요 (TODO)"""

    def save_post(self) -> bool:
        """게시물 저장 (TODO)"""

    def extract_followers(self, max_count: int) -> list:
        """팔로워 리스트 추출 (TODO)"""
```

**작업 항목**:
- [ ] Phase 1-5 코드에서 동작 추출
- [ ] 각 동작을 독립 함수로 리팩토링
- [ ] 좌표는 `get_coord()` 사용
- [ ] 성공/실패 감지 로직 추가
- [ ] 단위 테스트 작성

**참조할 파일**:
- `src/gramaddict_wrapper/navigation.py` - 대부분의 동작
- `src/gramaddict_wrapper/dm_sender.py` - DM 관련 동작
- `tests/phase*/` - 각 동작의 테스트 코드

**예상 소요 시간**: 5-7일

---

#### 6.3 Missing Actions (아직 없는 동작들 구현)
**우선순위**: 🟡 중간

**Phase 1-5에서 빠진 동작들**:

1. **해시태그 검색** (Phase 6.3.1)
   - 검색 탭 → 해시태그 입력 → 결과 선택
   - 좌표: 테스트 필요

2. **포스팅 상호작용** (Phase 6.3.2)
   - 좋아요: 하트 버튼
   - 댓글: 댓글 버튼 → 텍스트 입력
   - 저장: 북마크 버튼
   - 공유: 공유 버튼

3. **팔로워/팔로잉 리스트** (Phase 6.3.3)
   - 프로필 → 팔로워 클릭 → 스크롤 → 사용자명 추출

4. **스토리 기능** (Phase 6.3.4)
   - 스토리 보기
   - 리스토리 (Phase 6에서 테스트)

**작업 항목**:
- [ ] UI Automator로 버튼 좌표 찾기
- [ ] 각 동작 구현
- [ ] 테스트 작성
- [ ] 좌표를 설정 파일에 추가

**예상 소요 시간**: 7-10일

---

### 📌 Phase 7: Data Storage (데이터 저장)

**목표**: 수집한 데이터를 체계적으로 저장

**현재 상태**:
- ✅ Phase 4에서 JSON 파일로 저장 중
- `tests/phase4_integration/results/*.json`

**개선 방향**:

#### 옵션 1: JSON 파일 체계화 (간단)
```
data/
├── profiles/
│   └── liowish.json
├── campaigns/
│   └── 2025-10-17_influencer_outreach/
│       ├── config.yaml
│       ├── profiles.json
│       └── results.json
└── actions/
    └── 2025-10-17_actions.json
```

#### 옵션 2: 데이터베이스 도입 (나중에)
- SQLite 또는 PostgreSQL
- 실제 필요할 때 구현
- **지금은 JSON으로 충분**

**작업 항목**:
- [ ] JSON 파일 구조 표준화
- [ ] 파일명 규칙 정의
- [ ] 데이터 백업 스크립트
- [ ] (선택) 나중에 DB 마이그레이션

**예상 소요 시간**: 2-3일

---

### 📌 Phase 8: AI Agent Layer (AI 에이전트)

**목표**: 시나리오를 이해하고 자동으로 모듈을 조합하여 실행

#### 8.1 Scenario Definition (시나리오 정의)

**YAML 기반 시나리오 예시**:

```yaml
# scenarios/beauty_influencer_outreach.yaml
name: "Beauty Influencer DM Campaign"
description: "10K-100K 팔로워 뷰티 인플루언서에게 협업 제안 DM"

# === 타겟 기준 ===
criteria:
  follower_range:
    min: 10000
    max: 100000
  categories:
    - beauty
    - skincare
  is_verified: false
  is_private: false

# === 워크플로우 ===
workflow:
  # Step 1: 해시태그로 사용자 찾기
  - action: search_hashtag
    params:
      hashtag: "kbeauty"
      max_posts: 50
    save_to: "found_users"

  # Step 2: 프로필 스크래핑 (Phase 4 기능)
  - action: scrape_profiles
    source: "found_users"
    filters:
      - criteria.follower_range
      - criteria.categories
    save_to: "qualified_profiles"

  # Step 3: DM 전송 (Phase 5 기능)
  - action: send_dm_batch
    source: "qualified_profiles"
    message_template: |
      안녕하세요 {{username}}님!
      저희는 한국의 {{brand_name}} 브랜드입니다.
      {{username}}님의 {{content_category}} 콘텐츠를 보고
      협업을 제안드립니다. 관심 있으시면 DM 주세요!
    max_per_day: 20

# === 제한 사항 ===
limits:
  daily_actions:
    search: 100
    scrape: 50
    dm: 20
  delay_between_actions: 30  # seconds

# === 저장 경로 ===
output:
  directory: "campaigns/{{campaign_id}}"
  save_screenshots: true
  save_profiles: true
```

#### 8.2 Agent Implementation (에이전트 구현)

```python
# src/agents/scenario_agent.py
class ScenarioAgent:
    """
    YAML 시나리오를 읽고 자동 실행
    """

    def __init__(self):
        self.actions = AtomicActions()  # Phase 6에서 만든 것

    def execute_scenario(self, scenario_path: str):
        """
        시나리오 실행

        Example:
            agent = ScenarioAgent()
            agent.execute_scenario("scenarios/beauty_influencer.yaml")
        """
        # 1. YAML 로드
        scenario = self._load_yaml(scenario_path)

        # 2. 각 step 실행
        for step in scenario['workflow']:
            action_name = step['action']

            # 3. Atomic Action 매핑
            if action_name == "search_hashtag":
                self._handle_search_hashtag(step)
            elif action_name == "scrape_profiles":
                self._handle_scrape_profiles(step)
            elif action_name == "send_dm_batch":
                self._handle_send_dm_batch(step)

    def _handle_scrape_profiles(self, step):
        """
        프로필 스크래핑 핸들러 (Phase 4 활용)
        """
        usernames = self.context[step['source']]
        filters = step['filters']

        for username in usernames:
            # Atomic Action 사용
            profile = self.actions.scrape_profile_basic(username)

            # 필터 적용
            if self._apply_filters(profile, filters):
                self.context['qualified_profiles'].append(profile)

    def _handle_send_dm_batch(self, step):
        """
        DM 일괄 전송 핸들러 (Phase 5 활용)
        """
        profiles = self.context[step['source']]
        template = step['message_template']
        max_per_day = step['max_per_day']

        sent_count = 0
        for profile in profiles:
            if sent_count >= max_per_day:
                break

            # 메시지 개인화
            message = self._personalize(template, profile)

            # Atomic Action 사용
            if self.actions.send_dm(profile['username'], message):
                sent_count += 1

            # 딜레이
            time.sleep(30)
```

**작업 항목**:
- [ ] YAML 시나리오 파서
- [ ] ScenarioAgent 구현
- [ ] 각 action 핸들러 구현
- [ ] 진행 상황 로깅
- [ ] 에러 처리 및 복구

**예상 소요 시간**: 7-10일

---

### 📌 Phase 9: Advanced Features (고급 기능)

#### 9.1 Smart Scheduling (스마트 스케줄링)
- [ ] 시간대별 자동 실행
- [ ] Rate limiting (Instagram 탐지 회피)
- [ ] 사람처럼 행동하는 랜덤 딜레이

#### 9.2 Analytics (분석)
- [ ] 캠페인 성과 대시보드
- [ ] 인플루언서 순위 시스템
- [ ] 응답률 추적

#### 9.3 Multi-Account (멀티 계정)
- [ ] 여러 Instagram 계정 관리
- [ ] 계정별 독립 세션
- [ ] 계정 전환 자동화

**예상 소요 시간**: 10-15일

---

## 📅 전체 일정 (추정)

| Phase | 기간 | 누적 |
|-------|------|------|
| Phase 6.1: Device Config | 2-3일 | 3일 |
| Phase 6.2: Atomic Actions | 5-7일 | 10일 |
| Phase 6.3: Missing Actions | 7-10일 | 20일 |
| Phase 7: Data Storage | 2-3일 | 23일 |
| Phase 8: AI Agent Layer | 7-10일 | 33일 |
| Phase 9: Advanced Features | 10-15일 | 48일 |
| **총 예상 기간** | **~7주** | **7주** |

---

## 🎯 마일스톤

### Milestone 1: Modular Foundation (2주차)
- ✅ Device Config 완성
- ✅ Phase 1-5 동작들을 Atomic Actions로 추출
- ✅ 좌표 관리 시스템 완성

### Milestone 2: Complete Actions (4주차)
- ✅ 모든 Instagram 동작 구현 (해시태그, 좋아요, 댓글 등)
- ✅ 좌표 검증 완료
- ✅ 단위 테스트 통과

### Milestone 3: AI Automation (5주차)
- ✅ Scenario Agent 구현
- ✅ YAML 시나리오 실행
- ✅ 첫 번째 실전 캠페인 성공

### Milestone 4: Production Ready (7주차)
- ✅ 모든 고급 기능 구현
- ✅ 문서화 완료
- ✅ 안정적인 24시간 운영

---

## 🚀 즉시 시작 가능한 작업

### 1단계: Device Config 적용 (1일)

**Phase 1-5에서 검증된 좌표 수집:**

```bash
# 좌표 수집
grep -r "_adb_tap" src/ tests/ | grep -E "\([0-9]+, [0-9]+\)"

# 결과를 device config JSON으로 정리
```

**파일 생성:**
```
src/config/devices/R39M30H71LK_SM-N981N.json
```

### 2단계: Atomic Actions 추출 (3-5일)

**navigation.py에서 동작 추출:**
```python
# Before: navigation.py
def search_username(self, username):
    self._adb_tap(324, 2045)  # 검색 탭
    # ...

# After: atomic_actions.py
def goto_search(self):
    x, y = get_coord("nav_search")
    self._adb_tap(x, y)

def search_username(self, username):
    self.goto_search()
    # ...
```

### 3단계: 첫 번째 시나리오 실행 (1주)

**간단한 시나리오 작성:**
```yaml
# scenarios/simple_follow.yaml
name: "Simple Follow Test"
workflow:
  - action: search_username
    params: {username: "targetuser"}
  - action: follow_user
```

**실행:**
```python
agent = ScenarioAgent()
agent.execute_scenario("scenarios/simple_follow.yaml")
```

---

## 📝 다음 액션 아이템

**지금 당장 할 수 있는 것**:

1. ✅ **Device Config 구현 완료**
2. **Phase 1-5 좌표 수집** (30분)
   - `tests/` 폴더의 모든 좌표 찾기
   - JSON 파일로 정리
3. **navigation.py 리팩토링** (1일)
   - 좌표를 `get_coord()` 사용으로 변경
   - 테스트 실행하여 검증

---

## 💡 성공 기준

### Phase 6 완료 기준
- [ ] 모든 Phase 1-5 테스트가 Device Config 사용으로 통과
- [ ] 20개 이상의 Atomic Action 구현
- [ ] 좌표가 모두 설정 파일로 관리됨

### Phase 7 완료 기준
- [ ] JSON 파일 구조가 표준화됨
- [ ] 100개 이상의 프로필 데이터 저장 가능

### Phase 8 완료 기준
- [ ] 최소 3가지 시나리오가 YAML로 정의됨
- [ ] Agent가 시나리오를 자동 실행
- [ ] 에러 발생 시 로그 남기고 계속 진행

### Phase 9 완료 기준
- [ ] 실전 캠페인에서 100명 이상 처리
- [ ] 24시간 연속 운영 가능
- [ ] Instagram 탐지 없이 안정 운영

---

## 📞 참고

**Phase 1-5 테스트 참조:**
- `tests/phase1_infrastructure/` - 디바이스 연결
- `tests/phase2_navigation/` - 검색, 탭 이동
- `tests/phase3_vision/` - 팔로우, OCR
- `tests/phase4_integration/` - 프로필 스크래핑
- `tests/phase5_dm/` - DM 전송

**핵심 코드:**
- `src/gramaddict_wrapper/navigation.py` - 대부분의 동작
- `src/gramaddict_wrapper/vision_analyzer.py` - AI 분석
- `src/gramaddict_wrapper/dm_sender.py` - DM 관련
- `src/config/device_config.py` - 디바이스 설정 (새로 만듦)

---

이 로드맵은 **실제 검증된 Phase 1-5 기능**을 기반으로 작성되었습니다.
코드는 실제 개발하면서 작성하고, 이 문서는 방향성 가이드로 활용합니다.
