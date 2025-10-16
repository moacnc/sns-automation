# Google Cloud Run 배포 가이드

MOA Computer Use를 Google Cloud Run에 배포하는 방법입니다.

## 📋 사전 준비

### 1. 필수 도구 설치
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker Desktop](https://docs.docker.com/get-docker/)

### 2. GCP 프로젝트 설정
- 프로젝트 ID: `moa-robo`
- 리전: `asia-northeast3` (서울)

### 3. 환경 변수 준비
`.env` 파일에 다음 정보가 있어야 합니다:
```bash
GEMINI_API_KEY=your-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
FLASK_SECRET_KEY=your-secret-key
```

## 🚀 배포 방법

### 옵션 1: 자동 배포 스크립트 (권장)

```bash
cd gemini_browser_ui
./deploy.sh
```

**포함 기능**:
- ✅ GCP 프로젝트 설정
- ✅ 필요한 API 자동 활성화
- ✅ Docker 이미지 빌드 (Cloud Build)
- ✅ Cloud Run 배포
- ✅ 환경 변수 자동 설정
- ✅ 서비스 URL 자동 출력

**예상 소요 시간**: 3-5분

### 옵션 2: 빠른 배포 (가장 빠름)

```bash
cd gemini_browser_ui
./quick-deploy.sh
```

**특징**:
- ⚡ 가장 빠른 배포 (gcloud 자동 빌드)
- ⚠️ 환경 변수는 수동으로 설정 필요

**예상 소요 시간**: 2-3분

### 옵션 3: 수동 배포

#### Step 1: GCP 로그인
```bash
gcloud auth login
gcloud config set project moa-robo
```

#### Step 2: Docker 이미지 빌드
```bash
cd gemini_browser_ui

# Cloud Build로 빌드 (빠름)
gcloud builds submit --tag gcr.io/moa-robo/moa-computer-use

# 또는 로컬 빌드 (느림)
docker build -t gcr.io/moa-robo/moa-computer-use .
docker push gcr.io/moa-robo/moa-computer-use
```

#### Step 3: Cloud Run 배포
```bash
gcloud run deploy moa-computer-use \
  --image gcr.io/moa-robo/moa-computer-use \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=your-key,GOOGLE_CLIENT_ID=your-id
```

## ⚙️ 환경 변수 설정 (배포 후)

### Cloud Console에서 설정

1. [Cloud Run Console](https://console.cloud.google.com/run?project=moa-robo) 접속
2. `moa-computer-use` 서비스 클릭
3. **"새 버전 수정 및 배포"** 클릭
4. **"변수 및 보안 비밀"** 탭
5. 환경 변수 추가:

| 변수 이름 | 값 | 설명 |
|---------|-----|------|
| `GEMINI_API_KEY` | `AIzaSy...` | Gemini API 키 |
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-xxx` | OAuth Client Secret |
| `FLASK_SECRET_KEY` | `random-string` | Flask 세션 키 |
| `OAUTH_REDIRECT_URI` | `https://your-url/auth/google/callback` | OAuth 리다이렉트 URI |
| `PORT` | `8080` | 포트 (자동 설정됨) |
| `HEADLESS` | `true` | 헤드리스 모드 |

6. **"배포"** 클릭

### gcloud CLI로 설정

```bash
gcloud run services update moa-computer-use \
  --region asia-northeast3 \
  --update-env-vars \
    GEMINI_API_KEY=your-key,\
    GOOGLE_CLIENT_ID=your-id,\
    GOOGLE_CLIENT_SECRET=your-secret,\
    FLASK_SECRET_KEY=your-flask-secret,\
    OAUTH_REDIRECT_URI=https://your-url/auth/google/callback,\
    HEADLESS=true
```

## 🔧 Google OAuth 설정 업데이트

배포 후 서비스 URL을 받으면 Google Cloud Console에서 OAuth 설정을 업데이트해야 합니다.

### 1. 서비스 URL 확인
```bash
gcloud run services describe moa-computer-use \
  --region asia-northeast3 \
  --format 'value(status.url)'
```

예: `https://moa-computer-use-xxxxx-an.a.run.app`

### 2. Google Cloud Console에서 OAuth 업데이트

1. [Google Cloud Console - API 사용자 인증 정보](https://console.cloud.google.com/apis/credentials)
2. OAuth 2.0 클라이언트 ID 선택
3. **승인된 리디렉션 URI**에 추가:
   ```
   https://moa-computer-use-xxxxx-an.a.run.app/auth/google/callback
   ```
4. 저장

## 📊 배포 확인

### 서비스 상태 확인
```bash
gcloud run services describe moa-computer-use \
  --region asia-northeast3 \
  --format='table(status.url,status.conditions[0].status)'
```

### 로그 확인
```bash
gcloud run logs read moa-computer-use \
  --region asia-northeast3 \
  --limit 50
```

### Health Check
```bash
SERVICE_URL=$(gcloud run services describe moa-computer-use \
  --region asia-northeast3 \
  --format 'value(status.url)')

curl ${SERVICE_URL}/api/health
```

## 🔄 업데이트 배포

코드 수정 후 재배포:

```bash
cd gemini_browser_ui
./deploy.sh
```

또는:

```bash
gcloud builds submit --tag gcr.io/moa-robo/moa-computer-use
gcloud run deploy moa-computer-use \
  --image gcr.io/moa-robo/moa-computer-use \
  --region asia-northeast3
```

## 💰 비용 최적화

### Cloud Run 설정
- **Min instances**: 0 (사용하지 않을 때 비용 없음)
- **Max instances**: 10 (동시 사용자 제한)
- **CPU**: 2 vCPU
- **Memory**: 2 GiB
- **Timeout**: 300초

### 예상 비용 (월)
- **무료 할당량**: 
  - 요청 2백만 건
  - CPU 시간 180,000 vCPU-초
  - 메모리 360,000 GiB-초
  
- **유료 사용 시**: 
  - 요청당 $0.40 / 백만 건
  - CPU 시간 $0.00002400 / vCPU-초
  - 메모리 $0.00000250 / GiB-초

**대부분의 사용량은 무료 할당량 내에서 해결됩니다!**

## 🐛 문제 해결

### 배포 실패
```bash
# 로그 확인
gcloud run logs read moa-computer-use --region asia-northeast3 --limit 100

# 서비스 재배포
gcloud run services delete moa-computer-use --region asia-northeast3
./deploy.sh
```

### 환경 변수 확인
```bash
gcloud run services describe moa-computer-use \
  --region asia-northeast3 \
  --format='yaml(spec.template.spec.containers[0].env)'
```

### Playwright 오류
Dockerfile에 Playwright 브라우저가 포함되어 있는지 확인:
```dockerfile
RUN playwright install chromium
RUN playwright install-deps chromium
```

## 📚 참고 자료

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Container Registry](https://cloud.google.com/container-registry/docs)

## 🎉 완료!

배포가 완료되면 다음을 확인하세요:
1. ✅ 서비스 URL 접속 가능
2. ✅ Google 로그인 작동
3. ✅ Gemini API 연결 확인
4. ✅ 브라우저 자동화 테스트

**서비스 URL**: https://console.cloud.google.com/run?project=moa-robo
