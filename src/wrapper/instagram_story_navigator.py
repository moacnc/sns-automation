"""
Instagram Story Navigator - UIAutomator2 기반 스토리 탐색

기능:
- 해시태그 검색
- 스토리 탭 이동
- 스토리 목록 수집
- 스토리 콘텐츠 추출 (스크린샷 + OCR)
- 리스토리 액션
"""

from __future__ import annotations

import time
import uuid
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

import uiautomator2 as u2

from src.utils.logger import get_logger


class InstagramStoryNavigator:
    """Instagram 스토리 탐색 및 리스토리"""

    def __init__(self, device_id: str, screenshots_dir: str = "screenshots"):
        """
        초기화

        Args:
            device_id: Android 디바이스 ID (adb devices)
            screenshots_dir: 스크린샷 저장 디렉토리
        """
        self.device_id = device_id
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger()
        self.device = None
        self.package_name = "com.instagram.android"

        self.logger.info(f"InstagramStoryNavigator 초기화: {device_id}")

    def connect(self):
        """디바이스 연결"""
        try:
            self.device = u2.connect(self.device_id)
            self.logger.info(f"디바이스 연결 성공: {self.device_id}")
            self.logger.info(f"디바이스 정보: {self.device.info}")
            return True
        except Exception as e:
            self.logger.error(f"디바이스 연결 실패: {e}")
            return False

    def launch_instagram(self) -> bool:
        """
        Instagram 앱 실행

        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info("Instagram 앱 실행...")

            # monkey 명령으로 앱 실행 (더 안정적)
            self.device.shell(
                f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1"
            )
            time.sleep(4)

            # 앱이 실행되었는지 확인
            current_app = self.device.app_current()
            if current_app and current_app.get('package') == self.package_name:
                self.logger.info("✅ Instagram 앱 실행 성공")
                return True
            else:
                self.logger.warning(f"현재 앱: {current_app}")
                self.logger.error("❌ Instagram 앱 실행 실패")
                return False

        except Exception as e:
            self.logger.error(f"Instagram 실행 중 오류: {e}")
            return False

    def search_hashtag(self, hashtag: str) -> bool:
        """
        해시태그 검색

        Args:
            hashtag: 검색할 해시태그 (# 없이)

        Returns:
            bool: 검색 성공 여부
        """
        try:
            self.logger.info(f"해시태그 검색: #{hashtag}")

            # 검색 버튼 찾기 (돋보기 아이콘)
            # Instagram UI는 버전마다 다를 수 있으므로 여러 방법 시도
            search_selectors = [
                {'resourceId': f'{self.package_name}:id/search_tab'},
                {'description': '검색'},
                {'description': 'Search'},
                {'text': '검색'},
                {'text': 'Search'}
            ]

            search_button = None
            for selector in search_selectors:
                if self.device(**selector).exists:
                    search_button = self.device(**selector)
                    break

            if not search_button:
                self.logger.error("검색 버튼을 찾을 수 없습니다")
                return False

            # 검색 버튼 클릭
            search_button.click()
            time.sleep(2)

            # 검색창 찾기
            search_box_selectors = [
                {'resourceId': f'{self.package_name}:id/action_bar_search_edit_text'},
                {'className': 'android.widget.EditText'},
            ]

            search_box = None
            for selector in search_box_selectors:
                if self.device(**selector).exists:
                    search_box = self.device(**selector)
                    break

            if not search_box:
                self.logger.error("검색창을 찾을 수 없습니다")
                return False

            # 해시태그 입력
            search_text = f"#{hashtag}"
            search_box.click()
            time.sleep(0.5)
            search_box.set_text(search_text)
            time.sleep(2)

            # 검색 결과에서 첫 번째 해시태그 클릭
            # 해시태그는 보통 "#해시태그" 형식으로 표시됨
            if self.device(textContains=search_text).exists:
                self.device(textContains=search_text).click()
                time.sleep(2)
                self.logger.info(f"✅ 해시태그 검색 성공: #{hashtag}")
                return True
            else:
                self.logger.warning(f"해시태그 결과를 찾을 수 없습니다: #{hashtag}")
                return False

        except Exception as e:
            self.logger.error(f"해시태그 검색 중 오류: {e}")
            return False

    def navigate_to_stories(self) -> bool:
        """
        스토리 탭으로 이동

        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info("스토리 탭으로 이동...")

            # 해시태그 페이지에서 "최근" 탭 찾기
            # Instagram에서는 보통 상단에 "인기", "최근", "스토리" 탭이 있음
            story_tab_selectors = [
                {'text': '스토리'},
                {'text': 'Stories'},
                {'description': '스토리'},
                {'description': 'Stories'}
            ]

            story_tab = None
            for selector in story_tab_selectors:
                if self.device(**selector).exists:
                    story_tab = self.device(**selector)
                    break

            if story_tab:
                story_tab.click()
                time.sleep(2)
                self.logger.info("✅ 스토리 탭 이동 성공")
                return True
            else:
                self.logger.warning("스토리 탭을 찾을 수 없습니다 (해시태그 스토리가 없을 수 있음)")
                return False

        except Exception as e:
            self.logger.error(f"스토리 탭 이동 중 오류: {e}")
            return False

    def capture_story_screenshot(self, story_id: str = None) -> str:
        """
        현재 화면 스크린샷 촬영

        Args:
            story_id: 스토리 ID (파일명에 사용)

        Returns:
            str: 스크린샷 파일 경로
        """
        if not story_id:
            story_id = str(uuid.uuid4())[:8]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_{story_id}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        try:
            # UIAutomator2로 스크린샷 촬영
            self.device.screenshot(str(filepath))
            self.logger.debug(f"스크린샷 저장: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"스크린샷 촬영 실패: {e}")
            return None

    def get_story_username(self) -> Optional[str]:
        """
        현재 스토리의 작성자 username 추출

        Returns:
            str: username (없으면 None)
        """
        try:
            # 스토리 상단에 보통 username이 표시됨
            # resourceId나 className으로 찾기
            username_selectors = [
                {'resourceId': f'{self.package_name}:id/reel_viewer_title'},
                {'resourceId': f'{self.package_name}:id/username'},
            ]

            for selector in username_selectors:
                if self.device(**selector).exists:
                    username = self.device(**selector).get_text()
                    if username:
                        return username.strip()

            # 못 찾은 경우 화면 상단의 텍스트 찾기
            # 보통 첫 번째 TextView가 username
            if self.device(className="android.widget.TextView").exists:
                first_text = self.device(className="android.widget.TextView")[0].get_text()
                if first_text and len(first_text) < 30:  # username은 보통 짧음
                    return first_text.strip()

            return None

        except Exception as e:
            self.logger.error(f"Username 추출 실패: {e}")
            return None

    def tap_restory_button(self) -> bool:
        """
        리스토리 버튼 클릭

        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info("리스토리 버튼 찾기...")

            # 스토리 화면에서 공유 버튼 찾기 (보통 우측 하단에 비행기 모양)
            # 먼저 공유 버튼 클릭
            share_button_selectors = [
                {'description': '공유'},
                {'description': 'Share'},
                {'resourceId': f'{self.package_name}:id/direct_share_button'},
            ]

            share_button = None
            for selector in share_button_selectors:
                if self.device(**selector).exists:
                    share_button = self.device(**selector)
                    break

            if not share_button:
                self.logger.warning("공유 버튼을 찾을 수 없습니다")
                return False

            # 공유 버튼 클릭
            share_button.click()
            time.sleep(1.5)

            # "스토리에 추가" 또는 "Add to Story" 버튼 찾기
            add_to_story_selectors = [
                {'text': '스토리에 추가'},
                {'text': 'Add to Story'},
                {'textContains': '스토리'},
                {'textContains': 'Story'},
            ]

            add_to_story_button = None
            for selector in add_to_story_selectors:
                if self.device(**selector).exists:
                    add_to_story_button = self.device(**selector)
                    break

            if not add_to_story_button:
                self.logger.warning("'스토리에 추가' 버튼을 찾을 수 없습니다")
                # 뒤로가기
                self.device.press("back")
                return False

            # 스토리에 추가 버튼 클릭
            add_to_story_button.click()
            time.sleep(2)

            # 확인 또는 공유 버튼 찾기 (리스토리 최종 확인)
            confirm_selectors = [
                {'text': '공유'},
                {'text': 'Share'},
                {'resourceId': f'{self.package_name}:id/share_button'},
            ]

            for selector in confirm_selectors:
                if self.device(**selector).exists:
                    self.device(**selector).click()
                    time.sleep(2)
                    self.logger.info("✅ 리스토리 성공")
                    return True

            self.logger.warning("리스토리 확인 버튼을 찾을 수 없습니다")
            return False

        except Exception as e:
            self.logger.error(f"리스토리 실패: {e}")
            return False

    def next_story(self) -> bool:
        """
        다음 스토리로 이동 (화면 우측 탭)

        Returns:
            bool: 성공 여부
        """
        try:
            # 화면 우측을 탭하여 다음 스토리로 이동
            screen_width = self.device.window_size()[0]
            screen_height = self.device.window_size()[1]

            # 우측 80% 지점, 중앙 높이
            tap_x = int(screen_width * 0.8)
            tap_y = int(screen_height * 0.5)

            self.device.click(tap_x, tap_y)
            time.sleep(1.5)

            return True

        except Exception as e:
            self.logger.error(f"다음 스토리 이동 실패: {e}")
            return False

    def close_story(self):
        """스토리 닫기 (뒤로가기)"""
        try:
            self.device.press("back")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"스토리 닫기 실패: {e}")

    def go_home(self):
        """Instagram 홈 화면으로 이동"""
        try:
            # 홈 버튼 찾기
            home_selectors = [
                {'resourceId': f'{self.package_name}:id/feed_tab'},
                {'description': '홈'},
                {'description': 'Home'},
            ]

            for selector in home_selectors:
                if self.device(**selector).exists:
                    self.device(**selector).click()
                    time.sleep(1)
                    self.logger.debug("홈 화면으로 이동")
                    return

            # 못 찾으면 여러 번 뒤로가기
            for _ in range(3):
                self.device.press("back")
                time.sleep(0.5)

        except Exception as e:
            self.logger.error(f"홈 이동 실패: {e}")


if __name__ == "__main__":
    # CLI 테스트
    import sys

    print("=" * 60)
    print("Instagram Story Navigator 테스트")
    print("=" * 60)

    # 디바이스 ID
    device_id = "R3CN70D9ZBY"  # 연결된 디바이스 ID

    # Navigator 초기화
    navigator = InstagramStoryNavigator(device_id)

    # 디바이스 연결
    print("\n[1] 디바이스 연결...")
    if not navigator.connect():
        print("❌ 디바이스 연결 실패")
        sys.exit(1)
    print("✅ 디바이스 연결 성공")

    # Instagram 실행
    print("\n[2] Instagram 실행...")
    if not navigator.launch_instagram():
        print("❌ Instagram 실행 실패")
        sys.exit(1)
    print("✅ Instagram 실행 성공")

    # 해시태그 검색
    print("\n[3] 해시태그 검색...")
    hashtag = "korea"
    if not navigator.search_hashtag(hashtag):
        print(f"❌ 해시태그 검색 실패: #{hashtag}")
        sys.exit(1)
    print(f"✅ 해시태그 검색 성공: #{hashtag}")

    # 스토리 탭으로 이동 (옵션)
    print("\n[4] 스토리 탭 이동...")
    if navigator.navigate_to_stories():
        print("✅ 스토리 탭 이동 성공")
    else:
        print("⚠️  스토리 탭 없음 (계속 진행)")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
    print("\n💡 다음 단계: 실제 스토리 수집 및 리스토리 테스트")
