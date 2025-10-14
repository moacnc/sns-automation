"""
Log Parser 테스트
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.wrapper.log_parser import LogParser


class TestLogParser:
    """LogParser 테스트"""

    @pytest.fixture
    def temp_log_dir(self):
        """임시 로그 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_log_file(self, temp_log_dir):
        """샘플 로그 파일 생성"""
        log_content = """
2025-10-10 10:00:00 | INFO | Session start
2025-10-10 10:01:00 | INFO | Liked photo of @user1
2025-10-10 10:02:00 | INFO | Followed @user2
2025-10-10 10:03:00 | INFO | Liked 3 photos
2025-10-10 10:04:00 | ERROR | Connection timeout
2025-10-10 10:05:00 | INFO | Unfollowed @user3
2025-10-10 10:06:00 | INFO | Commented: 'Nice photo!'
2025-10-10 10:07:00 | INFO | Session end
"""
        log_file = temp_log_dir / "test.log"
        with open(log_file, "w") as f:
            f.write(log_content.strip())
        return log_file

    def test_pattern_matching_like(self):
        """좋아요 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        assert parser.patterns['like'].search("Liked photo of @user1")
        assert parser.patterns['like'].search("Liked 3 photos")
        assert parser.patterns['like'].search("LIKED THE POST")

    def test_pattern_matching_follow(self):
        """팔로우 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        match = parser.patterns['follow'].search("Followed @testuser")
        assert match
        assert match.group(1) == "testuser"

        match = parser.patterns['follow'].search("Following user123")
        assert match
        assert match.group(1) == "user123"

    def test_pattern_matching_unfollow(self):
        """언팔로우 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        match = parser.patterns['unfollow'].search("Unfollowed @olduser")
        assert match
        assert match.group(1) == "olduser"

    def test_pattern_matching_comment(self):
        """댓글 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        assert parser.patterns['comment'].search("Commented: 'Great photo!'")
        assert parser.patterns['comment'].search("Comment Nice!")

    def test_pattern_matching_error(self):
        """에러 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        assert parser.patterns['error'].search("ERROR: Connection failed")
        assert parser.patterns['error'].search("Exception occurred")
        assert parser.patterns['error'].search("timeout")
        assert parser.patterns['error'].search("[ERROR] Something went wrong")

    def test_pattern_matching_session(self):
        """세션 시작/종료 패턴 매칭 테스트"""
        parser = LogParser(db_handler=None)
        assert parser.patterns['session_start'].search("Session start")
        assert parser.patterns['session_start'].search("Starting session")
        assert parser.patterns['session_end'].search("Session end")
        assert parser.patterns['session_end'].search("Total interactions: 10")

    def test_parse_log_file_stats(self, sample_log_file):
        """로그 파일 파싱 통계 테스트 (DB 없이)"""
        # DB 핸들러 없이 파서 생성 (패턴 매칭만 테스트)
        parser = LogParser(db_handler=None)

        stats = {
            'total_lines': 0,
            'likes': 0,
            'follows': 0,
            'unfollows': 0,
            'comments': 0,
            'errors': 0,
            'parsed_interactions': 0,
        }

        # 수동으로 파일 파싱
        with open(sample_log_file, 'r') as f:
            for line in f:
                stats['total_lines'] += 1
                # 간단한 카운팅 (DB 저장 제외)
                if parser.patterns['like'].search(line):
                    stats['likes'] += 1
                elif parser.patterns['follow'].search(line):
                    stats['follows'] += 1
                elif parser.patterns['unfollow'].search(line):
                    stats['unfollows'] += 1
                elif parser.patterns['comment'].search(line):
                    stats['comments'] += 1
                elif parser.patterns['error'].search(line):
                    stats['errors'] += 1

        assert stats['total_lines'] == 8
        assert stats['likes'] >= 2  # 최소 2개
        assert stats['follows'] >= 1
        assert stats['unfollows'] >= 1
        assert stats['comments'] >= 1
        assert stats['errors'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
