#!/usr/bin/env python3
"""
Instagram 프로필 스크래퍼 with GramAddict 통합
"""
import sys
import time
from datetime import datetime
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

# GramAddict 모듈 import
from GramAddict.core.device_facade import DeviceFacade
from GramAddict.core.views import ProfileView
from GramAddict.core.navigation import nav_to_blogger

# 설정
DEVICE_ID = "R3CN70D9ZBY"
ACCOUNT_NAME = "hyoeunsagong"

# 초기화
logger = get_logger()
db = DatabaseHandler()

def scrape_profile(username: str):
    """
    특정 사용자의 프로필 정보를 스크래핑

    Args:
        username: Instagram 사용자명

    Returns:
        dict: 프로필 정보 (followers, following, posts)
    """
    try:
        logger.info(f"=== 프로필 스크래핑 시작: @{username} ===")

        # 1. 기기 연결
        logger.info("기기 연결 중...")
        device = DeviceFacade(DEVICE_ID, app_id="com.instagram.android")
        logger.info(f"✓ 기기 연결 완료: {device.device_id}")

        # 2. 사용자 프로필로 이동 (GramAddict 내장 함수 사용)
        logger.info(f"@{username} 프로필로 이동...")
        result = nav_to_blogger(device, username, None)

        if not result:
            logger.error(f"프로필 이동 실패: @{username}")
            return None

        logger.info(f"✓ @{username} 프로필 열기 완료")
        time.sleep(2)

        # 5. 프로필 정보 추출
        logger.info("프로필 정보 추출 중...")
        profile_view = ProfileView(device)

        # 팔로워 수 가져오기
        followers_count = profile_view.getFollowersCount()
        following_count = profile_view.getFollowingCount()
        posts_count = profile_view.getPostsCount()

        profile_data = {
            'username': username,
            'followers': followers_count,
            'following': following_count,
            'posts': posts_count,
            'scraped_at': datetime.now()
        }

        logger.info(f"✓ 프로필 정보:")
        logger.info(f"  - 팔로워: {followers_count}")
        logger.info(f"  - 팔로잉: {following_count}")
        logger.info(f"  - 게시물: {posts_count}")

        # 6. 데이터베이스에 기록
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type="profile_scrape",
            details=f"@{username}: {followers_count} 팔로워, {following_count} 팔로잉, {posts_count} 게시물",
            status="success"
        )
        logger.info("✓ 데이터베이스 기록 완료")

        # 7. 뒤로가기 - 홈으로
        device.back()
        time.sleep(1)
        navigate(device, Tabs.HOME)

        logger.info("=== 프로필 스크래핑 완료 ===\n")
        return profile_data

    except Exception as e:
        logger.error(f"프로필 스크래핑 실패: {e}")
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type="profile_scrape",
            details=f"@{username} 스크래핑 실패: {e}",
            status="failed"
        )
        return None

def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("사용법: python profile_scraper.py <username>")
        print("예시: python profile_scraper.py hon.hono7")
        sys.exit(1)

    target_username = sys.argv[1]

    try:
        result = scrape_profile(target_username)

        if result:
            print(f"\n✅ 성공!")
            print(f"사용자: @{result['username']}")
            print(f"팔로워: {result['followers']:,}")
            print(f"팔로잉: {result['following']:,}")
            print(f"게시물: {result['posts']:,}")
        else:
            print("\n❌ 스크래핑 실패")
            sys.exit(1)

    finally:
        db.close()
        logger.info("데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
