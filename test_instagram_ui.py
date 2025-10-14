"""
Instagram UI 탐색 테스트
실제 디바이스에서 Instagram 화면 요소를 찾아봅니다.
"""

import uiautomator2 as u2
import time

print("=" * 60)
print("Instagram UI 탐색 테스트")
print("=" * 60)

# 디바이스 연결
device_id = "R3CN70D9ZBY"
d = u2.connect(device_id)
print(f"✅ 디바이스 연결 성공")

# Instagram으로 전환
print("\n[1] Instagram 앱으로 전환...")
d.shell("am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.instagram.android/.activity.MainTabActivity")
time.sleep(3)

# 현재 앱 확인
current = d.app_current()
print(f"현재 앱: {current.get('package')}")

if current.get('package') == 'com.instagram.android':
    print("✅ Instagram이 포그라운드에 있습니다!")

    # UI 요소 찾기
    print("\n[2] UI 요소 탐색...")

    # 검색 버튼
    search_methods = [
        ("resourceId", f"com.instagram.android:id/search_tab"),
        ("description (검색)", "검색"),
        ("description (Search)", "Search"),
        ("text (검색)", "검색"),
        ("text (Search)", "Search")
    ]

    print("\n검색 버튼 찾기:")
    for method, selector in search_methods:
        if method.startswith("resourceId"):
            exists = d(resourceId=selector).exists
        elif method.startswith("description"):
            exists = d(description=selector).exists
        else:
            exists = d(text=selector).exists

        print(f"  {method}: {'✅ 발견!' if exists else '❌ 없음'}")

    # 하단 탭 바 요소들
    print("\n하단 탭 바 요소:")
    tab_ids = [
        "feed_tab",  # 홈
        "search_tab",  # 검색
        "clips_tab",  # 릴스
        "igtv_tab",  # IGTV
        "profile_tab"  # 프로필
    ]

    for tab_id in tab_ids:
        full_id = f"com.instagram.android:id/{tab_id}"
        exists = d(resourceId=full_id).exists
        print(f"  {tab_id}: {'✅ 발견!' if exists else '❌ 없음'}")

    # 스크린샷 촬영
    print("\n[3] 스크린샷 촬영...")
    d.screenshot("screenshots/instagram_current.png")
    print("✅ 스크린샷 저장: screenshots/instagram_current.png")

    # UI 계층 덤프
    print("\n[4] UI 계층 덤프 저장...")
    xml = d.dump_hierarchy()
    with open("screenshots/instagram_hierarchy.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("✅ UI 계층 저장: screenshots/instagram_hierarchy.xml")

else:
    print(f"❌ Instagram이 포그라운드에 없습니다. 현재: {current.get('package')}")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
