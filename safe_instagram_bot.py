#!/usr/bin/env python3
"""
안전한 Instagram 봇
GramAddict의 안전 철학 + UIAutomator2 구현

GramAddict 안전 원칙:
1. 랜덤 딜레이 (2-5초 기본, 작업별 조정)
2. 인간 행동 모방 (불규칙한 패턴)
3. 작업 속도 제한
4. 에러 시 안전하게 복구
5. 모든 작업 로깅
"""
import sys
import time
import random
import re
from datetime import datetime
from typing import Optional, Dict, Any
import uiautomator2 as u2

sys.path.insert(0, '/Users/kyounghogwack/MOAcnc/Dev/PantaRheiX/AI SNS flow')
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger


class SafetyConfig:
    """
    GramAddict 스타일 안전 설정
    """
    # 딜레이 설정 (초)
    MIN_DELAY = 2.0
    MAX_DELAY = 5.0
    ACTION_DELAY_MIN = 1.5
    ACTION_DELAY_MAX = 3.5
    SWIPE_DELAY_MIN = 0.8
    SWIPE_DELAY_MAX = 1.5

    # 작업 제한
    MAX_ACTIONS_PER_HOUR = 30
    MAX_ERRORS_BEFORE_STOP = 5

    # 재시도 설정
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0


class SafeInstagramBot:
    """
    안전한 Instagram 자동화 봇

    GramAddict 개념 적용:
    - 랜덤화된 모든 동작
    - 사람처럼 행동
    - 안전한 속도
    - 완전한 로깅
    - 에러 복구
    """

    def __init__(self, device_id: str, account_name: str):
        """
        봇 초기화

        Args:
            device_id: Android 기기 ID
            account_name: Instagram 계정명 (로깅용)
        """
        self.device_id = device_id
        self.account_name = account_name

        # UIAutomator2 연결
        self.device = u2.connect(device_id)
        self.screen_width = self.device.info['displayWidth']
        self.screen_height = self.device.info['displayHeight']

        # 유틸리티
        self.logger = get_logger()
        self.db = DatabaseHandler()

        # 통계
        self.actions_count = 0
        self.errors_count = 0
        self.session_start = datetime.now()

        self.logger.info(f"✓ 안전 봇 초기화 완료")
        self.logger.info(f"  - 계정: {account_name}")
        self.logger.info(f"  - 기기: {device_id}")
        self.logger.info(f"  - 화면: {self.screen_width}x{self.screen_height}")

    # ============ GramAddict 스타일 안전 함수 ============

    def random_sleep(self, min_sec: float = None, max_sec: float = None):
        """
        랜덤 딜레이 (GramAddict 핵심 기능)

        사람은 항상 정확한 시간에 행동하지 않음
        """
        min_sec = min_sec or SafetyConfig.MIN_DELAY
        max_sec = max_sec or SafetyConfig.MAX_DELAY

        delay = random.uniform(min_sec, max_sec)
        # 가끔 더 긴 딜레이 (10% 확률)
        if random.random() < 0.1:
            delay *= 1.5

        self.logger.debug(f"💤 {delay:.2f}초 대기...")
        time.sleep(delay)

    def safe_click(self, x: int, y: int, description: str = ""):
        """
        안전한 클릭 (GramAddict 방식)

        - 클릭 전 짧은 딜레이
        - 좌표에 약간의 랜덤성 추가
        - 클릭 후 딜레이
        """
        # 클릭 전 딜레이
        self.random_sleep(
            SafetyConfig.ACTION_DELAY_MIN,
            SafetyConfig.ACTION_DELAY_MAX
        )

        # 좌표에 랜덤성 추가 (±5px)
        x_random = x + random.randint(-5, 5)
        y_random = y + random.randint(-5, 5)

        self.logger.debug(f"👆 클릭: ({x_random}, {y_random}) {description}")
        self.device.click(x_random, y_random)

        # 클릭 후 딜레이
        self.random_sleep(1.0, 2.0)

        self.actions_count += 1

    def safe_swipe(self, fx: int, fy: int, tx: int, ty: int):
        """
        안전한 스와이프 (GramAddict 방식)

        - 불규칙한 속도
        - 랜덤 궤적
        """
        self.random_sleep(
            SafetyConfig.SWIPE_DELAY_MIN,
            SafetyConfig.SWIPE_DELAY_MAX
        )

        # 스와이프 속도 랜덤화
        duration = random.uniform(0.3, 0.7)

        self.logger.debug(f"👆 스와이프: ({fx},{fy}) → ({tx},{ty})")
        self.device.swipe(fx, fy, tx, ty, duration)

        self.random_sleep(0.8, 1.5)

        self.actions_count += 1

    def safe_input(self, text: str):
        """
        안전한 텍스트 입력

        ADB를 사용하되 안전하게
        """
        import subprocess
        self.random_sleep(0.5, 1.0)

        subprocess.run(
            ['adb', '-s', self.device_id, 'shell', 'input', 'text', text],
            capture_output=True
        )

        self.random_sleep(1.5, 2.5)

    def log_action(self, action_type: str, details: str, status: str = "success"):
        """작업 로깅 (GramAddict 방식)"""
        try:
            self.db.log_action(
                account_name=self.account_name,
                action_type=action_type,
                details=details,
                status=status
            )
        except Exception as e:
            self.logger.error(f"로그 기록 실패: {e}")

    def handle_error(self, error: Exception, context: str):
        """
        에러 처리 (GramAddict 방식)

        에러 발생 시 안전하게 복구
        """
        self.errors_count += 1
        self.logger.error(f"❌ 오류 발생 ({context}): {error}")

        if self.errors_count >= SafetyConfig.MAX_ERRORS_BEFORE_STOP:
            self.logger.error(f"⚠️ 오류 한계 도달 ({self.errors_count}회), 중단")
            raise Exception(f"너무 많은 오류 발생: {self.errors_count}회")

        # 오류 후 긴 딜레이
        self.logger.info(f"⏳ 복구를 위해 {SafetyConfig.RETRY_DELAY}초 대기...")
        time.sleep(SafetyConfig.RETRY_DELAY)

    # ============ Instagram 네비게이션 ============

    def go_to_tab(self, tab_name: str):
        """
        하단 탭으로 이동

        Args:
            tab_name: 'home', 'search', 'reels', 'shop', 'profile'
        """
        self.logger.info(f"📱 {tab_name} 탭으로 이동...")

        tab_positions = {
            'home': self.screen_width // 10,
            'search': self.screen_width * 3 // 10,
            'add': self.screen_width * 5 // 10,
            'reels': self.screen_width * 7 // 10,
            'profile': self.screen_width * 9 // 10
        }

        x = tab_positions.get(tab_name, self.screen_width // 2)
        y = self.screen_height - 100

        self.safe_click(x, y, f"{tab_name} 탭")
        self.log_action("navigate", f"{tab_name} 탭으로 이동")

    def search_and_open_profile(self, username: str) -> bool:
        """
        사용자 검색 및 프로필 페이지 열기

        GramAddict 방식: 안전하고 확실하게

        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info(f"🔍 검색 및 프로필 접근: @{username}")

            # 1. 검색 탭으로 이동
            self.go_to_tab('search')

            # 2. 검색창 클릭
            self.logger.debug("검색창 클릭...")
            self.safe_click(self.screen_width // 2, 120, "검색창")

            # 3. 사용자명 입력
            self.logger.debug(f"사용자명 입력: {username}")
            self.safe_input(username)

            # 4. 엔터로 검색 실행
            self.logger.debug("검색 실행...")
            import subprocess
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'input', 'keyevent', '66'],
                capture_output=True
            )
            self.random_sleep(3, 4)

            # 5. "계정" 탭 클릭 (검색 결과 필터)
            self.logger.debug("'계정' 탭 선택...")
            accounts_tab_x = self.screen_width // 4
            accounts_tab_y = 220
            self.safe_click(accounts_tab_x, accounts_tab_y, "계정 탭")

            # 6. 첫 번째 계정 선택
            self.logger.debug("첫 번째 계정 선택...")
            first_result_x = self.screen_width // 2
            first_result_y = 350
            self.safe_click(first_result_x, first_result_y, "첫 번째 계정")

            self.log_action("navigate_profile", f"@{username} 프로필 접근")
            self.logger.info(f"✓ @{username} 프로필 페이지 접근 완료")

            return True

        except Exception as e:
            self.handle_error(e, "search_and_open_profile")
            self.log_action("navigate_profile", f"@{username} 실패: {e}", "failed")
            return False

    def extract_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        프로필 정보 추출

        XML 파싱으로 데이터 수집
        """
        try:
            self.logger.info("📊 프로필 정보 추출 중...")

            # 스크린샷 저장
            screenshot_path = f"/tmp/profile_{username}_{int(time.time())}.png"
            self.device.screenshot(screenshot_path)
            self.logger.debug(f"📸 스크린샷: {screenshot_path}")

            # XML에서 정보 추출
            xml = self.device.dump_hierarchy()

            def parse_korean_number(text: str) -> int:
                """한국어 숫자 표현 파싱"""
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

            # 정규식으로 정보 찾기
            posts_match = re.search(r'([\\d,]+)\\s*게시물', xml)
            followers_match = re.search(r'([\\d,.]+만?)\\s*팔로워', xml)
            following_match = re.search(r'([\\d,]+)\\s*팔로잉', xml)

            posts = parse_korean_number(posts_match.group(1)) if posts_match else 0
            followers = parse_korean_number(followers_match.group(1)) if followers_match else 0
            following = parse_korean_number(following_match.group(1)) if following_match else 0

            profile_data = {
                'username': username,
                'followers': followers,
                'following': following,
                'posts': posts,
                'screenshot': screenshot_path,
                'scraped_at': datetime.now()
            }

            self.logger.info(f"✓ 프로필 정보:")
            self.logger.info(f"  - 사용자: @{username}")
            self.logger.info(f"  - 팔로워: {followers:,}")
            self.logger.info(f"  - 팔로잉: {following:,}")
            self.logger.info(f"  - 게시물: {posts:,}")

            return profile_data

        except Exception as e:
            self.handle_error(e, "extract_profile_data")
            return None

    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        프로필 완전 스크래핑 (메인 함수)

        GramAddict 방식: 안전하고 완전한 프로세스
        """
        try:
            self.logger.info(f"{'='*50}")
            self.logger.info(f"프로필 스크래핑 시작: @{username}")
            self.logger.info(f"{'='*50}")

            # 1. 프로필 페이지로 이동
            if not self.search_and_open_profile(username):
                self.logger.error("프로필 접근 실패")
                return None

            # 2. 프로필 정보 추출
            profile_data = self.extract_profile_data(username)

            if not profile_data:
                self.logger.error("프로필 정보 추출 실패")
                return None

            # 3. 데이터베이스 기록
            self.log_action(
                "profile_scrape",
                f"@{username}: {profile_data['followers']:,} 팔로워, "
                f"{profile_data['following']:,} 팔로잉, {profile_data['posts']:,} 게시물 "
                "[GramAddict-Style Safe Bot]",
                "success"
            )

            # 4. 홈으로 복귀
            self.logger.info("🏠 홈으로 복귀...")
            self.go_to_tab('home')

            self.logger.info(f"✅ 프로필 스크래핑 완료: @{username}")
            self.logger.info(f"{'='*50}\\n")

            return profile_data

        except Exception as e:
            self.logger.error(f"❌ 프로필 스크래핑 실패: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

            self.log_action(
                "profile_scrape",
                f"@{username} 완전 실패: {e}",
                "failed"
            )

            return None

    def get_stats(self) -> Dict[str, Any]:
        """세션 통계"""
        duration = (datetime.now() - self.session_start).total_seconds()
        return {
            'account': self.account_name,
            'actions': self.actions_count,
            'errors': self.errors_count,
            'duration_sec': duration,
            'actions_per_hour': (self.actions_count / duration * 3600) if duration > 0 else 0
        }

    def close(self):
        """리소스 정리 및 통계 출력"""
        stats = self.get_stats()

        self.logger.info("="*50)
        self.logger.info("세션 종료")
        self.logger.info("="*50)
        self.logger.info(f"계정: {stats['account']}")
        self.logger.info(f"총 작업: {stats['actions']}회")
        self.logger.info(f"오류: {stats['errors']}회")
        self.logger.info(f"소요 시간: {stats['duration_sec']:.1f}초")
        self.logger.info(f"시간당 작업: {stats['actions_per_hour']:.1f}회")
        self.logger.info("="*50)

        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============ 메인 실행 ============

if __name__ == "__main__":
    DEVICE_ID = "R3CN70D9ZBY"
    ACCOUNT_NAME = "hyoeunsagong"

    target_username = sys.argv[1] if len(sys.argv) > 1 else "hon.hono7"

    with SafeInstagramBot(DEVICE_ID, ACCOUNT_NAME) as bot:
        result = bot.scrape_profile(target_username)

        if result:
            print(f"\\n{'='*50}")
            print(f"✅ 스크래핑 성공!")
            print(f"{'='*50}")
            print(f"사용자: @{result['username']}")
            print(f"팔로워: {result['followers']:,}")
            print(f"팔로잉: {result['following']:,}")
            print(f"게시물: {result['posts']:,}")
            print(f"스크린샷: {result['screenshot']}")
            print(f"{'='*50}")
        else:
            print(f"\\n❌ 스크래핑 실패")
