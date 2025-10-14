"""
Log Parser
GramAddict 로그를 파싱하여 데이터베이스에 저장
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, Any

from ..utils.logger import get_logger
from ..utils.db_handler import DatabaseHandler


class LogParser:
    """GramAddict 로그 파서"""

    def __init__(self, db_handler: Optional[DatabaseHandler] = None):
        """
        로그 파서 초기화

        Args:
            db_handler: 데이터베이스 핸들러 (None이면 새로 생성)
        """
        self.logger = get_logger()
        self.db = db_handler or DatabaseHandler()

        # GramAddict 로그 패턴 정의 (더 정교한 매칭)
        self.patterns = {
            # 좋아요: "Liked 3 photos of @username"
            'like': re.compile(
                r'(liked?\s+(?:the\s+)?(?:photo|post|image))|'
                r'(liked?\s+\d+\s+(?:photo|post|image)s?)',
                re.IGNORECASE
            ),
            # 팔로우: "Followed @username" or "Following @username"
            'follow': re.compile(
                r'(?:followed?|following)\s+@?(\w+)',
                re.IGNORECASE
            ),
            # 언팔로우: "Unfollowed @username"
            'unfollow': re.compile(
                r'unfollowed?\s+@?(\w+)',
                re.IGNORECASE
            ),
            # 댓글: "Commented: 'Nice photo!'"
            'comment': re.compile(
                r'commented?[:|\s]+[\'"]?(.+?)[\'"]?$',
                re.IGNORECASE
            ),
            # 에러: 다양한 에러 패턴
            'error': re.compile(
                r'(error|exception|failed?|crash|timeout|not\s+found)|'
                r'(\[ERROR\]|\[CRITICAL\])|'
                r'(traceback)',
                re.IGNORECASE
            ),
            # 성공
            'success': re.compile(
                r'(success|done|completed?|finished)|'
                r'(\[SUCCESS\]|\[INFO\].*done)',
                re.IGNORECASE
            ),
            # 상호작용 건너뛰기
            'skip': re.compile(
                r'(skip|ignore|pass)(?:ed|ing)?',
                re.IGNORECASE
            ),
            # 세션 정보
            'session_start': re.compile(
                r'(session\s+start|starting\s+session)',
                re.IGNORECASE
            ),
            'session_end': re.compile(
                r'(session\s+end|session\s+finish|total\s+interactions)',
                re.IGNORECASE
            ),
        }

    def parse_log_file(self, log_file_path: str, session_id: str) -> Dict[str, Any]:
        """
        로그 파일 파싱

        Args:
            log_file_path: 로그 파일 경로
            session_id: 세션 ID

        Returns:
            파싱 결과 통계
        """
        log_path = Path(log_file_path)
        if not log_path.exists():
            self.logger.error(f"로그 파일을 찾을 수 없습니다: {log_file_path}")
            return {'error': 'File not found'}

        self.logger.info(f"로그 파일 파싱 시작: {log_file_path}")

        stats = {
            'total_lines': 0,
            'likes': 0,
            'follows': 0,
            'unfollows': 0,
            'comments': 0,
            'errors': 0,
            'parsed_interactions': 0
        }

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_lines'] += 1
                    self._parse_line(line, session_id, stats)

            self.logger.info(f"로그 파싱 완료: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"로그 파싱 중 오류: {e}")
            return {'error': str(e)}

    def _parse_line(self, line: str, session_id: str, stats: Dict[str, Any]):
        """
        로그 한 줄 파싱 (개선된 패턴 매칭)

        Args:
            line: 로그 라인
            session_id: 세션 ID
            stats: 통계 딕셔너리 (업데이트됨)
        """
        line = line.strip()
        if not line:
            return

        # 에러 먼저 체크 (우선순위 높음)
        if self.patterns['error'].search(line):
            self._log_interaction(session_id, 'error', 'error', 'failed', error_message=line[:500])
            stats['errors'] += 1
            return

        # 좋아요
        match = self.patterns['like'].search(line)
        if match:
            self._log_interaction(session_id, 'post', 'like', 'success')
            stats['likes'] += 1
            stats['parsed_interactions'] += 1
            return

        # 팔로우
        match = self.patterns['follow'].search(line)
        if match:
            target_user = match.group(1) if match.groups() else None
            self._log_interaction(session_id, 'user', 'follow', 'success', target_user=target_user)
            stats['follows'] += 1
            stats['parsed_interactions'] += 1
            return

        # 언팔로우
        match = self.patterns['unfollow'].search(line)
        if match:
            target_user = match.group(1) if match.groups() else None
            self._log_interaction(session_id, 'user', 'unfollow', 'success', target_user=target_user)
            stats['unfollows'] += 1
            stats['parsed_interactions'] += 1
            return

        # 댓글
        match = self.patterns['comment'].search(line)
        if match:
            self._log_interaction(session_id, 'post', 'comment', 'success')
            stats['comments'] += 1
            stats['parsed_interactions'] += 1
            return

        # 세션 시작/종료 (통계만 업데이트)
        if self.patterns['session_start'].search(line):
            stats.setdefault('session_events', []).append('start')
        elif self.patterns['session_end'].search(line):
            stats.setdefault('session_events', []).append('end')

    def _log_interaction(self, session_id: str, interaction_type: str, action: str,
                        status: str, target_user: Optional[str] = None,
                        error_message: Optional[str] = None):
        """인터랙션 데이터베이스 기록"""
        try:
            self.db.log_interaction(
                session_id=session_id,
                interaction_type=interaction_type,
                action=action,
                status=status,
                target_user=target_user,
                error_message=error_message
            )
        except Exception as e:
            self.logger.error(f"인터랙션 로그 저장 실패: {e}")

    def parse_log_directory(self, log_dir: str, session_id: str) -> Dict[str, Any]:
        """
        로그 디렉토리 내 모든 로그 파일 파싱

        Args:
            log_dir: 로그 디렉토리 경로
            session_id: 세션 ID

        Returns:
            전체 파싱 결과 통계
        """
        log_path = Path(log_dir)
        if not log_path.exists() or not log_path.is_dir():
            self.logger.error(f"로그 디렉토리를 찾을 수 없습니다: {log_dir}")
            return {'error': 'Directory not found'}

        total_stats = {
            'total_files': 0,
            'total_lines': 0,
            'likes': 0,
            'follows': 0,
            'unfollows': 0,
            'comments': 0,
            'errors': 0,
            'parsed_interactions': 0
        }

        # .log 파일만 파싱
        log_files = list(log_path.glob('*.log'))
        self.logger.info(f"발견된 로그 파일 수: {len(log_files)}")

        for log_file in log_files:
            self.logger.debug(f"파싱 중: {log_file.name}")
            stats = self.parse_log_file(str(log_file), session_id)

            if 'error' not in stats:
                total_stats['total_files'] += 1
                for key in ['total_lines', 'likes', 'follows', 'unfollows', 'comments', 'errors', 'parsed_interactions']:
                    total_stats[key] += stats.get(key, 0)

        self.logger.info(f"로그 디렉토리 파싱 완료: {total_stats}")
        return total_stats

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 요약 정보 조회"""
        return self.db.get_session_stats(session_id)

    def close(self):
        """리소스 정리"""
        if self.db:
            self.db.close()


if __name__ == "__main__":
    # 테스트
    parser = LogParser()

    # 테스트 로그 생성
    test_log_dir = Path("logs/test")
    test_log_dir.mkdir(parents=True, exist_ok=True)

    test_log_file = test_log_dir / "test.log"
    with open(test_log_file, 'w', encoding='utf-8') as f:
        f.write("2025-10-03 10:00:00 | INFO | Liked post from @user1\n")
        f.write("2025-10-03 10:01:00 | INFO | Followed @user2\n")
        f.write("2025-10-03 10:02:00 | ERROR | Connection failed\n")
        f.write("2025-10-03 10:03:00 | INFO | Commented on post\n")

    # 파싱 테스트
    import uuid
    test_session_id = str(uuid.uuid4())
    stats = parser.parse_log_file(str(test_log_file), test_session_id)
    print("파싱 결과:", stats)

    # 요약 조회
    summary = parser.get_session_summary(test_session_id)
    print("세션 요약:", summary)

    parser.close()
