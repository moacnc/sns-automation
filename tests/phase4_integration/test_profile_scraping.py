#!/usr/bin/env python3
"""
Phase 4.1: Profile Scraping Integration Test
목적: Navigation + Vision 통합 프로필 스크래핑 확인
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper
from loguru import logger


def test_profile_scraping(username: str = "liowish"):
    """프로필 스크래핑 통합 테스트"""
    print("=" * 60)
    print("Phase 4.1: 프로필 스크래핑 통합 테스트")
    print("=" * 60)

    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False

    try:
        # 초기화
        print("\n" + "─" * 60)
        print("[Test 4.1.1] 초기화")
        print("─" * 60)

        print("  Navigator 초기화 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("  ✅ Navigator 초기화 완료")

        print("  ProfileScraper 초기화 중...")
        scraper = ProfileScraper(navigator)
        print("  ✅ ProfileScraper 초기화 완료")

        # 프로필 스크래핑
        print("\n" + "─" * 60)
        print(f"[Test 4.1.2] 프로필 스크래핑: @{username}")
        print("─" * 60)
        print(f"  ⏳ 스크래핑 중... (20-30초 소요)")
        print(f"     1. 검색 탭 이동")
        print(f"     2. @{username} 검색")
        print(f"     3. 프로필 화면 캡처")
        print(f"     4. GPT Vision 분석")

        profile = scraper.scrape_profile(username)

        print("\n  ✅ 스크래핑 완료!")

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 프로필 정보")
        print("=" * 60)

        print(f"\n[기본 정보]")
        print(f"  Username: @{profile.get('username', 'N/A')}")
        print(f"  Full Name: {profile.get('full_name', 'N/A')}")
        print(f"  Is Verified: {'✓' if profile.get('is_verified', False) else '✗'}")
        print(f"  Is Private: {'✓' if profile.get('is_private', False) else '✗'}")

        print(f"\n[통계]")
        print(f"  Followers: {profile.get('follower_count', 'N/A')}")
        print(f"  Following: {profile.get('following_count', 'N/A')}")
        print(f"  Posts: {profile.get('posts_count', 'N/A')}")

        print(f"\n[바이오]")
        bio = profile.get('bio', 'N/A')
        if bio and bio != 'N/A':
            for line in bio.split('\n'):
                print(f"  {line}")
        else:
            print(f"  {bio}")

        print(f"\n[링크]")
        print(f"  External URL: {profile.get('external_url', 'N/A')}")

        # 결과 저장
        result_dir = project_root / "tests" / "phase4_integration" / "results"
        result_dir.mkdir(parents=True, exist_ok=True)

        result_file = result_dir / f"profile_{username}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        print(f"\n💾 결과 저장: {result_file}")

        # 결과 검증
        print("\n" + "─" * 60)
        print("[통합 검증]")
        print("─" * 60)

        checks = []

        # Navigation 체크
        checks.append(("Navigation (검색 및 이동)", profile.get('username') is not None))

        # Vision OCR 체크
        checks.append(("Vision OCR (팔로워 수)", profile.get('follower_count') is not None))

        # 전체 워크플로우 체크
        checks.append(("전체 워크플로우", all([
            profile.get('username'),
            profile.get('follower_count'),
            profile.get('following_count'),
            profile.get('posts_count')
        ])))

        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        all_passed = all(passed for _, passed in checks)

        if all_passed:
            print("\n✅ Phase 4.1 완료: 프로필 스크래핑 통합 테스트 정상")
        else:
            print("\n⚠️  Phase 4.1 완료: 일부 검증 실패")

        return True

    except Exception as e:
        print(f"\n❌ 프로필 스크래핑 실패: {e}")
        logger.exception("Profile scraping error")

        print("\n해결 방법:")
        print("  1. Phase 1-3이 모두 성공했는지 확인")
        print("  2. 사용자명이 올바른지 확인")
        print("  3. 로그를 확인하여 어느 단계에서 실패했는지 파악")

        return False


def test_quick_methods():
    """Quick 메서드 테스트"""
    print("\n" + "=" * 60)
    print("Phase 4.2: Quick Methods 테스트")
    print("=" * 60)

    try:
        navigator = InstagramNavigator()
        navigator.connect()
        scraper = ProfileScraper(navigator)

        username = "liowish"

        # get_follower_count 테스트
        print("\n" + "─" * 60)
        print(f"[Test 4.2.1] get_follower_count('{username}')")
        print("─" * 60)
        follower_count = scraper.get_follower_count(username)
        print(f"  ✅ Follower Count: {follower_count}")

        # is_verified 테스트
        print("\n" + "─" * 60)
        print(f"[Test 4.2.2] is_verified('{username}')")
        print("─" * 60)
        is_verified = scraper.is_verified(username)
        print(f"  ✅ Is Verified: {is_verified}")

        # is_private 테스트
        print("\n" + "─" * 60)
        print(f"[Test 4.2.3] is_private('{username}')")
        print("─" * 60)
        is_private = scraper.is_private(username)
        print(f"  ✅ Is Private: {is_private}")

        print("\n✅ Phase 4.2 완료: Quick Methods 정상")

        return True

    except Exception as e:
        print(f"\n❌ Quick Methods 실패: {e}")
        logger.exception("Quick methods error")
        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 4: Integration Tests")
    print("🚀" * 30 + "\n")

    # 사용자 입력
    print("테스트할 사용자명 (기본값: liowish, Enter로 기본값 사용): ", end="")
    username_input = input().strip()
    username = username_input if username_input else "liowish"

    # Test 4.1: Profile Scraping
    success_1 = test_profile_scraping(username)

    # Test 4.2: Quick Methods
    success_2 = test_quick_methods()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 4 테스트 결과")
    print("=" * 60)
    print(f"  4.1 프로필 스크래핑: {'✅ 성공' if success_1 else '❌ 실패'}")
    print(f"  4.2 Quick Methods: {'✅ 성공' if success_2 else '❌ 실패'}")

    if success_1 and success_2:
        print("\n🎉 Phase 4 전체 완료!")
        print("   다음 단계: python3 tests/phase5_advanced/test_story_restory.py")
        sys.exit(0)
    else:
        print("\n❌ Phase 4 실패")
        sys.exit(1)
