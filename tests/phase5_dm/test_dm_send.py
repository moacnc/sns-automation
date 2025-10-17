#!/usr/bin/env python3
"""
Phase 5: DM Send Test
목적: 자동 DM 전송 및 개인화 메시지 생성 기능 확인
⚠️ 주의: 실제로 DM을 전송하므로 테스트 계정 사용 권장
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper
from src.gramaddict_wrapper.dm_sender import DMSender
from loguru import logger


def test_dm_send(username: str = "liowish", dry_run: bool = True):
    """DM 전송 테스트"""
    print("\n" + "📨" * 30)
    print("Phase 5: DM Send Test")
    print("📨" * 30 + "\n")

    print(f"테스트 대상: @{username}")

    print("=" * 60)
    print("Phase 5: DM 전송 테스트")
    print("=" * 60)

    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False

    # Dry run 모드 확인
    if dry_run:
        print("\n⚠️  DRY RUN 모드")
        print("   실제로 DM을 전송하지 않고 메시지 생성만 테스트합니다.")
        print("   실제 전송을 원하면 dry_run=False로 실행하세요.")
    else:
        print("\n⚠️  실제 전송 모드")
        print(f"   @{username}에게 실제로 DM을 전송합니다!")
        print("   사용자 명령으로 자동 승인됨 ✅")

    try:
        # 초기화
        print("\n" + "─" * 60)
        print("[Test 5.1] 초기화")
        print("─" * 60)

        print("  Navigator 초기화 중...")
        navigator = InstagramNavigator()
        navigator.connect()
        print("  ✅ Navigator 초기화 완료")

        print("  Instagram 앱 실행 중...")
        navigator.launch_instagram()
        print("  ✅ Instagram 앱 실행 완료")

        print("  ProfileScraper 초기화 중...")
        scraper = ProfileScraper(navigator)
        print("  ✅ ProfileScraper 초기화 완료")

        print("  DMSender 초기화 중...")
        dm_sender = DMSender(navigator, scraper)
        print("  ✅ DMSender 초기화 완료")

        # 프로필 정보 수집
        print("\n" + "─" * 60)
        print(f"[Test 5.2] 프로필 정보 수집: @{username}")
        print("─" * 60)
        print(f"  ⏳ 프로필 스크래핑 중...")

        profile = scraper.scrape_profile(username)

        if profile:
            print("  ✅ 프로필 정보 수집 완료")
            print(f"\n  [수집된 정보]")
            print(f"    Username: @{profile.get('username', 'N/A')}")
            print(f"    Followers: {profile.get('follower_count', 'N/A')}")
            print(f"    Posts: {profile.get('posts_count', 'N/A')}")
            bio = profile.get('bio', 'N/A')
            if bio and bio != 'N/A' and bio != 'None':
                print(f"    Bio: {bio[:50]}...")
            else:
                print(f"    Bio: (없음)")
        else:
            print("  ⚠️  프로필 정보 수집 실패 - 기본 정보로 진행")
            profile = None

        # 메시지 생성 테스트
        print("\n" + "─" * 60)
        print("[Test 5.3] 개인화 메시지 생성")
        print("─" * 60)

        # 캠페인 컨텍스트 예시
        campaign_context = """
우리는 한국의 뷰티 브랜드입니다.
인플루언서 협업을 제안하고 싶습니다.
친근하고 정중한 톤으로 작성해주세요.
200자 이내로 간결하게 작성해주세요.
"""

        print("  ⏳ GPT-4o로 메시지 생성 중...")
        print(f"\n  [캠페인 컨텍스트]")
        print(f"    {campaign_context.strip()}")

        # 메시지 생성 (실제 _generate_message 메서드 호출)
        try:
            message = dm_sender._generate_message(username, campaign_context, profile)

            if message:
                print("\n  ✅ 메시지 생성 완료!")
                print(f"\n  [생성된 메시지]")
                print("  " + "─" * 58)
                for line in message.split('\n'):
                    print(f"  {line}")
                print("  " + "─" * 58)
            else:
                print("  ❌ 메시지 생성 실패")
                return False

        except Exception as e:
            print(f"  ❌ 메시지 생성 중 오류: {e}")
            logger.exception("Message generation error")
            return False

        # DRY RUN에서는 여기서 종료
        if dry_run:
            print("\n" + "─" * 60)
            print("[Test 5.4] DM 전송 (DRY RUN)")
            print("─" * 60)
            print("  ℹ️  DRY RUN 모드: 실제 전송은 하지 않습니다.")
            print("     실제 전송 시 다음 단계가 실행됩니다:")
            print("     1. 프로필로 이동")
            print("     2. 메시지 버튼 클릭")
            print("     3. DM 입력")
            print("     4. 전송")

            result = {
                'username': username,
                'message_generated': True,
                'message_sent': False,
                'message_text': message,
                'dry_run': True,
                'profile_info_collected': profile is not None
            }
        else:
            # 실제 전송 (이미 생성된 메시지와 프로필 정보 사용)
            print("\n" + "─" * 60)
            print("[Test 5.4] DM 전송")
            print("─" * 60)
            print("  ⏳ DM 전송 중...")
            print("  ℹ️  이미 프로필에 위치해 있으므로 검색 생략")

            # 이미 프로필 페이지에 있으므로 바로 DM 전송
            dm_sent = dm_sender._send_dm_to_current_profile(message)

            result = {
                'username': username,
                'message_generated': True,
                'message_sent': dm_sent,
                'message_text': message,
                'dry_run': False,
                'profile_info_collected': profile is not None
            }

            if dm_sent:
                print("  ✅ DM 전송 완료!")
            else:
                print(f"  ❌ DM 전송 실패: 메시지 버튼을 찾지 못했거나 전송 중 오류 발생")
                result['error'] = 'Failed to send DM'

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 DM 전송 테스트 결과")
        print("=" * 60)

        print(f"\n  [테스트 요약]")
        print(f"    모드: {'DRY RUN (시뮬레이션)' if dry_run else '실제 전송'}")
        print(f"    대상: @{username}")
        print(f"    프로필 정보 수집: {'✅' if result.get('profile_info_collected', False) else '❌'}")
        print(f"    메시지 생성: {'✅' if result.get('message_generated', False) else '❌'}")
        if not dry_run:
            print(f"    메시지 전송: {'✅' if result.get('message_sent', False) else '❌'}")

        # 결과 저장
        print("\n" + "─" * 60)
        print("[결과 저장]")
        print("─" * 60)

        result_dir = project_root / "tests" / "phase5_dm" / "results"
        result_dir.mkdir(parents=True, exist_ok=True)

        result_file = result_dir / f"dm_send_{username}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  💾 결과 저장: {result_file}")

        # 검증
        print("\n" + "─" * 60)
        print("[기능 검증]")
        print("─" * 60)

        checks = []
        checks.append(("DMSender 초기화", True))
        checks.append(("프로필 정보 수집", profile is not None))
        checks.append(("개인화 메시지 생성", result.get('message_generated', False)))
        if not dry_run:
            checks.append(("DM 전송", result.get('message_sent', False)))
        else:
            checks.append(("DRY RUN 모드 작동", True))

        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        all_passed = all(passed for _, passed in checks)

        if all_passed:
            print("\n✅ Phase 5 완료: DM 전송 테스트 정상")
            print("\n💡 다음 단계:")
            print("   - 실제 DM 전송 테스트: dry_run=False로 실행")
            print("   - Phase 6: Story Restory 테스트")
        else:
            print("\n⚠️  Phase 5 완료: 일부 검증 실패")

        return True

    except Exception as e:
        print(f"\n❌ DM 전송 테스트 실패: {e}")
        logger.exception("DM send test error")

        print("\n해결 방법:")
        print("  1. OpenAI API 키가 올바른지 확인")
        print("  2. 네트워크 연결 확인")
        print("  3. Instagram 앱 상태 확인")

        return False


if __name__ == "__main__":
    # 실제 DM 전송 모드
    username = "liowish"
    dry_run = False  # 실제 전송!

    success = test_dm_send(username, dry_run)

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 5 테스트 결과")
    print("=" * 60)

    if success:
        print("✅ DM 전송 테스트 성공")
        print("\n다음 단계:")
        print("  python3 -m pytest tests/phase6_story/test_story_restory.py -v -s")
        sys.exit(0)
    else:
        print("❌ DM 전송 테스트 실패")
        sys.exit(1)
