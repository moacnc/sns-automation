#!/usr/bin/env python3
"""
Phase 4.3: Advanced Profile Analysis Test
목적: GPT-4 Vision 고급 분석 기능 테스트
- analyze_profile_advanced(): 성향, 인플루언서 티어, 협업 가능성 분석
- analyze_grid_posts(): 포스팅 그리드 분석, 콘텐츠 일관성 확인
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator
from src.gramaddict_wrapper.vision_analyzer import VisionAnalyzer
from loguru import logger


def test_advanced_analysis():
    """고급 프로필 분석 테스트"""
    print("\n" + "🔬" * 30)
    print("Phase 4.3: Advanced Profile Analysis")
    print("🔬" * 30 + "\n")

    # 기본 사용자명 사용
    username = "hon.hono7"
    print(f"분석할 사용자명: {username}")

    print("\n" + "=" * 60)
    print("Phase 4.3: 고급 프로필 분석 테스트")
    print("=" * 60)

    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False

    try:
        # 초기화
        print("\n" + "─" * 60)
        print("[초기화]")
        print("─" * 60)

        print("  Navigator 초기화 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("  ✅ Navigator 초기화 완료")

        print("  VisionAnalyzer 초기화 중...")
        analyzer = VisionAnalyzer()
        print("  ✅ VisionAnalyzer 초기화 완료")

        # 프로필로 이동
        print("\n" + "─" * 60)
        print(f"[프로필 이동] @{username}")
        print("─" * 60)
        print(f"  ⏳ 검색 및 이동 중...")

        navigator.search_username(username)
        print("  ✅ 프로필 도착")

        # 스크린샷 촬영
        print("\n" + "─" * 60)
        print("[스크린샷 촬영]")
        print("─" * 60)

        screenshot_path = f"screenshots/profiles/{username}_profile.png"
        navigator.screenshot(screenshot_path)
        print(f"  ✅ 스크린샷 저장: {screenshot_path}")

        # === Test 4.3.1: 기본 프로필 분석 ===
        print("\n" + "=" * 60)
        print("📊 [Test 4.3.1] 기본 프로필 분석")
        print("=" * 60)
        print("  ⏳ GPT-4 Vision 분석 중...")

        basic_profile = analyzer.analyze_profile_screenshot(screenshot_path)

        if basic_profile:
            print("\n  ✅ 기본 분석 완료!")
            print(f"\n[기본 정보]")
            print(f"  Username: @{basic_profile.get('username', 'N/A')}")
            print(f"  Full Name: {basic_profile.get('full_name', 'N/A')}")
            print(f"  Posts: {basic_profile.get('posts_count', 'N/A')}")
            print(f"  Followers: {basic_profile.get('follower_count', 'N/A')}")
            print(f"  Following: {basic_profile.get('following_count', 'N/A')}")
            print(f"  Is Verified: {'✓' if basic_profile.get('is_verified', False) else '✗'}")
            print(f"  Is Private: {'✓' if basic_profile.get('is_private', False) else '✗'}")
        else:
            print("  ❌ 기본 분석 실패")

        # === Test 4.3.2: 고급 프로필 분석 ===
        print("\n" + "=" * 60)
        print("🎯 [Test 4.3.2] 고급 프로필 분석")
        print("=" * 60)
        print("  ⏳ GPT-4 Vision 고급 분석 중...")
        print("     - 계정 타입 분류")
        print("     - 콘텐츠 카테고리 추출")
        print("     - 인플루언서 티어 판별")
        print("     - 타겟 오디언스 분석")
        print("     - 협업 가능성 평가")

        advanced_analysis = analyzer.analyze_profile_advanced(screenshot_path)

        if advanced_analysis:
            print("\n  ✅ 고급 분석 완료!")
            print(f"\n[고급 분석 결과]")
            print(f"  Account Type: {advanced_analysis.get('account_type', 'N/A')}")
            print(f"  Content Categories: {', '.join(advanced_analysis.get('content_categories', []))}")
            print(f"  Engagement Quality: {advanced_analysis.get('engagement_quality', 'N/A')}")
            print(f"  Influencer Tier: {advanced_analysis.get('influencer_tier', 'N/A')}")
            print(f"  Target Audience: {advanced_analysis.get('target_audience', 'N/A')}")

            print(f"\n[프로필 미학]")
            print(f"  Style: {advanced_analysis.get('profile_aesthetic', 'N/A')}")

            print(f"\n[바이오 감성]")
            print(f"  Tone: {advanced_analysis.get('bio_sentiment', 'N/A')}")

            print(f"\n[진정성 평가]")
            print(f"  Assessment: {advanced_analysis.get('authenticity_assessment', 'N/A')}")

            print(f"\n[협업 가능성]")
            print(f"  Potential: {advanced_analysis.get('potential_collaboration', 'N/A')}")
        else:
            print("  ❌ 고급 분석 실패")

        # === Test 4.3.3: 그리드 포스팅 분석 ===
        print("\n" + "=" * 60)
        print("🖼️  [Test 4.3.3] 그리드 포스팅 분석")
        print("=" * 60)
        print("  ⏳ GPT-4 Vision 그리드 분석 중...")
        print("     - 비주얼 테마 추출")
        print("     - 콘텐츠 일관성 평가")
        print("     - 포스팅 스타일 분석")
        print("     - 브랜드 협업 탐지")

        grid_analysis = analyzer.analyze_grid_posts(screenshot_path)

        if grid_analysis:
            print("\n  ✅ 그리드 분석 완료!")
            print(f"\n[그리드 분석 결과]")

            visual_themes = grid_analysis.get('visual_themes', [])
            if isinstance(visual_themes, list):
                print(f"  Visual Themes: {', '.join(visual_themes)}")
            else:
                print(f"  Visual Themes: {visual_themes}")

            print(f"  Content Consistency: {grid_analysis.get('content_consistency', 'N/A')}")
            print(f"  Posting Style: {grid_analysis.get('posting_style', 'N/A')}")

            dominant_subjects = grid_analysis.get('dominant_subjects', [])
            if isinstance(dominant_subjects, list):
                print(f"  Dominant Subjects: {', '.join(dominant_subjects)}")
            else:
                print(f"  Dominant Subjects: {dominant_subjects}")

            print(f"  Brand Collaborations: {'✓' if grid_analysis.get('brand_collaborations_visible', False) else '✗'}")
            print(f"  Grid Aesthetic Quality: {grid_analysis.get('grid_aesthetic_quality', 'N/A')}")
            print(f"  Content Variety: {grid_analysis.get('content_variety', 'N/A')}")
        else:
            print("  ❌ 그리드 분석 실패")

        # 결과 저장
        print("\n" + "─" * 60)
        print("[결과 저장]")
        print("─" * 60)

        result_dir = project_root / "tests" / "phase4_integration" / "results"
        result_dir.mkdir(parents=True, exist_ok=True)

        # 통합 결과 저장
        combined_result = {
            "username": username,
            "basic_profile": basic_profile,
            "advanced_analysis": advanced_analysis,
            "grid_analysis": grid_analysis
        }

        result_file = result_dir / f"advanced_analysis_{username}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(combined_result, f, ensure_ascii=False, indent=2)

        print(f"  💾 결과 저장: {result_file}")

        # 결과 검증
        print("\n" + "=" * 60)
        print("📋 통합 검증")
        print("=" * 60)

        checks = []
        checks.append(("기본 프로필 분석", basic_profile is not None))
        checks.append(("고급 프로필 분석", advanced_analysis is not None))
        checks.append(("그리드 포스팅 분석", grid_analysis is not None))
        checks.append(("계정 타입 분류", advanced_analysis.get('account_type') is not None if advanced_analysis else False))
        checks.append(("콘텐츠 카테고리 추출", len(advanced_analysis.get('content_categories', [])) > 0 if advanced_analysis else False))
        checks.append(("비주얼 테마 추출", len(grid_analysis.get('visual_themes', [])) > 0 if grid_analysis else False))

        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        all_passed = all(passed for _, passed in checks)

        # 최종 결과
        print("\n" + "=" * 60)
        print("Phase 4.3 테스트 결과")
        print("=" * 60)
        print(f"  4.3.1 기본 프로필 분석: {'✅ 성공' if basic_profile else '❌ 실패'}")
        print(f"  4.3.2 고급 프로필 분석: {'✅ 성공' if advanced_analysis else '❌ 실패'}")
        print(f"  4.3.3 그리드 포스팅 분석: {'✅ 성공' if grid_analysis else '❌ 실패'}")

        if all_passed:
            print("\n🎉 Phase 4.3 전체 완료!")
            print("\n" + "=" * 60)
            print("💡 활용 가능한 인사이트")
            print("=" * 60)
            print("  ✅ 타겟 사용자 필터링 (인플루언서 티어 기반)")
            print("  ✅ 브랜드 매칭 (콘텐츠 카테고리 기반)")
            print("  ✅ 협업 대상 선정 (협업 가능성 점수 기반)")
            print("  ✅ 콘텐츠 전략 분석 (그리드 일관성 기반)")
            return True
        else:
            print("\n⚠️  Phase 4.3 완료: 일부 검증 실패")
            return False

    except Exception as e:
        print(f"\n❌ 고급 분석 실패: {e}")
        logger.exception("Advanced analysis error")

        print("\n해결 방법:")
        print("  1. OpenAI API 키가 올바른지 확인")
        print("  2. 스크린샷이 정상적으로 저장되었는지 확인")
        print("  3. 로그를 확인하여 어느 단계에서 실패했는지 파악")

        return False


if __name__ == "__main__":
    success = test_advanced_analysis()
    sys.exit(0 if success else 1)
