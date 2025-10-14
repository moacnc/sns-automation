# Instagram Automation System

GramAddict 기반 Instagram 자동화 시스템 (Stage 1)

## 프로젝트 개요

실제 Android 디바이스를 연결하여 Instagram 앱을 자동으로 제어하는 시스템입니다.
GramAddict 오픈소스를 기반으로 커스텀 Wrapper를 구축하여 작업 관리 및 로그 수집 기능을 추가합니다.

## 주요 기능

- ✅ Instagram 로그인/로그아웃 자동화
- ✅ 해시태그 기반 상호작용 (좋아요, 팔로우)
- ✅ 사용자 팔로워 상호작용
- ✅ 안전한 작업 속도 제어 (인간 행동 패턴)
- ✅ 작업 로그 수집 및 데이터베이스 저장
- ✅ 작업 스케줄링
- ✅ GramAddict 런타임 래핑 (동적 설정 생성, 세션별 로그/스크린샷 분리)
- 🤖 **AI 기반 설정 생성** (OpenAI Agents SDK 통합)
- 🤖 **지능형 작업 계획** (계정 통계 분석 및 자동 최적화)

## 시스템 요구사항

### 필수
- **Python**: 3.6 - 3.9 (3.10 미지원)
- **OS**: macOS, Linux, Windows
- **Android 디바이스**: Android 5.0 이상, Instagram 앱 설치
- **ADB**: Android Debug Bridge
- **PostgreSQL**: 12+ 또는 **AlloyDB** (Google Cloud)

### 권장
- Android 디바이스 (실제 기기 권장, 에뮬레이터 가능)
- USB 케이블 또는 Wi-Fi ADB 연결
- PostgreSQL 로컬 설치 또는 AlloyDB 클러스터

## 빠른 시작 (로컬 개발)

### 자동 설정 (권장)

```bash
# 한 줄로 모든 설정 완료
./scripts/setup_dev.sh
```

이 스크립트는 Docker, PostgreSQL, Python 환경을 자동으로 설정합니다.

**📘 완전한 개발 가이드**: **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** ⭐ **이 문서 하나로 모든 것을 파악하세요!**

---

## GramAddict Wrapper 아키텍처

`src/gramaddict_adapter` 패키지가 GramAddict 실행을 위한 핵심 래퍼입니다.

- `GramAddictConfigAdapter`: 전역/계정 YAML을 병합해 세션별 설정을 `config/generated/`에 생성합니다.
- `GramAddictSessionRunner`: GramAddict CLI를 호출하며 stdout/stderr를 실시간 수집하고 세션별 로그/스크린샷 디렉토리를 준비합니다.
- `TaskManager`: 위 어댑터를 이용해 세션 등록, 실행, 로그 파싱을 한 번에 처리합니다.

실행 방법은 다음과 같습니다.

```bash
python3 src/main.py --config config/accounts/myaccount.yml
```

실행이 끝나면 런타임 로그는 `logs/gramaddict/<SESSION_ID>/`, 동적 설정 파일은 `config/generated/` 아래에 저장됩니다 (`.gitignore` 처리됨).

---

## 설치 방법 (수동)

### 1. ADB 설치

**macOS (Homebrew)**:
```bash
brew install android-platform-tools
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install android-tools-adb
```

**Windows**:
[Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools) 다운로드

### 2. Python 가상환경 생성

```bash
python3 -m venv gramaddict-env
source gramaddict-env/bin/activate  # Mac/Linux
# gramaddict-env\Scripts\activate   # Windows
```

### 3. PostgreSQL / AlloyDB 설정

**로컬 개발 (PostgreSQL)**:
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Linux
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# 데이터베이스 생성
psql -U postgres
CREATE DATABASE instagram_automation;
\q
```

**프로덕션 (AlloyDB)**: [DOC/PostgreSQL_Setup.md](DOC/PostgreSQL_Setup.md) 참고

### 4. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (DB 연결 정보 입력)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=your_password
```

### 5. 의존성 설치

```bash
pip install -r requirements.txt
```

### 6. Android 디바이스 설정

1. **개발자 옵션 활성화**:
   - 설정 → 휴대전화 정보 → 빌드 번호 7번 탭

2. **USB 디버깅 활성화**:
   - 설정 → 개발자 옵션 → USB 디버깅 ON

3. **디바이스 연결 확인**:
   ```bash
   adb devices
   ```
   출력 예시:
   ```
   List of devices attached
   ABCD1234    device
   ```

#### WiFi를 통한 무선 연결 (선택사항)

USB 케이블 없이 WiFi로 기기를 연결할 수 있습니다.

**사전 요구사항**:
- 컴퓨터와 Android 기기가 같은 WiFi 네트워크에 연결되어 있어야 함
- 초기 설정 시 USB 케이블 필요

**WiFi 연결 설정 방법**:

1. **기기 IP 주소 확인**:
   ```bash
   # USB로 연결된 상태에서
   adb -s <DEVICE_ID> shell ip addr show wlan0 | grep inet
   ```
   또는 기기 설정에서: 설정 → WiFi → 연결된 네트워크 → IP 주소

2. **WiFi 디버깅 활성화**:
   ```bash
   adb -s <DEVICE_ID> tcpip 5555
   ```
   출력: `restarting in TCP mode port: 5555`

3. **WiFi로 연결**:
   ```bash
   adb connect <기기_IP>:5555
   ```
   예시: `adb connect 192.168.1.100:5555`

4. **USB 케이블 분리**:
   - 이제 USB 케이블을 제거해도 됩니다
   - 필요하면 충전용으로만 사용 가능

5. **연결 확인**:
   ```bash
   adb devices
   ```
   출력 예시:
   ```
   List of devices attached
   192.168.1.100:5555    device
   ```

**WiFi 연결 해제 및 문제 해결**:

```bash
# WiFi 연결 해제
adb disconnect <기기_IP>:5555

# 연결이 안될 때
adb kill-server
adb connect <기기_IP>:5555

# USB 연결로 다시 전환
adb usb
```

**주의사항**:
- WiFi 네트워크가 변경되면 재연결 필요
- 컴퓨터 재부팅 시 재연결 필요
- USB 연결보다 속도가 느릴 수 있음
- 여러 기기 연결 시 각각의 IP:포트로 연결

**scrcpy 화면 미러링 (WiFi 연결 시)**:
```bash
# WiFi 연결된 기기 미러링
scrcpy --serial <기기_IP>:5555

# 예시
scrcpy --serial 192.168.1.100:5555
```

## 설정 방법

### 1. 계정 설정 파일 생성

`config/accounts/example.yml` 파일을 복사하여 자신의 계정 설정 생성:

```bash
cp config/accounts/example.yml config/accounts/myaccount.yml
```

### 2. 설정 파일 편집

`config/accounts/myaccount.yml`:
```yaml
# Instagram 계정 정보 (실제 값으로 변경)
username: your_instagram_username
device: DEVICE_ID  # adb devices 출력에서 확인

# 작업 설정
interactions:
  - interact-hashtag-posts:
      hashtags:
        - travel
        - photography
      likes-count: 2-4
      follow-percentage: 30
      amount: 10-20

# 안전 설정
limits:
  likes-per-day: 50
  follows-per-day: 30

working-hours:
  - 09:00-12:00
  - 14:00-18:00

speed-multiplier: 1.5  # 느리게 (더 안전)
```

## 사용 방법

### 🤖 AI 기반 사용 (권장)

**자연어로 설정 생성 및 실행**:

```python
from src.wrapper.smart_task_manager import SmartTaskManager

# 자연어로 TaskManager 생성
tm = SmartTaskManager.from_prompt(
    "여행 계정 성장, 주당 50명 팔로워, 안전 모드",
    username="travel_account"
)

# AI가 계정 데이터 분석하여 최적 계획 생성
plan = tm.get_intelligent_plan()

# 계획 적용하여 실행
result = tm.run_with_plan(plan)
```

**자세한 AI 기능 사용법**: [docs/AGENTS_USAGE_GUIDE.md](docs/AGENTS_USAGE_GUIDE.md)

### 기본 실행 (YAML 설정 파일)

```bash
python3 src/main.py --config config/accounts/myaccount.yml
```

### Task Manager 사용 (개발 예정)

```bash
python3 src/main.py --schedule --config config/accounts/myaccount.yml
```

## 프로젝트 구조

```
instagram-automation/
├── config/
│   ├── accounts/
│   │   ├── example.yml        # 예시 설정
│   │   └── myaccount.yml      # 실제 설정 (gitignore)
│   └── global_config.yml      # 전역 설정
├── src/
│   ├── agents/                # 🤖 OpenAI Agents SDK
│   │   ├── config_agent.py    # 자연어 → YAML 설정 변환
│   │   ├── planning_agent.py  # 계정 통계 분석 및 계획 생성
│   │   └── agent_manager.py   # Agent 통합 관리자
│   ├── wrapper/
│   │   ├── task_manager.py    # GramAddict CLI 래퍼
│   │   ├── smart_task_manager.py  # 🤖 AI 강화 TaskManager
│   │   ├── log_parser.py      # 로그 수집/분석
│   │   └── scheduler.py       # 작업 스케줄링
│   ├── utils/
│   │   ├── logger.py          # 로깅 유틸리티
│   │   ├── db_handler.py      # PostgreSQL/AlloyDB 처리
│   │   └── session_lock.py    # 세션 동시성 제어
│   └── main.py                # 메인 진입점
├── logs/
│   ├── gramaddict/            # GramAddict 원본 로그
│   └── custom/                # 커스텀 로그
├── data/
│   └── automation.db          # 작업 로그 DB
├── DOC/
│   └── 개발문서.md             # 개발 문서
├── requirements.txt
├── .gitignore
└── README.md
```

## 안전 사용 가이드

### ⚠️ 중요 주의사항

1. **테스트 계정 사용**: 처음에는 제재되어도 괜찮은 테스트 계정 사용
2. **보수적 설정**: 낮은 작업량으로 시작 (하루 30-50개 좋아요)
3. **작업 시간 분산**: 24시간 작동 금지, 새벽 작업 금지
4. **신규 계정 워밍업**: 최소 2주 수동 사용 후 자동화 시작

### ✅ 권장 설정

```yaml
limits:
  likes-per-day: 30-50
  follows-per-day: 20-30
  unfollows-per-day: 20-30
  comments-per-day: 5-10

speed-multiplier: 1.5-2.0  # 느리게

working-hours:
  - 09:00-11:00
  - 14:00-16:00
  - 19:00-21:00
```

## 문제 해결

### ADB 디바이스 인식 안됨
```bash
# ADB 서버 재시작
adb kill-server
adb start-server
adb devices
```

### Python 버전 오류
- Python 3.10은 지원하지 않습니다
- Python 3.6-3.9 사용하세요

### GramAddict 설치 오류
```bash
pip install --upgrade pip
pip install gramaddict
```

## 개발 로드맵

### Stage 1 (완료)
- [x] 프로젝트 구조 생성
- [x] 기본 설정 파일 작성
- [x] Task Manager 개발
- [x] 로그 수집기 개발
- [x] 데이터베이스 연동 (PostgreSQL/AlloyDB)
- [x] DB 재연결 로직 구현
- [x] 세션 동시성 제어
- [x] 로그 파싱 패턴 개선
- [x] 유닛 테스트 추가
- [x] 🤖 OpenAI Agents SDK 통합
  - [x] ConfigGeneratorAgent (자연어 → YAML)
  - [x] PlanningAgent (통계 분석 및 계획)
  - [x] SmartTaskManager (AI 강화 실행)
  - [x] 종합 사용 가이드

### Stage 2 (계획)
- [ ] 스케줄링 기능
- [ ] 통합 테스트 추가
- [ ] 모니터링 및 알림 시스템
- [ ] 추가 AI Agent 개발
  - [ ] SafetyMonitorAgent (실시간 안전성 모니터링)
  - [ ] LogAnalysisAgent (로그 이상 패턴 감지)
- [ ] 웹 대시보드 (선택)

## 라이선스

본 프로젝트는 GramAddict (MIT License)를 기반으로 합니다.

⚠️ **면책 조항**: 이 프로젝트는 교육 목적으로 제공됩니다. Instagram의 이용약관을 위반할 수 있으며, 계정 제재의 위험이 있습니다. 사용자 책임 하에 사용하세요.

## 테스트

### 유닛 테스트 실행

```bash
# 테스트 환경 설정
source gramaddict-env/bin/activate
pip install pytest pytest-cov

# 모든 테스트 실행
pytest

# 커버리지 리포트와 함께 실행
pytest --cov=src --cov-report=html

# 특정 테스트만 실행
pytest tests/test_config_adapter.py -v
```

### 커버리지 확인

테스트 실행 후 `htmlcov/index.html` 파일을 브라우저로 열어 코드 커버리지를 확인할 수 있습니다.

## 최근 개선 사항

**2025-10-10 업데이트**:
- ✅ DB 연결 재시도 로직 구현 (3회, 타임아웃 10초)
- ✅ 세션 동시성 제어 (파일 기반 락)
- ✅ 로그 파싱 패턴 개선 (정교한 정규식)
- ✅ 타입 힌팅 일관성 개선
- ✅ 유닛 테스트 추가 (pytest)
- 🤖 **OpenAI Agents SDK 통합** (자연어 설정 생성, 지능형 작업 계획)

자세한 내용은 [IMPROVEMENTS.md](IMPROVEMENTS.md)와 [docs/AGENTS_USAGE_GUIDE.md](docs/AGENTS_USAGE_GUIDE.md)를 참고하세요.

## 📚 문서

### 핵심 문서
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** ⭐ **단일 통합 개발 가이드 (필독!)**
- [README.md](README.md) - 프로젝트 개요 (현재 문서)
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 개선 사항 로그
- [OPENAI_AGENTS_INTEGRATION.md](OPENAI_AGENTS_INTEGRATION.md) - AI 통합 계획

### 아카이브 (참고용)
- [docs/archive/개발문서.md](docs/archive/개발문서.md) - 초기 개발 문서
- [docs/archive/Local_Development.md](docs/archive/Local_Development.md) - 로컬 개발 상세
- [docs/archive/PostgreSQL_Setup.md](docs/archive/PostgreSQL_Setup.md) - DB 설정 상세
- [docs/archive/AGENTS_USAGE_GUIDE.md](docs/archive/AGENTS_USAGE_GUIDE.md) - Agents 상세 가이드
- [docs/archive/PROJECT_ARCHITECTURE.md](docs/archive/PROJECT_ARCHITECTURE.md) - 아키텍처 상세

### 외부 링크
- [GramAddict 공식 문서](https://docs.gramaddict.org/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/ko/)
- [Android ADB 가이드](https://developer.android.com/studio/command-line/adb)

## 지원

문제가 발생하면 [Issues](../../issues)에 등록해주세요.
