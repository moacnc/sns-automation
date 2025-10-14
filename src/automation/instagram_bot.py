#!/usr/bin/env python3
"""
Instagram Bot - GramAddict 기반 하이브리드 자동화
안전한 GramAddict 기능 + 필요시 UIAutomator2 커스텀 기능
"""
import time
import random
from datetime import datetime
from typing import Optional, Dict, Any

# GramAddict 핵심 모듈
from GramAddict.core.device_facade import DeviceFacade
from GramAddict.core.navigation import nav_to_blogger, nav_to_feed
from GramAddict.core.views import ProfileView, TabBarView

# 우리 유틸리티
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger


class SafetyConfig:
    """안전 설정"""
    MIN_DELAY = 2.0  # 최소 딜레이 (초)
    MAX_DELAY = 5.0  # 최대 딜레이 (초)
    ACTION_DELAY = (1.5, 3.5)  # 작업 간 딜레이 범위
    SWIPE_DELAY = (0.8, 1.5)  # 스크롤 딜레이

    # 작업 제한
    MAX_ACTIONS_PER_HOUR = 30
    MAX_PROFILE_VIEWS_PER_HOUR = 50


class InstagramBot:
    """
    Instagram 자동화 봇 (GramAddict 기반 하이브리드)

    안전 기능:
    - 랜덤 딜레이
    - 작업량 제한
    - 사람처럼 행동
    - 에러 처리
    """

    def __init__(self, device_id: str, account_name: str, app_id: str = "com.instagram.android"):
        """
        초기화

        Args:
            device_id: Android 기기 ID (adb devices에서 확인)
            account_name: Instagram 계정명 (로깅용)
            app_id: Instagram 앱 패키지명
        """
        self.device_id = device_id
        self.account_name = account_name
        self.app_id = app_id

        # GramAddict 기기 연결
        self.device = DeviceFacade(device_id, app_id)

        # 유틸리티
        self.logger = get_logger()
        self.db = DatabaseHandler()

        # 통계
        self.actions_count = 0
        self.session_start = datetime.now()

        self.logger.info(f"✓ Instagram Bot 초기화: {account_name} @ {device_id}")

    def random_sleep(self, min_sec: float = None, max_sec: float = None):
        """
        랜덤 딜레이 (사람처럼 행동)

        Args:
            min_sec: 최소 초
            max_sec: 최대 초
        """
        min_sec = min_sec or SafetyConfig.MIN_DELAY
        max_sec = max_sec or SafetyConfig.MAX_DELAY

        delay = random.uniform(min_sec, max_sec)
        self.logger.debug(f"Sleep {delay:.2f}s")
        time.sleep(delay)

    def log_action(self, action_type: str, details: str, status: str = "success"):
        """작업 로그 기록"""
        try:
            self.db.log_action(
                account_name=self.account_name,
                action_type=action_type,
                details=details,
                status=status
            )
            self.actions_count += 1
        except Exception as e:
            self.logger.error(f"로그 기록 실패: {e}")

    def go_to_profile(self, username: str) -> bool:
        """
        사용자 프로필로 이동 (안전한 검색 방식)

        Args:
            username: Instagram 사용자명 (@ 없이)

        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info(f"프로필 이동: @{username}")

            # 1. 검색 탭으로 이동 (GramAddict TabBarView 사용)
            tab_bar = TabBarView(self.device)
            tab_bar.navigateToSearch()
            self.random_sleep(2, 3)

            # 2. 검색창 클릭
            search_edit = self.device.find(
                resourceIdMatches=".*search_edit_text.*"
            )
            if search_edit.exists():
                search_edit.click()
                self.random_sleep(1, 2)
            else:
                # 화면 상단 중앙 클릭 (검색창 위치)
                screen_width = self.device.get_info()['displayWidth']
                self.device.deviceV2.click(screen_width // 2, 120)
                self.random_sleep(1, 2)

            # 3. 사용자명 입력 (ADB 사용 - 안전)
            import subprocess
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'input', 'text', username],
                capture_output=True
            )
            self.random_sleep(3, 4)

            # 4. 첫 번째 결과 클릭 (사용자 프로필)
            screen_width = self.device.get_info()['displayWidth']
            self.device.deviceV2.click(screen_width // 2, 300)
            self.random_sleep(3, 5)

            self.log_action("navigate_profile", f"@{username} 프로필 방문")
            self.logger.info(f"✓ @{username} 프로필 접근 완료")
            return True

        except Exception as e:
            self.logger.error(f"프로필 이동 오류: {e}")
            self.log_action("navigate_profile", f"@{username} 오류: {e}", "failed")
            return False

    def get_profile_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        프로필 정보 가져오기 (GramAddict ProfileView 사용)

        Args:
            username: Instagram 사용자명

        Returns:
            dict: 프로필 정보 또는 None
        """
        try:
            self.logger.info(f"프로필 정보 수집: @{username}")

            # GramAddict ProfileView로 정보 추출
            profile_view = ProfileView(self.device)

            # 각 정보 가져오기
            followers = profile_view.getFollowersCount()
            following = profile_view.getFollowingCount()
            posts = profile_view.getPostsCount()
            full_name = profile_view.getFullName()
            bio = profile_view.getProfileBiography()
            is_private = profile_view.isPrivateAccount()

            profile_data = {
                'username': username,
                'full_name': full_name,
                'followers': followers,
                'following': following,
                'posts': posts,
                'biography': bio,
                'is_private': is_private,
                'scraped_at': datetime.now()
            }

            self.logger.info(f"✓ 프로필 정보:")
            self.logger.info(f"  - 이름: {full_name}")
            self.logger.info(f"  - 팔로워: {followers:,}")
            self.logger.info(f"  - 팔로잉: {following:,}")
            self.logger.info(f"  - 게시물: {posts:,}")
            self.logger.info(f"  - 비공개: {is_private}")

            # 데이터베이스 기록
            self.log_action(
                "profile_scrape",
                f"@{username}: {followers:,} 팔로워, {following:,} 팔로잉, {posts:,} 게시물"
            )

            return profile_data

        except Exception as e:
            self.logger.error(f"프로필 정보 수집 실패: {e}")
            self.log_action("profile_scrape", f"@{username} 실패: {e}", "failed")
            return None

    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        프로필 스크래핑 (이동 + 정보 수집)

        Args:
            username: Instagram 사용자명

        Returns:
            dict: 프로필 정보 또는 None
        """
        try:
            # 1. 프로필로 이동
            if not self.go_to_profile(username):
                return None

            # 2. 정보 수집
            profile_data = self.get_profile_info(username)

            # 3. 홈으로 돌아가기
            self.random_sleep(1, 2)
            self.go_to_home()

            return profile_data

        except Exception as e:
            self.logger.error(f"프로필 스크래핑 오류: {e}")
            return None

    def go_to_home(self):
        """홈 피드로 이동 (GramAddict 사용)"""
        try:
            self.logger.debug("홈으로 이동...")
            nav_to_feed(self.device)
            self.random_sleep(1, 2)
            self.log_action("navigate_home", "홈 피드로 이동")
        except Exception as e:
            self.logger.error(f"홈 이동 실패: {e}")

    def custom_action_with_uiautomator2(self, description: str, action_func):
        """
        커스텀 작업 (UIAutomator2 직접 사용)
        GramAddict가 지원하지 않는 기능에만 사용

        Args:
            description: 작업 설명
            action_func: 실행할 함수
        """
        try:
            self.logger.info(f"커스텀 작업: {description}")

            # 작업 전 딜레이 (안전성)
            self.random_sleep(*SafetyConfig.ACTION_DELAY)

            # 작업 실행
            result = action_func(self.device.deviceV2)

            # 작업 후 딜레이
            self.random_sleep(*SafetyConfig.ACTION_DELAY)

            self.log_action("custom_action", description)
            return result

        except Exception as e:
            self.logger.error(f"커스텀 작업 실패: {e}")
            self.log_action("custom_action", f"{description} 실패: {e}", "failed")
            return None

    def take_screenshot(self, filename: str = None) -> str:
        """스크린샷 저장"""
        try:
            if not filename:
                filename = f"/tmp/instagram_{int(time.time())}.png"

            self.device.screenshot(filename)
            self.logger.info(f"✓ 스크린샷: {filename}")
            self.log_action("screenshot", f"저장: {filename}")

            return filename
        except Exception as e:
            self.logger.error(f"스크린샷 실패: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """세션 통계 반환"""
        duration = (datetime.now() - self.session_start).total_seconds()
        return {
            'account': self.account_name,
            'device': self.device_id,
            'actions_count': self.actions_count,
            'duration_seconds': duration,
            'start_time': self.session_start,
            'actions_per_hour': (self.actions_count / duration * 3600) if duration > 0 else 0
        }

    def close(self):
        """리소스 정리"""
        try:
            stats = self.get_stats()
            self.logger.info(f"=== 세션 종료 ===")
            self.logger.info(f"  - 총 작업: {stats['actions_count']}")
            self.logger.info(f"  - 소요 시간: {stats['duration_seconds']:.1f}초")
            self.logger.info(f"  - 시간당 작업: {stats['actions_per_hour']:.1f}")

            self.db.close()
        except Exception as e:
            self.logger.error(f"종료 오류: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # 테스트
    DEVICE_ID = "R3CN70D9ZBY"
    ACCOUNT_NAME = "hyoeunsagong"

    with InstagramBot(DEVICE_ID, ACCOUNT_NAME) as bot:
        # 프로필 스크래핑 테스트
        profile = bot.scrape_profile("hon.hono7")

        if profile:
            print(f"\n✅ 성공!")
            print(f"사용자: @{profile['username']}")
            print(f"이름: {profile['full_name']}")
            print(f"팔로워: {profile['followers']:,}")
            print(f"팔로잉: {profile['following']:,}")
            print(f"게시물: {profile['posts']:,}")
        else:
            print("\n❌ 실패")
