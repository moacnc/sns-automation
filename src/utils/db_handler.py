"""
데이터베이스 핸들러
PostgreSQL (AlloyDB)를 사용한 작업 로그 저장 및 조회
"""

from __future__ import annotations

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from dotenv import load_dotenv


class DatabaseHandler:
    """PostgreSQL 데이터베이스 핸들러 (AlloyDB 호환)"""

    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """
        데이터베이스 핸들러 초기화

        Args:
            db_config: 데이터베이스 설정 딕셔너리
                {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'instagram_automation',
                    'user': 'username',
                    'password': 'password'
                }
                None일 경우 환경변수에서 로드
        """
        # 환경변수 로드
        load_dotenv()

        # 설정 우선순위: 인자 > 환경변수 > 기본값
        self.config = db_config or self._load_config_from_env()

        self.connection = None
        self.pool = None
        self._init_connection()
        self._init_database()

    def _load_config_from_env(self) -> Dict[str, str]:
        """환경변수에서 데이터베이스 설정 로드"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'instagram_automation'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'sslmode': os.getenv('DB_SSLMODE', 'prefer')  # AlloyDB는 'require' 권장
        }

    def _init_connection(self, max_retries: int = 3, retry_delay: int = 2):
        """
        데이터베이스 연결 초기화 (재시도 로직 포함)

        Args:
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간 대기 시간 (초)
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # 커넥션 풀 생성 (성능 향상)
                self.pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['database'],
                    user=self.config['user'],
                    password=self.config['password'],
                    sslmode=self.config.get('sslmode', 'prefer'),
                    connect_timeout=10  # 연결 타임아웃 10초
                )

                # 단일 연결 (기본 작업용)
                self.connection = self.pool.getconn()
                self.connection.autocommit = False

                # 연결 테스트
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()

                return  # 연결 성공

            except psycopg2.Error as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        # 모든 재시도 실패
        raise ConnectionError(
            f"데이터베이스 연결 실패 ({max_retries}회 시도): {last_error}"
        )

    def _ensure_connection(self):
        """
        연결 상태 확인 및 필요시 재연결

        Returns:
            bool: 연결 성공 여부
        """
        try:
            if self.connection is None or self.connection.closed:
                self.connection = self.pool.getconn()
                self.connection.autocommit = False
                return True

            # 연결 테스트
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True

        except (psycopg2.Error, AttributeError):
            # 재연결 시도
            try:
                if self.connection and not self.connection.closed:
                    self.pool.putconn(self.connection)
                self.connection = self.pool.getconn()
                self.connection.autocommit = False
                return True
            except psycopg2.Error:
                return False

    def _init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        self._ensure_connection()
        cursor = self.connection.cursor()

        try:
            # 세션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    device_id VARCHAR(255),
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status VARCHAR(50),
                    total_interactions INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_follows INTEGER DEFAULT 0,
                    total_unfollows INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 세션 인덱스
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_username
                ON sessions(username)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time
                ON sessions(start_time DESC)
            """)

            # 인터랙션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    interaction_type VARCHAR(50) NOT NULL,
                    target_user VARCHAR(255),
                    target_post VARCHAR(255),
                    action VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    duration_ms INTEGER,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)

            # 인터랙션 인덱스
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_interactions_session
                ON interactions(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_interactions_timestamp
                ON interactions(timestamp DESC)
            """)

            # 통계 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    total_likes INTEGER DEFAULT 0,
                    total_follows INTEGER DEFAULT 0,
                    total_unfollows INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    sessions_count INTEGER DEFAULT 0,
                    success_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(username, date)
                )
            """)

            # 통계 인덱스
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_statistics_username_date
                ON statistics(username, date DESC)
            """)

            self.connection.commit()

        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"테이블 생성 실패: {e}")
        finally:
            cursor.close()

    def create_session(self, session_id: str, username: str, device_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        새 세션 생성

        Args:
            session_id: 세션 ID
            username: Instagram 사용자명
            device_id: 디바이스 ID
            metadata: 추가 메타데이터

        Returns:
            생성된 세션의 DB ID
        """
        self._ensure_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO sessions (session_id, username, device_id, start_time, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_id,
                username,
                device_id,
                datetime.now(),
                'running',
                json.dumps(metadata) if metadata else None
            ))
            result = cursor.fetchone()
            self.connection.commit()
            return result[0] if result else None
        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"세션 생성 실패: {e}")
        finally:
            cursor.close()

    def update_session(self, session_id: str, **kwargs):
        """
        세션 정보 업데이트

        Args:
            session_id: 세션 ID
            **kwargs: 업데이트할 필드들
        """
        if not kwargs:
            return

        self._ensure_connection()
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"""
                UPDATE sessions
                SET {set_clause}
                WHERE session_id = %s
            """, values)
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"세션 업데이트 실패: {e}")
        finally:
            cursor.close()

    def end_session(self, session_id: str, status: str = 'completed'):
        """
        세션 종료

        Args:
            session_id: 세션 ID
            status: 종료 상태 (completed, failed, stopped)
        """
        self.update_session(
            session_id,
            end_time=datetime.now(),
            status=status
        )

    def log_interaction(self, session_id: str, interaction_type: str, action: str,
                       status: str, target_user: Optional[str] = None,
                       target_post: Optional[str] = None, duration_ms: Optional[int] = None,
                       error_message: Optional[str] = None):
        """
        인터랙션 로그 기록

        Args:
            session_id: 세션 ID
            interaction_type: 인터랙션 타입 (hashtag, user, post 등)
            action: 수행한 액션 (like, follow, comment 등)
            status: 상태 (success, failed)
            target_user: 대상 사용자
            target_post: 대상 게시물
            duration_ms: 소요 시간 (밀리초)
            error_message: 에러 메시지
        """
        self._ensure_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO interactions
                (session_id, interaction_type, target_user, target_post, action, status, duration_ms, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, interaction_type, target_user, target_post, action, status, duration_ms, error_message))
            self.connection.commit()

            # 세션 통계 업데이트
            self._update_session_stats(session_id, action, status)
        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"인터랙션 로그 실패: {e}")
        finally:
            cursor.close()

    def _update_session_stats(self, session_id: str, action: str, status: str):
        """세션 통계 업데이트"""
        field_map = {
            'like': 'total_likes',
            'follow': 'total_follows',
            'unfollow': 'total_unfollows',
            'comment': 'total_comments'
        }

        updates = {'total_interactions': 1}
        if status != 'success':
            updates['errors'] = 1

        if action in field_map:
            updates[field_map[action]] = 1

        # 증가 업데이트
        set_clause = ", ".join([f"{key} = {key} + %s" for key in updates.keys()])
        values = list(updates.values()) + [session_id]

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"""
                UPDATE sessions
                SET {set_clause}
                WHERE session_id = %s
            """, values)
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"통계 업데이트 실패: {e}")
        finally:
            cursor.close()

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 통계 조회"""
        self._ensure_connection()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM sessions WHERE session_id = %s
            """, (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()

    def get_daily_stats(self, username: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """일일 통계 조회"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self._ensure_connection()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM statistics WHERE username = %s AND date = %s
            """, (username, date))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()

    def get_recent_sessions(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 세션 목록 조회"""
        self._ensure_connection()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM sessions
                WHERE username = %s
                ORDER BY start_time DESC
                LIMIT %s
            """, (username, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def log_action(self, account_name: str, action_type: str, details: str, status: str = "success"):
        """
        간단한 작업 로그 기록 (세션 없이)

        Args:
            account_name: 계정 이름
            action_type: 작업 타입 (app_start, scroll, like, screenshot 등)
            details: 작업 상세 내용
            status: 상태 (success, failed)
        """
        # 임시 세션 ID 생성
        import uuid
        session_id = f"quick_{uuid.uuid4().hex[:8]}"

        # 세션이 없으면 생성
        self._ensure_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO sessions (session_id, username, start_time, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (session_id, account_name, datetime.now(), 'running'))

            # 인터랙션 기록
            cursor.execute("""
                INSERT INTO interactions
                (session_id, interaction_type, action, status, error_message, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session_id, action_type, action_type, status, details if status == 'failed' else None, datetime.now()))

            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            raise Exception(f"작업 로그 실패: {e}")
        finally:
            cursor.close()

    def get_recent_logs(self, account_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최근 작업 로그 조회

        Args:
            account_name: 계정 이름 (None이면 전체)
            limit: 조회 개수

        Returns:
            로그 목록
        """
        self._ensure_connection()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            if account_name:
                cursor.execute("""
                    SELECT i.*, s.username
                    FROM interactions i
                    JOIN sessions s ON i.session_id = s.session_id
                    WHERE s.username = %s
                    ORDER BY i.timestamp DESC
                    LIMIT %s
                """, (account_name, limit))
            else:
                cursor.execute("""
                    SELECT i.*, s.username
                    FROM interactions i
                    JOIN sessions s ON i.session_id = s.session_id
                    ORDER BY i.timestamp DESC
                    LIMIT %s
                """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'timestamp': row['timestamp'],
                    'action_type': row['action'],
                    'status': row['status'],
                    'details': row['error_message'] or f"{row['interaction_type']} 작업"
                })
            return results
        finally:
            cursor.close()

    def execute_query(self, query: str, params: tuple = None) -> None:
        """
        쿼리 실행 (INSERT, UPDATE, DELETE)

        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 파라미터 튜플
        """
        self._ensure_connection()
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def fetch_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        SELECT 쿼리 실행

        Args:
            query: 실행할 SELECT 쿼리
            params: 쿼리 파라미터 튜플

        Returns:
            결과 리스트 (딕셔너리 형태)
        """
        self._ensure_connection()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            cursor.close()

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.pool.putconn(self.connection)
        if self.pool:
            self.pool.closeall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # 테스트
    import uuid

    # 테스트용 설정 (실제 사용 시 환경변수 사용)
    test_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'instagram_automation',
        'user': 'postgres',
        'password': 'password'
    }

    try:
        db = DatabaseHandler(test_config)

        # 세션 생성
        session_id = str(uuid.uuid4())
        db.create_session(session_id, "test_user", "device123", {"test": True})

        # 인터랙션 로그
        db.log_interaction(session_id, "hashtag", "like", "success", target_user="user1", duration_ms=1500)
        db.log_interaction(session_id, "hashtag", "follow", "success", target_user="user2", duration_ms=2000)

        # 세션 종료
        db.end_session(session_id, "completed")

        # 통계 조회
        stats = db.get_session_stats(session_id)
        print("세션 통계:", stats)

        db.close()
    except Exception as e:
        print(f"테스트 실패: {e}")
