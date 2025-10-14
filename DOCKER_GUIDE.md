# Docker 환경 가이드

Instagram Automation 프로젝트를 Docker 환경에서 실행하기 위한 가이드입니다.

## 📋 사전 요구사항

1. **Docker Desktop 설치**
   - macOS: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **ADB 디바이스 연결**
   - USB 케이블로 Android 디바이스 연결
   - USB 디버깅 활성화
   - `adb devices`로 연결 확인

## 🚀 빠른 시작

### 1. Docker 이미지 빌드

```bash
docker-compose build
```

### 2. 컨테이너 실행

```bash
# 백그라운드에서 실행
docker-compose up -d

# 또는 인터랙티브 모드
docker-compose run --rm instagram-automation /bin/bash
```

### 3. 테스트 실행

#### 방법 1: 스크립트 사용 (권장)

```bash
# Phase 1 테스트
./docker-test.sh 1

# Phase 2 테스트
./docker-test.sh 2

# Phase 3 테스트
./docker-test.sh 3

# Phase 4 테스트
./docker-test.sh 4

# 모든 테스트 실행
./docker-test.sh all

# 인터랙티브 쉘 열기
./docker-test.sh shell
```

#### 방법 2: 직접 실행

```bash
# 컨테이너 내부로 접속
docker-compose exec instagram-automation /bin/bash

# 테스트 실행
python3 tests/phase1_infrastructure/test_device_connection.py
python3 tests/phase1_infrastructure/test_instagram_launch.py
python3 tests/phase2_navigation/test_tab_navigation.py
# ... etc
```

## 📁 Docker 구성

### Dockerfile
- Python 3.9 기반
- ADB (Android Debug Bridge) 포함
- 모든 Python 의존성 설치
- 필요한 디렉토리 자동 생성

### docker-compose.yml
- **instagram-automation**: 메인 애플리케이션 컨테이너
  - Host 네트워크 모드 (ADB 연결용)
  - Privileged 모드 (USB 디바이스 접근)
  - 소스 코드 볼륨 마운트
  - .env 파일 자동 로드

- **postgres**: PostgreSQL 데이터베이스 (선택사항)
  - 프로덕션 환경용
  - 기본적으로 비활성화

### .dockerignore
- 불필요한 파일 제외하여 이미지 크기 최적화
- 빌드 속도 향상

## 🔧 유용한 명령어

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f instagram-automation
```

### ADB 확인

```bash
# 컨테이너 내부에서 ADB 확인
docker-compose exec instagram-automation adb devices

# ADB 서버 재시작
docker-compose exec instagram-automation adb kill-server
docker-compose exec instagram-automation adb start-server
```

### 개발 워크플로우

```bash
# 1. 코드 수정 (호스트에서)
# 2. 컨테이너에서 자동 반영 (볼륨 마운트)
# 3. 테스트 실행
docker-compose exec instagram-automation python3 tests/your_test.py
```

## 🐛 트러블슈팅

### ADB 디바이스가 보이지 않을 때

```bash
# 호스트에서 ADB 서버 중지
adb kill-server

# 컨테이너 재시작
docker-compose restart instagram-automation

# 컨테이너 내부에서 확인
docker-compose exec instagram-automation adb devices
```

### Permission 에러

```bash
# ADB 디바이스 권한 확인
docker-compose exec instagram-automation adb devices

# Privileged 모드 확인
docker-compose down
docker-compose up -d
```

### 이미지 재빌드

```bash
# 캐시 없이 완전히 재빌드
docker-compose build --no-cache

# 컨테이너 삭제 후 재시작
docker-compose down
docker-compose up -d
```

## 📊 Phase별 테스트 설명

### Phase 1: Infrastructure
- ADB 디바이스 연결 확인
- UIAutomator2 서비스 확인
- Instagram 앱 실행 테스트

### Phase 2: Navigation
- 탭 네비게이션 (홈/검색/프로필)
- 사용자 검색 및 프로필 이동

### Phase 3: Vision
- GPT-4 Vision 프로필 OCR
- 콘텐츠 적절성 검사

### Phase 4: Integration
- Navigation + Vision 통합 테스트
- 프로필 스크래핑 전체 워크플로우

## 🔐 환경 변수

`.env` 파일이 자동으로 로드됩니다:

```env
OPENAI_API_KEY=sk-...
DB_HOST=localhost
DB_PORT=5432
# ... etc
```

## 📝 주의사항

1. **USB 디바이스**: Docker Desktop (Mac)에서는 USB 디바이스 직접 연결이 제한적일 수 있습니다.
   - 해결책: `adb connect <device-ip>:<port>`로 네트워크 연결 사용

2. **네트워크 모드**: `network_mode: host`는 Linux에서만 완전히 작동합니다.
   - Mac: 대안 솔루션 필요할 수 있음

3. **볼륨 마운트**: 소스 코드가 볼륨으로 마운트되므로 호스트에서 수정 즉시 반영됩니다.

## 🎯 다음 단계

1. Docker 환경 확인: `docker-compose ps`
2. Phase 1 테스트: `./docker-test.sh 1`
3. 순차적으로 Phase 2-4 진행
4. 전체 테스트: `./docker-test.sh all`
