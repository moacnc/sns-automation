#!/usr/bin/env python3
"""
Coordinate Capture Tool

사용법:
1. 스크립트 실행
2. 요청받은 UI 요소를 디바이스에서 터치
3. 터치한 좌표가 자동으로 출력됨
"""

import subprocess
import re
import time

def capture_touch_coordinates(element_name: str, timeout: int = 10) -> tuple:
    """
    터치 이벤트를 캡처하여 좌표 반환

    Args:
        element_name: 캡처할 요소 이름 (로깅용)
        timeout: 대기 시간 (초)

    Returns:
        (x, y) 좌표 tuple
    """
    print(f"\n{'='*60}")
    print(f"📍 {element_name} 캡처 대기 중...")
    print(f"{'='*60}")
    print(f"\n👉 디바이스에서 [{element_name}]를 터치해주세요!")
    print(f"   ({timeout}초 동안 대기합니다...)\n")

    # Clear existing getevent buffer
    subprocess.run(
        ["adb", "shell", "getevent", "-c", "1"],
        capture_output=True,
        timeout=1
    )

    # Start capturing touch events
    start_time = time.time()
    process = subprocess.Popen(
        ["adb", "shell", "getevent"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    x_coord = None
    y_coord = None

    try:
        for line in process.stdout:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"⚠️  타임아웃: {timeout}초 내에 터치가 감지되지 않았습니다.")
                break

            # Parse touch event
            # Format: /dev/input/eventX XXXX XXXX XXXXXXXX
            if "ABS_MT_POSITION_X" in line or "0035" in line:
                # Extract hex value and convert to decimal
                match = re.search(r'([0-9a-f]{8})$', line.strip())
                if match:
                    x_coord = int(match.group(1), 16)
                    print(f"   X 좌표 캡처: {x_coord}")

            elif "ABS_MT_POSITION_Y" in line or "0036" in line:
                match = re.search(r'([0-9a-f]{8})$', line.strip())
                if match:
                    y_coord = int(match.group(1), 16)
                    print(f"   Y 좌표 캡처: {y_coord}")

            # If both coordinates captured, we're done
            if x_coord is not None and y_coord is not None:
                break

    finally:
        process.terminate()
        process.wait()

    if x_coord is None or y_coord is None:
        print(f"❌ 좌표 캡처 실패")
        return None

    print(f"\n✅ 캡처 완료: ({x_coord}, {y_coord})")
    return (x_coord, y_coord)


def main():
    """Main coordinate capture workflow"""

    print("\n" + "="*60)
    print("Instagram Navigation Coordinate Capture")
    print("="*60)

    # Get device info
    result = subprocess.run(
        ["adb", "shell", "wm", "size"],
        capture_output=True,
        text=True
    )
    print(f"\n📱 Device: {result.stdout.strip()}")

    # Check if Instagram is running
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "window", "|", "grep", "mCurrentFocus"],
        capture_output=True,
        text=True,
        shell=True
    )
    print(f"📱 Current App: {result.stdout.strip()}")

    print("\n⚠️  Instagram이 실행되어 있고 메인 화면에 있는지 확인해주세요!")
    input("\n준비되면 Enter를 눌러주세요...")

    # Capture coordinates for each tab
    coordinates = {}

    tabs = [
        ("Home Tab", "홈 탭"),
        ("Search Tab", "검색 탭"),
        ("Create Tab", "만들기 탭"),
        ("Reels Tab", "릴스 탭"),
        ("Profile Tab", "프로필 탭")
    ]

    for tab_id, tab_name in tabs:
        coords = capture_touch_coordinates(tab_name, timeout=15)
        if coords:
            coordinates[tab_id] = coords

        print("\n" + "-"*60)
        cont = input(f"\n다음 요소로 계속하시겠습니까? (y/n): ")
        if cont.lower() != 'y':
            break

    # Print summary
    print("\n" + "="*60)
    print("📊 캡처된 좌표 요약")
    print("="*60)

    for tab_id, coords in coordinates.items():
        print(f"\n{tab_id}:")
        print(f"  좌표: {coords}")

    # Generate code snippet
    print("\n" + "="*60)
    print("📝 코드 스니펫 (navigation.py에 사용)")
    print("="*60)
    print("\n```python")
    print("# Tab coordinates (captured from actual device)")
    print("TAB_COORDINATES = {")
    for tab_id, coords in coordinates.items():
        print(f"    '{tab_id}': {coords},")
    print("}")
    print("```")


if __name__ == "__main__":
    main()
