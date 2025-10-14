#!/usr/bin/env python3
"""
Instagram Automation System - Main Entry Point
GramAddict 기반 Instagram 자동화 시스템
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.wrapper.task_manager import TaskManager
from src.wrapper.log_parser import LogParser


def main():
    """메인 함수"""
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(
        description='Instagram Automation System (GramAddict 기반)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 실행
  python3 src/main.py --config config/accounts/myaccount.yml

  # 디바이스 연결 확인만
  python3 src/main.py --check-device

  # 로그 파싱
  python3 src/main.py --parse-logs logs/gramaddict --session SESSION_ID
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        help='계정 설정 파일 경로 (예: config/accounts/myaccount.yml)'
    )

    parser.add_argument(
        '--check-device',
        action='store_true',
        help='ADB 디바이스 연결 확인만 수행'
    )

    parser.add_argument(
        '--parse-logs',
        type=str,
        metavar='LOG_DIR',
        help='로그 디렉토리 파싱 (로그 분석용)'
    )

    parser.add_argument(
        '--session',
        type=str,
        help='세션 ID (로그 파싱 시 필요)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='최근 세션 통계 출력'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )

    args = parser.parse_args()

    # 로거 초기화
    logger = get_logger()

    # 인자 검증
    if not any([args.config, args.check_device, args.parse_logs, args.stats]):
        parser.print_help()
        sys.exit(1)

    try:
        # 디바이스 연결 확인 모드
        if args.check_device:
            logger.info("=== ADB 디바이스 연결 확인 ===")
            task_manager = TaskManager("config/accounts/example.yml")  # 더미 설정
            if task_manager.check_device_connection():
                logger.info("✅ 디바이스 연결 성공")
                sys.exit(0)
            else:
                logger.error("❌ 디바이스 연결 실패")
                logger.info("\n해결 방법:")
                logger.info("1. Android 디바이스를 USB로 연결하세요")
                logger.info("2. 디바이스에서 USB 디버깅을 활성화하세요")
                logger.info("3. 'adb devices' 명령어로 연결을 확인하세요")
                sys.exit(1)

        # 로그 파싱 모드
        elif args.parse_logs:
            if not args.session:
                logger.error("--session 인자가 필요합니다")
                sys.exit(1)

            logger.info(f"=== 로그 파싱 시작: {args.parse_logs} ===")
            parser = LogParser()
            stats = parser.parse_log_directory(args.parse_logs, args.session)

            if 'error' in stats:
                logger.error(f"로그 파싱 실패: {stats['error']}")
                sys.exit(1)
            else:
                logger.info("=== 파싱 결과 ===")
                logger.info(f"파일 수: {stats['total_files']}")
                logger.info(f"총 라인 수: {stats['total_lines']}")
                logger.info(f"좋아요: {stats['likes']}")
                logger.info(f"팔로우: {stats['follows']}")
                logger.info(f"언팔로우: {stats['unfollows']}")
                logger.info(f"댓글: {stats['comments']}")
                logger.info(f"에러: {stats['errors']}")
                parser.close()
                sys.exit(0)

        # 통계 출력 모드
        elif args.stats:
            if not args.config:
                logger.error("--config 인자가 필요합니다")
                sys.exit(1)

            logger.info("=== 최근 세션 통계 ===")
            task_manager = TaskManager(args.config)
            sessions = task_manager.get_recent_sessions(limit=10)

            if not sessions:
                logger.info("세션 기록이 없습니다")
            else:
                for i, session in enumerate(sessions, 1):
                    logger.info(f"\n[{i}] Session ID: {session['session_id'][:8]}...")
                    logger.info(f"    시작: {session['start_time']}")
                    logger.info(f"    종료: {session.get('end_time', 'N/A')}")
                    logger.info(f"    상태: {session.get('status', 'unknown')}")
                    logger.info(f"    좋아요: {session.get('total_likes', 0)}")
                    logger.info(f"    팔로우: {session.get('total_follows', 0)}")
                    logger.info(f"    에러: {session.get('errors', 0)}")

            task_manager.close()
            sys.exit(0)

        # 메인 실행 모드
        elif args.config:
            logger.info("=" * 50)
            logger.info("Instagram Automation System 시작")
            logger.info("=" * 50)

            # 설정 파일 존재 확인
            if not Path(args.config).exists():
                logger.error(f"설정 파일을 찾을 수 없습니다: {args.config}")
                logger.info("\n설정 파일 생성 방법:")
                logger.info("1. config/accounts/example.yml 파일을 복사하세요")
                logger.info("2. Instagram 계정 정보를 입력하세요")
                logger.info("3. 작업 설정을 조정하세요")
                sys.exit(1)

            # Task Manager 실행
            with TaskManager(args.config) as task_manager:
                # 디바이스 연결 확인
                logger.info("디바이스 연결 확인 중...")
                if not task_manager.check_device_connection():
                    logger.error("디바이스가 연결되지 않았습니다")
                    logger.info("ADB 디바이스를 연결한 후 다시 시도하세요")
                    sys.exit(1)

                logger.info("✅ 디바이스 연결 확인 완료")

                # GramAddict 실행
                logger.info("GramAddict 실행 중...")
                result = task_manager.run()

                # 결과 출력
                if result.succeeded:
                    logger.info("=" * 50)
                    logger.info("✅ 작업 완료")
                    logger.info("=" * 50)

                    # 세션 통계
                    stats = task_manager.get_session_stats(result.session_id)
                    if stats:
                        logger.info(f"좋아요: {stats.get('total_likes', 0)}")
                        logger.info(f"팔로우: {stats.get('total_follows', 0)}")
                        logger.info(f"언팔로우: {stats.get('total_unfollows', 0)}")
                        logger.info(f"댓글: {stats.get('total_comments', 0)}")
                        logger.info(f"에러: {stats.get('errors', 0)}")

                    logger.info("로그 위치: %s", result.runtime_paths.log_dir)
                    sys.exit(0)
                else:
                    logger.error("=" * 50)
                    logger.error("❌ 작업 실패")
                    logger.error("=" * 50)
                    logger.error(f"오류 메시지: {result.stderr.strip() or 'Unknown error'}")
                    logger.error(f"로그 확인: {result.stderr_log_path}")
                    sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 중단되었습니다")
        sys.exit(130)
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
