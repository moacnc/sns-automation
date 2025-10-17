#!/usr/bin/env python3
"""
하이브리드 모드 테스트
Google Search Grounding + Computer Use
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from computer_use_wrapper import GeminiComputerUseAgent

# Load environment
project_root = Path(__file__).parent.parent
load_dotenv(dotenv_path=project_root / '.env')

logger.info("=" * 70)
logger.info("🧪 하이브리드 모드 테스트")
logger.info("=" * 70)

# Test cases
test_cases = [
    {
        'name': '검색 전용 (Search Grounding)',
        'task': '구글에서 "Gemini API 사용법" 검색',
        'expected_strategy': 'search_only'
    },
    {
        'name': '브라우저 전용 (Computer Use)',
        'task': '인스타그램 프로필 페이지 열기',
        'expected_strategy': 'browser_only'
    },
    {
        'name': '하이브리드 (Search + Browser)',
        'task': '네이버 블로그에서 AI 트렌드 검색하고 첫 번째 글 제목 가져오기',
        'expected_strategy': 'hybrid'
    }
]

def test_search_only():
    """검색 전용 테스트"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: 검색 전용 (Google Search Grounding)")
    logger.info("="*70)

    with GeminiComputerUseAgent() as agent:
        task = '구글에서 "Anthropic Claude" 검색'
        logger.info(f"📝 작업: {task}")

        result = agent.execute_hybrid_task(task, max_steps=5)

        logger.info(f"\n✅ 결과:")
        logger.info(f"   상태: {result.get('status')}")
        logger.info(f"   전략: {result.get('strategy')}")

        if result.get('search_results'):
            logger.info(f"   검색 결과: {len(result['search_results'])}개")
            for i, r in enumerate(result['search_results'][:3], 1):
                logger.info(f"     {i}. {r['title']}")
                logger.info(f"        {r['url'][:80]}...")

        logger.info(f"\n📄 응답:")
        logger.info(result.get('response', 'No response')[:500])

        return result

def test_browser_only():
    """브라우저 전용 테스트"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: 브라우저 전용 (Computer Use)")
    logger.info("="*70)

    with GeminiComputerUseAgent() as agent:
        task = 'github.com으로 이동해서 페이지 제목 확인'
        logger.info(f"📝 작업: {task}")

        # 브라우저 시작
        agent.start_browser(headless=True)

        result = agent.execute_hybrid_task(task, max_steps=5)

        logger.info(f"\n✅ 결과:")
        logger.info(f"   상태: {result.get('status')}")
        logger.info(f"   전략: {result.get('strategy')}")
        logger.info(f"   실행 단계: {result.get('steps')}")

        return result

def test_task_analysis():
    """작업 유형 분석 테스트"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: 작업 유형 자동 분석")
    logger.info("="*70)

    agent = GeminiComputerUseAgent()

    test_tasks = [
        "구글에서 파이썬 튜토리얼 검색",
        "유튜브에서 동영상 재생",
        "네이버 블로그 검색",
        "인스타그램 로그인",
        "아마존에서 상품 검색하고 첫 번째 상품 클릭"
    ]

    logger.info("\n작업 유형 분석 결과:")
    logger.info("-" * 70)

    for task in test_tasks:
        analysis = agent._analyze_task_type(task)
        logger.info(f"\n📝 작업: {task}")
        logger.info(f"   전략: {analysis['strategy']}")
        logger.info(f"   검색 필요: {analysis['needs_search']}")
        logger.info(f"   브라우저 필요: {analysis['needs_browser']}")
        if analysis.get('search_query'):
            logger.info(f"   검색어: {analysis['search_query']}")

def main():
    """메인 테스트 실행"""

    logger.info("\n🚀 하이브리드 모드 테스트 시작\n")

    try:
        # Test 1: 작업 분석
        logger.info("=" * 70)
        logger.info("1️⃣  작업 유형 자동 분석 테스트")
        logger.info("=" * 70)
        test_task_analysis()

        # Test 2: 검색 전용
        logger.info("\n" + "=" * 70)
        logger.info("2️⃣  검색 전용 모드 테스트 (Google Search Grounding)")
        logger.info("=" * 70)
        test_search_only()

        # Test 3: 브라우저 전용 (선택적)
        # logger.info("\n" + "=" * 70)
        # logger.info("3️⃣  브라우저 전용 모드 테스트 (Computer Use)")
        # logger.info("=" * 70)
        # test_browser_only()

        logger.info("\n" + "=" * 70)
        logger.info("✅ 모든 테스트 완료!")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
