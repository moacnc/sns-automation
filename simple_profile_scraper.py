#!/usr/bin/env python3
"""
Instagram 프로필 스크래퍼 (간단 버전)
UIAutomator2 직접 사용
"""
import sys
import time
import re
from datetime import datetime
import uiautomator2 as u2
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

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
        username: Instagram 사용자명 (@ 없이)

    Returns:
        dict: 프로필 정보 (followers, following, posts)
    """
    try:
        logger.info(f"=== 프로필 스크래핑 시작: @{username} ===")

        # 1. 기기 연결
        logger.info("기기 연결 중...")
        d = u2.connect(DEVICE_ID)
        logger.info(f"✓ 기기 연결 완료")

        # 2. 검색 탭 클릭 (하단 네비게이션)
        logger.info("검색 탭으로 이동...")
        screen_width = d.info['displayWidth']
        screen_height = d.info['displayHeight']
        search_x = screen_width * 3 // 10
        search_y = screen_height - 100
        d.click(search_x, search_y)
        time.sleep(2)

        # 3. 검색창 클릭 및 사용자명 입력
        logger.info(f"사용자 검색: {username}")
        # 검색창 클릭 (상단)
        d.click(screen_width // 2, 120)
        time.sleep(1)

        # 사용자명 입력 (ADB 직접 사용)
        import subprocess
        subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'input', 'text', username],
                      capture_output=True)
        time.sleep(3)

        # 4. 첫 번째 결과 클릭 (사용자 프로필)
        logger.info("검색 결과에서 프로필 선택...")
        # 검색 결과 첫 번째 항목 (대략적인 위치)
        d.click(screen_width // 2, 300)
        time.sleep(3)

        # 5. 프로필 페이지에서 정보 추출
        logger.info("프로필 정보 추출 중...")

        # 스크린샷 저장
        screenshot_path = f"/tmp/profile_{username}_{int(time.time())}.png"
        d.screenshot(screenshot_path)
        logger.info(f"스크린샷 저장: {screenshot_path}")

        # UI 텍스트에서 숫자 찾기
        # Instagram 프로필 구조: 게시물 / 팔로워 / 팔로잉
        time.sleep(2)

        # XML dump로 화면 요소 가져오기
        xml = d.dump_hierarchy()

        # 숫자 패턴 찾기 (게시물, 팔로워, 팔로잉)
        # 패턴: "68 게시물", "11.8만 팔로워", "82 팔로잉"

        def parse_korean_number(text):
            """한국어 숫자 표현 파싱 (만, 천 등)"""
            if not text:
                return 0
            text = text.replace(',', '').strip()

            if '만' in text:
                # "11.8만" -> 118000
                num = float(text.replace('만', ''))
                return int(num * 10000)
            elif '천' in text:
                # "1.5천" -> 1500
                num = float(text.replace('천', ''))
                return int(num * 1000)
            else:
                try:
                    return int(text)
                except:
                    return 0

        posts_match = re.search(r'([\\d,]+)\\s*게시물', xml)
        followers_match = re.search(r'([\\d,.]+만?)\\s*팔로워', xml)
        following_match = re.search(r'([\\d,]+)\\s*팔로잉', xml)

        posts_count = parse_korean_number(posts_match.group(1)) if posts_match else 0
        followers_count = parse_korean_number(followers_match.group(1)) if followers_match else 0
        following_count = parse_korean_number(following_match.group(1)) if following_match else 0

        profile_data = {
            'username': username,
            'followers': followers_count,
            'following': following_count,
            'posts': posts_count,
            'scraped_at': datetime.now(),
            'screenshot': screenshot_path
        }

        logger.info(f"✓ 프로필 정보:")
        logger.info(f"  - 사용자: @{username}")
        logger.info(f"  - 팔로워: {followers_count:,}")
        logger.info(f"  - 팔로잉: {following_count:,}")
        logger.info(f"  - 게시물: {posts_count:,}")

        # 6. 데이터베이스에 기록
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type="profile_scrape",
            details=f"@{username}: {followers_count:,} 팔로워, {following_count:,} 팔로잉, {posts_count:,} 게시물",
            status="success"
        )
        logger.info("✓ 데이터베이스 기록 완료")

        # 7. 홈으로 돌아가기
        home_x = screen_width // 10
        home_y = screen_height - 100
        d.click(home_x, home_y)
        time.sleep(1)

        logger.info("=== 프로필 스크래핑 완료 ===\\n")
        return profile_data

    except Exception as e:
        logger.error(f"프로필 스크래핑 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        print("사용법: python simple_profile_scraper.py <username>")
        print("예시: python simple_profile_scraper.py hon.hono7")
        sys.exit(1)

    target_username = sys.argv[1].replace('@', '')  # @ 제거

    try:
        result = scrape_profile(target_username)

        if result:
            print(f"\\n✅ 성공!")
            print(f"사용자: @{result['username']}")
            print(f"팔로워: {result['followers']:,}")
            print(f"팔로잉: {result['following']:,}")
            print(f"게시물: {result['posts']:,}")
            print(f"스크린샷: {result['screenshot']}")
        else:
            print("\\n❌ 스크래핑 실패")
            sys.exit(1)

    finally:
        db.close()
        logger.info("데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
