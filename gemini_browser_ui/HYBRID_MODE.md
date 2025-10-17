# 🚀 하이브리드 모드: DuckDuckGo + Computer Use

## 개요

GCP 배포 환경에서 Google 검색 시 reCAPTCHA 문제를 해결하기 위한 하이브리드 아키텍처입니다.

## 문제 상황

### ❌ 기존 방식 (Playwright로 Google 검색)

```
사용자: "구글에서 AI 검색"
    ↓
Playwright로 Google 접속
    ↓
❌ reCAPTCHA 차단!
    ↓
클라우드 IP 감지
봇 행동 패턴 감지
→ 검색 실패
```

**Google의 봇 감지 이유:**
- GCP/AWS 같은 클라우드 IP 주소
- Playwright WebDriver 흔적
- 행동 패턴 분석 (마우스, 타이핑)
- Browser Fingerprinting

---

## ✅ 해결 방안: DuckDuckGo + Computer Use

### 왜 DuckDuckGo인가?

| 특징 | Google | DuckDuckGo |
|------|--------|-----------|
| reCAPTCHA | ❌ 항상 나옴 | ✅ 전혀 없음 |
| 봇 감지 | ❌ 강력함 | ✅ 거의 없음 |
| Playwright 호환 | ❌ 차단됨 | ✅ 완벽 작동 |
| GCP 배포 | ❌ IP 차단 | ✅ 문제없음 |
| 비용 | ✅ 무료 | ✅ 무료 |
| 검색 품질 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 테스트 결과

```bash
$ python3 test_duckduckgo.py

✅ 테스트 1: "Anthropic Claude AI"
   - reCAPTCHA: 없음
   - 결과: 10개
   - 소요 시간: 3.4초

✅ 테스트 2: "Python tutorial"
   - reCAPTCHA: 없음
   - 결과: 10개
   - 소요 시간: 3.2초

✅ 테스트 3: "인공지능 최신 트렌드"
   - reCAPTCHA: 없음
   - 결과: 10개 (한국어 완벽 지원)
   - 소요 시간: 3.5초

성공률: 100% (3/3)
```

---

## 🏗️ 아키텍처

### 전체 플로우

```
사용자 요청: "네이버 블로그에서 AI 트렌드 검색"
    ↓
┌─────────────────────────────────────────────┐
│  1. 작업 유형 분석                          │
│     - 검색 필요: YES                        │
│     - 검색어: "AI 트렌드 site:blog.naver"  │
│     - 브라우저 필요: YES (결과 페이지 방문) │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  2. DuckDuckGo 검색 (Playwright)           │
│     ✅ reCAPTCHA 없음                      │
│     ✅ 10개 URL 수집                       │
└─────────────────────────────────────────────┘
    ↓
    URLs: [
      "https://blog.naver.com/post1",
      "https://blog.naver.com/post2",
      ...
    ]
    ↓
┌─────────────────────────────────────────────┐
│  3. Computer Use로 페이지 방문              │
│     - 첫 번째 URL로 이동                    │
│     - 스크린샷 분석                         │
│     - 클릭, 스크롤, 데이터 추출             │
└─────────────────────────────────────────────┘
    ↓
최종 결과 반환
```

### 코드 구조

```python
# computer_use_wrapper.py

class GeminiComputerUseAgent:

    def search_with_duckduckgo(self, query, num_results=10):
        """
        DuckDuckGo로 검색 (reCAPTCHA 없음)

        Returns:
            [
                {
                    'title': '...',
                    'url': '...',
                    'snippet': '...'
                },
                ...
            ]
        """
        # Playwright로 DuckDuckGo 검색
        # reCAPTCHA 걱정 없이 안전하게 검색

    def execute_hybrid_task(self, task, max_steps=30):
        """
        하이브리드 실행:
        1. 작업 분석 (검색 필요? 브라우저 필요?)
        2. 검색 → DuckDuckGo
        3. 브라우저 → Computer Use
        """

        analysis = self._analyze_task_type(task)

        if analysis['needs_search']:
            # DuckDuckGo로 검색
            results = self.search_with_duckduckgo(
                query=analysis['search_query']
            )

            if analysis['needs_browser']:
                # Computer Use로 페이지 방문
                self.navigate_to(results[0]['url'])
                return self.execute_task(task)
            else:
                # 검색 결과만 반환
                return {'search_results': results}

        else:
            # 검색 불필요 → 바로 Computer Use
            return self.execute_task(task)
```

---

## 📊 전략별 비교

### 작업 유형에 따른 전략

| 작업 예시 | 전략 | 사용 도구 | 비용 |
|----------|------|----------|------|
| "구글에서 AI 검색" | search_only | DuckDuckGo | $0 |
| "인스타그램 프로필 열기" | browser_only | Computer Use | $0 |
| "네이버 블로그 검색하고 첫 글 읽기" | hybrid | DuckDuckGo + Computer Use | $0 |

### 대안 방법과의 비교

| 방법 | reCAPTCHA | 비용/월 | GCP 안정성 | 추천도 |
|------|-----------|---------|-----------|--------|
| **DuckDuckGo + Playwright** | ✅ 없음 | $0 | ⭐⭐⭐⭐⭐ | 🥇 |
| SerpAPI | ✅ 없음 | $50 (5K 검색) | ⭐⭐⭐⭐⭐ | 🥈 |
| Google Custom Search API | ✅ 없음 | $5 (1K 검색) | ⭐⭐⭐⭐⭐ | 🥉 |
| Playwright + Google | ❌ 항상 | $0 | ⭐ | ❌ |

---

## 🚀 사용 방법

### 1. 자동 모드 (기본값)

```python
agent = GeminiComputerUseAgent()

# 하이브리드 실행 (자동으로 전략 선택)
result = agent.execute_hybrid_task("구글에서 Anthropic 검색")

# 결과:
# - 작업 분석 → search_only 전략
# - DuckDuckGo로 검색
# - 10개 결과 반환
```

### 2. 수동 검색

```python
agent = GeminiComputerUseAgent()

# DuckDuckGo 직접 사용
results = agent.search_with_duckduckgo("Python tutorial", num_results=5)

for r in results:
    print(f"{r['title']}")
    print(f"  → {r['url']}")
```

### 3. Flask 서버에서 사용

```python
# run.py에서 자동으로 하이브리드 모드 사용

@app.route('/api/execute', methods=['POST'])
def execute_task():
    prompt = request.json['prompt']

    # 하이브리드 실행 (DuckDuckGo + Computer Use)
    result = agent_instance.execute_hybrid_task(
        prompt,
        max_steps=50
    )

    return jsonify(result)
```

---

## 🧪 테스트

### 단일 테스트

```bash
# DuckDuckGo 검색 테스트
cd gemini_browser_ui
python3 test_duckduckgo.py
```

### 하이브리드 테스트

```bash
# 전체 하이브리드 모드 테스트
python3 test_hybrid.py
```

### 실제 시나리오 테스트

```python
from computer_use_wrapper import GeminiComputerUseAgent

agent = GeminiComputerUseAgent()

# 테스트 1: 검색 전용
result = agent.execute_hybrid_task("파이썬 튜토리얼 검색")
print(result['search_results'])

# 테스트 2: 하이브리드
result = agent.execute_hybrid_task(
    "네이버 블로그에서 AI 트렌드 검색하고 첫 번째 글 제목 가져오기"
)
print(result['response'])
```

---

## 📝 로그 예시

```
🎯 하이브리드 작업 실행: 구글에서 Anthropic 검색
🔍 작업 유형 분석 중: 구글에서 Anthropic 검색
📊 전략: search_only
   - 검색 필요: True
   - 브라우저 필요: False
🦆 DuckDuckGo 검색: Anthropic
DuckDuckGo 접속 중...
📊 검색 결과 10개 발견
✅ DuckDuckGo 검색 완료: 10개 결과
  1. Claude - Anthropic...
  2. Anthropic's Claude AI...
  3. What is Claude? Everything you need to know...
✅ 검색 완료: 10개 결과
```

---

## 🔧 설정

### 환경 변수

```bash
# .env 파일
GEMINI_API_KEY=your_api_key_here
HEADLESS=true  # GCP 배포용
```

### 검색 엔진 변경

향후 다른 검색 엔진 추가 가능:

```python
# computer_use_wrapper.py

# DuckDuckGo (기본값)
results = agent.search_with_duckduckgo(query)

# 향후 추가 가능:
# results = agent.search_with_bing(query)
# results = agent.search_with_yahoo(query)
```

---

## 🎯 GCP 배포 시 주의사항

### ✅ 작동하는 것

- DuckDuckGo 검색 (reCAPTCHA 없음)
- Playwright headless 모드
- Computer Use로 페이지 방문/조작

### ❌ 작동하지 않는 것

- Google 검색 (reCAPTCHA로 차단됨)
- Cloudflare 강력 보호 사이트

### 권장 설정

```dockerfile
# Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver

ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin/chromium
ENV HEADLESS=true

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN playwright install chromium

CMD ["python", "run.py"]
```

---

## 📚 참고 자료

- [DuckDuckGo](https://duckduckgo.com)
- [Playwright Documentation](https://playwright.dev/)
- [Gemini Computer Use API](https://ai.google.dev/gemini-api/docs/computer-use)
- [테스트 결과](test_duckduckgo.py)

---

## 🤝 기여

문제가 발생하거나 개선 사항이 있으면 이슈를 생성해주세요.

---

**Last Updated:** 2025-10-17
**Status:** ✅ Production Ready
