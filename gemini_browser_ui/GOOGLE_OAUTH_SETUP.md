# Google OAuth 2.0 Setup Guide

이 가이드는 MOA Computer Use에 Google 로그인 기능을 추가하기 위한 OAuth 2.0 자격 증명 설정 방법입니다.

## 🔧 Step 1: Google Cloud Console 설정

### 1. Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 선택 또는 새 프로젝트 생성

### 2. OAuth 동의 화면 구성
1. 왼쪽 메뉴에서 **"API 및 서비스" → "OAuth 동의 화면"** 선택
2. **User Type** 선택:
   - **외부(External)**: 누구나 로그인 가능 (권장)
   - **내부(Internal)**: Google Workspace 조직 내부만
3. **앱 정보 입력**:
   - 앱 이름: `MOA Computer Use`
   - 사용자 지원 이메일: 본인 이메일
   - 앱 로고: (선택사항)
   - 앱 도메인:
     - 홈페이지: `http://localhost:8080`
     - 개인정보처리방침: (선택사항)
     - 서비스 약관: (선택사항)
   - 승인된 도메인: (비워둠)
   - 개발자 연락처: 본인 이메일
4. **범위(Scopes) 추가**:
   - "범위 추가 또는 삭제" 클릭
   - 다음 범위 선택:
     - `userinfo.email` - 이메일 주소 확인
     - `userinfo.profile` - 프로필 정보 확인
     - `openid` - OpenID 인증
5. **테스트 사용자 추가** (외부 선택 시):
   - 본인 Gmail 계정 추가
   - 테스트 모드에서는 이 계정들만 로그인 가능
6. **저장 및 계속**

### 3. OAuth 2.0 클라이언트 ID 생성
1. 왼쪽 메뉴에서 **"API 및 서비스" → "사용자 인증 정보"** 선택
2. 상단의 **"+ 사용자 인증 정보 만들기"** 클릭
3. **"OAuth 클라이언트 ID"** 선택
4. **애플리케이션 유형**: `웹 애플리케이션`
5. **이름**: `MOA Computer Use Web Client`
6. **승인된 자바스크립트 원본**:
   ```
   http://localhost:8080
   ```
7. **승인된 리디렉션 URI**:
   ```
   http://localhost:8080/auth/google/callback
   ```
8. **만들기** 클릭
9. **클라이언트 ID**와 **클라이언트 보안 비밀번호** 복사 (나중에 사용)

## 🔑 Step 2: 환경 변수 설정

`.env` 파일에 다음 내용 추가:

```bash
# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Flask Session Secret (랜덤 문자열 생성)
FLASK_SECRET_KEY=your-super-secret-random-string-here

# OAuth Redirect URI
OAUTH_REDIRECT_URI=http://localhost:8080/auth/google/callback
```

### Flask Secret Key 생성 방법:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## ✅ Step 3: 테스트

1. 서버 재시작:
   ```bash
   cd gemini_browser_ui
   python3 run.py
   ```

2. 브라우저에서 `http://localhost:8080` 접속

3. "Google로 로그인" 버튼 클릭

4. Google 계정으로 로그인

5. 권한 승인

6. 로그인 성공!

## 🚨 주의사항

### 개발 환경 (localhost)
- OAuth 동의 화면이 "테스트" 모드인 경우, 테스트 사용자로 추가된 계정만 로그인 가능
- 프로덕션으로 배포 시 "게시" 상태로 변경 필요

### 프로덕션 배포 시
1. 실제 도메인으로 변경:
   - 승인된 자바스크립트 원본: `https://yourdomain.com`
   - 승인된 리디렉션 URI: `https://yourdomain.com/auth/google/callback`

2. `.env` 파일 업데이트:
   ```bash
   OAUTH_REDIRECT_URI=https://yourdomain.com/auth/google/callback
   ```

3. OAuth 동의 화면 "게시" 상태로 변경

## 📚 참고 자료

- [Google OAuth 2.0 문서](https://developers.google.com/identity/protocols/oauth2)
- [Authlib Flask 문서](https://docs.authlib.org/en/latest/client/flask.html)

## 🐛 문제 해결

### "리디렉션 URI 불일치" 오류
- Google Cloud Console의 승인된 리디렉션 URI와 `.env`의 `OAUTH_REDIRECT_URI`가 정확히 일치하는지 확인
- 끝에 슬래시(`/`) 여부 확인

### "앱이 확인되지 않음" 경고
- 테스트 모드에서는 정상
- "고급" → "MOA Computer Use(으)로 이동(안전하지 않음)" 클릭하여 계속 진행

### 테스트 사용자만 로그인 가능
- OAuth 동의 화면에서 테스트 사용자 추가
- 또는 앱을 "게시" 상태로 변경 (검토 필요)
