#!/usr/bin/env python3
"""
Phase 2.2: User Search Test
목적: 사용자 검색 및 프로필로 이동 확인
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator
from loguru import logger


def test_search_user(username: str = "liowish"):
    """사용자 검색 테스트"""
    print("=" * 60)
    print("Phase 2.2: 사용자 검색 테스트")
    print("=" * 60)

    try:
        print("\n[초기화] Navigator 연결 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("✅ 연결 완료")

        # 스크린샷 저장 디렉토리
        screenshot_dir = project_root / "tests" / "phase2_navigation" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Test 1: 검색 탭으로 이동
        print("\n" + "─" * 60)
        print("[Test 2.2.1] 검색 탭으로 이동")
        print("─" * 60)
        navigator.goto_search()
        time.sleep(2)
        print("✅ 검색 탭 이동 완료")

        # Test 2: 사용자 검색
        print("\n" + "─" * 60)
        print(f"[Test 2.2.2] 사용자 검색: @{username}")
        print("─" * 60)
        print(f"검색 중: {username}")

        success = navigator.search_username(username)

        if success:
            print(f"✅ @{username} 검색 성공")
            time.sleep(3)  # 프로필 로딩 대기

            # 스크린샷
            screenshot_path = screenshot_dir / f"04_profile_{username}.png"
            navigator.screenshot(str(screenshot_path))
            print(f"📸 스크린샷 저장: {screenshot_path}")

            print("\n[확인사항]")
            print(f"  - @{username}의 프로필 화면이 보여야 합니다.")
            print("  - 팔로워 수, 팔로잉 수, 게시물 수가 보여야 합니다.")
            print("  - 프로필 사진과 바이오가 보여야 합니다.")

        else:
            print(f"❌ @{username} 검색 실패")
            return False

        # Test 3: 뒤로 가기 테스트
        print("\n" + "─" * 60)
        print("[Test 2.2.3] 뒤로 가기")
        print("─" * 60)
        navigator.go_back()
        time.sleep(2)
        print("✅ 뒤로 가기 성공")

        # Test 4: 다른 사용자 검색 (선택사항) - 자동 스킵
        print("\n" + "─" * 60)
        print("[Test 2.2.4] 다른 사용자 검색 (선택)")
        print("─" * 60)
        print("추가 검색 테스트 스킵 (자동 실행 모드)")

        other_username = ""  # 자동 스킵
        if other_username:
            print(f"\n검색 중: {other_username}")
            success_2 = navigator.search_username(other_username)

            if success_2:
                print(f"✅ @{other_username} 검색 성공")
                time.sleep(2)

                screenshot_path = screenshot_dir / f"05_profile_{other_username}.png"
                navigator.screenshot(str(screenshot_path))
                print(f"📸 스크린샷 저장: {screenshot_path}")
            else:
                print(f"⚠️  @{other_username} 검색 실패 (선택사항이므로 계속 진행)")

        print("\n✅ Phase 2.2 완료: 사용자 검색 정상")
        print(f"\n📁 스크린샷 디렉토리: {screenshot_dir}")

        return True

    except Exception as e:
        print(f"\n❌ 사용자 검색 실패: {e}")
        logger.exception("User search error")

        print("\n해결 방법:")
        print("  1. 사용자명이 정확한지 확인")
        print("  2. 네트워크 연결 확인")
        print("  3. Instagram 검색 기능이 정상인지 확인")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 2.2: User Search Test")
    print("🚀" * 30 + "\n")

    # 기본 테스트 사용자: liowish (자동 실행)
    username = "liowish"
    print(f"테스트할 사용자명: {username}")

    success = test_search_user(username)

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 2.2 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ 사용자 검색 성공")
        print("\n🎉 Phase 2 전체 완료!")
        print("   다음 단계: python3 tests/phase3_vision/test_profile_ocr.py")
        sys.exit(0)
    else:
        print("❌ 사용자 검색 실패")
        sys.exit(1)
