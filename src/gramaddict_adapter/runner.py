"""Runtime execution helpers for orchestrating GramAddict sessions."""

from __future__ import annotations

import os
import subprocess
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from src.utils.logger import get_logger

from .config import GramAddictConfigAdapter, RuntimePaths


@dataclass
class SessionExecutionResult:
    """Structured result describing the outcome of a GramAddict session."""

    session_id: str
    returncode: int
    stdout: str
    stderr: str
    config_path: Path
    runtime_paths: RuntimePaths
    stdout_log_path: Path
    stderr_log_path: Path

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


class GramAddictSessionRunner:
    """Run GramAddict with runtime configuration and optional DB integration."""

    def __init__(
        self,
        config_adapter: GramAddictConfigAdapter,
        db_handler=None,
        *,
        gramaddict_executable: str = "gramaddict",
        extra_env: Optional[Dict[str, str]] = None,
        logger=None,
    ) -> None:
        self.config_adapter = config_adapter
        self.db_handler = db_handler
        self.gramaddict_executable = gramaddict_executable
        self.extra_env = extra_env or {}
        self.logger = logger or get_logger()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        config_overrides: Optional[Dict[str, Any]] = None,
        cli_args: Optional[Iterable[str]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> SessionExecutionResult:
        """Execute a GramAddict session and capture logs and outputs."""
        session_id = self._generate_session_id()
        runtime_config_path = self.config_adapter.write_runtime_config(
            session_id, overrides=config_overrides
        )
        runtime_paths = self.config_adapter.prepare_runtime_paths(session_id)

        stdout_log_path = runtime_paths.log_dir / "gramaddict_stdout.log"
        stderr_log_path = runtime_paths.log_dir / "gramaddict_stderr.log"

        account_config = self.config_adapter.account_config
        username = account_config.get("username", "unknown")
        device_id = account_config.get("device")

        metadata = {
            "config_path": str(runtime_config_path),
            "log_dir": str(runtime_paths.log_dir),
            "stdout_log": str(stdout_log_path),
            "stderr_log": str(stderr_log_path),
        }

        self._register_session(session_id, username, device_id, metadata)

        command = self._build_command(runtime_config_path, cli_args)
        env = self._build_environment(runtime_paths, environment)

        self.logger.info("GramAddict 실행 명령어: %s", " ".join(command))
        self.logger.debug("GramAddict 환경 변수: %s", env)

        stdout_buffer: List[str] = []
        stderr_buffer: List[str] = []

        try:
            process = subprocess.Popen(  # noqa: S603 - execution of trusted CLI
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=env,
            )
        except FileNotFoundError as exc:
            self.logger.error("GramAddict 실행 파일을 찾을 수 없습니다: %s", exc)
            self._finalize_session(session_id, "failed")
            raise
        except Exception as exc:  # pragma: no cover - unexpected runtime failure
            self.logger.error("GramAddict 실행 실패: %s", exc)
            self._finalize_session(session_id, "failed")
            raise

        stdout_thread = threading.Thread(
            target=self._stream_pipe,
            args=(process.stdout, stdout_log_path, stdout_buffer, False),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=self._stream_pipe,
            args=(process.stderr, stderr_log_path, stderr_buffer, True),
            daemon=True,
        )

        stdout_thread.start()
        stderr_thread.start()

        process.wait()

        stdout_thread.join()
        stderr_thread.join()

        stdout = "".join(stdout_buffer)
        stderr = "".join(stderr_buffer)

        status = "completed" if process.returncode == 0 else "failed"
        self._finalize_session(session_id, status)

        result = SessionExecutionResult(
            session_id=session_id,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr,
            config_path=runtime_config_path,
            runtime_paths=runtime_paths,
            stdout_log_path=stdout_log_path,
            stderr_log_path=stderr_log_path,
        )

        if result.succeeded:
            self.logger.info("GramAddict 세션(%s)이 성공적으로 종료되었습니다.", session_id)
        else:
            self.logger.error(
                "GramAddict 세션(%s)이 실패했습니다. returncode=%s",
                session_id,
                process.returncode,
            )

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_command(
        self,
        runtime_config_path: Path,
        cli_args: Optional[Iterable[str]] = None,
    ) -> List[str]:
        command: List[str] = [self.gramaddict_executable, "run", "--config", str(runtime_config_path)]
        if cli_args:
            command.extend(list(cli_args))
        return command

    def _build_environment(
        self,
        runtime_paths: RuntimePaths,
        user_environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        environment = os.environ.copy()
        environment.update(self.extra_env)
        if user_environment:
            environment.update(user_environment)

        environment.setdefault("GRAMADDICT_LOG_PATH", str(runtime_paths.log_dir))
        environment.setdefault("GRAMADDICT_SCREENSHOT_PATH", str(runtime_paths.screenshot_dir))
        environment.setdefault("GRAMADDICT_CRASH_PATH", str(runtime_paths.crash_dir))
        environment.setdefault("PYTHONUNBUFFERED", "1")

        return environment

    def _stream_pipe(self, pipe, sink_path: Path, buffer: List[str], is_stderr: bool) -> None:
        level = self.logger.error if is_stderr else self.logger.debug
        sink_path.parent.mkdir(parents=True, exist_ok=True)
        with sink_path.open("w", encoding="utf-8") as sink:
            if pipe is None:
                return
            for line in iter(pipe.readline, ""):
                sink.write(line)
                sink.flush()
                buffer.append(line)
                level(line.rstrip())
        if pipe is not None:
            pipe.close()

    def _register_session(
        self,
        session_id: str,
        username: str,
        device_id: Optional[str],
        metadata: Dict[str, str],
    ) -> None:
        if not self.db_handler:
            return
        try:
            self.db_handler.create_session(session_id, username, device_id, metadata)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("세션 등록 실패 (무시하고 계속 진행): %s", exc)

    def _finalize_session(self, session_id: str, status: str) -> None:
        if not self.db_handler:
            return
        try:
            self.db_handler.end_session(session_id, status)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("세션 종료 기록 실패 (무시하고 계속 진행): %s", exc)

    @staticmethod
    def _generate_session_id() -> str:
        return uuid.uuid4().hex
