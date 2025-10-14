#!/usr/bin/env python3
"""
Phase 1.1: Device Connection Test
목적: ADB 연결 및 디바이스 인식 확인
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger


def test_adb_connection():
    """ADB 연결 테스트"""
    print("=" * 60)
    print("Phase 1.1: ADB 디바이스 연결 테스트")
    print("=" * 60)

    try:
        # ADB devices 실행
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("\n[ADB Devices 출력]")
        print(result.stdout)

        # 연결된 디바이스 파싱
        lines = result.stdout.strip().split('\n')
        devices = [line.split('\t')[0] for line in lines[1:] if '\tdevice' in line]

        if not devices:
            print("❌ 연결된 디바이스가 없습니다.")
            print("\n해결 방법:")
            print("  1. USB 케이블 연결 확인")
            print("  2. 개발자 옵션 → USB 디버깅 활성화")
            print("  3. 'adb devices' 실행 후 디바이스에서 승인")
            return False

        print(f"✅ 연결된 디바이스: {devices}")

        # 첫 번째 디바이스 정보 확인
        device_id = devices[0]
        print(f"\n[디바이스 정보: {device_id}]")

        # 디바이스 모델명
        model_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  모델명: {model_result.stdout.strip()}")

        # Android 버전
        version_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  Android 버전: {version_result.stdout.strip()}")

        # 화면 해상도
        resolution_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "wm", "size"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  화면 해상도: {resolution_result.stdout.strip()}")

        print("\n✅ Phase 1.1 완료: 디바이스 연결 정상")
        return True

    except FileNotFoundError:
        print("❌ ADB가 설치되지 않았습니다.")
        print("\n해결 방법:")
        print("  macOS: brew install android-platform-tools")
        print("  Linux: sudo apt-get install adb")
        return False

    except subprocess.TimeoutExpired:
        print("❌ ADB 명령 실행 시간 초과")
        return False

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        logger.exception("Device connection error")
        return False


def test_uiautomator2_service():
    """UIAutomator2 서비스 확인"""
    print("\n" + "=" * 60)
    print("Phase 1.2: UIAutomator2 서비스 확인")
    print("=" * 60)

    try:
        # 연결된 디바이스 가져오기
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

        lines = result.stdout.strip().split('\n')
        devices = [line.split('\t')[0] for line in lines[1:] if '\tdevice' in line]

        if not devices:
            print("❌ 연결된 디바이스가 없습니다.")
            return False

        device_id = devices[0]

        # UIAutomator2 서비스 확인 (ATX agent)
        print(f"\n[UIAutomator2 서비스 확인]")
        service_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "pm", "list", "packages", "|", "grep", "atx"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )

        if "com.github.uiautomator" in service_result.stdout:
            print("✅ UIAutomator2 서비스가 설치되어 있습니다.")
            print(f"  {service_result.stdout.strip()}")
        else:
            print("⚠️  UIAutomator2 서비스가 설치되지 않았습니다.")
            print("\n자동으로 UIAutomator2 초기화를 시작합니다...")

            print("\nUIAutomator2 초기화 중...")
            init_result = subprocess.run(
                ["python3", "-m", "uiautomator2", "init"],
                capture_output=True,
                text=True,
                timeout=120
            )
            print(init_result.stdout)
            if init_result.stderr:
                print(init_result.stderr)

            if init_result.returncode == 0:
                print("✅ UIAutomator2 초기화 완료")
            else:
                print("❌ UIAutomator2 초기화 실패")
                print("\n수동으로 초기화하세요:")
                print("  python3 -m uiautomator2 init")
                return False

        print("\n✅ Phase 1.2 완료: UIAutomator2 서비스 정상")
        return True

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        logger.exception("UIAutomator2 service check error")
        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("Phase 1: Infrastructure Tests")
    print("🚀" * 30 + "\n")

    # Test 1.1: ADB Connection
    success_1 = test_adb_connection()

    # Test 1.2: UIAutomator2 Service
    success_2 = test_uiautomator2_service()

    # 최종 결과
    print("\n" + "=" * 60)
    print("Phase 1 테스트 결과")
    print("=" * 60)
    print(f"  1.1 ADB 연결: {'✅ 성공' if success_1 else '❌ 실패'}")
    print(f"  1.2 UIAutomator2: {'✅ 성공' if success_2 else '❌ 실패'}")

    if success_1 and success_2:
        print("\n🎉 Phase 1 완료! Phase 2로 진행하세요.")
        print("   실행 명령: python3 tests/phase2_navigation/test_tab_navigation.py")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 실패. 위의 해결 방법을 참고하여 문제를 해결하세요.")
        sys.exit(1)
