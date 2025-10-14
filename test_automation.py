#!/usr/bin/env python3
"""
간단한 Instagram 자동화 테스트 with 데이터베이스 로깅
"""
import uiautomator2 as u2
import time
from datetime import datetime
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger

# 로거 설정
logger = get_logger()

# 데이터베이스 연결
db = DatabaseHandler()
logger.info("데이터베이스 연결 완료")

# 기기 연결
DEVICE_ID = "R3CN70D9ZBY"
d = u2.connect(DEVICE_ID)
logger.info(f"기기 연결 완료: {d.info['productName']}")

# 계정 정보 (현재 로그인된 계정)
ACCOUNT_NAME = "hyoeunsagong"

def log_action(action_type, details, status="success"):
    """작업을 데이터베이스에 기록"""
    try:
        db.log_action(
            account_name=ACCOUNT_NAME,
            action_type=action_type,
            details=details,
            status=status
        )
        logger.info(f"✓ DB 기록: {action_type} - {details}")
    except Exception as e:
        logger.error(f"✗ DB 기록 실패: {e}")

def test_instagram_automation():
    """Instagram 자동화 테스트"""

    logger.info("=== Instagram 자동화 시작 ===")

    # 1. Instagram 앱 실행
    try:
        logger.info("1. Instagram 앱 실행...")
        # ADB로 직접 실행 (UIAutomator2의 app_start 이슈 회피)
        import subprocess
        subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'monkey', '-p',
                       'com.instagram.android', '-c', 'android.intent.category.LAUNCHER', '1'],
                      capture_output=True)
        time.sleep(3)
        log_action("app_start", "Instagram 앱 실행")
        logger.info("✓ Instagram 앱 실행 완료")
    except Exception as e:
        logger.error(f"✗ 앱 실행 실패: {e}")
        log_action("app_start", f"실패: {e}", "failed")
        return

    # 2. 화면 캡처
    try:
        logger.info("2. 초기 화면 캡처...")
        screenshot_path = f"/tmp/instagram_{int(time.time())}.png"
        d.screenshot(screenshot_path)
        log_action("screenshot", f"화면 캡처: {screenshot_path}")
        logger.info(f"✓ 스크린샷 저장: {screenshot_path}")
    except Exception as e:
        logger.error(f"✗ 스크린샷 실패: {e}")

    # 3. 피드 스크롤
    try:
        logger.info("3. 피드 스크롤...")
        d.swipe(500, 1200, 500, 400, 0.1)
        time.sleep(1)
        log_action("scroll", "피드 아래로 스크롤")
        logger.info("✓ 스크롤 완료")
    except Exception as e:
        logger.error(f"✗ 스크롤 실패: {e}")
        log_action("scroll", f"실패: {e}", "failed")

    # 4. 좋아요 클릭
    try:
        logger.info("4. 좋아요 버튼 클릭...")
        d.click(48, 387)
        time.sleep(1)
        log_action("like", "게시물 좋아요")
        logger.info("✓ 좋아요 완료")
    except Exception as e:
        logger.error(f"✗ 좋아요 실패: {e}")
        log_action("like", f"실패: {e}", "failed")

    # 5. 다시 위로 스크롤
    try:
        logger.info("5. 위로 스크롤...")
        d.swipe(500, 400, 500, 1200, 0.1)
        time.sleep(1)
        log_action("scroll", "피드 위로 스크롤")
        logger.info("✓ 스크롤 완료")
    except Exception as e:
        logger.error(f"✗ 스크롤 실패: {e}")

    # 6. 최종 화면 캡처
    try:
        logger.info("6. 최종 화면 캡처...")
        screenshot_path = f"/tmp/instagram_final_{int(time.time())}.png"
        d.screenshot(screenshot_path)
        log_action("screenshot", f"최종 화면 캡처: {screenshot_path}")
        logger.info(f"✓ 스크린샷 저장: {screenshot_path}")
    except Exception as e:
        logger.error(f"✗ 스크린샷 실패: {e}")

    logger.info("=== Instagram 자동화 완료 ===")

def view_logs():
    """데이터베이스에 기록된 로그 조회"""
    logger.info("\n=== 최근 작업 로그 (최근 10개) ===")
    try:
        logs = db.get_recent_logs(account_name=ACCOUNT_NAME, limit=10)
        if logs:
            for log in logs:
                print(f"[{log['timestamp']}] {log['action_type']:12} | {log['status']:8} | {log['details']}")
        else:
            logger.info("기록된 로그가 없습니다.")
    except Exception as e:
        logger.error(f"로그 조회 실패: {e}")

if __name__ == "__main__":
    try:
        # 자동화 실행
        test_instagram_automation()

        # 로그 조회
        view_logs()

    finally:
        # 정리
        db.close()
        logger.info("데이터베이스 연결 종료")
