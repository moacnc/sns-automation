#!/usr/bin/env python3
"""
Phase 3.3: Follow User Test
목적: 프로필 페이지에서 팔로우 기능 테스트
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator
from loguru import logger


def test_follow_user(username: str = "liowish"):
    """팔로우 기능 테스트"""
    print("=" * 60)
    print("Phase 3.3: 팔로우 기능 테스트")
    print("=" * 60)

    try:
        print("\n[초기화] Navigator 연결 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("✅ 연결 완료")

        # 스크린샷 저장 디렉토리
        screenshot_dir = project_root / "tests" / "phase3_vision" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Test 1: 사용자 프로필로 이동
        print("\n" + "─" * 60)
        print(f"[Test 3.3.1] 사용자 프로필로 이동: @{username}")
        print("─" * 60)

        success = navigator.search_username(username)
        if not success:
            print(f"❌ @{username} 검색 실패")
            return False

        print(f"✅ @{username} 프로필로 이동 완료")
        time.sleep(2)

        # 프로필 스크린샷 (팔로우 전)
        screenshot_path = screenshot_dir / f"01_profile_{username}_before_follow.png"
        navigator.screenshot(str(screenshot_path))
        print(f"📸 스크린샷 저장: {screenshot_path}")

        # Test 2: 팔로우 상태 확인
        print("\n" + "─" * 60)
        print("[Test 3.3.2] 팔로우 상태 확인")
        print("─" * 60)

        status = navigator.check_follow_status()
        print(f"현재 팔로우 상태: {status}")

        if status == "following":
            print("✅ 이미 팔로우 중입니다.")
            print("   (언팔로우하지 않으므로 팔로우 액션은 스킵됩니다)")
        elif status == "requested":
            print("✅ 팔로우 요청이 이미 전송되었습니다. (비공개 계정)")
        elif status == "follow":
            print("ℹ️  현재 팔로우하지 않은 상태입니다.")
        else:
            print("⚠️  팔로우 상태를 확인할 수 없습니다.")

        # Test 3: 팔로우 실행
        print("\n" + "─" * 60)
        print("[Test 3.3.3] 팔로우 실행")
        print("─" * 60)

        if status == "following":
            print("→ 이미 팔로우 중이므로 팔로우 액션을 실행하지 않습니다.")
            follow_success = True
        else:
            print(f"→ @{username} 팔로우 시도 중...")
            follow_success = navigator.follow_user()

            if follow_success:
                print(f"✅ @{username} 팔로우 성공")
            else:
                print(f"❌ @{username} 팔로우 실패")
                return False

        time.sleep(2)

        # 프로필 스크린샷 (팔로우 후)
        screenshot_path = screenshot_dir / f"02_profile_{username}_after_follow.png"
        navigator.screenshot(str(screenshot_path))
        print(f"📸 스크린샷 저장: {screenshot_path}")

        # Test 4: 팔로우 상태 재확인
        print("\n" + "─" * 60)
        print("[Test 3.3.4] 팔로우 상태 재확인")
        print("─" * 60)

        new_status = navigator.check_follow_status()
        print(f"최종 팔로우 상태: {new_status}")

        if new_status in ["following", "requested"]:
            print("✅ 팔로우 상태 확인 완료")
        else:
            print("⚠️  팔로우 상태가 변경되지 않았습니다.")

        # Test 5: 뒤로 가기
        print("\n" + "─" * 60)
        print("[Test 3.3.5] 뒤로 가기")
        print("─" * 60)
        navigator.go_back()
        time.sleep(2)
        print("✅ 뒤로 가기 성공")

        print("\n✅ Phase 3.3 완료: 팔로우 기능 정상")
        print(f"\n📁 스크린샷 디렉토리: {screenshot_dir}")

        print("\n[테스트 요약]")
        print(f"  대상 사용자: @{username}")
        print(f"  초기 상태: {status}")
        print(f"  최종 상태: {new_status}")
        print(f"  팔로우 액션: {'실행됨' if status == 'follow' else '스킵됨 (이미 팔로우 중)'}")

        return True

    except Exception as e:
        print(f"\n❌ 팔로우 테스트 실패: {e}")
        logger.exception("Follow test error")

        print("\n해결 방법:")
        print("  1. 사용자명이 정확한지 확인")
        print("  2. 네트워크 연결 확인")
        print("  3. Instagram 계정이 로그인되어 있는지 확인")
        print("  4. 디바이스 화면이 켜져 있는지 확인")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 3.3: Follow User Test")
    print("🚀" * 30 + "\n")

    # 기본 테스트 사용자
    username = "liowish"
    print(f"테스트할 사용자명: {username}")

    success = test_follow_user(username)

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 3.3 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ 팔로우 기능 테스트 성공")
        print("\n🎉 Phase 3 완료!")
        print("   다음 단계: python3 tests/phase4_integration/test_profile_scraping.py")
        sys.exit(0)
    else:
        print("❌ 팔로우 기능 테스트 실패")
        sys.exit(1)
