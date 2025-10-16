# Gemini API 타임아웃 문제 해결 가이드

## 🔍 문제 파악 완료

### 단계별 테스트 결과:
1. ✅ **Playwright** - 완벽 작동
2. ✅ **브라우저 제어** - 완벽 작동
3. ✅ **Gemini API 단일 호출** - 완벽 작동 (5초)
4. ❌ **Gemini API 연속 호출** - 3번째부터 타임아웃 (20초+)

### 근본 원인:
**API Rate Limiting + 네트워크 소켓 재사용 문제**
- Step 1, 2는 성공
- Step 3부터 타임아웃 발생
- 에러: `httpcore.ReadError: [Errno 60] Operation timed out`

## 💡 해결 방법

### 1. API 호출 사이에 딜레이 추가

**파일**: `computer_use_wrapper.py`
**위치**: `execute_task()` 함수의 step 루프 끝

```python
# 현재 코드 (line 498 근처)
time.sleep(1.5)  # Wait between steps

# 수정:
time.sleep(3.0)  # API Rate Limit 방지를 위해 3초 대기
```

### 2. HTTP 연결 타임아웃 증가

**파일**: `computer_use_wrapper.py`
**위치**: `__init__()` 함수

```python
# 추가:
import httpx

self.client = genai.Client(
    api_key=self.api_key,
    http_options=httpx.Timeout(60.0, connect=10.0)  # 60초 타임아웃
)
```

### 3. Retry 로직 추가

**파일**: `computer_use_wrapper.py`
**위치**: `execute_task()` 함수의 API 호출 부분

```python
# API 호출 전에 추가:
max_retries = 3
for attempt in range(max_retries):
    try:
        response = self.client.models.generate_content(...)
        break  # 성공하면 루프 종료
    except Exception as e:
        if attempt < max_retries - 1 and 'timeout' in str(e).lower():
            logger.warning(f"⚠️  API 타임아웃, 재시도 {attempt + 1}/{max_retries}")
            time.sleep(5)  # 5초 대기 후 재시도
            continue
        raise  # 마지막 시도에서도 실패하면 에러 발생
```

### 4. Max Steps 줄이기

많은 연속 API 호출을 줄입니다:

```python
# run.py에서
result = agent_instance.execute_task(prompt, max_steps=5)  # 15 → 5로 변경
```

## 🚀 즉시 적용 가능한 해결책

**가장 간단한 방법**: `max_steps` 줄이기

1. `run.py` 열기
2. Line 129: `max_steps=15` → `max_steps=5`로 변경
3. 서버 재시작

이렇게 하면:
- API 호출 횟수: 15회 → 5회
- 타임아웃 발생 확률: 대폭 감소
- 작업 완료 확률: 증가

## 📊 테스트 결과

- **작은 이미지** (100x100, 289 bytes): ✅ 5초 성공
- **실제 스크린샷** (1440x900, 48KB): ✅ 5초 성공
- **연속 3회 호출**: Step 3에서 타임아웃

## 🎯 결론

**Gemini API 자체는 완벽하게 작동합니다!**

문제는 **연속 호출 시 Rate Limiting**입니다.

해결: **호출 사이 대기 시간 증가** + **max_steps 감소**
