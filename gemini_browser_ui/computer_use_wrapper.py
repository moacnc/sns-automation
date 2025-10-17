#!/usr/bin/env python3
"""
Gemini Computer Use Wrapper

Provides a simplified interface to Google's Gemini Computer Use API
for browser automation tasks with proper function call execution.
"""

import os
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright, Browser, Page

# Ensure Path is imported for storage_state check


class GeminiComputerUseAgent:
    """
    Gemini Computer Use Agent for browser automation

    Uses Google's Gemini 2.5 model with Computer Use capabilities
    to control web browsers and interact with websites using AI.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Computer Use Agent

        Args:
            api_key: Google AI API key (or uses GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Model configuration
        self.model_name = "gemini-2.5-computer-use-preview-10-2025"

        # Playwright browser and page
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.user_data_dir = None  # Track temp directory for cleanup

        # Session state
        self.session_history: List[Dict[str, Any]] = []

        # Stop flag for manual cancellation
        self.should_stop = False

        # Progress callback for real-time updates
        self.progress_callback = None

        logger.info("✓ Gemini Computer Use Agent initialized")

    def start_browser(self, headless: bool = True) -> None:
        """
        Start Playwright browser with persistent context to avoid CAPTCHA

        Args:
            headless: Run browser in headless mode (default True for stability)
        """
        try:
            logger.info(f"Starting browser (headless={headless})...")
            self.playwright = sync_playwright().start()

            # Use unique temporary directory for each session to avoid cache pollution
            # This prevents bot detection from accumulated browsing history
            import tempfile
            import uuid
            session_id = str(uuid.uuid4())[:8]  # Short unique ID
            self.user_data_dir = Path(tempfile.mkdtemp(prefix=f"playwright_{session_id}_"))
            logger.info(f"📁 User data directory (unique session): {self.user_data_dir}")

            # Launch persistent context (better for avoiding CAPTCHA)
            try:
                # Try Chrome first (more stable)
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(self.user_data_dir),
                    channel='chrome',
                    headless=headless,
                    viewport={'width': 1440, 'height': 900},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-setuid-sandbox',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu',
                        '--hide-scrollbars',
                        '--mute-audio',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                logger.info("✓ Using Chrome with persistent context")
            except Exception as e:
                logger.warning(f"Chrome not available, using Chromium: {e}")
                # Fallback to Chromium
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(self.user_data_dir),
                    headless=headless,
                    viewport={'width': 1440, 'height': 900},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-setuid-sandbox',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu',
                        '--hide-scrollbars',
                        '--mute-audio',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                logger.info("✓ Using Chromium with persistent context")

            # Get the first page (persistent context auto-creates one)
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.browser = None  # Not used with persistent context

            # Auto-dismiss JavaScript dialogs (alert, confirm, prompt)
            def handle_dialog(dialog):
                logger.info(f"🚨 Auto-dismissing dialog: {dialog.type} - {dialog.message}")
                dialog.dismiss()

            self.page.on("dialog", handle_dialog)
            logger.info("✓ Auto-dialog handler registered (alert/confirm/prompt will be auto-dismissed)")

            # Enable Chrome console logging for debugging
            def handle_console(msg):
                log_type = msg.type
                log_text = msg.text

                # Log to Python console with appropriate level
                if log_type == 'error':
                    logger.error(f"🖥️  [Browser Console ERROR] {log_text}")
                elif log_type == 'warning':
                    logger.warning(f"🖥️  [Browser Console WARN] {log_text}")
                elif log_type == 'info':
                    logger.info(f"🖥️  [Browser Console INFO] {log_text}")
                else:
                    logger.debug(f"🖥️  [Browser Console {log_type.upper()}] {log_text}")

            self.page.on("console", handle_console)
            logger.info("✓ Browser console logging enabled")

            # Inject anti-bot detection scripts
            self.page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Randomize plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Randomize languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ko-KR', 'ko', 'en-US', 'en']
                });

                // Mock Chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Canvas fingerprinting protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    if (type === 'image/png' && this.width === 280 && this.height === 60) {
                        // Randomize canvas fingerprint slightly
                        const context = this.getContext('2d');
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] = imageData.data[i] ^ Math.floor(Math.random() * 2);
                        }
                        context.putImageData(imageData, 0, 0);
                    }
                    return originalToDataURL.apply(this, arguments);
                };

                // WebGL fingerprinting protection
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {  // UNMASKED_VENDOR_WEBGL
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {  // UNMASKED_RENDERER_WEBGL
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };

                // Screen resolution consistency
                Object.defineProperty(screen, 'width', {
                    get: () => 1440
                });
                Object.defineProperty(screen, 'height', {
                    get: () => 900
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1440
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 877
                });

                // Battery API
                Object.defineProperty(navigator, 'getBattery', {
                    get: () => undefined
                });

                // Connection API spoofing
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 100,
                        downlink: 10,
                        saveData: false
                    })
                });

                // Timezone consistency
                Date.prototype.getTimezoneOffset = function() {
                    return -540; // KST (UTC+9)
                };
            """)
            logger.info("✓ Anti-bot detection scripts injected")

            # Navigate to DuckDuckGo homepage on startup (no reCAPTCHA!)
            try:
                logger.info("🦆 Navigating to DuckDuckGo homepage...")
                self.page.goto("https://duckduckgo.com", wait_until="domcontentloaded", timeout=10000)
                logger.info("✓ Started at DuckDuckGo homepage")
            except Exception as nav_error:
                logger.warning(f"⚠️  Could not navigate to DuckDuckGo: {nav_error}")
                # Continue anyway - not critical

            logger.info("✓ Browser and page initialized")
            logger.info("✓ Persistent context maintains cookies and sessions")
            logger.info("✓ Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    def close_browser(self) -> None:
        """Close browser and cleanup - ensure complete shutdown"""
        try:
            logger.info("🧹 Closing browser...")

            # Close in reverse order of creation
            if self.page:
                try:
                    self.page.close()
                    self.page = None
                    logger.debug("✓ Page closed")
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")

            if self.context:
                try:
                    self.context.close()
                    self.context = None
                    logger.debug("✓ Context closed")
                except Exception as e:
                    logger.warning(f"Error closing context: {e}")

            if self.browser:
                try:
                    self.browser.close()
                    self.browser = None
                    logger.debug("✓ Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")

            if self.playwright:
                try:
                    self.playwright.stop()
                    self.playwright = None
                    logger.debug("✓ Playwright stopped")
                except Exception as e:
                    logger.warning(f"Error stopping playwright: {e}")

            # Clean up temporary user data directory
            if self.user_data_dir and self.user_data_dir.exists():
                try:
                    import shutil
                    import time
                    time.sleep(1.0)  # Brief delay to ensure files are released
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                    logger.info(f"🗑️  Deleted temporary profile: {self.user_data_dir}")
                    self.user_data_dir = None
                except Exception as e:
                    logger.warning(f"⚠️  Could not delete temp directory: {e}")

            logger.info("✓ Browser closed and cleaned up")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    def take_screenshot(self, save_path: Optional[str] = None) -> str:
        """
        Take screenshot of current page

        Args:
            save_path: Path to save screenshot (auto-generated if None)

        Returns:
            Path to saved screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        if not save_path:
            timestamp = int(time.time())
            save_path = f"/tmp/gemini_screenshot_{timestamp}.png"

        self.page.screenshot(path=save_path)
        logger.info(f"✓ Screenshot saved: {save_path}")
        return save_path

    def navigate_to(self, url: str) -> None:
        """
        Navigate to URL

        Args:
            url: URL to navigate to
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Navigating to: {url}")
        try:
            # Use domcontentloaded for faster navigation (YouTube is heavy)
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            logger.info(f"✓ Loaded: {url}")
        except Exception as e:
            logger.warning(f"⚠️  Navigation timeout: {e}")
            # Continue anyway - page might be partially loaded
            logger.info(f"⚠️  Continuing with partial load...")

    def _extract_final_answer(self, full_response: str) -> str:
        """
        Extract clean final answer from Gemini's verbose response

        Looks for patterns like:
        - "Final Answer: ..."
        - Last sentence/paragraph that contains actual answer
        - Removes intermediate thinking steps
        """
        import re

        # Pattern 1: Look for "Final Answer:" marker
        if "Final Answer:" in full_response:
            parts = full_response.split("Final Answer:")
            if len(parts) > 1:
                answer = parts[-1].strip()
                # Remove any trailing evaluation text
                answer = re.split(r'I have evaluated step \d+', answer)[0].strip()
                return answer

        # Pattern 2: Look for conclusion markers
        conclusion_markers = [
            "In conclusion",
            "Therefore",
            "The answer is",
            "The result is",
            "Based on",
            "According to"
        ]

        lines = full_response.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if not line:
                continue

            # Check if this line starts with a conclusion marker
            for marker in conclusion_markers:
                if line.startswith(marker):
                    # Get this line and maybe a few more
                    remaining_lines = lines[i:]
                    clean_answer = '\n'.join(remaining_lines).strip()
                    # Remove evaluation steps
                    clean_answer = re.split(r'I have evaluated step \d+', clean_answer)[0].strip()
                    return clean_answer

        # Pattern 3: Get last meaningful paragraph (skip "Round X:" lines and evaluation steps)
        paragraphs = []
        current_para = []

        for line in lines:
            line = line.strip()
            # Skip round markers and evaluation steps
            if line.startswith("Round ") or "I have evaluated step" in line:
                if current_para:
                    paragraphs.append('\n'.join(current_para))
                    current_para = []
                continue

            if line:
                current_para.append(line)
            elif current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []

        if current_para:
            paragraphs.append('\n'.join(current_para))

        # Return last meaningful paragraph
        if paragraphs:
            return paragraphs[-1]

        # Fallback: return original
        return full_response

    def _format_action(self, function_call) -> str:
        """Format function call into human-readable text"""
        func_name = function_call.name
        args = dict(function_call.args)

        if func_name == "navigate":
            return f"Navigated to {args.get('url', 'unknown URL')}"
        elif func_name == "click_at":
            return f"Clicked at position ({args.get('x')}, {args.get('y')})"
        elif func_name == "type_text_at":
            text = args.get('text', '')
            return f"Typed '{text}'"
        elif func_name == "scroll_document":
            direction = args.get('direction', 'down')
            return f"Scrolled {direction}"
        elif func_name == "search":
            return "Opened page search (Cmd+F)"
        elif func_name == "open_web_browser":
            return "Opened browser"
        elif func_name == "go_back":
            return "Went back"
        elif func_name == "go_forward":
            return "Went forward"
        elif func_name == "wait_5_seconds":
            return "Waited 5 seconds"
        else:
            return f"Executed {func_name}"

    def _build_prompt_for_round(self, round_num: int, task: str, max_steps: int, scroll_count: int = 0) -> str:
        """
        Build optimized prompt for each round with context-aware instructions

        Args:
            round_num: Current round number (0-indexed)
            task: The task description
            max_steps: Maximum allowed steps
            scroll_count: Number of scrolls performed so far

        Returns:
            Optimized prompt string
        """
        current_url = self.page.url if self.page else "unknown"

        # === ROUND 0: Full structured prompt ===
        if round_num == 0:
            return f"""당신은 브라우저 자동화 에이전트입니다. 최소한의 단계로 작업을 완료하고 검증 가능한 증거를 제공하세요.

## 작업
{task}

## 핵심 루프 (최대 {max_steps} 단계)
각 단계: 계획 (1줄) → 실행 (1개 액션) → 관찰 (간략히) → 종료 조건 확인

## 🦆 검색 엔진 사용 규칙 (매우 중요!)
**웹 검색이 필요한 경우:**
- ✅ 반드시 DuckDuckGo (duckduckgo.com)를 사용하세요
- ❌ Google은 절대 사용하지 마세요 (reCAPTCHA로 차단됨)
- 현재 브라우저는 이미 DuckDuckGo 홈페이지에 있습니다
- 검색창에 검색어를 입력하고 Enter를 누르세요

**검색이 필요한 예시:**
- "유명한 유튜버 찾기" → DuckDuckGo에서 검색
- "최신 뉴스 확인" → DuckDuckGo에서 검색
- 특정 사이트는 직접 접속 (예: youtube.com, instagram.com)

## 탐색 전략
1. **스크롤 전에 찾기**: 먼저 페이지 내 검색/목차/탭 사용
2. **일괄 스크롤**: 필요시 2-3회 연속 스크롤 (최대 12회)
3. **스마트 대기**: 네비게이션 후 네트워크 유휴 + 주요 요소 대기
4. **선택자 우선순위**: role/aria > test-id > 안정적인 CSS > XPath

## 상호작용 규칙
- 클릭 전에 요소를 화면에 스크롤
- 긴 페이지의 경우: 여러 번 연속 스크롤, 일찍 포기하지 말 것
- 페이지네이션: 작업에서 더 필요하지 않으면 최대 3페이지까지 스캔
- 로그인/폼/캡챠 우회 금지

## 출력 요구사항 (매우 중요!)
**모든 응답은 반드시 한국어로 작성하세요.**

**매 단계마다 이 순서를 반드시 따르세요:**
1. **먼저 한국어 텍스트로 설명**:
   - 화면에 보이는 것
   - 현재 상황 분석
   - 다음에 할 액션과 그 이유

2. **그 다음 function call로 액션 실행**

3. **액션 실행 후**: 다음 라운드에서 결과를 한국어로 설명

**텍스트 설명 예시:**
"현재 네이버 블로그 검색 결과 페이지가 보입니다. 하단에 더 많은 게시물이 있을 것 같아 스크롤을 내리겠습니다."
"링크를 클릭했는데 아직 페이지가 변경되지 않았습니다. 조금 더 기다려보겠습니다."
"화면에 알림창(alert)이 떠 있어서 스크롤이 작동하지 않는 것 같습니다."

**중요 - 팝업/알림 처리 (필수):**
- JavaScript alert/confirm/prompt는 자동으로 닫힙니다
- HTML modal/popup이 화면에 보이면:
  1. "팝업이 보입니다. 닫기 버튼을 클릭하겠습니다" 라고 한국어로 설명
  2. 닫기 버튼 (X, 닫기, 확인, Close 등)을 클릭하여 팝업 닫기
  3. 팝업을 닫은 후 원래 작업 계속
- 스크롤이 2-3회 연속 작동하지 않으면 화면에 팝업/overlay가 있는지 확인하고 닫기

## 📊 최종 답변 요구사항 (필수!)
**작업 완료 시 반드시 다음 형식으로 최종 답변을 제공하세요:**

```
최종 답변:

[작업 요약]
- 수행한 작업 간략 설명

[핵심 발견사항]
- 주요 발견 내용 (데이터, 통계, 관찰 등)

[분석 및 결론]
- 수집한 정보를 바탕으로 한 분석
- 최종 결론 및 인사이트
```

**예시:**
```
최종 답변:

[작업 요약]
유튜브에서 상위 3명의 뷰티 크리에이터를 조사하고 최근 영상의 댓글 반응을 분석했습니다.

[핵심 발견사항]
1. 올리브영 채널 - 구독자 200만, 최근 영상 조회수 평균 50만
2. 다솜 뷰티 - 구독자 180만, 최근 영상 조회수 평균 45만
3. 이사배 - 구독자 150만, 최근 영상 조회수 평균 40만

[분석 및 결론]
올리브영 채널이 가장 유명하며, 댓글 반응은 대체로 긍정적입니다.
특히 제품 리뷰 영상의 참여율이 높고, 시청자들의 구매 의도가 강하게 나타납니다.
```

## 시작
현재 URL: {current_url}
현재 페이지는 아래 스크린샷에 표시됩니다.

**첫 번째 응답 형식:**
1. 먼저 한국어로 화면 분석과 계획 설명
2. 그 다음 첫 번째 액션 실행"""

        # === ROUNDS 1-23: Lightweight continuation ===
        elif round_num < max_steps - 2:
            reminder = f"""작업 계속: {task}

**중요 - 응답 형식:**
1. 먼저 한국어로 이전 액션의 결과와 현재 화면 분석
2. 그 다음 다음 액션 계획 설명
3. 마지막으로 function call 실행

알림 (중요):
- 긴 페이지의 경우 2-3회 연속 스크롤 - 일찍 포기하지 말 것
- 확인: 최종 답변을 위한 충분한 증거가 있는가?
- 진행 상황: {round_num + 1}/{max_steps} 단계
"""

            # Add specific warnings based on context
            if scroll_count > 5:
                reminder += "\n⚠️ **경고**: 여러 번 스크롤했는데 진전이 없습니다!\n"
                reminder += "**즉시 다음 확인:**\n"
                reminder += "1. 화면에 팝업, 알림창, modal, overlay가 보이는지 확인\n"
                reminder += "2. 보이면 \"팝업이 보입니다. 닫기 버튼 클릭하겠습니다\"라고 설명 후 닫기 버튼 클릭\n"
                reminder += "3. 팝업이 없으면 다른 전략 시도 (페이지 내 검색/탭 전환)\n"

            if round_num > 10 and round_num % 5 == 0:
                reminder += f"\n⚠️  {round_num + 1} 단계 수행됨 - 답변할 충분한 정보가 있는지 고려하세요\n"

            reminder += f"\n현재 URL: {current_url}\n"
            reminder += "\n**응답 예시:**\n"
            reminder += "\"이전 스크롤로 페이지 하단에 도달했습니다. 다음 페이지 버튼을 클릭하겠습니다.\"\n"
            reminder += "\n완료되었으면 '최종 답변: ...' 제공"

            return reminder

        # === ROUNDS 24-25: Forced completion ===
        else:
            return f"""긴급: 최대 단계 도달 ({round_num + 1}/{max_steps})

작업: {task}
현재 URL: {current_url}

지금 수집한 정보로 최종 답변을 제공해야 합니다.

다음 형식으로 응답하세요:
최종 답변: <수집한 증거를 바탕으로 한 답변>

1-2개의 추가 액션이 필요하면 명확히 명시하되, 결론을 준비하세요."""

    def _execute_function_call(self, function_call) -> bool:
        """
        Execute a single Gemini Computer Use function call

        Supports ALL 14+ Computer Use API functions:
        - Browser: open_web_browser, navigate, go_back, go_forward, search
        - Mouse: click_at, hover_at, drag_and_drop
        - Keyboard: type_text_at, key_combination
        - Scroll: scroll_document, scroll_at
        - Utility: wait_5_seconds

        Args:
            function_call: Function call from Gemini response

        Returns:
            True if executed successfully
        """
        try:
            func_name = function_call.name
            args = dict(function_call.args)

            logger.info(f"🤖 Gemini Computer Use: {func_name}")
            logger.debug(f"   Arguments: {args}")

            # Get screen dimensions for coordinate conversion
            viewport = self.page.viewport_size
            width = viewport['width']
            height = viewport['height']

            # Convert normalized coordinates (0-999) to actual pixels
            def norm_x(val):
                return int((float(val) / 999.0) * width)

            def norm_y(val):
                return int((float(val) / 999.0) * height)

            # ============ BROWSER/NAVIGATION FUNCTIONS ============

            if func_name == "open_web_browser":
                logger.info(f"   ✓ Browser already open (no-op)")
                return True

            elif func_name == "navigate":
                url = args.get('url', '')
                logger.info(f"   → Navigating to: {url}")
                self.navigate_to(url)
                return True

            elif func_name == "go_back":
                logger.info(f"   ← Going back")
                self.page.go_back()
                time.sleep(1)
                return True

            elif func_name == "go_forward":
                logger.info(f"   → Going forward")
                self.page.go_forward()
                time.sleep(1)
                return True

            elif func_name == "search":
                logger.info(f"   🔍 Opening search (Command+F / Ctrl+F)")
                self.page.keyboard.press("Meta+F" if os.name == 'posix' else "Control+F")
                time.sleep(0.5)
                return True

            elif func_name == "wait_5_seconds":
                logger.info(f"   ⏳ Waiting 5 seconds...")
                time.sleep(5)
                return True

            # ============ MOUSE/INTERACTION FUNCTIONS ============

            elif func_name == "click_at":
                x = norm_x(args.get('x', 0))
                y = norm_y(args.get('y', 0))
                logger.info(f"   🖱️  Click at ({x}, {y}) px")
                self.page.mouse.click(x, y)
                time.sleep(0.8)
                return True

            elif func_name == "hover_at":
                x = norm_x(args.get('x', 0))
                y = norm_y(args.get('y', 0))
                logger.info(f"   👆 Hover at ({x}, {y}) px")
                self.page.mouse.move(x, y)
                time.sleep(0.5)
                return True

            elif func_name == "drag_and_drop":
                x = norm_x(args.get('x', 0))
                y = norm_y(args.get('y', 0))
                dest_x = norm_x(args.get('destination_x', 0))
                dest_y = norm_y(args.get('destination_y', 0))
                logger.info(f"   🫳 Drag from ({x}, {y}) to ({dest_x}, {dest_y}) px")
                self.page.mouse.move(x, y)
                self.page.mouse.down()
                time.sleep(0.3)
                self.page.mouse.move(dest_x, dest_y)
                self.page.mouse.up()
                time.sleep(0.5)
                return True

            # ============ KEYBOARD/TEXT FUNCTIONS ============

            elif func_name == "type_text_at":
                x = norm_x(args.get('x', 0))
                y = norm_y(args.get('y', 0))
                text = args.get('text', '')
                press_enter = args.get('press_enter', True)
                clear_before = args.get('clear_before_typing', True)

                logger.info(f"   ⌨️  Type '{text}' at ({x}, {y}) px")

                # Click to focus
                self.page.mouse.click(x, y)
                time.sleep(0.3)

                # Clear if requested
                if clear_before:
                    # Select all and delete
                    self.page.keyboard.press("Meta+A" if os.name == 'posix' else "Control+A")
                    time.sleep(0.1)
                    self.page.keyboard.press("Backspace")
                    time.sleep(0.1)

                # Type text
                self.page.keyboard.type(text, delay=50)  # 50ms delay between keys
                time.sleep(0.3)

                # Press enter if requested
                if press_enter:
                    logger.info(f"   ↵ Pressing Enter")
                    self.page.keyboard.press("Enter")
                    time.sleep(0.5)

                return True

            elif func_name == "key_combination":
                keys = args.get('keys', '')
                logger.info(f"   ⌨️  Key combination: {keys}")

                # Handle special keys
                if keys.lower() == 'enter':
                    self.page.keyboard.press("Enter")
                elif keys.lower() == 'escape':
                    self.page.keyboard.press("Escape")
                elif keys.lower() == 'tab':
                    self.page.keyboard.press("Tab")
                elif '+' in keys:
                    # Handle combinations like Control+C, Meta+V
                    self.page.keyboard.press(keys)
                else:
                    self.page.keyboard.press(keys)

                time.sleep(0.5)
                return True

            # ============ SCROLLING FUNCTIONS ============

            elif func_name == "scroll_document":
                direction = args.get('direction', 'down')
                logger.info(f"   📜 Scroll {direction}")

                # Increased from 500 to 1500 pixels (3x) for faster navigation through long pages
                scroll_amount = 1500  # pixels
                if direction == 'down':
                    self.page.mouse.wheel(0, scroll_amount)
                elif direction == 'up':
                    self.page.mouse.wheel(0, -scroll_amount)
                elif direction == 'right':
                    self.page.mouse.wheel(scroll_amount, 0)
                elif direction == 'left':
                    self.page.mouse.wheel(-scroll_amount, 0)

                time.sleep(0.3)  # Reduced from 0.5s for faster scrolling
                return True

            elif func_name == "scroll_at":
                x = norm_x(args.get('x', 0))
                y = norm_y(args.get('y', 0))
                direction = args.get('direction', 'down')
                magnitude = args.get('magnitude', 800)

                # Convert normalized magnitude (0-999) to pixels
                # Increased 2.5x for faster scrolling through long pages
                scroll_px = int((float(magnitude) / 999.0) * 2500)

                logger.info(f"   📜 Scroll {direction} at ({x}, {y}) px, magnitude {scroll_px}")

                # Move to position first
                self.page.mouse.move(x, y)
                time.sleep(0.2)

                # Scroll at that position
                if direction == 'down':
                    self.page.mouse.wheel(0, scroll_px)
                elif direction == 'up':
                    self.page.mouse.wheel(0, -scroll_px)
                elif direction == 'right':
                    self.page.mouse.wheel(scroll_px, 0)
                elif direction == 'left':
                    self.page.mouse.wheel(-scroll_px, 0)

                time.sleep(0.3)  # Reduced from 0.5s for faster scrolling
                return True

            # ============ UNKNOWN FUNCTION ============

            else:
                logger.warning(f"   ❌ Unknown Gemini Computer Use function: {func_name}")
                logger.warning(f"   Supported functions: open_web_browser, navigate, go_back, go_forward, search, wait_5_seconds, click_at, hover_at, drag_and_drop, type_text_at, key_combination, scroll_document, scroll_at")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Failed to execute {func_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def execute_hybrid_task(self, task: str, max_steps: int = 50) -> Dict[str, Any]:
        """
        Computer Use 중심 실행 (DuckDuckGo 검색 권장)

        핵심 전략:
        1. 모든 작업을 Computer Use (Gemini)에게 맡김
        2. Gemini가 필요하면 스스로 DuckDuckGo 검색 수행
        3. 시스템 프롬프트에 "검색은 DuckDuckGo 사용" 명시
        4. 최종 분석 및 결론 도출

        Args:
            task: 사용자 작업 설명
            max_steps: Computer Use 최대 단계

        Returns:
            실행 결과 (분석 및 결론 포함)
        """
        logger.info(f"🎯 Computer Use 중심 실행: {task}")

        if self.progress_callback:
            self.progress_callback({
                'type': 'info',
                'message': f'🤖 Computer Use로 작업 시작'
            })

        # 브라우저 시작 (아직 안 되어 있으면)
        if not self.page:
            self.start_browser(headless=os.getenv('HEADLESS', 'false').lower() == 'true')

        # Computer Use에 DuckDuckGo 사용 안내
        enhanced_task = f"""{task}

**중요 지침:**
- 웹 검색이 필요하면 반드시 DuckDuckGo (duckduckgo.com)를 사용하세요
- Google은 사용하지 마세요 (reCAPTCHA로 차단됨)
- 현재 브라우저는 이미 DuckDuckGo 홈페이지에 있습니다
- 작업을 완료한 후 반드시 최종 분석 및 결론을 제시하세요"""

        # Computer Use 실행
        return self.execute_task(enhanced_task, max_steps=max_steps)

    def execute_task(self, task: str, max_steps: int = 50) -> Dict[str, Any]:
        """
        Execute a task using Gemini Computer Use with autonomous multi-step execution

        Gemini analyzes the task, plans the approach, and executes multiple
        function calls autonomously. We just provide the screenshot and task,
        then execute the function calls it returns.

        Args:
            task: Natural language task description
            max_steps: Maximum number of interaction rounds (default: 50)

        Returns:
            Result dictionary with status, actions taken, and analysis
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        # Reset stop flag for new task
        self.should_stop = False

        logger.info(f"🎯 Task: {task}")
        logger.info(f"📝 Max interaction rounds: {max_steps}")

        actions_taken = []
        text_responses = []
        screenshot_path = None
        conversation_history = []
        scroll_count = 0  # Track number of scrolls for context-aware prompts

        try:
            # Configure Gemini with Computer Use tool
            config = types.GenerateContentConfig(
                tools=[types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER
                    )
                )],
                temperature=0.3,
            )

            # Start autonomous execution loop
            for round_num in range(max_steps):
                # Check if user requested stop
                if self.should_stop:
                    logger.warning("🛑 Task stopped by user")
                    if self.progress_callback:
                        self.progress_callback({
                            'type': 'stopped',
                            'message': '사용자가 작업을 중지했습니다.'
                        })
                    break

                logger.info(f"\n{'='*60}")
                logger.info(f"Round {round_num + 1}/{max_steps}")
                logger.info(f"{'='*60}")

                # Take screenshot
                screenshot_path = self.take_screenshot()

                # Build optimized prompt for this round
                prompt = self._build_prompt_for_round(
                    round_num=round_num,
                    task=task,
                    max_steps=max_steps,
                    scroll_count=scroll_count
                )

                # Upload screenshot
                with open(screenshot_path, 'rb') as f:
                    image_bytes = f.read()

                logger.info("🤔 Asking Gemini for next actions...")

                # Build conversation with history
                user_content = types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type='image/png'
                        )
                    ]
                )

                conversation_history.append(user_content)

                # Try API call with retries
                max_retries = 2
                response = None

                for retry in range(max_retries):
                    try:
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=conversation_history,
                            config=config
                        )

                        # Check if response is valid
                        if response and hasattr(response, 'candidates') and response.candidates:
                            break  # Success!

                        # Log the reason for failure
                        if response and hasattr(response, 'prompt_feedback'):
                            logger.warning(f"⚠️  Prompt feedback: {response.prompt_feedback}")

                        logger.warning(f"⚠️  Empty response, retry {retry + 1}/{max_retries}")

                        if retry < max_retries - 1:
                            time.sleep(1 * (retry + 1))  # 1s, 2s

                    except Exception as e:
                        logger.error(f"❌ API call failed: {e}")
                        if retry < max_retries - 1:
                            time.sleep(1 * (retry + 1))

                # Final check
                if response is None or not hasattr(response, 'candidates') or response.candidates is None:
                    logger.error("❌ Gemini API returned None after retries")
                    logger.error("Reasons: safety filter, token limit, or rate limiting")
                    logger.info(f"⏭️  Skipping round {round_num + 1}")

                    if self.progress_callback:
                        self.progress_callback({
                            'type': 'error',
                            'round': round_num + 1,
                            'message': f'⚠️ API 응답 실패 (Round {round_num + 1}) - 계속 진행...'
                        })
                    continue  # Skip to next round

                # Process response parts
                has_actions = False
                round_text = []
                round_actions = []
                assistant_parts = []

                for candidate in response.candidates:
                    # Check if candidate has valid content
                    if not hasattr(candidate, 'content') or candidate.content is None:
                        logger.warning("⚠️  Candidate has no content")
                        continue

                    if not hasattr(candidate.content, 'parts') or candidate.content.parts is None:
                        logger.warning("⚠️  Candidate content has no parts")
                        continue

                    for part in candidate.content.parts:
                        assistant_parts.append(part)

                        # Check for text response
                        if hasattr(part, 'text') and part.text:
                            round_text.append(part.text)
                            logger.info(f"💬 Gemini: {part.text[:200]}...")

                            # Send Gemini's reasoning to frontend
                            if self.progress_callback:
                                self.progress_callback({
                                    'type': 'gemini_text',
                                    'round': round_num + 1,
                                    'message': f"💭 {part.text}"
                                })

                        # Check for function calls (Gemini can return multiple!)
                        if hasattr(part, 'function_call') and part.function_call:
                            has_actions = True
                            func_call = part.function_call
                            action_desc = f"{func_call.name}({dict(func_call.args)})"
                            actions_taken.append(action_desc)

                            # Create human-readable action description
                            readable_action = self._format_action(func_call)
                            round_actions.append(readable_action)

                            logger.info(f"⚡ Action: {readable_action}")

                            # Send action update
                            if self.progress_callback:
                                self.progress_callback({
                                    'type': 'action',
                                    'round': round_num + 1,
                                    'message': f"⚡ {readable_action}"
                                })

                            # Execute the action immediately
                            success = self._execute_function_call(func_call)
                            if not success:
                                logger.warning("⚠️  Action execution failed")

                            # Track scroll actions for context-aware prompts
                            if func_call.name in ['scroll_document', 'scroll_at']:
                                scroll_count += 1

                # Add assistant response to conversation history
                if assistant_parts:
                    conversation_history.append(
                        types.Content(role="model", parts=assistant_parts)
                    )

                # Combine text from this round
                if round_text:
                    text_responses.extend(round_text)

                # If no text but actions exist, add action summary
                if not round_text and round_actions:
                    action_summary = f"Round {round_num + 1}: " + ", ".join(round_actions)
                    text_responses.append(action_summary)

                # If no actions were taken, Gemini is done
                if not has_actions:
                    logger.info("✅ Gemini completed the task (no more actions)")
                    break

                # Small delay between rounds
                time.sleep(0.3)

            # Build result - extract only the final answer
            full_response = "\n\n".join(text_responses) if text_responses else "Task completed"

            # Try to extract clean final answer
            final_answer = self._extract_final_answer(full_response)

            result = {
                "status": "success",
                "task": task,
                "actions": actions_taken,
                "text_responses": text_responses,
                "response": final_answer,  # Use cleaned response
                "full_response": full_response,  # Keep original for debugging
                "screenshot": screenshot_path,
                "rounds": round_num + 1,
                "steps": round_num + 1,  # Compatibility with frontend
                "actions_count": len(actions_taken)
            }

            logger.info(f"\n{'='*60}")
            logger.info(f"✅ Task completed!")
            logger.info(f"{'='*60}")
            logger.info(f"Rounds: {round_num + 1}")
            logger.info(f"Actions executed: {len(actions_taken)}")
            if actions_taken:
                logger.info(f"Actions: {actions_taken[:5]}...")  # Show first 5

            self.session_history.append(result)
            return result

        except Exception as e:
            logger.error(f"❌ Failed to execute task: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "task": task,
                "error": str(e),
                "actions": actions_taken,
                "text_responses": text_responses,
                "screenshot": screenshot_path
            }

    def stop_task(self):
        """Stop the currently executing task"""
        logger.warning("🛑 Stop requested by user")
        self.should_stop = True

    def reset_stop_flag(self):
        """Reset stop flag before starting new task"""
        self.should_stop = False

    def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information

        Returns:
            Dictionary with page title, URL, etc.
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        return {
            "url": self.page.url,
            "title": self.page.title(),
            "viewport": self.page.viewport_size,
        }

    def __enter__(self):
        """Context manager entry"""
        if not self.browser:
            self.start_browser(headless=True)  # Use headless for stability
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Quick test
    from dotenv import load_dotenv
    load_dotenv()

    with GeminiComputerUseAgent() as agent:
        # Navigate to Google
        agent.navigate_to("https://www.google.com")

        # Get page info
        info = agent.get_page_info()
        print(f"Current page: {info['title']}")
        print(f"URL: {info['url']}")

        # Ask Gemini to analyze and interact
        result = agent.execute_task(
            "What is the main search box on this page? Describe its location."
        )

        print(f"\nTask status: {result['status']}")
        print(f"Actions taken: {result['actions_count']}")
        print(f"Response: {result['response'][:300]}")
