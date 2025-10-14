#!/usr/bin/env python3
"""
Phase 2.1: Tab Navigation Test
목적: GramAddict TabBarView를 사용한 탭 이동 확인
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator
from loguru import logger


def test_tab_navigation():
    """탭 네비게이션 테스트"""
    print("=" * 60)
    print("Phase 2.1: 탭 네비게이션 테스트")
    print("=" * 60)

    try:
        print("\n[초기화] Navigator 연결 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("✅ 연결 완료")

        # 스크린샷 저장 디렉토리
        screenshot_dir = project_root / "tests" / "phase2_navigation" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Test 1: 홈 탭으로 이동
        print("\n" + "─" * 60)
        print("[Test 2.1.1] 홈 탭으로 이동")
        print("─" * 60)
        success_home = navigator.goto_home()

        if success_home:
            print("✅ 홈 탭 이동 성공")
            time.sleep(2)

            # 스크린샷
            screenshot_path = screenshot_dir / "01_home_tab.png"
            navigator.screenshot(str(screenshot_path))
            print(f"📸 스크린샷 저장: {screenshot_path}")
        else:
            print("❌ 홈 탭 이동 실패")
            return False

        # Test 2: 검색 탭으로 이동
        print("\n" + "─" * 60)
        print("[Test 2.1.2] 검색 탭으로 이동")
        print("─" * 60)
        success_search = navigator.goto_search()

        if success_search:
            print("✅ 검색 탭 이동 성공")
            time.sleep(2)

            # 스크린샷
            screenshot_path = screenshot_dir / "02_search_tab.png"
            navigator.screenshot(str(screenshot_path))
            print(f"📸 스크린샷 저장: {screenshot_path}")
        else:
            print("❌ 검색 탭 이동 실패")
            return False

        # Test 3: 프로필 탭으로 이동
        print("\n" + "─" * 60)
        print("[Test 2.1.3] 프로필 탭으로 이동")
        print("─" * 60)
        success_profile = navigator.goto_profile()

        if success_profile:
            print("✅ 프로필 탭 이동 성공")
            time.sleep(2)

            # 스크린샷
            screenshot_path = screenshot_dir / "03_profile_tab.png"
            navigator.screenshot(str(screenshot_path))
            print(f"📸 스크린샷 저장: {screenshot_path}")
        else:
            print("❌ 프로필 탭 이동 실패")
            return False

        # Test 4: 다시 홈으로 돌아가기
        print("\n" + "─" * 60)
        print("[Test 2.1.4] 홈 탭으로 복귀")
        print("─" * 60)
        success_return = navigator.goto_home()

        if success_return:
            print("✅ 홈 탭 복귀 성공")
            time.sleep(1)
        else:
            print("❌ 홈 탭 복귀 실패")
            return False

        print("\n✅ Phase 2.1 완료: 모든 탭 네비게이션 정상")
        print(f"\n📁 스크린샷 디렉토리: {screenshot_dir}")
        print("   각 탭의 스크린샷을 확인하세요.")

        return True

    except Exception as e:
        print(f"\n❌ 탭 네비게이션 실패: {e}")
        logger.exception("Tab navigation error")

        print("\n해결 방법:")
        print("  1. Instagram이 최신 버전인지 확인")
        print("  2. GramAddict TabBarView selector 확인")
        print("  3. 디바이스 화면 해상도 확인")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 2.1: Tab Navigation Test")
    print("🚀" * 30 + "\n")

    success = test_tab_navigation()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 2.1 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ 탭 네비게이션 성공")
        print("\n다음 단계:")
        print("  python3 tests/phase2_navigation/test_search_user.py")
        sys.exit(0)
    else:
        print("❌ 탭 네비게이션 실패")
        sys.exit(1)
