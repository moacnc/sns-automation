"""Task orchestration utilities built around the GramAddict core."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, Optional

from src.gramaddict_adapter import (
    ConfigLoadError,
    GramAddictConfigAdapter,
    GramAddictSessionRunner,
    SessionExecutionResult,
)
from src.utils.db_handler import DatabaseHandler
from src.utils.logger import get_logger
from src.utils.session_lock import session_lock, SessionLockError
from .log_parser import LogParser


class TaskManager:
    """High-level orchestrator for GramAddict sessions."""

    def __init__(
        self,
        config_path: str | Path,
        global_config_path: str | Path = "config/global_config.yml",
        *,
        db_handler: Optional[DatabaseHandler] = None,
    ) -> None:
        self.logger = get_logger()
        self.logger.debug("TaskManager 초기화: config=%s", config_path)

        try:
            self.config_adapter = GramAddictConfigAdapter(
                config_path,
                global_config_path=global_config_path,
            )
        except ConfigLoadError as exc:
            self.logger.error("설정 파일 로드 실패: %s", exc)
            raise

        self.global_config = self.config_adapter.global_config
        self.username = self.config_adapter.account_config.get("username", "unknown")
        self.device_id = self.config_adapter.account_config.get("device")

        self.db = db_handler or self._init_db_handler()
        self.log_parser = LogParser(self.db) if self.db else None

        self.runner = GramAddictSessionRunner(
            self.config_adapter,
            db_handler=self.db,
            gramaddict_executable=self._resolve_executable(),
            logger=self.logger,
        )

        self.logger.info("TaskManager 초기화 완료: %s", self.username)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        config_overrides: Optional[Dict] = None,
        cli_args: Optional[list[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        use_lock: bool = True,
        lock_timeout: int = 300,
    ) -> SessionExecutionResult:
        """
        Execute a GramAddict session and parse resulting logs.

        Args:
            config_overrides: Configuration overrides
            cli_args: Additional CLI arguments
            environment: Environment variables
            use_lock: Use session lock to prevent concurrent runs
            lock_timeout: Lock timeout in seconds

        Returns:
            SessionExecutionResult: Execution result
        """
        # 세션 락 사용 여부 확인
        if use_lock:
            try:
                with session_lock(self.username, timeout=lock_timeout):
                    return self._run_session(config_overrides, cli_args, environment)
            except SessionLockError as exc:
                self.logger.error("세션 락 실패: %s", exc)
                raise
        else:
            return self._run_session(config_overrides, cli_args, environment)

    def _run_session(
        self,
        config_overrides: Optional[Dict] = None,
        cli_args: Optional[list[str]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> SessionExecutionResult:
        """Internal session execution (without lock)."""
        self.logger.info("GramAddict 세션 시작: %s", self.username)
        result = self.runner.run(
            config_overrides=config_overrides,
            cli_args=cli_args,
            environment=environment,
        )

        if result.succeeded and self.log_parser:
            try:
                self.log_parser.parse_log_directory(
                    str(result.runtime_paths.log_dir), result.session_id
                )
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("GramAddict 로그 파싱 실패 (무시): %s", exc)

        return result

    def get_session_stats(self, session_id: str):
        if not self.db:
            return None
        try:
            return self.db.get_session_stats(session_id)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("세션 통계 조회 실패: %s", exc)
            return None

    def get_recent_sessions(self, limit: int = 10):
        if not self.db:
            return []
        try:
            return self.db.get_recent_sessions(self.username, limit)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("최근 세션 조회 실패: %s", exc)
            return []

    def check_device_connection(self) -> bool:
        """Check whether at least one Android device is connected via ADB."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except FileNotFoundError:
            self.logger.error("ADB가 설치되어 있지 않습니다.")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("ADB 명령이 시간 초과되었습니다.")
            return False

        if result.returncode != 0:
            self.logger.error("ADB 명령 실패: %s", result.stderr.strip())
            return False

        lines = result.stdout.strip().splitlines()[1:]
        connected = [line.split()[0] for line in lines if "device" in line]

        if not connected:
            self.logger.warning("연결된 디바이스가 없습니다.")
            return False

        self.logger.info("연결된 디바이스: %s", connected)
        return True

    def close(self) -> None:
        if self.log_parser:
            # Avoid double-closing the shared DB handler.
            self.log_parser = None
        if self.db:
            try:
                self.db.close()
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("데이터베이스 종료 실패: %s", exc)
            self.db = None

    def __enter__(self) -> "TaskManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()
        return False  # Don't suppress exceptions

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_executable(self) -> str:
        gramaddict_section = self.global_config.get("gramaddict", {})
        executable = gramaddict_section.get("executable", "gramaddict")
        return executable

    def _init_db_handler(self) -> Optional[DatabaseHandler]:
        db_config = self.global_config.get("database")
        if db_config is None:
            try:
                return DatabaseHandler()
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("데이터베이스 초기화 실패 (무시): %s", exc)
                return None

        if not isinstance(db_config, Dict):
            self.logger.warning("database 설정이 딕셔너리가 아닙니다. 기본값 사용.")
            try:
                return DatabaseHandler()
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("데이터베이스 초기화 실패 (무시): %s", exc)
                return None

        try:
            return DatabaseHandler(db_config)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("데이터베이스 연결 실패 (무시): %s", exc)
            return None

