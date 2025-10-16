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

            # Use persistent context to maintain cookies/sessions and avoid CAPTCHA
            import tempfile
            user_data_dir = Path(tempfile.gettempdir()) / "playwright_gemini_profile"
            user_data_dir.mkdir(exist_ok=True)
            logger.info(f"📁 User data directory: {user_data_dir}")

            # Launch persistent context (better for avoiding CAPTCHA)
            try:
                # Try Chrome first (more stable)
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(user_data_dir),
                    channel='chrome',
                    headless=headless,
                    viewport={'width': 1440, 'height': 900},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                    ]
                )
                logger.info("✓ Using Chrome with persistent context")
            except Exception as e:
                logger.warning(f"Chrome not available, using Chromium: {e}")
                # Fallback to Chromium
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(user_data_dir),
                    headless=headless,
                    viewport={'width': 1440, 'height': 900},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                logger.info("✓ Using Chromium with persistent context")

            # Get the first page (persistent context auto-creates one)
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.browser = None  # Not used with persistent context

            # Navigate to Google homepage on startup
            try:
                logger.info("🌐 Navigating to Google homepage...")
                self.page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=10000)
                logger.info("✓ Started at Google homepage")
            except Exception as nav_error:
                logger.warning(f"⚠️  Could not navigate to Google: {nav_error}")
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

            # CRITICAL: Longer delay to ensure profile lock is released
            # Persistent context needs more time to clean up SingletonLock file
            import time
            import tempfile
            time.sleep(2.0)  # Increased from 0.5s to 2.0s

            # Additional check: verify lock file is released
            profile_dir = Path(tempfile.gettempdir()) / "playwright_gemini_profile"
            lock_file = profile_dir / "SingletonLock"

            # Wait up to 3 more seconds for lock to be released
            if lock_file.exists():
                for i in range(6):
                    if not lock_file.exists():
                        logger.debug("✓ Profile lock released")
                        break
                    time.sleep(0.5)
                    logger.debug(f"⏳ Waiting for profile lock release... ({i+1}/6)")
                else:
                    # Force remove lock file if still exists
                    if lock_file.exists():
                        logger.warning("⚠️ Force removing stale lock file")
                        try:
                            lock_file.unlink()
                        except:
                            pass

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
            return f"""You are a browser automation agent. Complete this task with minimal steps and verifiable evidence.

## TASK
{task}

## Core Loop (max {max_steps} steps)
Each step: PLAN (1 line) → ACT (1 action) → OBSERVE (brief) → CHECK stopping condition

## Navigation Strategy
1. **Find before scroll**: Use in-page search/TOC/tabs first
2. **Batch scrolling**: If needed, scroll 2-3 times in succession (max 12 total)
3. **Smart waiting**: Wait for network idle + key elements after navigation
4. **Selector priority**: role/aria > test-id > stable CSS > XPath

## Interaction Rules
- Scroll element into view before clicking
- For long pages: scroll MULTIPLE times in succession, don't give up early
- For pagination: scan up to 3 pages unless task requires more
- NO logins/forms/captcha bypass

## Output Requirements
- Explain your thinking before each action
- Describe what you see on screen
- Explain why you're taking each action
- After action, briefly describe what happened
- When task complete, provide clear final answer with "Final Answer:" prefix

## START
Current URL: {current_url}
Current page shown in screenshot below.

Provide your first 1-line PLAN:"""

        # === ROUNDS 1-23: Lightweight continuation ===
        elif round_num < max_steps - 2:
            reminder = f"""Continue task: {task}

REMINDERS (Critical):
- Scroll 2-3 times in succession for long pages - don't give up early
- Check: do you have enough evidence for final answer?
- Progress: Step {round_num + 1}/{max_steps}
"""

            # Add specific warnings based on context
            if scroll_count > 5:
                reminder += "⚠️  Many scrolls with no progress? Try different strategy (search/tabs)\n"

            if round_num > 10 and round_num % 5 == 0:
                reminder += f"⚠️  {round_num + 1} steps taken - consider if you have enough info to answer\n"

            reminder += f"\nCurrent URL: {current_url}\n\nNext 1-line PLAN (or provide 'Final Answer: ...' if complete):"

            return reminder

        # === ROUNDS 24-25: Forced completion ===
        else:
            return f"""URGENT: Approaching max steps ({round_num + 1}/{max_steps})

Task: {task}
Current URL: {current_url}

You MUST provide final answer now with what you've gathered.

Respond with:
Final Answer: <your answer based on evidence collected>

If you need 1-2 more actions, state them clearly, but prepare to conclude."""

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
