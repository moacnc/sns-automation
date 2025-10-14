#!/usr/bin/env python3
"""
GramAddict 하이브리드 테스트
간단하고 안전한 프로필 스크래핑
"""
import sys
import time
import random
from datetime import datetime

# GramAddict
from GramAddict.core.device_facade import DeviceFacade
from GramAddict.core.views import ProfileView

# 우리 유틸리티
sys.path.insert(0, '/Users/kyounghogwack/MOAcnc/Dev/PantaRheiX/AI SNS flow')
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

# 설정
DEVICE_ID = "R3CN70D9ZBY"
ACCOUNT_NAME = "hyoeunsagong"
TARGET_USERNAME = "hon.hono7"

logger = get_logger()
db = DatabaseHandler()

def random_sleep(min_sec=2.0, max_sec=5.0):
    """랜덤 딜레이 (안전성)"""
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Sleep {delay:.2f}s...")
    time.sleep(delay)

def scrape_profile_hybrid(username):
    """
    하이브리드 프로필 스크래핑
    GramAddict ProfileView + 안전 기능
    """
    try:
        logger.info(f"=== 프로필 스크래핑 시작: @{username} ===")

        # 1. 기기 연결 (GramAddict)
        logger.info("기기 연결 중...")
        device = DeviceFacade(DEVICE_ID, "com.instagram.android")
        logger.info(f"✓ 기기 연결 완료")

        # 2. 검색 탭으로 이동 (UIAutomator2 직접 사용)
        logger.info("검색 탭 클릭...")
        screen_info = device.get_info()
        screen_width = screen_info['displayWidth']
        screen_height = screen_info['displayHeight']

        # 하단 네비게이션 - 검색 아이콘
        search_x = screen_width * 3 // 10
        search_y = screen_height - 100
        device.deviceV2.click(search_x, search_y)
        random_sleep(2, 3)

        # 3. 검색창 클릭
        logger.info(f"검색: {username}")
        device.deviceV2.click(screen_width // 2, 120)
        random_sleep(1, 2)

        # 4. 사용자명 입력 (ADB)
        import subprocess
        subprocess.run(
            ['adb', '-s', DEVICE_ID, 'shell', 'input', 'text', username],
            capture_output=True
        )
        random_sleep(3, 4)

        # 5. 첫 번째 결과 클릭
        logger.info("검색 결과 선택...")
        device.deviceV2.click(screen_width // 2, 300)
        random_sleep(3, 5)

        # 6. 프로필 정보 추출 (GramAddict ProfileView)
        logger.info("프로필 정보 수집 중...")
        profile_view = ProfileView(device)

        followers = profile_view.getFollowersCount()
        following = profile_view.getFollowingCount()
        posts = profile_view.getPostsCount()
        full_name = profile_view.getFullName()
        is_private = profile_view.isPrivateAccount()

        # 7. 결과 출력
        logger.info(f"✓ 프로필 정보:")
        logger.info(f"  - 사용자: @{username}")
        logger.info(f"  - 이름: {full_name}")
        logger.info(f"  - 팔로워: {followers:,}")
        logger.info(f"  - 팔로잉: {following:,}")
        logger.info(f"  - 게시물: {posts:,}")
        logger.info(f"  - 비공개: {is_private}")

        # 8. 데이터베이스 기록
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type="profile_scrape",
            details=f"@{username}: {followers:,} 팔로워, {following:,} 팔로잉, {posts:,} 게시물 [GramAddict Hybrid]"
        )

        # 9. 홈으로 돌아가기
        logger.info("홈으로 이동...")
        home_x = screen_width // 10
        home_y = screen_height - 100
        device.deviceV2.click(home_x, home_y)
        random_sleep(1, 2)

        logger.info("=== 프로필 스크래핑 완료 ===")

        return {
            'username': username,
            'full_name': full_name,
            'followers': followers,
            'following': following,
            'posts': posts,
            'is_private': is_private
        }

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type="profile_scrape",
            details=f"@{username} 실패: {e}",
            status="failed"
        )
        return None

if __name__ == "__main__":
    try:
        result = scrape_profile_hybrid(TARGET_USERNAME)

        if result:
            print(f"\n✅ 성공!")
            print(f"사용자: @{result['username']}")
            print(f"이름: {result['full_name']}")
            print(f"팔로워: {result['followers']:,}")
            print(f"팔로잉: {result['following']:,}")
            print(f"게시물: {result['posts']:,}")
            print(f"비공개: {result['is_private']}")
        else:
            print("\n❌ 실패")

    finally:
        db.close()
        logger.info("데이터베이스 연결 종료")
