#!/usr/bin/env python3
"""
Orchestrator Agent - Multi-Agent Coordinator

Analyzes user tasks, creates execution plans, and coordinates between
SearchAgent (Google Search Grounding) and ComputerUseAgent (browser automation).
"""

import os
import json
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from google import genai
from google.genai import types

from .search_agent import SearchAgent
# Import computer use agent from parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from computer_use_wrapper import GeminiComputerUseAgent


class OrchestratorAgent:
    """
    Orchestrator Agent - Multi-Agent Task Coordinator

    Analyzes user requests, determines which agents to use,
    and coordinates their execution to complete complex tasks.
    """

    def __init__(self, api_key: Optional[str] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize Orchestrator Agent

        Args:
            api_key: Google AI API key
            progress_callback: Callback for progress updates
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Initialize Gemini client for planning
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash-exp"

        # Progress callback
        self.progress_callback = progress_callback

        # Initialize sub-agents (lazy initialization)
        self.search_agent: Optional[SearchAgent] = None
        self.computer_use_agent: Optional[GeminiComputerUseAgent] = None

        logger.info("🎯 OrchestratorAgent initialized")

    def _get_search_agent(self) -> SearchAgent:
        """Lazy initialization of SearchAgent"""
        if self.search_agent is None:
            self.search_agent = SearchAgent(
                api_key=self.api_key,
                progress_callback=self.progress_callback
            )
        return self.search_agent

    def _get_computer_use_agent(self) -> GeminiComputerUseAgent:
        """Lazy initialization of ComputerUseAgent"""
        if self.computer_use_agent is None:
            self.computer_use_agent = GeminiComputerUseAgent(
                api_key=self.api_key
            )
            # Set progress callback
            self.computer_use_agent.progress_callback = self.progress_callback
        return self.computer_use_agent

    def get_computer_use_agent(self) -> Optional[GeminiComputerUseAgent]:
        """Get ComputerUseAgent instance (for external access like stop/screenshot)"""
        return self.computer_use_agent

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """
        Analyze user task and create execution plan

        Args:
            task: User's request

        Returns:
            Execution plan with:
            - needs_search: Whether web search is needed
            - needs_browser: Whether browser interaction is needed
            - search_queries: List of search queries (if needs_search)
            - browser_instructions: Instructions for browser (if needs_browser)
            - execution_order: ['search', 'browser'] or ['browser'] or ['search']
        """
        try:
            logger.info(f"🎯 Analyzing task: {task}")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'orchestrator',
                    'type': 'info',
                    'message': f'🎯 작업 분석 중: "{task}"'
                })

            # Build analysis prompt
            analysis_prompt = f"""당신은 작업 분석 전문가입니다. 사용자의 요청을 분석하고 실행 계획을 수립하세요.

사용자 요청: {task}

분석할 항목:
1. 웹 검색이 필요한가? (yes/no)
   - 최신 정보, 통계, 뉴스, 인물 정보 등이 필요하면 yes
   - 이미 알려진 웹사이트 URL로 직접 가면 되는 경우 no

2. 브라우저 조작이 필요한가? (yes/no)
   - 웹사이트 방문, 클릭, 입력, 데이터 추출이 필요하면 yes
   - 단순 정보 검색만 필요하면 no

3. 검색어 (웹 검색이 필요한 경우):
   - 최적화된 검색어 1-3개 (배열로)

4. 브라우저 작업 지시사항 (브라우저 조작이 필요한 경우):
   - 어떤 웹사이트에 가야 하는지
   - 무엇을 해야 하는지 구체적으로

5. 실행 순서:
   - ["search", "browser"]: 검색 후 브라우저
   - ["browser"]: 브라우저만
   - ["search"]: 검색만

**반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):**

{{
  "needs_search": true/false,
  "needs_browser": true/false,
  "search_queries": ["검색어1", "검색어2"],
  "browser_instructions": "브라우저 작업 지시사항",
  "target_url": "방문할 URL (알고 있는 경우)",
  "execution_order": ["search", "browser"],
  "reasoning": "왜 이렇게 계획했는지 간단히"
}}

예시 1:
요청: "한국 유명 뷰티 유튜버 찾아줘"
응답:
{{
  "needs_search": true,
  "needs_browser": true,
  "search_queries": ["한국 유명 뷰티 유튜버 2025", "인기 뷰티 크리에이터"],
  "browser_instructions": "검색 결과에서 찾은 유튜버들을 youtube.com에서 검색하고 구독자 수, 최근 영상 등 정보 수집",
  "target_url": "https://youtube.com",
  "execution_order": ["search", "browser"],
  "reasoning": "먼저 검색으로 유명 유튜버 목록을 찾고, YouTube에서 상세 정보 확인"
}}

예시 2:
요청: "youtube.com에서 'AI news' 검색해줘"
응답:
{{
  "needs_search": false,
  "needs_browser": true,
  "search_queries": [],
  "browser_instructions": "youtube.com에 접속하여 'AI news' 검색 수행",
  "target_url": "https://youtube.com",
  "execution_order": ["browser"],
  "reasoning": "URL을 이미 알고 있고, YouTube 내부 검색만 하면 됨"
}}

예시 3:
요청: "2025년 AI 트렌드 알려줘"
응답:
{{
  "needs_search": true,
  "needs_browser": false,
  "search_queries": ["2025 AI 트렌드", "인공지능 트렌드 2025"],
  "browser_instructions": "",
  "target_url": "",
  "execution_order": ["search"],
  "reasoning": "최신 정보 검색만으로 충분, 브라우저 조작 불필요"
}}

이제 다음 요청을 분석하세요:
요청: {task}
"""

            # Call Gemini for analysis
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for consistent planning
                )
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Clean up markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            plan = json.loads(response_text.strip())

            logger.info(f"📋 Execution plan created:")
            logger.info(f"  - Needs search: {plan.get('needs_search')}")
            logger.info(f"  - Needs browser: {plan.get('needs_browser')}")
            logger.info(f"  - Execution order: {plan.get('execution_order')}")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'orchestrator',
                    'type': 'gemini_text',
                    'message': f'💭 실행 계획:\n- 검색 필요: {plan.get("needs_search")}\n- 브라우저 필요: {plan.get("needs_browser")}\n- 순서: {" → ".join(plan.get("execution_order", []))}\n- 이유: {plan.get("reasoning", "")}'
                })

            return plan

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse plan JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Fallback: assume both search and browser needed
            return {
                'needs_search': True,
                'needs_browser': True,
                'search_queries': [task],
                'browser_instructions': task,
                'target_url': '',
                'execution_order': ['search', 'browser'],
                'reasoning': 'Failed to parse plan, using fallback'
            }

        except Exception as e:
            logger.error(f"❌ Task analysis failed: {e}")
            raise

    def execute(self, task: str, max_steps: int = 50, headless: bool = True) -> Dict[str, Any]:
        """
        Execute task with multi-agent coordination

        Args:
            task: User's request
            max_steps: Max steps for Computer Use agent
            headless: Whether to run browser in headless mode

        Returns:
            Execution result with data from all agents
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 ORCHESTRATOR EXECUTING: {task}")
            logger.info(f"{'='*60}")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'orchestrator',
                    'type': 'info',
                    'message': f'🚀 멀티 에이전트 실행 시작'
                })

            # Step 1: Analyze task
            plan = self.analyze_task(task)

            # Results container
            search_results = None
            browser_results = None

            # Step 2: Execute according to plan
            execution_order = plan.get('execution_order', ['search', 'browser'])

            for agent_type in execution_order:
                if agent_type == 'search' and plan.get('needs_search'):
                    # Execute search agent
                    search_results = self._execute_search(plan)

                elif agent_type == 'browser' and plan.get('needs_browser'):
                    # Execute browser agent
                    browser_results = self._execute_browser(plan, search_results, max_steps, headless)

            # Step 3: Synthesize final result
            final_result = self._synthesize_results(task, plan, search_results, browser_results)

            logger.info("✅ Orchestrator execution completed")

            return final_result

        except Exception as e:
            logger.error(f"❌ Orchestrator execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'orchestrator',
                    'type': 'error',
                    'message': f'❌ 실행 실패: {str(e)}'
                })

            return {
                'status': 'error',
                'task': task,
                'error': str(e),
                'plan': plan if 'plan' in locals() else None
            }

    def _execute_search(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search agent"""
        search_queries = plan.get('search_queries', [])

        if not search_queries:
            return None

        logger.info(f"🔍 Executing SearchAgent with queries: {search_queries}")

        if self.progress_callback:
            self.progress_callback({
                'agent': 'orchestrator',
                'type': 'action',
                'message': f'⚡ SearchAgent 실행: {len(search_queries)}개 검색어'
            })

        search_agent = self._get_search_agent()

        # Perform searches (single or multiple)
        if len(search_queries) == 1:
            return search_agent.search(search_queries[0])
        else:
            return search_agent.multi_search(search_queries)

    def _execute_browser(self, plan: Dict[str, Any], search_results: Optional[Dict], max_steps: int, headless: bool) -> Dict[str, Any]:
        """Execute computer use agent"""
        browser_instructions = plan.get('browser_instructions', '')

        if not browser_instructions:
            return None

        logger.info(f"🖱️  Executing ComputerUseAgent")

        if self.progress_callback:
            self.progress_callback({
                'agent': 'orchestrator',
                'type': 'action',
                'message': f'⚡ ComputerUseAgent 실행'
            })

        # Build enhanced task with search context
        enhanced_task = self._build_browser_task(browser_instructions, search_results, plan)

        computer_use_agent = self._get_computer_use_agent()

        # Start browser if not started
        if not computer_use_agent.page:
            computer_use_agent.start_browser(headless=headless)

        try:
            # Execute browser task
            result = computer_use_agent.execute_task(enhanced_task, max_steps=max_steps)
            return result

        finally:
            # Close browser after task
            computer_use_agent.close_browser()

    def _build_browser_task(self, browser_instructions: str, search_results: Optional[Dict], plan: Dict[str, Any]) -> str:
        """
        Build enhanced browser task with search context

        Args:
            browser_instructions: Original browser instructions
            search_results: Results from search agent (if any)
            plan: Execution plan

        Returns:
            Enhanced task description for Computer Use agent
        """
        # Start with base instructions
        task_parts = [browser_instructions]

        # Add search context if available
        if search_results:
            task_parts.append("\n\n## 검색 결과 컨텍스트:")

            # Single search result
            if 'summary' in search_results:
                task_parts.append(f"\n**검색어**: {search_results.get('query', '')}")
                task_parts.append(f"\n**요약**: {search_results['summary'][:500]}")

                sources = search_results.get('sources', [])
                if sources:
                    task_parts.append(f"\n\n**주요 소스**:")
                    for i, source in enumerate(sources[:5], 1):
                        task_parts.append(f"{i}. {source['title']}: {source['url']}")

            # Multi-search results
            elif 'results' in search_results:
                for result in search_results['results']:
                    task_parts.append(f"\n**검색어**: {result.get('query', '')}")
                    task_parts.append(f"**요약**: {result['summary'][:300]}")

        # Add target URL hint if available
        target_url = plan.get('target_url', '')
        if target_url:
            task_parts.append(f"\n\n## 목표 URL: {target_url}")

        # Add reminder about direct navigation
        task_parts.append("\n\n**중요**: 검색 엔진 사용 금지! 위 URL로 직접 접속하거나 사이트 내부 검색 기능을 사용하세요.")

        return "\n".join(task_parts)

    def _synthesize_results(self, task: str, plan: Dict[str, Any], search_results: Optional[Dict], browser_results: Optional[Dict]) -> Dict[str, Any]:
        """
        Synthesize final result from all agents

        Args:
            task: Original user task
            plan: Execution plan
            search_results: SearchAgent results
            browser_results: ComputerUseAgent results

        Returns:
            Synthesized final result
        """
        logger.info("🔄 Synthesizing final result...")

        if self.progress_callback:
            self.progress_callback({
                'agent': 'orchestrator',
                'type': 'info',
                'message': '🔄 최종 결과 정리 중...'
            })

        # Build comprehensive response
        response_parts = []

        # Add search summary
        if search_results:
            if 'summary' in search_results:
                response_parts.append(f"## 검색 결과\n{search_results['summary']}")
            elif 'results' in search_results:
                response_parts.append("## 검색 결과")
                for result in search_results['results']:
                    response_parts.append(f"\n### {result.get('query')}\n{result['summary']}")

        # Add browser results
        if browser_results:
            browser_response = browser_results.get('response', browser_results.get('full_response', ''))
            if browser_response:
                response_parts.append(f"\n## 상세 분석\n{browser_response}")

        final_response = "\n\n".join(response_parts) if response_parts else "작업을 완료했습니다."

        # Build result dictionary
        result = {
            'status': 'success',
            'task': task,
            'response': final_response,
            'plan': plan,
            'search_results': search_results,
            'browser_results': browser_results,
            'agents_used': []
        }

        if search_results:
            result['agents_used'].append('search')
        if browser_results:
            result['agents_used'].append('computer_use')

        logger.info(f"✅ Final result synthesized (agents used: {result['agents_used']})")

        return result


# Test function
if __name__ == "__main__":
    """Test OrchestratorAgent"""

    def test_callback(update):
        agent_icons = {
            'search': '🔍',
            'computer_use': '🖱️',
            'orchestrator': '🎯'
        }
        icon = agent_icons.get(update.get('agent', ''), '📌')
        print(f"{icon} [{update.get('type')}] {update.get('message', '')}")

    orchestrator = OrchestratorAgent(progress_callback=test_callback)

    # Test 1: Search only
    print("\n" + "="*60)
    print("TEST 1: Search Only")
    print("="*60)

    result1 = orchestrator.execute("2025년 AI 트렌드 알려줘", max_steps=10, headless=True)
    print(f"\nStatus: {result1['status']}")
    print(f"Agents used: {result1['agents_used']}")

    # Test 2: Search + Browser
    print("\n" + "="*60)
    print("TEST 2: Search + Browser")
    print("="*60)

    result2 = orchestrator.execute("한국 유명 뷰티 유튜버 찾아줘", max_steps=20, headless=True)
    print(f"\nStatus: {result2['status']}")
    print(f"Agents used: {result2['agents_used']}")
