"""
간단한 디바이스 연결 및 Instagram 실행 테스트
"""

import uiautomator2 as u2
import time

print("=" * 60)
print("디바이스 연결 테스트")
print("=" * 60)

# 디바이스 연결
device_id = "R3CN70D9ZBY"
print(f"\n[1] 디바이스 연결 중: {device_id}")
d = u2.connect(device_id)
print(f"✅ 연결 성공!")
print(f"디바이스 정보: {d.info}")

# Instagram 실행
print("\n[2] Instagram 실행...")
result = d.shell("monkey -p com.instagram.android -c android.intent.category.LAUNCHER 1")
print(f"실행 결과: {result}")

time.sleep(5)

# 현재 앱 확인
current = d.app_current()
print(f"\n[3] 현재 실행 중인 앱: {current}")

if current.get('package') == 'com.instagram.android':
    print("✅ Instagram이 실행 중입니다!")

    # 화면 덤프 확인
    print("\n[4] 화면 UI 요소 확인...")
    xml = d.dump_hierarchy()
    print(f"UI 계층 구조 길이: {len(xml)} 문자")

    # 검색 버튼 찾기
    if d(descriptionContains="검색").exists or d(descriptionContains="Search").exists:
        print("✅ 검색 버튼 발견!")
    else:
        print("⚠️  검색 버튼을 찾을 수 없습니다")

else:
    print(f"❌ Instagram이 실행되지 않았습니다. 현재 앱: {current.get('package')}")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
