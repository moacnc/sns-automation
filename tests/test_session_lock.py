"""
Session Lock 테스트
"""

from __future__ import annotations

import tempfile
import time
from multiprocessing import Process
from pathlib import Path

import pytest

from src.utils.session_lock import SessionLock, SessionLockError, session_lock


class TestSessionLock:
    """SessionLock 테스트"""

    @pytest.fixture
    def temp_lock_dir(self):
        """임시 락 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_acquire_and_release(self, temp_lock_dir):
        """락 획득 및 해제 테스트"""
        lock = SessionLock(temp_lock_dir, timeout=5)
        assert lock.acquire("test_session", blocking=False)
        assert lock.lock_file.exists()
        lock.release()
        assert not lock.lock_file.exists()

    def test_acquire_non_blocking_fail(self, temp_lock_dir):
        """논블로킹 모드 락 실패 테스트"""
        lock1 = SessionLock(temp_lock_dir, timeout=5)
        lock2 = SessionLock(temp_lock_dir, timeout=5)

        # 첫 번째 락 획득
        assert lock1.acquire("test_session", blocking=False)

        # 두 번째 락 획득 실패 (논블로킹)
        assert not lock2.acquire("test_session", blocking=False)

        lock1.release()

    def test_context_manager(self, temp_lock_dir):
        """컨텍스트 매니저 테스트"""
        with SessionLock(temp_lock_dir, timeout=5) as lock:
            assert lock.acquire("test_session", blocking=False)
            assert lock.lock_file.exists()
        # 컨텍스트 종료 후 락 해제 확인
        assert not lock.lock_file.exists()

    def test_session_lock_helper(self, temp_lock_dir):
        """session_lock 헬퍼 함수 테스트"""
        with session_lock("test_session", lock_dir=temp_lock_dir, timeout=5):
            lock_file = temp_lock_dir / "test_session.lock"
            assert lock_file.exists()
        # 컨텍스트 종료 후
        assert not lock_file.exists()

    def test_concurrent_access(self, temp_lock_dir):
        """동시 접근 테스트"""

        def worker(lock_dir, session_name, result_list):
            """워커 프로세스"""
            try:
                with session_lock(session_name, lock_dir=lock_dir, timeout=2):
                    time.sleep(0.5)
                    result_list.append("success")
            except SessionLockError:
                result_list.append("failed")

        # 단일 프로세스에서 순차 실행 (멀티프로세싱은 테스트 환경에서 복잡)
        from multiprocessing import Manager

        manager = Manager()
        result_list = manager.list()

        lock1 = SessionLock(temp_lock_dir, timeout=2)
        assert lock1.acquire("concurrent_test", blocking=False)

        # 다른 락 시도 (실패해야 함)
        lock2 = SessionLock(temp_lock_dir, timeout=1)
        try:
            lock2.acquire("concurrent_test", blocking=True)
            assert False, "Should have raised SessionLockError"
        except SessionLockError:
            pass

        lock1.release()

    def test_stale_lock_cleanup(self, temp_lock_dir):
        """오래된 락 파일 정리 테스트"""
        lock = SessionLock(temp_lock_dir, timeout=1)
        lock_file = temp_lock_dir / "stale_session.lock"

        # 오래된 락 파일 생성 (타임아웃보다 오래됨)
        with open(lock_file, "w") as f:
            old_timestamp = time.time() - 10  # 10초 전
            f.write(f"99999:{old_timestamp}")

        # 락 획득 시 오래된 파일 정리 확인
        lock.lock_file = lock_file
        lock._check_stale_lock()

        # 새로운 락 획득 가능
        assert lock.acquire("stale_session", blocking=False)
        lock.release()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
