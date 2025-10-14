#!/usr/bin/env python
"""
Quick Start Example: AI-Powered Instagram Automation

이 스크립트는 OpenAI Agents SDK를 사용한 기본적인 예제입니다.
자연어로 설정을 생성하고 지능형 계획을 수립합니다.

사용법:
    python examples/ai_quick_start.py
"""

import sys
import os
from pathlib import Path

# src 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.wrapper.smart_task_manager import SmartTaskManager
from src.utils.logger import get_logger

logger = get_logger()


def main():
    """메인 함수"""

    # OPENAI_API_KEY 확인
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        logger.info("설정 방법:")
        logger.info("  1. .env 파일에 추가: OPENAI_API_KEY=sk-...")
        logger.info("  2. 또는 export: export OPENAI_API_KEY=sk-...")
        return 1

    logger.info("=" * 60)
    logger.info("AI 기반 Instagram 자동화 Quick Start")
    logger.info("=" * 60)

    # Step 1: 자연어로 SmartTaskManager 생성
    logger.info("\n[Step 1] 자연어 프롬프트로 설정 생성 중...")

    prompt = """
    여행 블로거 계정 성장
    - 타겟: 주당 50명 팔로워
    - 일일 좋아요: 30개
    - 매우 안전한 접근
    - travel, photography, wanderlust 해시태그 사용
    """

    try:
        tm = SmartTaskManager.from_prompt(
            prompt=prompt,
            username="ai_test_account",
            save_config=True  # config/accounts/ai_test_account_ai_generated.yml로 저장
        )
        logger.info("✅ SmartTaskManager 생성 완료")
        logger.info(f"   Username: {tm.username}")
        logger.info(f"   AI Agents: {tm.agents_enabled}")

    except Exception as e:
        logger.error(f"❌ SmartTaskManager 생성 실패: {e}")
        return 1

    # Step 2: 지능형 계획 생성
    if tm.agents_enabled:
        logger.info("\n[Step 2] AI가 계정 데이터 분석 및 계획 생성 중...")

        try:
            plan = tm.get_intelligent_plan(
                goals={
                    "followers": 50,
                    "timeframe": "1 week"
                }
            )

            if plan:
                logger.info("✅ AI 계획 생성 완료\n")

                # 계획 출력
                import json
                logger.info("=== AI 생성 계획 ===")
                logger.info(json.dumps(plan, indent=2, ensure_ascii=False))

                # 핵심 추천사항 하이라이트
                if 'plan' in plan:
                    p = plan['plan']
                    logger.info("\n=== 핵심 추천사항 ===")
                    logger.info(f"✓ 일일 좋아요: {p.get('daily_likes', 'N/A')}")
                    logger.info(f"✓ 일일 팔로우: {p.get('daily_follows', 'N/A')}")
                    logger.info(f"✓ 속도 배수: {p.get('speed_multiplier', 'N/A')}")

                    if 'best_times' in p:
                        logger.info(f"✓ 최적 시간대: {', '.join(p['best_times'])}")

                    if 'recommended_hashtags' in p:
                        logger.info(f"✓ 추천 해시태그: {', '.join(p['recommended_hashtags'])}")

                # 경고 확인
                if 'warnings' in plan and plan['warnings']:
                    logger.warning("\n=== AI 경고 ===")
                    for warning in plan['warnings']:
                        logger.warning(f"⚠️  {warning}")

                # 신뢰도
                if 'confidence' in plan:
                    confidence = plan['confidence']
                    logger.info(f"\n신뢰도: {confidence:.1%}")

            else:
                logger.warning("⚠️  계획 생성이 None을 반환했습니다.")

        except Exception as e:
            logger.error(f"❌ 계획 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    # Step 3: 실행 (실제로는 주석 처리 - 데모용이므로)
    logger.info("\n[Step 3] 세션 실행 (데모이므로 주석 처리됨)")
    logger.info("실제 실행하려면 아래 코드의 주석을 해제하세요:")
    logger.info("""
    # 디바이스 연결 확인
    if not tm.check_device_connection():
        logger.error("Android 디바이스가 연결되지 않았습니다.")
        return 1

    # 계획 기반 실행
    result = tm.run_with_plan(plan)

    if result.succeeded:
        logger.info("✅ 세션 성공 완료")
        stats = tm.get_session_stats(result.session_id)
        logger.info(f"좋아요: {stats.get('total_likes')}")
        logger.info(f"팔로우: {stats.get('total_follows')}")
    else:
        logger.error(f"❌ 세션 실패: {result.errors}")
    """)

    # Cleanup
    tm.close()

    logger.info("\n" + "=" * 60)
    logger.info("Quick Start 완료!")
    logger.info("=" * 60)
    logger.info("\n생성된 설정 파일:")
    logger.info("  config/accounts/ai_test_account_ai_generated.yml")
    logger.info("\n자세한 사용법:")
    logger.info("  docs/AGENTS_USAGE_GUIDE.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
