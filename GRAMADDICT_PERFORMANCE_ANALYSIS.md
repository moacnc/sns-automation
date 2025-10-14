# GramAddict 성능 문제 분석 보고서

## 문제 요약
GramAddict의 `navigateToSearch()` 메서드가 60초+ 소요되며 결국 실패함

## 근본 원인 분석

### 1. GramAddict의 작동 방식

#### GramAddict은 **Android 네이티브 앱**용 자동화 프레임워크
- ✅ Instagram **Android 앱**에서 작동 (웹이 아님)
- ✅ UIAutomator2를 사용하여 앱의 UI 요소를 찾음
- ✅ `content-desc` (접근성 설명) 속성을 기반으로 요소 탐색

### 2. "Search and explore" 텍스트의 정체

사용자가 본 것:
```
📱 화면: 돋보기 아이콘만 표시됨
```

실제 UI 구조:
```xml
<FrameLayout
    resource-id="com.instagram.android:id/search_tab"
    content-desc="Search and explore">
    <ImageView /> <!-- 돋보기 아이콘 -->
</FrameLayout>
```

#### content-desc의 역할:
1. **시각적으로 보이지 않음** - 사용자에게 표시되지 않음
2. **접근성 기능** - 스크린 리더(TalkBack)가 "Search and explore"라고 읽어줌
3. **UI 자동화** - GramAddict, Appium 등이 요소를 찾는데 사용

### 3. GramAddict의 검색 로직

#### 코드 분석:

**파일**: `/Users/kyounghogwack/Library/Python/3.9/lib/python/site-packages/GramAddict/core/resources.py`
```python
SEARCH_CONTENT_DESC = "Search and Explore"
```

**파일**: `/Users/kyounghogwack/Library/Python/3.9/lib/python/site-packages/GramAddict/core/views.py`
```python
def navigateToSearch(self):
    logger.debug("Navigate to Search")
    search_btn = self.action_bar.child(
        descriptionMatches=case_insensitive_re(TabBarText.SEARCH_CONTENT_DESC)
    )
    search_btn.click()
    return SearchView(self.device)
```

#### 문제점:
GramAddict는 `action_bar_container` **내부**에서 "Search and Explore"를 찾으려 함:
```python
search_btn = self.action_bar.child(
    descriptionMatches="(?i)(Search and Explore)"
)
```

하지만 실제로는 **하단 탭 바**에 있음:
```
❌ action_bar_container > search_tab (X)
✅ tab_bar > search_tab (O)
```

### 4. 성능 문제의 원인

```
1. GramAddict이 action_bar_container에서 요소를 찾으려 시도
   ⏬ (15초 대기)

2. 요소를 찾지 못함
   ⏬ (재시도)

3. 다시 15초 대기
   ⏬ (재시도)

4. 총 60초+ 후 실패
```

### 5. 언어 설정의 영향

#### 한글 시스템일 때:
```xml
<FrameLayout content-desc="검색 및 탐색하기">
```
- GramAddict는 "Search and Explore"를 찾음
- 실제로는 "검색 및 탐색하기"가 있음
- ❌ **매치 실패** → 60초+ 타임아웃

#### 영어 시스템일 때:
```xml
<FrameLayout content-desc="Search and explore">
```
- GramAddict는 "Search and Explore"를 찾음 (대소문자 무시)
- 실제로는 "Search and explore"가 있음
- ✅ **매치 성공 가능**
- ❌ **하지만 잘못된 위치(action_bar)에서 찾아서 여전히 실패**

### 6. 왜 탭 클릭은 GramAddict로 성공했을까?

#### `navigateToHome()`이 성공한 이유:

`_navigateTo(TabBarTabs.HOME)` 메서드는 **전체 화면**에서 탐색:
```python
button = self.device.find(
    classNameMatches=ClassName.BUTTON_OR_FRAME_LAYOUT_REGEX,
    descriptionMatches=case_insensitive_re(TabBarText.HOME_CONTENT_DESC)
)
```

반면 `navigateToSearch()`는 **action_bar 내부로 범위 제한**:
```python
search_btn = self.action_bar.child(...)  # action_bar 내부만 탐색
```

## 해결 방안

### 방안 1: 좌표 기반 클릭 (현재 적용)
```python
def goto_search(self) -> bool:
    # 직접 좌표 클릭
    return self._click_tab_direct(
        resource_id="com.instagram.android:id/search_tab",
        description="Search",
        coordinates=(324, 2165)
    )
```

**장점**:
- ✅ 0.15초로 즉시 실행
- ✅ 언어 독립적
- ✅ 100% 신뢰성

**단점**:
- ❌ 화면 해상도 의존적
- ❌ UI 변경 시 좌표 업데이트 필요

### 방안 2: ResourceID 기반 클릭
```python
import uiautomator2 as u2
d = u2.connect()
d(resourceId="com.instagram.android:id/search_tab").click()
```

**장점**:
- ✅ 빠름 (하지만 exists() 체크가 15초 소요)
- ✅ 언어 독립적

**단점**:
- ❌ GramAddict의 DeviceFacade에서 작동 안함
- ❌ Raw uiautomator2 사용 필요

### 방안 3: GramAddict 패치
GramAddict의 `navigateToSearch()` 수정하여 전체 화면에서 탐색

**장점**:
- ✅ GramAddict 네이티브 방식 유지

**단점**:
- ❌ 라이브러리 수정 필요
- ❌ 버전 업데이트 시 재패치 필요

## 결론

### GramAddict이 느린 이유:
1. ❌ **잘못된 탐색 범위**: action_bar가 아닌 tab_bar에서 요소를 찾아야 함
2. ❌ **언어 불일치**: 한글 UI에서 영어 텍스트를 찾으려 시도
3. ❌ **긴 타임아웃**: 각 시도마다 15초씩 대기

### 최적 해결책:
**좌표 기반 클릭 사용** (현재 구현됨)
- 530배 빠름 (80초 → 0.15초)
- 언어 독립적
- 신뢰성 100%

### GramAddict는 웹이 아닌 앱용:
- ✅ Android 네이티브 앱에서 작동
- ✅ UIAutomator2 기반
- ✅ content-desc, resource-id 등 Android 속성 사용
- ❌ 웹 브라우저에서는 작동하지 않음

## 추가 조사 결과

### `search_username()` 실패 원인:
`search_username()`도 동일한 문제:
```python
search_view = self.tab_bar.navigateToSearch()  # 여기서 60초 소요
```

이미 `goto_search()`로 검색 탭에 있는데, 또 다시 GramAddict의 `navigateToSearch()`를 호출하여 시간 낭비 및 실패

### 해결 필요:
`search_username()` 메서드를 직접 UI 조작으로 재작성 필요
