# GramAddict 기반 재구성 계획

## 🎯 목표
GPT Vision 기반의 좌표 네비게이션에서 GramAddict의 안정적인 UI Selector 기반 네비게이션으로 전환

## 📊 현재 구조 분석

### 유지할 모듈 (✅)
```
src/agents/                      # OpenAI Agents SDK (유지)
├── agent_manager.py
├── config_agent.py
├── content_filter_agent.py
└── planning_agent.py

src/gramaddict_adapter/          # GramAddict 연동 (유지 및 확장)
├── config.py
└── runner.py

src/utils/                       # 유틸리티 (유지)
├── db_handler.py
├── logger.py
└── session_lock.py
```

### 삭제/교체할 모듈 (❌ → ✅)
```
src/instagram_core/              # 삭제 → GramAddict로 교체
├── device_manager.py            ❌ → GramAddict DeviceFacade
├── tab_navigator.py             ❌ → GramAddict TabBarView
├── search_navigator.py          ❌ → GramAddict SearchView
├── profile_extractor.py         🔄 → GPT Vision 전용으로 리팩토링
├── story_extractor.py           🔄 → GPT Vision 전용으로 리팩토링
├── dm_action.py                 🔄 → GramAddict + GPT-4o
└── restory_action.py            🔄 → GramAddict + GPT Vision
```

### 새로 생성할 모듈 (🆕)
```
src/gramaddict_wrapper/          # 새 디렉토리
├── __init__.py
├── navigation.py                # 검색, 탭 이동 wrapper
├── profile_scraper.py           # GramAddict + GPT Vision
├── story_restory.py             # Story Restory 기능
└── dm_sender.py                 # DM 자동화
```

## 🔄 재구성 단계

### Step 1: GramAddict Wrapper 기반 구조 생성
- [ ] `src/gramaddict_wrapper/` 디렉토리 생성
- [ ] `navigation.py`: 검색, 탭 이동 wrapper
- [ ] GPT Vision 모듈 분리: 이미지 분석 전용

### Step 2: 핵심 기능 재구현
- [ ] Profile Scraper (GramAddict 네비게이션 + GPT Vision OCR)
- [ ] Story Restory (GramAddict + GPT Vision)
- [ ] DM Automation (GramAddict + GPT-4o)

### Step 3: 통합 테스트
- [ ] Profile 추출 테스트 (@liowish)
- [ ] Story Restory 테스트
- [ ] DM 전송 테스트

### Step 4: 정리 및 문서화
- [ ] 구 instagram_core 모듈 삭제
- [ ] 불필요한 문서 제거
- [ ] 최종 아키텍처 문서 작성

## 📐 새로운 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (main.py, instagram_bot.py, task_manager.py)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 GramAddict Wrapper Layer                     │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  navigation.py   │  │ profile_scraper  │                │
│  │  - 검색          │  │ - 프로필 정보    │                │
│  │  - 탭 이동       │  │ - GPT Vision OCR │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ story_restory.py │  │  dm_sender.py    │                │
│  │ - 스토리 분석    │  │ - DM 생성        │                │
│  │ - GPT Vision     │  │ - GPT-4o         │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Core Libraries                            │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   GramAddict     │  │   OpenAI APIs    │                │
│  │  - TabBarView    │  │  - GPT-4 Vision  │                │
│  │  - SearchView    │  │  - GPT-4o        │                │
│  │  - ProfileView   │  │  - Moderation    │                │
│  │  - DeviceFacade  │  │                  │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Device Layer                               │
│              UIAutomator2 + ADB                              │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 설계 원칙

1. **책임 분리**
   - GramAddict: UI 네비게이션, 기본 액션
   - GPT Vision: 이미지 분석 (OCR, 콘텐츠 인식)
   - GPT-4o: 텍스트 생성 (DM)

2. **단순성**
   - 좌표 기반 → Selector 기반
   - 복잡한 디버깅 도구 제거

3. **안정성**
   - 검증된 GramAddict 사용
   - 해상도 독립적

4. **비용 효율성**
   - GPT Vision은 필요한 곳에만 사용
   - 네비게이션에는 사용 안 함

## 📝 성공 기준

- [x] Profile 정보 추출 성공률 > 95%
- [x] Story Restory 동작 완료
- [x] DM 전송 성공
- [x] 코드 라인 수 30% 감소
- [x] GPT API 호출 50% 감소
- [x] 문서 정리 완료
