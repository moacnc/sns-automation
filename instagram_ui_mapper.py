"""
Instagram UI Mapper - 전체 UI 요소 매핑 및 테스트

이 스크립트는 Instagram의 모든 주요 UI 요소를 자동으로 탐색하고,
각 요소의 정보를 수집하여 문서화합니다.

수집 정보:
- resourceId
- className
- text
- description
- 좌표 (bounds)
- 스크린샷
- UI 계층 구조 (XML)
"""

import uiautomator2 as u2
import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class InstagramUIMapper:
    """Instagram UI 요소 자동 매핑"""

    def __init__(self, device_id: str, output_dir: str = "ui_mapping"):
        self.device_id = device_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.device = None
        self.package = "com.instagram.android"
        self.mapping_data = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "instagram_version": None,
            "elements": {}
        }

    def connect(self):
        """디바이스 연결"""
        print(f"디바이스 연결 중: {self.device_id}")
        self.device = u2.connect(self.device_id)
        print(f"✅ 연결 성공")
        print(f"   화면 크기: {self.device.window_size()}")

    def prepare_device(self):
        """디바이스 준비 (화면 켜기, 잠금 해제)"""
        print("\n화면 준비 중...")

        # 화면 켜기
        if not self.device.info['screenOn']:
            self.device.screen_on()
            time.sleep(1)

            # 잠금 해제 (스와이프)
            w, h = self.device.window_size()
            self.device.swipe(w // 2, int(h * 0.8), w // 2, int(h * 0.2), duration=0.3)
            time.sleep(1)

        print("✅ 화면 준비 완료")

    def launch_instagram(self) -> bool:
        """Instagram 실행"""
        print("\nInstagram 실행 중...")

        # Activity 직접 실행
        self.device.shell(
            "am start -a android.intent.action.MAIN "
            "-c android.intent.category.LAUNCHER "
            "-n com.instagram.android/.activity.MainTabActivity"
        )
        time.sleep(5)

        # 확인
        current = self.device.app_current()
        if current.get('package') == self.package:
            print("✅ Instagram 실행 성공")

            # 버전 정보 추출
            try:
                version_info = self.device.shell(
                    f"dumpsys package {self.package} | grep versionName"
                ).output
                if "versionName" in version_info:
                    version = version_info.split("versionName=")[1].split()[0]
                    self.mapping_data['instagram_version'] = version
                    print(f"   Instagram 버전: {version}")
            except:
                pass

            return True
        else:
            print(f"❌ 실행 실패. 현재 앱: {current.get('package')}")
            return False

    def capture_screen(self, name: str, description: str = ""):
        """화면 캡처 및 UI 계층 덤프"""
        # 스크린샷
        screenshot_path = self.output_dir / f"{name}.png"
        self.device.screenshot(str(screenshot_path))

        # UI 계층
        xml_path = self.output_dir / f"{name}.xml"
        xml = self.device.dump_hierarchy()
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml)

        print(f"   📷 {name}.png")
        print(f"   📄 {name}.xml")

        return str(screenshot_path), str(xml_path)

    def find_elements(self, description: str, **selectors) -> List[Dict]:
        """UI 요소 찾기 및 정보 수집"""
        found_elements = []

        for selector_name, selector_value in selectors.items():
            try:
                if selector_name == "resourceId":
                    elements = self.device(resourceId=selector_value)
                elif selector_name == "text":
                    elements = self.device(text=selector_value)
                elif selector_name == "textContains":
                    elements = self.device(textContains=selector_value)
                elif selector_name == "description":
                    elements = self.device(description=selector_value)
                elif selector_name == "className":
                    elements = self.device(className=selector_value)
                else:
                    continue

                if elements.exists:
                    info = elements.info
                    found_elements.append({
                        "selector_type": selector_name,
                        "selector_value": selector_value,
                        "found": True,
                        "info": info
                    })
                else:
                    found_elements.append({
                        "selector_type": selector_name,
                        "selector_value": selector_value,
                        "found": False
                    })
            except Exception as e:
                found_elements.append({
                    "selector_type": selector_name,
                    "selector_value": selector_value,
                    "found": False,
                    "error": str(e)
                })

        return found_elements

    def map_bottom_tab_bar(self):
        """하단 탭 바 매핑"""
        print("\n" + "=" * 70)
        print("1. 하단 탭 바 (Bottom Tab Bar)")
        print("=" * 70)

        # 홈으로 이동 (혹시 다른 화면에 있을 경우)
        self.device.press("back")
        self.device.press("back")
        time.sleep(2)

        screenshot, xml = self.capture_screen("01_bottom_tab_bar", "하단 탭 바")

        # 각 탭 버튼 찾기
        tabs = {
            "home": {
                "resourceId": f"{self.package}:id/feed_tab",
                "description": "홈",
                "description_en": "Home"
            },
            "search": {
                "resourceId": f"{self.package}:id/search_tab",
                "description": "검색",
                "description_en": "Search"
            },
            "reels": {
                "resourceId": f"{self.package}:id/clips_tab",
                "description": "릴스",
                "description_en": "Reels"
            },
            "profile": {
                "resourceId": f"{self.package}:id/profile_tab",
                "description": "프로필",
                "description_en": "Profile"
            }
        }

        tab_results = {}
        for tab_name, selectors in tabs.items():
            print(f"\n[{tab_name.upper()}] 탭 찾기...")
            elements = self.find_elements(tab_name, **selectors)

            for elem in elements:
                if elem['found']:
                    print(f"   ✅ {elem['selector_type']}: {elem['selector_value']}")
                    tab_results[tab_name] = elem
                    break
            else:
                print(f"   ❌ {tab_name} 탭을 찾을 수 없습니다")

        self.mapping_data['elements']['bottom_tab_bar'] = {
            "screenshot": screenshot,
            "xml": xml,
            "tabs": tab_results
        }

    def map_search_page(self):
        """검색 페이지 매핑"""
        print("\n" + "=" * 70)
        print("2. 검색 페이지 (Search)")
        print("=" * 70)

        # 검색 탭 클릭
        print("\n검색 탭 클릭...")

        # 좌표 기반 탭 (하단 좌측에서 두 번째)
        w, h = self.device.window_size()
        search_x = int(w * 0.3)
        search_y = int(h * 0.96)

        self.device.click(search_x, search_y)
        time.sleep(3)

        screenshot, xml = self.capture_screen("02_search_page", "검색 페이지")

        # 검색창 찾기
        print("\n검색창 찾기...")
        search_box_selectors = {
            "resourceId": f"{self.package}:id/action_bar_search_edit_text",
            "className": "android.widget.EditText"
        }

        search_box_results = self.find_elements("search_box", **search_box_selectors)

        for elem in search_box_results:
            if elem['found']:
                print(f"   ✅ {elem['selector_type']}: {elem['selector_value']}")

        self.mapping_data['elements']['search_page'] = {
            "screenshot": screenshot,
            "xml": xml,
            "search_box": search_box_results,
            "tab_coordinates": {"x": search_x, "y": search_y}
        }

    def map_search_input(self):
        """검색어 입력 및 결과"""
        print("\n" + "=" * 70)
        print("3. 검색어 입력 (Search Input)")
        print("=" * 70)

        # 검색창 클릭 (화면 상단 중앙)
        w, h = self.device.window_size()
        search_box_x = int(w * 0.5)
        search_box_y = int(h * 0.08)

        print(f"\n검색창 클릭 ({search_box_x}, {search_box_y})...")
        self.device.click(search_box_x, search_box_y)
        time.sleep(2)

        # 텍스트 입력 (ADB 방식)
        test_query = "forteclinicjpn"
        print(f"\n텍스트 입력: {test_query}")

        # ADB shell input text (안전)
        self.device.shell(f"input text {test_query}")
        time.sleep(3)

        screenshot, xml = self.capture_screen("03_search_input", f"검색어 입력: {test_query}")

        # 검색 결과 요소 찾기
        print("\n검색 결과 요소 찾기...")
        result_selectors = {
            "textContains": "forteclinic"
        }

        result_elements = self.find_elements("search_results", **result_selectors)

        for elem in result_elements:
            if elem['found']:
                print(f"   ✅ 검색 결과 발견")

        self.mapping_data['elements']['search_input'] = {
            "screenshot": screenshot,
            "xml": xml,
            "query": test_query,
            "input_method": "adb_shell",
            "results": result_elements
        }

    def map_profile_page(self):
        """프로필 페이지 매핑"""
        print("\n" + "=" * 70)
        print("4. 프로필 페이지 (Profile)")
        print("=" * 70)

        # 첫 번째 검색 결과 클릭
        print("\n첫 번째 검색 결과 클릭...")

        # 화면 중앙 상단 탭 (검색 결과 첫 번째 항목)
        w, h = self.device.window_size()
        first_result_x = int(w * 0.5)
        first_result_y = int(h * 0.3)

        self.device.click(first_result_x, first_result_y)
        time.sleep(4)

        screenshot, xml = self.capture_screen("04_profile_page", "프로필 페이지")

        # 프로필 정보 추출
        print("\n프로필 요소 찾기...")

        # TextView 요소들 스캔 (username, fullname, bio, stats)
        textviews = self.device(className="android.widget.TextView")

        profile_texts = []
        print("\n   발견된 텍스트 요소:")
        for i, tv in enumerate(textviews):
            try:
                text = tv.get_text()
                if text and len(text) < 100:  # 짧은 텍스트만
                    info = tv.info
                    profile_texts.append({
                        "index": i,
                        "text": text,
                        "bounds": info.get('bounds')
                    })
                    print(f"   [{i}] {text}")
            except:
                pass

        # 팔로워/팔로잉 버튼 찾기
        follower_selectors = {
            "textContains": "팔로워",
            "textContains_en": "followers"
        }

        follower_elements = self.find_elements("followers", **follower_selectors)

        self.mapping_data['elements']['profile_page'] = {
            "screenshot": screenshot,
            "xml": xml,
            "text_elements": profile_texts,
            "follower_elements": follower_elements
        }

    def map_story_viewer(self):
        """스토리 뷰어 매핑 (가능한 경우)"""
        print("\n" + "=" * 70)
        print("5. 스토리 뷰어 (Story Viewer) - 선택적")
        print("=" * 70)

        # 프로필 페이지에서 스토리 링이 있는지 확인
        # 있으면 클릭하여 스토리 뷰어 진입

        # 여기서는 스킵 (실제 스토리가 없을 수 있음)
        print("   ⚠️  스토리 매핑은 실제 스토리가 있을 때 수행합니다")
        print("   💡 수동으로 스토리를 열고 UI 계층을 덤프하여 분석하세요")

    def save_mapping_data(self):
        """매핑 데이터 저장"""
        output_file = self.output_dir / "mapping_data.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.mapping_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 매핑 데이터 저장: {output_file}")

    def generate_report(self):
        """매핑 결과 리포트 생성"""
        report_file = self.output_dir / "MAPPING_REPORT.md"

        report = f"""# Instagram UI Mapping Report

**생성 시각**: {self.mapping_data['timestamp']}
**디바이스**: {self.device_id}
**Instagram 버전**: {self.mapping_data.get('instagram_version', 'Unknown')}

---

## 수집된 데이터

"""

        for section, data in self.mapping_data['elements'].items():
            report += f"\n### {section}\n\n"
            report += f"- 📷 스크린샷: `{data.get('screenshot', 'N/A')}`\n"
            report += f"- 📄 UI 계층: `{data.get('xml', 'N/A')}`\n"

            if 'tabs' in data:
                report += "\n**탭 정보:**\n\n"
                for tab_name, tab_info in data['tabs'].items():
                    if tab_info:
                        report += f"- **{tab_name}**: {tab_info.get('selector_type')} = `{tab_info.get('selector_value')}`\n"

            if 'text_elements' in data:
                report += f"\n**발견된 텍스트 요소**: {len(data['text_elements'])}개\n"

        report += f"\n---\n\n## 파일 목록\n\n"

        for file in sorted(self.output_dir.iterdir()):
            if file.is_file():
                report += f"- `{file.name}`\n"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 리포트 생성: {report_file}")

    def run(self):
        """전체 매핑 실행"""
        print("=" * 70)
        print("Instagram UI Mapper")
        print("=" * 70)

        try:
            self.connect()
            self.prepare_device()

            if not self.launch_instagram():
                print("\n❌ Instagram 실행 실패. 종료합니다.")
                return

            # 각 영역 매핑
            self.map_bottom_tab_bar()
            self.map_search_page()
            self.map_search_input()
            self.map_profile_page()
            # self.map_story_viewer()  # 선택적

            # 결과 저장
            self.save_mapping_data()
            self.generate_report()

            print("\n" + "=" * 70)
            print("✅ UI 매핑 완료!")
            print("=" * 70)
            print(f"\n출력 디렉토리: {self.output_dir}")
            print("\n다음 단계:")
            print("1. 생성된 스크린샷 확인")
            print("2. UI 계층 XML 파일 분석")
            print("3. mapping_data.json 확인")
            print("4. MAPPING_REPORT.md 읽기")

        except KeyboardInterrupt:
            print("\n\n⚠️  사용자가 중단했습니다.")
        except Exception as e:
            print(f"\n\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    mapper = InstagramUIMapper(
        device_id="R3CN70D9ZBY",
        output_dir="ui_mapping"
    )
    mapper.run()
