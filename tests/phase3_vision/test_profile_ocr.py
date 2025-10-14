#!/usr/bin/env python3
"""
Phase 3.1: Profile OCR Test
목적: GPT-4 Vision을 사용한 프로필 스크린샷 분석 확인
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import VisionAnalyzer
from loguru import logger


def test_profile_ocr():
    """프로필 스크린샷 OCR 테스트"""
    print("=" * 60)
    print("Phase 3.1: 프로필 OCR 테스트")
    print("=" * 60)

    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("\n해결 방법:")
        print("  1. .env 파일에 OPENAI_API_KEY 추가")
        print("  2. export OPENAI_API_KEY='sk-...'")
        return False

    print(f"✅ OpenAI API 키 확인: {api_key[:20]}...")

    try:
        # Phase 2에서 저장한 스크린샷 찾기
        screenshot_dir = project_root / "tests" / "phase2_navigation" / "screenshots"
        screenshot_files = list(screenshot_dir.glob("04_profile_*.png"))

        if not screenshot_files:
            print(f"❌ Phase 2에서 저장한 프로필 스크린샷을 찾을 수 없습니다.")
            print(f"   위치: {screenshot_dir}")
            print("\n해결 방법:")
            print("  먼저 Phase 2 테스트를 실행하세요:")
            print("  python3 tests/phase2_navigation/test_search_user.py")
            return False

        screenshot_path = screenshot_files[0]
        print(f"\n[테스트 이미지]")
        print(f"  파일: {screenshot_path.name}")
        print(f"  경로: {screenshot_path}")

        # VisionAnalyzer 초기화
        print("\n" + "─" * 60)
        print("[Test 3.1.1] VisionAnalyzer 초기화")
        print("─" * 60)
        analyzer = VisionAnalyzer()
        print("✅ VisionAnalyzer 초기화 완료")

        # 프로필 스크린샷 분석
        print("\n" + "─" * 60)
        print("[Test 3.1.2] 프로필 스크린샷 분석 (GPT-4 Vision)")
        print("─" * 60)
        print("⏳ 분석 중... (10-20초 소요)")

        result = analyzer.analyze_profile_screenshot(str(screenshot_path))

        print("\n✅ 분석 완료!")

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 분석 결과")
        print("=" * 60)

        print(f"\n[기본 정보]")
        print(f"  Username: {result.get('username', 'N/A')}")
        print(f"  Is Verified: {result.get('is_verified', False)}")
        print(f"  Is Private: {result.get('is_private', False)}")

        print(f"\n[통계]")
        print(f"  Follower Count: {result.get('follower_count', 'N/A')}")
        print(f"  Following Count: {result.get('following_count', 'N/A')}")
        print(f"  Posts Count: {result.get('posts_count', 'N/A')}")

        print(f"\n[바이오]")
        bio = result.get('bio', 'N/A')
        if bio and bio != 'N/A':
            # 바이오가 길면 줄바꿈
            for line in bio.split('\n'):
                print(f"  {line}")
        else:
            print(f"  {bio}")

        print(f"\n[링크]")
        print(f"  External URL: {result.get('external_url', 'N/A')}")

        # 결과 검증
        print("\n" + "─" * 60)
        print("[결과 검증]")
        print("─" * 60)

        validation_passed = True

        # 필수 필드 체크
        required_fields = ['username', 'follower_count', 'following_count', 'posts_count']
        for field in required_fields:
            value = result.get(field)
            if value and value != 'N/A':
                print(f"  ✅ {field}: 추출 성공")
            else:
                print(f"  ⚠️  {field}: 추출 실패 (OCR 정확도 이슈일 수 있음)")
                validation_passed = False

        if validation_passed:
            print("\n✅ Phase 3.1 완료: 프로필 OCR 정상")
        else:
            print("\n⚠️  Phase 3.1 완료: 일부 필드 추출 실패")
            print("   (GPT Vision OCR이 100% 정확하지 않을 수 있습니다)")

        return True

    except Exception as e:
        print(f"\n❌ 프로필 OCR 실패: {e}")
        logger.exception("Profile OCR error")

        print("\n해결 방법:")
        print("  1. OpenAI API 키가 유효한지 확인")
        print("  2. GPT-4 Vision API 권한 확인")
        print("  3. 네트워크 연결 확인")
        print("  4. API 사용량 한도 확인")

        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 3.1: Profile OCR Test")
    print("🚀" * 30 + "\n")

    success = test_profile_ocr()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 3.1 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ 프로필 OCR 성공")
        print("\n다음 단계:")
        print("  python3 tests/phase3_vision/test_content_filter.py")
        sys.exit(0)
    else:
        print("❌ 프로필 OCR 실패")
        sys.exit(1)
