"""
통합 테스트: Instagram 프로필 정보 추출

테스트 시나리오:
1. Instagram 실행
2. 'liowish' 검색
3. 프로필 정보 추출 (GPT-4 Vision)
4. 팔로워 수 및 모든 정보 확인
5. JSON 파일로 저장
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.instagram_core import (
    DeviceManager,
    TabNavigator,
    SearchNavigator,
    ProfileExtractor
)


def test_profile_extraction():
    """프로필 정보 추출 통합 테스트"""

    print("=" * 70)
    print("Instagram 프로필 정보 추출 통합 테스트")
    print("=" * 70)

    device = None
    results = {
        "test_time": datetime.now().isoformat(),
        "device_id": "R3CN70D9ZBY",
        "target_username": "liowish",
        "steps": {},
        "profile_data": None,
        "success": False,
        "error": None
    }

    try:
        # Step 1: 디바이스 연결
        print("\n[Step 1] 디바이스 연결 중...")
        device = DeviceManager("R3CN70D9ZBY", screenshots_dir="test_screenshots")

        if not device.connect():
            raise Exception("디바이스 연결 실패")

        results["steps"]["device_connection"] = {
            "status": "success",
            "screen_size": device.get_screen_size()
        }
        print(f"✅ 디바이스 연결 성공 (화면 크기: {device.get_screen_size()})")

        # Step 2: 화면 준비
        print("\n[Step 2] 화면 준비 중...")
        if not device.prepare_screen():
            raise Exception("화면 준비 실패")

        results["steps"]["screen_preparation"] = {"status": "success"}
        print("✅ 화면 준비 완료")

        # Step 3: Instagram 실행
        print("\n[Step 3] Instagram 실행 중...")
        if not device.launch_instagram():
            raise Exception("Instagram 실행 실패")

        results["steps"]["instagram_launch"] = {"status": "success"}
        print("✅ Instagram 실행 성공")

        time.sleep(3)  # 앱 완전 로딩 대기

        # Step 4: 검색 탭 이동
        print("\n[Step 4] 검색 탭으로 이동 중...")
        tab_nav = TabNavigator(device)

        if not tab_nav.goto_search():
            raise Exception("검색 탭 이동 실패")

        results["steps"]["search_tab_navigation"] = {"status": "success"}
        print("✅ 검색 탭 이동 완료")

        # Step 5: 사용자 검색
        print("\n[Step 5] 'liowish' 검색 중...")
        search_nav = SearchNavigator(device, tab_nav)

        if not search_nav.search_username("liowish"):
            raise Exception("사용자명 검색 실패")

        results["steps"]["username_search"] = {
            "status": "success",
            "query": "liowish"
        }
        print("✅ 'liowish' 검색 완료")

        # Step 6: 첫 번째 결과 클릭
        print("\n[Step 6] 검색 결과 클릭 중...")
        if not search_nav.click_first_result():
            raise Exception("검색 결과 클릭 실패")

        results["steps"]["profile_navigation"] = {"status": "success"}
        print("✅ 프로필 페이지 이동 완료")

        time.sleep(3)  # 프로필 페이지 로딩 대기

        # Step 7: 프로필 정보 추출 (GPT-4 Vision)
        print("\n[Step 7] 프로필 정보 추출 중 (GPT-4 Vision)...")
        profile_extractor = ProfileExtractor(device)

        profile_data = profile_extractor.extract_profile_info(save_screenshot=True)

        if not profile_data:
            raise Exception("프로필 정보 추출 실패")

        results["steps"]["profile_extraction"] = {
            "status": "success",
            "method": "GPT-4 Vision (gpt-4o)"
        }
        results["profile_data"] = profile_data
        results["success"] = True

        # Step 8: 결과 출력
        print("\n" + "=" * 70)
        print("📊 추출된 프로필 정보")
        print("=" * 70)
        print(f"사용자명: @{profile_data.get('username', 'N/A')}")
        print(f"전체 이름: {profile_data.get('fullname', 'N/A')}")
        print(f"팔로워 수: {profile_data.get('follower_count', 'N/A')}")
        print(f"팔로잉 수: {profile_data.get('following_count', 'N/A')}")
        print(f"게시물 수: {profile_data.get('post_count', 'N/A')}")
        print(f"인증 배지: {'✅' if profile_data.get('is_verified') else '❌'}")
        print(f"비공개 계정: {'✅' if profile_data.get('is_private') else '❌'}")
        print(f"비즈니스 계정: {'✅' if profile_data.get('is_business') else '❌'}")

        if profile_data.get('bio'):
            print(f"\n자기소개:")
            print(f"  {profile_data['bio']}")

        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        results["success"] = False
        results["error"] = str(e)

        import traceback
        traceback.print_exc()

    finally:
        # Step 9: 결과 저장
        print("\n[Step 9] 결과 저장 중...")
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"profile_extraction_test_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"✅ 결과 저장: {output_file}")

        # 최종 상태
        print("\n" + "=" * 70)
        if results["success"]:
            print("✅ 테스트 성공!")
        else:
            print("❌ 테스트 실패")
        print("=" * 70)

        return results


if __name__ == "__main__":
    result = test_profile_extraction()

    # 종료 코드 반환
    sys.exit(0 if result["success"] else 1)
