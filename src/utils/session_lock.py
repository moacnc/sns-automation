"""
세션 락 관리 유틸리티
파일 기반 락을 사용하여 동시 세션 실행 방지
"""

from __future__ import annotations

import os
import time
import fcntl
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class SessionLockError(Exception):
    """세션 락 관련 예외"""
    pass


class SessionLock:
    """세션 실행 동시성 제어를 위한 락 관리자"""

    def __init__(self, lock_dir: str | Path = "locks", timeout: int = 300):
        """
        세션 락 초기화

        Args:
            lock_dir: 락 파일 저장 디렉토리
            timeout: 락 타임아웃 (초)
        """
        self.lock_dir = Path(lock_dir).expanduser().resolve()
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.lock_file: Optional[Path] = None
        self.lock_fd: Optional[int] = None

    def acquire(self, session_name: str, blocking: bool = True) -> bool:
        """
        세션 락 획득

        Args:
            session_name: 세션 이름 (계정명 또는 세션 ID)
            blocking: 블로킹 모드 (True: 대기, False: 즉시 반환)

        Returns:
            bool: 락 획득 성공 여부

        Raises:
            SessionLockError: 락 획득 실패 또는 타임아웃
        """
        self.lock_file = self.lock_dir / f"{session_name}.lock"

        # 기존 락 파일 타임아웃 확인
        self._check_stale_lock()

        start_time = time.time()

        while True:
            try:
                # 락 파일 열기 (없으면 생성)
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_RDWR)

                # 비블로킹 모드로 락 시도
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                # 락 획득 성공
                self.lock_fd = fd

                # 락 정보 기록
                os.write(fd, f"{os.getpid()}:{time.time()}".encode())
                os.fsync(fd)

                return True

            except (OSError, IOError) as e:
                # 락 실패
                if fd is not None:
                    os.close(fd)

                if not blocking:
                    return False

                # 타임아웃 확인
                if time.time() - start_time > self.timeout:
                    raise SessionLockError(
                        f"세션 락 획득 타임아웃 ({self.timeout}초): {session_name}"
                    )

                # 재시도 대기
                time.sleep(1)

    def release(self):
        """세션 락 해제"""
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
            except (OSError, IOError):
                pass
            finally:
                self.lock_fd = None

        # 락 파일 삭제
        if self.lock_file and self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except OSError:
                pass

    def _check_stale_lock(self):
        """오래된 락 파일 정리"""
        if not self.lock_file or not self.lock_file.exists():
            return

        try:
            with open(self.lock_file, 'r') as f:
                content = f.read().strip()
                if ':' in content:
                    pid_str, timestamp_str = content.split(':', 1)
                    timestamp = float(timestamp_str)

                    # 타임아웃 경과 확인
                    if time.time() - timestamp > self.timeout:
                        # 프로세스 존재 확인
                        try:
                            pid = int(pid_str)
                            os.kill(pid, 0)  # 프로세스 존재 확인만
                        except (OSError, ValueError):
                            # 프로세스가 없으면 락 파일 삭제
                            self.lock_file.unlink()
        except (OSError, IOError, ValueError):
            pass

    def __enter__(self) -> SessionLock:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


@contextmanager
def session_lock(session_name: str, lock_dir: str | Path = "locks", timeout: int = 300):
    """
    세션 락 컨텍스트 매니저

    Args:
        session_name: 세션 이름
        lock_dir: 락 파일 디렉토리
        timeout: 타임아웃 (초)

    Example:
        with session_lock("my_account"):
            # 세션 실행 코드
            pass
    """
    lock = SessionLock(lock_dir, timeout)
    try:
        if not lock.acquire(session_name, blocking=True):
            raise SessionLockError(f"세션 락 획득 실패: {session_name}")
        yield lock
    finally:
        lock.release()


if __name__ == "__main__":
    # 테스트
    import sys

    print("세션 락 테스트 시작")

    try:
        with session_lock("test_account", timeout=10) as lock:
            print("락 획득 성공")
            print("5초 대기...")
            time.sleep(5)
            print("작업 완료")
    except SessionLockError as e:
        print(f"락 실패: {e}")
        sys.exit(1)

    print("세션 락 테스트 완료")
