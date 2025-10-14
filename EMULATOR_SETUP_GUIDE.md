# Android 에뮬레이터 설정 가이드

Instagram 자동화를 위한 Android 에뮬레이터 설정 방법입니다.

## 📊 에뮬레이터 비교

### 1. **Android Studio Emulator** (⭐ 추천 - 개발용)

**장점:**
- Google 공식 에뮬레이터
- Android Studio와 완벽한 통합
- ADB 및 UIAutomator2 완벽 지원
- Google Play Services 내장
- 다양한 Android 버전 지원
- 무료

**단점:**
- RAM 사용량이 많음 (인스턴스당 2.5GB)
- 초기 설정이 복잡함

**적합한 경우:**
- 개발 및 테스트 환경
- 다양한 Android 버전 테스트 필요
- 장기적인 프로젝트

---

### 2. **Genymotion** (⭐ 추천 - 프로페셔널)

**장점:**
- 매우 빠른 성능 (OpenGL 가속)
- ADB over TCP 기본 지원 (CI/CD에 최적)
- 다양한 디바이스 프로필
- GPS, 배터리, 네트워크 시뮬레이션
- Android 4.1 ~ 12 지원

**단점:**
- 무료 버전은 기능 제한적
- 상용 라이선스 필요 (프로페셔널 기능)

**적합한 경우:**
- 프로페셔널 QA/테스트
- CI/CD 파이프라인
- 대규모 자동화 프로젝트

---

### 3. **NoxPlayer** (게이밍 + 자동화)

**장점:**
- 5개의 Android 커널 지원 (4.4, 5.1, 7.1, 9, 12)
- 멀티 인스턴스 관리
- 스크립트 레코더 (JavaScript)
- 무료

**단점:**
- 2021년 보안 사고 이력
- 런처 광고 존재
- 일부 버전에 멀웨어 포함 이력

**적합한 경우:**
- 여러 인스턴스 동시 실행
- 버전별 버그 테스트
- 게임 자동화

---

## 🚀 권장: Android Studio Emulator 설정 (macOS)

Instagram 자동화 프로젝트에 **Android Studio Emulator**를 추천합니다.

### 1. Android Studio 설치

#### Homebrew로 설치 (권장)
```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Android Studio 설치
brew install --cask android-studio
```

#### 수동 설치
1. [Android Studio 다운로드](https://developer.android.com/studio)
2. DMG 파일 실행 후 Applications 폴더로 드래그

---

### 2. Android SDK 및 Platform Tools 설정

Android Studio 실행 후:

1. **SDK Manager 열기**
   - `Android Studio > Preferences > Appearance & Behavior > System Settings > Android SDK`

2. **필수 SDK 설치**
   - SDK Platforms 탭:
     - ✅ Android 13.0 (Tiramisu) - API Level 33
     - ✅ Android 9.0 (Pie) - API Level 28 (호환성)

   - SDK Tools 탭:
     - ✅ Android SDK Build-Tools
     - ✅ Android SDK Platform-Tools
     - ✅ Android Emulator
     - ✅ Intel x86 Emulator Accelerator (HAXM installer) - Intel Mac
     - ✅ Google Play services

3. **환경 변수 설정**

```bash
# ~/.zshrc 또는 ~/.bash_profile 에 추가
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin

# 적용
source ~/.zshrc  # 또는 source ~/.bash_profile
```

4. **확인**
```bash
adb version
emulator -version
```

---

### 3. AVD (Android Virtual Device) 생성

1. **AVD Manager 열기**
   - `Tools > AVD Manager` 또는 상단 툴바 아이콘

2. **Create Virtual Device 클릭**

3. **디바이스 선택**
   - 카테고리: **Phone**
   - 권장: **Pixel 5** (1080 x 2340, 440 dpi)
   - **Next** 클릭

4. **시스템 이미지 선택**
   - **Recommended** 탭
   - **Tiramisu** (API Level 33) 선택
   - Release Name: **S** (Google APIs)
   - **Download** 클릭 후 설치
   - **Next** 클릭

5. **AVD 설정**
   ```
   AVD Name: Instagram_Automation
   Startup orientation: Portrait

   Advanced Settings:
   - RAM: 3072 MB (3GB)
   - VM heap: 256 MB
   - Internal Storage: 2048 MB
   - SD card: 512 MB

   Emulated Performance:
   - Graphics: Hardware - GLES 2.0
   ```

6. **Finish** 클릭

---

### 4. 에뮬레이터 실행

#### GUI로 실행
```bash
# AVD Manager에서 ▶️ 버튼 클릭
```

#### 커맨드라인으로 실행
```bash
# AVD 목록 확인
emulator -list-avds

# 에뮬레이터 실행
emulator -avd Instagram_Automation
```

#### 백그라운드 실행 (헤드리스)
```bash
emulator -avd Instagram_Automation -no-window -no-audio &
```

---

### 5. ADB 연결 확인

```bash
# 디바이스 확인
adb devices

# 출력 예시:
# List of devices attached
# emulator-5554  device
```

---

### 6. Instagram APK 설치

#### 방법 1: APKMirror에서 다운로드 (권장)

1. **APKMirror 접속**
   - https://www.apkmirror.com/apk/instagram/instagram-instagram/instagram-instagram-260-0-0-23-115-release/

2. **적절한 Variant 선택**
   - Architecture: **arm64-v8a**
   - DPI: **360-480dpi** (또는 nodpi)
   - Min Android: **5.0+**

3. **APK 다운로드**

4. **설치**
```bash
# APK 파일 설치
adb install ~/Downloads/Instagram_260.0.0.23.115.apk

# 기존 앱이 있다면 언인스톨 후 설치
adb uninstall com.instagram.android
adb install ~/Downloads/Instagram_260.0.0.23.115.apk
```

#### 방법 2: Google Play Store 사용

```bash
# 에뮬레이터에서 Play Store 앱 실행
# Instagram 검색 후 설치
# (최신 버전이 설치됨 - 호환성 문제 가능)
```

---

### 7. UIAutomator2 초기화

```bash
# UIAutomator2 서비스 설치
python3 -m uiautomator2 init

# 확인
adb shell pm list packages | grep uiautomator
# com.github.uiautomator
# com.github.uiautomator.test
```

---

### 8. 프로젝트 테스트 실행

```bash
cd "/Users/kyounghogwack/MOAcnc/Dev/PantaRheiX/AI SNS flow"

# Phase 1: 인프라 테스트
python3 tests/phase1_infrastructure/test_device_connection.py
python3 tests/phase1_infrastructure/test_instagram_launch.py

# Phase 2: 네비게이션 테스트
python3 tests/phase2_navigation/test_tab_navigation.py
python3 tests/phase2_navigation/test_search_user.py

# Phase 3: Vision 테스트
python3 tests/phase3_vision/test_profile_ocr.py
python3 tests/phase3_vision/test_content_filter.py

# Phase 4: 통합 테스트
python3 tests/phase4_integration/test_profile_scraping.py
```

---

## 🛠️ 트러블슈팅

### 1. 에뮬레이터가 느린 경우

```bash
# RAM 증가
# AVD Manager > Edit > Advanced Settings > RAM: 4096 MB

# CPU 코어 증가
emulator -avd Instagram_Automation -cores 4
```

### 2. ADB 연결 안 되는 경우

```bash
# ADB 서버 재시작
adb kill-server
adb start-server
adb devices
```

### 3. Instagram 로그인 안 되는 경우

- 에뮬레이터 GPS 활성화
- Google Play Services 로그인
- 시간/시간대 설정 확인

### 4. UIAutomator2 서비스 오류

```bash
# 재설치
python3 -m uiautomator2 init --reinstall

# ATX Agent 재시작
adb shell am force-stop com.github.uiautomator
python3 -m uiautomator2 init
```

---

## 📊 에뮬레이터 vs 실제 디바이스

| 항목 | 에뮬레이터 | 실제 디바이스 |
|------|------------|--------------|
| **비용** | 무료 | 디바이스 구매 필요 |
| **속도** | 느림 (리소스 의존) | 빠름 |
| **안정성** | 중간 | 높음 |
| **멀티 인스턴스** | 쉬움 | 어려움 (여러 디바이스 필요) |
| **APK 설치** | 쉬움 | 쉬움 |
| **Instagram 호환성** | 중간 (버전 의존) | 높음 |
| **CI/CD 통합** | 쉬움 | 어려움 |
| **디버깅** | 쉬움 | 중간 |

---

## 🎯 권장 워크플로우

### 개발 단계
1. **에뮬레이터 사용**
   - 빠른 테스트 및 디버깅
   - Instagram 260.0.0.23.115 설치
   - UIAutomator2 연동 테스트

### 프로덕션 단계
2. **실제 디바이스 사용**
   - 최종 검증
   - 장시간 실행 테스트
   - 안정성 확인

---

## 📝 다음 단계

1. ✅ Android Studio 설치
2. ✅ AVD 생성
3. ✅ Instagram 260.0.0.23.115 설치
4. ✅ UIAutomator2 초기화
5. ✅ Phase 1-4 테스트 실행
6. ✅ 결과 확인 및 리포트

---

## 🔗 참고 링크

- [Android Studio 다운로드](https://developer.android.com/studio)
- [APKMirror - Instagram](https://www.apkmirror.com/apk/instagram/)
- [GramAddict 문서](https://docs.gramaddict.org/)
- [UIAutomator2 문서](https://github.com/openatx/uiautomator2)
- [Genymotion](https://www.genymotion.com/)

---

## 💡 팁

- **Instagram 버전 고정**: 자동 업데이트 비활성화
- **스냅샷 활용**: 깨끗한 상태를 스냅샷으로 저장
- **멀티 인스턴스**: 여러 계정 테스트 시 AVD 복사 사용
- **리소스 관리**: 사용하지 않는 에뮬레이터는 종료

---

## ⚠️ 주의사항

1. **Instagram 정책 준수**: 자동화 도구 사용 시 계정 밴 가능
2. **Rate Limiting**: 과도한 요청 방지
3. **프라이버시**: 테스트 계정 사용 권장
4. **보안**: APK 다운로드 시 신뢰할 수 있는 소스만 사용
