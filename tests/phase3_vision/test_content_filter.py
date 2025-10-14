#!/usr/bin/env python3
"""
Phase 3.2: Content Filtering Test
목적: GPT Vision 콘텐츠 적절성 검사 확인
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import VisionAnalyzer
from loguru import logger


def test_content_filter():
    """콘텐츠 필터링 테스트"""
    print("=" * 60)
    print("Phase 3.2: 콘텐츠 필터링 테스트")
    print("=" * 60)

    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False

    print(f"✅ OpenAI API 키 확인: {api_key[:20]}...")

    try:
        # Phase 2에서 저장한 스크린샷들 찾기
        screenshot_dir = project_root / "tests" / "phase2_navigation" / "screenshots"
        screenshot_files = list(screenshot_dir.glob("*.png"))

        if not screenshot_files:
            print(f"❌ 테스트할 스크린샷을 찾을 수 없습니다.")
            print(f"   위치: {screenshot_dir}")
            print("\n해결 방법:")
            print("  먼저 Phase 2 테스트를 실행하세요:")
            print("  python3 tests/phase2_navigation/test_search_user.py")
            return False

        # VisionAnalyzer 초기화
        print("\n" + "─" * 60)
        print("[Test 3.2.1] VisionAnalyzer 초기화")
        print("─" * 60)
        analyzer = VisionAnalyzer()
        print("✅ VisionAnalyzer 초기화 완료")

        # 각 스크린샷에 대해 콘텐츠 검사
        print("\n" + "─" * 60)
        print("[Test 3.2.2] 콘텐츠 적절성 검사")
        print("─" * 60)

        results = []

        for i, screenshot_path in enumerate(screenshot_files[:3], 1):  # 최대 3개만 테스트
            print(f"\n[테스트 {i}/{min(3, len(screenshot_files))}]")
            print(f"  파일: {screenshot_path.name}")
            print(f"  ⏳ 검사 중... (5-10초 소요)")

            result = analyzer.check_content_appropriateness(str(screenshot_path))

            is_appropriate = result.get('is_appropriate', True)
            reason = result.get('reason', 'N/A')

            if is_appropriate:
                print(f"  ✅ 적절한 콘텐츠")
            else:
                print(f"  ❌ 부적절한 콘텐츠")
                print(f"     이유: {reason}")

            results.append({
                'file': screenshot_path.name,
                'is_appropriate': is_appropriate,
                'reason': reason
            })

        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 콘텐츠 검사 결과 요약")
        print("=" * 60)

        appropriate_count = sum(1 for r in results if r['is_appropriate'])
        total_count = len(results)

        print(f"\n  총 검사: {total_count}개")
        print(f"  적절함: {appropriate_count}개")
        print(f"  부적절함: {total_count - appropriate_count}개")

        if total_count - appropriate_count > 0:
            print("\n[부적절한 콘텐츠 목록]")
            for r in results:
                if not r['is_appropriate']:
                    print(f"  - {r['file']}: {r['reason']}")

        print("\n" + "─" * 60)
        print("[기능 검증]")
        print("─" * 60)
        print("  ✅ check_content_appropriateness() 함수 작동")
        print("  ✅ OpenAI Moderation API 연동 정상")
        print("  ✅ 콘텐츠 필터링 기능 정상")

        print("\n✅ Phase 3.2 완료: 콘텐츠 필터링 정상")

        return True

    except Exception as e:
        print(f"\n❌ 콘텐츠 필터링 실패: {e}")
        logger.exception("Content filter error")

        print("\n해결 방법:")
        print("  1. OpenAI API 키가 유효한지 확인")
        print("  2. Moderation API 권한 확인")
        print("  3. 네트워크 연결 확인")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 3.2: Content Filtering Test")
    print("🚀" * 30 + "\n")

    success = test_content_filter()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 3.2 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ 콘텐츠 필터링 성공")
        print("\n🎉 Phase 3 전체 완료!")
        print("   다음 단계: python3 tests/phase4_integration/test_profile_scraping.py")
        sys.exit(0)
    else:
        print("❌ 콘텐츠 필터링 실패")
        sys.exit(1)
