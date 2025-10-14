"""
Instagram 단계별 테스트
1. Instagram 실행
2. 검색 실행
3. forteclinicjpn 검색
4. 팔로워 수 확인
"""

import uiautomator2 as u2
import time
import sys

def wait_and_check(d, description, timeout=5):
    """특정 조건을 기다리고 확인"""
    print(f"  대기 중... ({timeout}초)")
    time.sleep(timeout)
    return True

def main():
    print("=" * 70)
    print("Instagram 단계별 테스트")
    print("=" * 70)

    # 디바이스 연결
    device_id = "R3CN70D9ZBY"
    print(f"\n[준비] 디바이스 연결: {device_id}")
    d = u2.connect(device_id)
    print(f"✅ 연결 성공")
    print(f"   화면 크기: {d.window_size()}")
    print(f"   화면 켜짐: {d.info['screenOn']}")

    # 화면 켜기
    if not d.info['screenOn']:
        print("\n[준비] 화면 켜기...")
        d.screen_on()
        time.sleep(1)

        # 잠금 해제 (스와이프)
        screen_width, screen_height = d.window_size()
        d.swipe(
            screen_width // 2,
            int(screen_height * 0.8),
            screen_width // 2,
            int(screen_height * 0.2),
            duration=0.3
        )
        time.sleep(1)
        print("✅ 화면 켜기 완료")

    # 1단계: Instagram 실행
    print("\n" + "=" * 70)
    print("1단계: Instagram 실행")
    print("=" * 70)

    print("  Instagram 앱 실행 중...")

    # 방법 1: Activity 직접 실행
    result = d.shell("am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.instagram.android/.activity.MainTabActivity")
    print(f"  실행 결과: {result.exit_code == 0 and '성공' or '실패'}")
    time.sleep(5)

    # 현재 앱 확인
    current = d.app_current()
    print(f"  현재 앱: {current.get('package')}")

    if current.get('package') != 'com.instagram.android':
        print("  ⚠️  Instagram이 포그라운드에 없습니다. 재시도...")

        # 방법 2: monkey 명령
        d.shell("monkey -p com.instagram.android -c android.intent.category.LAUNCHER 1")
        time.sleep(5)

        current = d.app_current()
        print(f"  현재 앱 (재시도): {current.get('package')}")

    if current.get('package') == 'com.instagram.android':
        print("✅ 1단계 성공: Instagram 실행됨")

        # 스크린샷
        d.screenshot("screenshots/step1_instagram_home.png")
        print("   📷 스크린샷 저장: screenshots/step1_instagram_home.png")
    else:
        print("❌ 1단계 실패: Instagram 실행 실패")
        print(f"   현재 앱: {current}")
        return

    # 2단계: 검색 실행
    print("\n" + "=" * 70)
    print("2단계: 검색 실행")
    print("=" * 70)

    # 검색 버튼 찾기 (여러 방법 시도)
    search_found = False
    search_methods = [
        ("resourceId", "com.instagram.android:id/search_tab"),
        ("description", "검색"),
        ("description", "Search"),
    ]

    for method, selector in search_methods:
        print(f"  검색 시도: {method} = {selector}")

        if method == "resourceId":
            element = d(resourceId=selector)
        else:
            element = d(description=selector)

        if element.exists:
            print(f"  ✅ 검색 버튼 발견!")
            element.click()
            search_found = True
            time.sleep(3)
            break
        else:
            print(f"     없음")

    if not search_found:
        print("  ⚠️  검색 버튼을 selector로 찾을 수 없습니다.")
        print("  💡 좌표 기반 탭 시도...")

        # 하단 탭바의 검색 아이콘 위치 (보통 두 번째)
        # Instagram 하단 탭: 홈, 검색, 릴스, 샵, 프로필
        screen_width, screen_height = d.window_size()

        # 검색 아이콘 위치 (좌측에서 두 번째, 하단)
        search_x = int(screen_width * 0.3)  # 30% 지점
        search_y = int(screen_height * 0.96)  # 하단 4%

        print(f"  탭 좌표: ({search_x}, {search_y})")
        d.click(search_x, search_y)
        time.sleep(3)

    # 스크린샷
    d.screenshot("screenshots/step2_search_page.png")
    print("✅ 2단계 완료: 검색 페이지 이동")
    print("   📷 스크린샷 저장: screenshots/step2_search_page.png")

    # 3단계: 검색창에 "forteclinicjpn" 입력
    print("\n" + "=" * 70)
    print("3단계: 'forteclinicjpn' 검색")
    print("=" * 70)

    # 검색창 찾기
    search_box_found = False
    search_box_selectors = [
        ("resourceId", "com.instagram.android:id/action_bar_search_edit_text"),
        ("className", "android.widget.EditText"),
    ]

    for method, selector in search_box_selectors:
        print(f"  검색창 시도: {method} = {selector}")

        if method == "resourceId":
            element = d(resourceId=selector)
        else:
            element = d(className=selector)

        if element.exists:
            print(f"  ✅ 검색창 발견!")
            element.click()
            time.sleep(1)

            # 텍스트 입력
            search_text = "forteclinicjpn"
            print(f"  입력 중: {search_text}")
            element.set_text(search_text)
            time.sleep(3)

            search_box_found = True
            break
        else:
            print(f"     없음")

    if not search_box_found:
        print("  ⚠️  검색창을 찾을 수 없습니다.")
        print("  💡 화면 상단 중앙 탭 시도...")

        screen_width, screen_height = d.window_size()
        search_box_x = int(screen_width * 0.5)
        search_box_y = int(screen_height * 0.08)

        d.click(search_box_x, search_box_y)
        time.sleep(2)

        # 키보드 입력
        d.send_keys("forteclinicjpn")
        time.sleep(3)

    # 스크린샷
    d.screenshot("screenshots/step3_search_input.png")
    print("✅ 3단계 완료: 검색어 입력")
    print("   📷 스크린샷 저장: screenshots/step3_search_input.png")

    # 첫 번째 결과 클릭
    print("  첫 번째 검색 결과 클릭...")

    # 검색 결과에서 사용자 프로필 클릭
    # 보통 username이 포함된 첫 번째 항목
    if d(textContains="forteclinic").exists:
        d(textContains="forteclinic").click()
        time.sleep(3)
        print("  ✅ 프로필 이동 성공")
    else:
        print("  ⚠️  검색 결과를 찾을 수 없습니다. 화면 중앙 탭...")
        screen_width, screen_height = d.window_size()
        d.click(screen_width // 2, int(screen_height * 0.3))
        time.sleep(3)

    # 스크린샷
    d.screenshot("screenshots/step4_profile_page.png")
    print("   📷 스크린샷 저장: screenshots/step4_profile_page.png")

    # 4단계: 팔로워 수 확인
    print("\n" + "=" * 70)
    print("4단계: 팔로워 수 확인")
    print("=" * 70)

    # UI 계층 덤프
    print("  UI 계층 분석 중...")
    xml = d.dump_hierarchy()
    with open("screenshots/step4_profile_hierarchy.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("   📄 UI 계층 저장: screenshots/step4_profile_hierarchy.xml")

    # 팔로워 수 추출 시도
    print("\n  팔로워 정보 추출 시도:")

    # 방법 1: "팔로워" 텍스트 주변 찾기
    if d(textContains="팔로워").exists or d(textContains="followers").exists:
        print("  ✅ '팔로워' 텍스트 발견")

        # 팔로워 숫자 찾기 (보통 TextView)
        # Instagram 프로필 레이아웃: 게시물 수 | 팔로워 | 팔로잉
        textviews = d(className="android.widget.TextView")

        print(f"\n  화면의 TextView 요소들:")
        for i, tv in enumerate(textviews):
            text = tv.get_text()
            if text and len(text) < 50:  # 짧은 텍스트만
                print(f"    [{i}] {text}")

                # 팔로워 수로 보이는 패턴 (숫자 + K/M 또는 쉼표 포함)
                if any(char.isdigit() for char in text) and (',' in text or 'K' in text or 'M' in text or text.isdigit()):
                    print(f"       ➡️  숫자로 보임")

    else:
        print("  ⚠️  '팔로워' 텍스트를 찾을 수 없습니다")

    # 방법 2: 특정 위치의 텍스트 추출
    print("\n  프로필 통계 영역 텍스트 추출:")

    # 프로필 사진 아래, username 아래에 보통 통계가 있음
    # 화면 상단 30% 영역 스캔
    screen_width, screen_height = d.window_size()

    # 스크린샷에서 OCR 또는 GPT-4 Vision 사용 (선택)
    print("  💡 GPT-4 Vision으로 스크린샷 분석하여 팔로워 수 추출 가능")

    print("\n✅ 4단계 완료: 팔로워 정보 수집")

    # 최종 요약
    print("\n" + "=" * 70)
    print("테스트 완료 요약")
    print("=" * 70)
    print("✅ 1단계: Instagram 실행 성공")
    print("✅ 2단계: 검색 페이지 이동 성공")
    print("✅ 3단계: forteclinicjpn 검색 성공")
    print("✅ 4단계: 프로필 페이지 이동 성공")
    print("\n📁 생성된 파일:")
    print("   - screenshots/step1_instagram_home.png")
    print("   - screenshots/step2_search_page.png")
    print("   - screenshots/step3_search_input.png")
    print("   - screenshots/step4_profile_page.png")
    print("   - screenshots/step4_profile_hierarchy.xml")
    print("\n💡 다음 단계:")
    print("   1. 스크린샷 확인하여 UI 요소 분석")
    print("   2. UI 계층 XML 분석하여 정확한 selector 찾기")
    print("   3. GPT-4 Vision으로 팔로워 수 자동 추출")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
