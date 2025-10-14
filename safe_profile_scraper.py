#!/usr/bin/env python3
"""
안전한 프로필 스크래퍼
GramAddict의 안전 개념 적용 + UIAutomator2 직접 사용
"""
import sys
import time
import random
import re
from datetime import datetime
import uiautomator2 as u2

sys.path.insert(0, '/Users/kyounghogwack/MOAcnc/Dev/PantaRheiX/AI SNS flow')
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

# 설정
DEVICE_ID = "R3CN70D9ZBY"
ACCOUNT_NAME = "hyoeunsagong"

logger = get_logger()
db = DatabaseHandler()


class SafeInstagramBot:
    """
    안전한 Instagram 봇
    - 랜덤 딜레이 (2-5초)
    - 사람처럼 행동
    - 작업 로깅
    """

    def __init__(self, device_id, account_name):
        self.device_id = device_id
        self.account_name = account_name
        self.device = u2.connect(device_id)
        self.screen_width = self.device.info['displayWidth']
        self.screen_height = self.device.info['displayHeight']
        logger.info(f"✓ 안전 봇 초기화: {account_name}")

    def random_sleep(self, min_sec=2.0, max_sec=5.0):
        """랜덤 딜레이 - 사람처럼"""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"💤 {delay:.2f}초 대기...")
        time.sleep(delay)

    def safe_click(self, x, y, description=""):
        """안전한 클릭 - 전후 딜레이"""
        self.random_sleep(0.5, 1.5)
        logger.debug(f"👆 클릭: ({x}, {y}) {description}")
        self.device.click(x, y)
        self.random_sleep(1, 2)

    def safe_swipe(self, fx, fy, tx, ty):
        """안전한 스와이프"""
        self.random_sleep(0.5, 1.0)
        duration = random.uniform(0.3, 0.6)
        self.device.swipe(fx, fy, tx, ty, duration)
        self.random_sleep(0.8, 1.5)

    def go_to_search_tab(self):
        """검색 탭으로 이동"""
        logger.info("🔍 검색 탭으로 이동...")
        search_x = self.screen_width * 3 // 10
        search_y = self.screen_height - 100
        self.safe_click(search_x, search_y, "검색 탭")

    def search_user(self, username):
        """사용자 검색 및 프로필 접근"""
        logger.info(f"🔎 검색: {username}")

        # 검색창 클릭
        self.safe_click(self.screen_width // 2, 120, "검색창")

        # 사용자명 입력 (ADB)
        import subprocess
        subprocess.run(
            ['adb', '-s', self.device_id, 'shell', 'input', 'text', username],
            capture_output=True
        )
        self.random_sleep(3, 4)

        # 중요: 검색 입력 후 다시 검색 아이콘을 클릭해야 검색 결과 화면이 나타남
        logger.info("🔍 검색 아이콘 재클릭 (검색 결과 표시)...")
        search_icon_x = self.screen_width * 3 // 10
        search_icon_y = self.screen_height - 100
        self.safe_click(search_icon_x, search_icon_y, "검색 아이콘")

        # 검색 결과 화면에서 프로필 아바타 선택
        logger.info("📱 검색 결과에서 프로필 아바타 클릭...")

        # 중요: 사용자명을 클릭하면 게시물이 열림
        # 프로필 페이지로 가려면 프로필 사진(아바타)을 클릭해야 함

        # XML에서 사용자명 위치를 찾고, 그 왼쪽의 아바타를 클릭
        import re
        xml = self.device.dump_hierarchy()
        username_match = re.search(rf'text=\"{username}\".*?bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"', xml)

        if username_match:
            # 사용자명의 위치
            x1, y1, x2, y2 = map(int, username_match.groups())

            # 프로필 아바타는 사용자명의 왼쪽에 있음
            # 대략 사용자명 Y 좌표는 유지하고, X는 왼쪽으로 이동
            avatar_x = x1 - 80  # 사용자명 왼쪽 80px (아바타 위치)
            avatar_y = (y1 + y2) // 2

            logger.info(f"👤 프로필 아바타 위치: ({avatar_x}, {avatar_y})")
            self.safe_click(avatar_x, avatar_y, f"@{username} 아바타 클릭")
        else:
            # 기본 위치: 검색 결과 첫번째 항목의 왼쪽 (아바타)
            logger.warning("사용자명 위치를 찾을 수 없음, 기본 아바타 위치 사용")
            avatar_x = self.screen_width // 6  # 왼쪽
            avatar_y = 350
            self.safe_click(avatar_x, avatar_y, "프로필 아바타")

    def extract_profile_info(self, username):
        """프로필 정보 추출"""
        logger.info("📊 프로필 정보 추출 중...")

        # 스크린샷
        screenshot_path = f"/tmp/profile_{username}_{int(time.time())}.png"
        self.device.screenshot(screenshot_path)
        logger.info(f"📸 스크린샷: {screenshot_path}")

        # XML에서 정보 추출
        xml = self.device.dump_hierarchy()

        def parse_korean_number(text):
            """한국어 숫자 파싱"""
            if not text:
                return 0
            text = text.replace(',', '').strip()
            if '만' in text:
                return int(float(text.replace('만', '')) * 10000)
            elif '천' in text:
                return int(float(text.replace('천', '')) * 1000)
            else:
                try:
                    return int(text)
                except:
                    return 0

        # 정규식으로 찾기
        posts_match = re.search(r'([\\d,]+)\\s*게시물', xml)
        followers_match = re.search(r'([\\d,.]+만?)\\s*팔로워', xml)
        following_match = re.search(r'([\\d,]+)\\s*팔로잉', xml)

        posts = parse_korean_number(posts_match.group(1)) if posts_match else 0
        followers = parse_korean_number(followers_match.group(1)) if followers_match else 0
        following = parse_korean_number(following_match.group(1)) if following_match else 0

        return {
            'username': username,
            'followers': followers,
            'following': following,
            'posts': posts,
            'screenshot': screenshot_path,
            'scraped_at': datetime.now()
        }

    def go_to_home(self):
        """홈으로 이동"""
        logger.info("🏠 홈으로 이동...")
        home_x = self.screen_width // 10
        home_y = self.screen_height - 100
        self.safe_click(home_x, home_y, "홈 탭")

    def scrape_profile(self, username):
        """프로필 완전 스크래핑"""
        try:
            logger.info(f"=== 프로필 스크래핑 시작: @{username} ===")

            # 1. 검색 탭으로 이동
            self.go_to_search_tab()

            # 2. 사용자 검색 및 프로필 접근
            self.search_user(username)

            # 3. 정보 추출
            profile_data = self.extract_profile_info(username)

            # 4. 결과 출력
            logger.info(f"✓ 프로필 정보:")
            logger.info(f"  - 사용자: @{profile_data['username']}")
            logger.info(f"  - 팔로워: {profile_data['followers']:,}")
            logger.info(f"  - 팔로잉: {profile_data['following']:,}")
            logger.info(f"  - 게시물: {profile_data['posts']:,}")

            # 5. 데이터베이스 기록
            db.log_action(
                account_name=self.account_name,
                action_type="profile_scrape",
                details=f"@{username}: {profile_data['followers']:,} 팔로워, {profile_data['following']:,} 팔로잉, {profile_data['posts']:,} 게시물 [Safe Bot]",
                status="success"
            )

            # 6. 홈으로 복귀
            self.go_to_home()

            logger.info(f"=== 프로필 스크래핑 완료 ===\\n")
            return profile_data

        except Exception as e:
            logger.error(f"❌ 오류: {e}")
            import traceback
            logger.error(traceback.format_exc())

            db.log_action(
                account_name=self.account_name,
                action_type="profile_scrape",
                details=f"@{username} 실패: {e}",
                status="failed"
            )
            return None


if __name__ == "__main__":
    target_username = sys.argv[1] if len(sys.argv) > 1 else "hon.hono7"

    try:
        bot = SafeInstagramBot(DEVICE_ID, ACCOUNT_NAME)
        result = bot.scrape_profile(target_username)

        if result:
            print(f"\\n✅ 성공!")
            print(f"사용자: @{result['username']}")
            print(f"팔로워: {result['followers']:,}")
            print(f"팔로잉: {result['following']:,}")
            print(f"게시물: {result['posts']:,}")
            print(f"스크린샷: {result['screenshot']}")
        else:
            print("\\n❌ 실패")

    finally:
        db.close()
        logger.info("데이터베이스 연결 종료")
