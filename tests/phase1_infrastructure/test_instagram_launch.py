#!/usr/bin/env python3
"""
Phase 1.3: Instagram App Launch Test
목적: Instagram 앱 실행 및 DeviceFacade 초기화 확인
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator
from loguru import logger


def test_instagram_launch():
    """Instagram 앱 실행 테스트"""
    print("=" * 60)
    print("Phase 1.3: Instagram 앱 실행 테스트")
    print("=" * 60)

    try:
        print("\n[1단계] InstagramNavigator 초기화 중...")
        navigator = InstagramNavigator()

        print("[2단계] 디바이스 연결 중...")
        success = navigator.connect()
        if not success:
            print("❌ 디바이스 연결 실패")
            return False
        print("✅ 디바이스 연결 성공")

        print("\n[3단계] Instagram 앱 실행 중...")
        success = navigator.launch_instagram()
        if not success:
            print("❌ Instagram 앱 실행 실패")
            return False
        print("✅ Instagram 앱 실행 성공")

        print("\n[4단계] 앱 로딩 대기 중...")
        # 5초 대기
        for i in range(5, 0, -1):
            print(f"  {i}초 대기 중...", end='\r')
            time.sleep(1)
        print("  완료!                ")

        print("\n[5단계] 스크린샷 촬영 테스트...")
        screenshot_path = project_root / "tests" / "phase1_infrastructure" / "test_instagram_screen.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        navigator.screenshot(str(screenshot_path))
        print(f"✅ 스크린샷 저장: {screenshot_path}")

        print("\n[6단계] 디바이스 정보 확인...")
        if navigator.device:
            print(f"  디바이스 ID: {navigator.device_id or 'default'}")
            print(f"  uiautomator2 연결: ✅")
        else:
            print("  ❌ uiautomator2 연결이 초기화되지 않았습니다.")
            return False

        print("\n✅ Phase 1.3 완료: Instagram 앱 실행 정상")
        print(f"\n📸 스크린샷을 확인하세요: {screenshot_path}")
        print("   Instagram 피드 화면이 보여야 합니다.")

        return True

    except Exception as e:
        print(f"\n❌ Instagram 앱 실행 실패: {e}")
        logger.exception("Instagram launch error")

        print("\n해결 방법:")
        print("  1. Instagram 앱이 설치되어 있는지 확인")
        print("  2. Instagram에 로그인되어 있는지 확인")
        print("  3. uiautomator2가 정상 설치되었는지 확인")
        print("     python3 -m uiautomator2 init")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 1.3: Instagram Launch Test")
    print("🚀" * 30 + "\n")

    success = test_instagram_launch()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 1.3 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ Instagram 앱 실행 성공")
        print("\n🎉 Phase 1 전체 완료!")
        print("   다음 단계: python3 tests/phase2_navigation/test_tab_navigation.py")
        sys.exit(0)
    else:
        print("❌ Instagram 앱 실행 실패")
        print("   위의 해결 방법을 참고하여 문제를 해결하세요.")
        sys.exit(1)
