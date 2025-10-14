#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
테이블 생성 및 초기 데이터 설정
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger


def main():
    """마이그레이션 실행"""
    logger = get_logger()

    logger.info("=" * 50)
    logger.info("데이터베이스 마이그레이션 시작")
    logger.info("=" * 50)

    try:
        # 데이터베이스 연결
        logger.info("데이터베이스 연결 중...")
        db = DatabaseHandler()
        logger.info("✓ 데이터베이스 연결 성공")

        # 테이블은 DatabaseHandler 초기화 시 자동 생성됨
        logger.info("✓ 테이블 생성/확인 완료")

        # 연결 테스트
        logger.info("연결 테스트 중...")
        import uuid
        test_session_id = str(uuid.uuid4())

        # 테스트 세션 생성
        db.create_session(
            session_id=test_session_id,
            username="migration_test",
            device_id="test_device",
            metadata={"test": True, "migration": True}
        )
        logger.info("✓ 세션 생성 테스트 성공")

        # 세션 조회
        stats = db.get_session_stats(test_session_id)
        if stats:
            logger.info(f"✓ 세션 조회 테스트 성공 (ID: {test_session_id[:8]}...)")
        else:
            logger.error("✗ 세션 조회 실패")
            sys.exit(1)

        # 테스트 세션 삭제 (정리)
        cursor = db.connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (test_session_id,))
        db.connection.commit()
        cursor.close()
        logger.info("✓ 테스트 데이터 정리 완료")

        # 테이블 정보 출력
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        cursor.close()

        logger.info("\n생성된 테이블:")
        for table in tables:
            logger.info(f"  - {table[0]}")

        # 인덱스 정보
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        indexes = cursor.fetchall()
        cursor.close()

        logger.info("\n생성된 인덱스:")
        current_table = None
        for idx_name, table_name in indexes:
            if current_table != table_name:
                logger.info(f"\n  [{table_name}]")
                current_table = table_name
            logger.info(f"    - {idx_name}")

        db.close()

        logger.info("\n" + "=" * 50)
        logger.info("✓ 마이그레이션 완료!")
        logger.info("=" * 50)

        return 0

    except Exception as e:
        logger.error(f"\n✗ 마이그레이션 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
