"""
Instagram UI Mapper - Simplified (Coordinate-based)

UIAutomator2 dump_hierarchy()의 NullPointerException 문제를 우회하여,
좌표 기반 상호작용과 스크린샷만으로 UI 매핑을 수행합니다.

수집 정보:
- 스크린샷
- 화면 크기 및 주요 영역 좌표
- 텍스트 요소 (find_elements로 찾을 수 있는 것만)
- 각 단계별 상호작용 결과
"""

import uiautomator2 as u2
import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class InstagramUIMapperSimple:
    """Instagram UI 요소 간편 매핑 (좌표 기반)"""

    def __init__(self, device_id: str, output_dir: str = "ui_mapping_simple"):
        self.device_id = device_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.device = None
        self.package = "com.instagram.android"
        self.mapping_data = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "instagram_version": None,
            "screen_size": None,
            "elements": {}
        }

    def connect(self):
        """디바이스 연결"""
        print(f"디바이스 연결 중: {self.device_id}")
        self.device = u2.connect(self.device_id)

        # 화면 크기 저장
        w, h = self.device.window_size()
        self.mapping_data['screen_size'] = {"width": w, "height": h}

        print(f"✅ 연결 성공")
        print(f"   화면 크기: {w} x {h}")

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

        # monkey 명령으로 앱 실행
        self.device.shell(
            f"monkey -p {self.package} -c android.intent.category.LAUNCHER 1"
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

    def capture_screenshot(self, name: str, description: str = "") -> str:
        """스크린샷만 캡처 (XML 덤프 없음)"""
        screenshot_path = self.output_dir / f"{name}.png"
        self.device.screenshot(str(screenshot_path))

        print(f"   📷 {name}.png - {description}")
        return str(screenshot_path)

    def find_text_elements(self, **selectors) -> List[Dict]:
        """텍스트 요소 찾기 (dump_hierarchy 없이)"""
        found_elements = []

        for selector_name, selector_value in selectors.items():
            try:
                if selector_name == "resourceId":
                    elem = self.device(resourceId=selector_value)
                elif selector_name == "text":
                    elem = self.device(text=selector_value)
                elif selector_name == "textContains":
                    elem = self.device(textContains=selector_value)
                elif selector_name == "description":
                    elem = self.device(description=selector_value)
                elif selector_name == "className":
                    elem = self.device(className=selector_value)
                else:
                    continue

                if elem.exists:
                    info = elem.info
                    found_elements.append({
                        "selector_type": selector_name,
                        "selector_value": selector_value,
                        "found": True,
                        "text": info.get('text', ''),
                        "bounds": info.get('bounds', {}),
                        "className": info.get('className', '')
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

    def extract_all_text_elements(self) -> List[str]:
        """화면에 표시된 모든 텍스트 추출"""
        texts = []
        try:
            # TextView 요소들 찾기
            textviews = self.device(className="android.widget.TextView")
            count = textviews.count

            for i in range(min(count, 50)):  # 최대 50개까지만
                try:
                    tv = textviews[i]
                    text = tv.get_text()
                    if text and len(text) < 200:  # 긴 텍스트 제외
                        texts.append(text)
                except:
                    pass
        except Exception as e:
            print(f"   ⚠️  텍스트 추출 오류: {e}")

        return texts

    def map_home_screen(self):
        """홈 화면 매핑"""
        print("\n" + "=" * 70)
        print("1. 홈 화면 (Home)")
        print("=" * 70)

        # 홈으로 이동
        self.device.press("back")
        self.device.press("back")
        time.sleep(2)

        screenshot = self.capture_screenshot("01_home_screen", "홈 화면")

        # 텍스트 요소 추출
        texts = self.extract_all_text_elements()
        print(f"\n   발견된 텍스트: {len(texts)}개")
        for i, text in enumerate(texts[:10]):  # 처음 10개만 출력
            print(f"   [{i}] {text}")

        # 하단 탭 좌표 계산
        w, h = self.device.window_size()
        bottom_tabs = {
            "home": {"x": int(w * 0.1), "y": int(h * 0.96)},
            "search": {"x": int(w * 0.3), "y": int(h * 0.96)},
            "reels": {"x": int(w * 0.5), "y": int(h * 0.96)},
            "shop": {"x": int(w * 0.7), "y": int(h * 0.96)},
            "profile": {"x": int(w * 0.9), "y": int(h * 0.96)}
        }

        self.mapping_data['elements']['home_screen'] = {
            "screenshot": screenshot,
            "texts": texts,
            "bottom_tabs": bottom_tabs
        }

    def map_search_screen(self):
        """검색 화면 매핑"""
        print("\n" + "=" * 70)
        print("2. 검색 화면 (Search)")
        print("=" * 70)

        # 검색 탭 클릭
        w, h = self.device.window_size()
        search_x = int(w * 0.3)
        search_y = int(h * 0.96)

        print(f"\n검색 탭 클릭 ({search_x}, {search_y})...")
        self.device.click(search_x, search_y)
        time.sleep(3)

        screenshot = self.capture_screenshot("02_search_screen", "검색 화면")

        # 텍스트 요소 추출
        texts = self.extract_all_text_elements()
        print(f"\n   발견된 텍스트: {len(texts)}개")

        # 검색창 좌표
        search_box = {"x": int(w * 0.5), "y": int(h * 0.08)}

        self.mapping_data['elements']['search_screen'] = {
            "screenshot": screenshot,
            "texts": texts,
            "search_box_coordinates": search_box
        }

    def map_search_input(self, query: str = "forteclinicjpn"):
        """검색어 입력 및 결과"""
        print("\n" + "=" * 70)
        print(f"3. 검색 실행 - '{query}'")
        print("=" * 70)

        # 검색창 클릭
        w, h = self.device.window_size()
        search_box_x = int(w * 0.5)
        search_box_y = int(h * 0.08)

        print(f"\n검색창 클릭 ({search_box_x}, {search_box_y})...")
        self.device.click(search_box_x, search_box_y)
        time.sleep(2)

        # 텍스트 입력 (ADB shell)
        print(f"텍스트 입력: {query}")
        self.device.shell(f"input text {query}")
        time.sleep(3)

        screenshot = self.capture_screenshot("03_search_results", f"검색 결과: {query}")

        # 검색 결과 텍스트 추출
        texts = self.extract_all_text_elements()
        print(f"\n   발견된 텍스트: {len(texts)}개")
        for i, text in enumerate(texts[:15]):
            print(f"   [{i}] {text}")

        # 첫 번째 결과 좌표
        first_result = {"x": int(w * 0.5), "y": int(h * 0.3)}

        self.mapping_data['elements']['search_results'] = {
            "screenshot": screenshot,
            "query": query,
            "texts": texts,
            "first_result_coordinates": first_result
        }

    def map_profile_screen(self):
        """프로필 화면 매핑"""
        print("\n" + "=" * 70)
        print("4. 프로필 화면 (Profile)")
        print("=" * 70)

        # 첫 번째 검색 결과 클릭
        w, h = self.device.window_size()
        first_result_x = int(w * 0.5)
        first_result_y = int(h * 0.3)

        print(f"\n첫 번째 결과 클릭 ({first_result_x}, {first_result_y})...")
        self.device.click(first_result_x, first_result_y)
        time.sleep(4)

        screenshot = self.capture_screenshot("04_profile_screen", "프로필 화면")

        # 프로필 정보 추출
        texts = self.extract_all_text_elements()
        print(f"\n   발견된 텍스트: {len(texts)}개")

        # 프로필 정보 파싱 시도
        profile_info = {
            "username": None,
            "fullname": None,
            "follower_count": None,
            "following_count": None,
            "post_count": None,
            "bio": None
        }

        for text in texts:
            print(f"   - {text}")
            # 팔로워 수 찾기 (예: "1,234 팔로워" 또는 "followers")
            if "팔로워" in text or "followers" in text.lower():
                try:
                    # 숫자 추출
                    import re
                    numbers = re.findall(r'[\d,]+', text)
                    if numbers:
                        profile_info['follower_count'] = numbers[0]
                        print(f"   ✅ 팔로워 수 발견: {numbers[0]}")
                except:
                    pass

        # 주요 버튼 좌표 (팔로우, 메시지, DM)
        buttons = {
            "follow_button": {"x": int(w * 0.25), "y": int(h * 0.30)},
            "message_button": {"x": int(w * 0.50), "y": int(h * 0.30)},
            "dm_button": {"x": int(w * 0.75), "y": int(h * 0.30)}
        }

        self.mapping_data['elements']['profile_screen'] = {
            "screenshot": screenshot,
            "texts": texts,
            "profile_info": profile_info,
            "button_coordinates": buttons
        }

    def map_hashtag_search(self, hashtag: str = "travel"):
        """해시태그 검색"""
        print("\n" + "=" * 70)
        print(f"5. 해시태그 검색 - '#{hashtag}'")
        print("=" * 70)

        # 검색 화면으로 돌아가기
        self.device.press("back")
        self.device.press("back")
        time.sleep(2)

        # 검색 탭 클릭
        w, h = self.device.window_size()
        search_x = int(w * 0.3)
        search_y = int(h * 0.96)
        self.device.click(search_x, search_y)
        time.sleep(2)

        # 검색창 클릭
        search_box_x = int(w * 0.5)
        search_box_y = int(h * 0.08)
        self.device.click(search_box_x, search_box_y)
        time.sleep(2)

        # 기존 텍스트 지우기
        for _ in range(20):
            self.device.shell("input keyevent KEYCODE_DEL")
        time.sleep(1)

        # 해시태그 입력
        print(f"해시태그 입력: #{hashtag}")
        self.device.shell(f"input text %23{hashtag}")  # %23 = #
        time.sleep(3)

        screenshot = self.capture_screenshot("05_hashtag_search", f"해시태그: #{hashtag}")

        # 결과 텍스트 추출
        texts = self.extract_all_text_elements()
        print(f"\n   발견된 텍스트: {len(texts)}개")
        for i, text in enumerate(texts[:10]):
            print(f"   [{i}] {text}")

        self.mapping_data['elements']['hashtag_search'] = {
            "screenshot": screenshot,
            "hashtag": hashtag,
            "texts": texts
        }

    def save_mapping_data(self):
        """매핑 데이터 저장"""
        output_file = self.output_dir / "mapping_data.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.mapping_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 매핑 데이터 저장: {output_file}")

    def generate_report(self):
        """매핑 결과 리포트 생성"""
        report_file = self.output_dir / "MAPPING_REPORT.md"

        report = f"""# Instagram UI Mapping Report (Simple)

**생성 시각**: {self.mapping_data['timestamp']}
**디바이스**: {self.device_id}
**Instagram 버전**: {self.mapping_data.get('instagram_version', 'Unknown')}
**화면 크기**: {self.mapping_data['screen_size']['width']} x {self.mapping_data['screen_size']['height']}

---

## 매핑 방식

이 매핑은 UIAutomator2의 dump_hierarchy() NullPointerException 문제를 우회하여:
- 스크린샷만 캡처
- 좌표 기반 상호작용
- 텍스트 요소 직접 추출 (가능한 경우)

---

## 수집된 화면

"""

        for section, data in self.mapping_data['elements'].items():
            report += f"\n### {section}\n\n"
            report += f"- 📷 스크린샷: `{data.get('screenshot', 'N/A')}`\n"

            if 'texts' in data and data['texts']:
                report += f"- 📝 텍스트 요소: {len(data['texts'])}개\n"

            if 'bottom_tabs' in data:
                report += "\n**하단 탭 좌표:**\n\n"
                for tab_name, coords in data['bottom_tabs'].items():
                    report += f"- **{tab_name}**: ({coords['x']}, {coords['y']})\n"

            if 'button_coordinates' in data:
                report += "\n**버튼 좌표:**\n\n"
                for btn_name, coords in data['button_coordinates'].items():
                    report += f"- **{btn_name}**: ({coords['x']}, {coords['y']})\n"

            if 'profile_info' in data and data['profile_info']['follower_count']:
                report += f"\n**팔로워 수**: {data['profile_info']['follower_count']}\n"

        report += f"\n---\n\n## 파일 목록\n\n"

        for file in sorted(self.output_dir.iterdir()):
            if file.is_file():
                report += f"- `{file.name}`\n"

        report += f"\n---\n\n## 다음 단계\n\n"
        report += "1. 스크린샷 확인하여 UI 레이아웃 분석\n"
        report += "2. 좌표 값 조정 (필요시)\n"
        report += "3. 모듈별 코드 작성 (DeviceManager, Navigator, Extractor)\n"
        report += "4. GPT-4 Vision을 활용한 화면 인식 통합\n"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 리포트 생성: {report_file}")

    def run(self):
        """전체 매핑 실행"""
        print("=" * 70)
        print("Instagram UI Mapper (Simple - Coordinate-based)")
        print("=" * 70)

        try:
            self.connect()
            self.prepare_device()

            if not self.launch_instagram():
                print("\n❌ Instagram 실행 실패. 종료합니다.")
                return

            # 각 화면 매핑
            self.map_home_screen()
            self.map_search_screen()
            self.map_search_input("forteclinicjpn")
            self.map_profile_screen()
            self.map_hashtag_search("travel")

            # 결과 저장
            self.save_mapping_data()
            self.generate_report()

            print("\n" + "=" * 70)
            print("✅ UI 매핑 완료!")
            print("=" * 70)
            print(f"\n출력 디렉토리: {self.output_dir}")
            print("\n다음 단계:")
            print("1. 생성된 스크린샷 확인")
            print("2. mapping_data.json 확인")
            print("3. MAPPING_REPORT.md 읽기")
            print("4. 좌표 기반 모듈 구현 시작")

        except KeyboardInterrupt:
            print("\n\n⚠️  사용자가 중단했습니다.")
        except Exception as e:
            print(f"\n\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    mapper = InstagramUIMapperSimple(
        device_id="R3CN70D9ZBY",
        output_dir="ui_mapping_simple"
    )
    mapper.run()
