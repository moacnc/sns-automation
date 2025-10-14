"""Configuration helper utilities for GramAddict integration."""

from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


_ENV_PATTERN = re.compile(r"\$\{([^:}]+)(?::-(.*?))?\}")


class ConfigLoadError(RuntimeError):
    """Raised when a configuration file cannot be loaded or parsed."""


@dataclass(frozen=True)
class RuntimePaths:
    """Container with resolved runtime paths for a GramAddict session."""

    session_id: str
    log_dir: Path
    screenshot_dir: Path
    crash_dir: Path
    base_dir: Path


class GramAddictConfigAdapter:
    """Loads and prepares configuration for GramAddict executions."""

    def __init__(
        self,
        account_config_path: str | Path,
        global_config_path: str | Path = "config/global_config.yml",
        runtime_dir: str | Path = "config/generated",
        environment: Optional[Dict[str, str]] = None,
    ) -> None:
        self.account_config_path = Path(account_config_path).expanduser().resolve()
        self.global_config_path = Path(global_config_path).expanduser().resolve()
        self.runtime_dir = Path(runtime_dir).expanduser().resolve()
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.environment = environment or dict(os.environ)

        self._global_config: Dict[str, Any] = {}
        self._account_config: Dict[str, Any] = {}
        self._gramaddict_defaults: Dict[str, Any] = {}

        self._load_configs()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def account_config(self) -> Dict[str, Any]:
        return deepcopy(self._account_config)

    @property
    def global_config(self) -> Dict[str, Any]:
        return deepcopy(self._global_config)

    @property
    def gramaddict_defaults(self) -> Dict[str, Any]:
        return deepcopy(self._gramaddict_defaults)

    def build_runtime_config(
        self,
        session_id: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return a merged runtime configuration dictionary for the session."""
        runtime_config = deepcopy(self._account_config)
        if overrides:
            runtime_config = _deep_merge_dicts(runtime_config, overrides)

        runtime_config.setdefault("_meta", {})
        runtime_config["_meta"].update(
            {
                "session_id": session_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "account": runtime_config.get("username"),
                "source_config": str(self.account_config_path),
            }
        )

        return runtime_config

    def prepare_runtime_paths(self, session_id: str) -> RuntimePaths:
        """Prepare per-session directories for GramAddict artefacts."""
        defaults = self._gramaddict_defaults

        base_dir = Path(defaults.get("log_dir", "logs/gramaddict")).expanduser().resolve() / session_id
        log_dir = base_dir
        screenshot_dir = Path(defaults.get("screenshot_dir", "logs/screenshots")).expanduser().resolve() / session_id
        crash_dir = Path(defaults.get("crash_dir", "logs/crashes")).expanduser().resolve() / session_id

        for directory in {base_dir, log_dir, screenshot_dir, crash_dir}:
            directory.mkdir(parents=True, exist_ok=True)

        return RuntimePaths(
            session_id=session_id,
            base_dir=base_dir,
            log_dir=log_dir,
            screenshot_dir=screenshot_dir,
            crash_dir=crash_dir,
        )

    def write_runtime_config(
        self,
        session_id: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Create a temporary configuration file tailored for the session."""
        runtime_config = self.build_runtime_config(session_id, overrides=overrides)
        filename = f"{self.account_config_path.stem}_{session_id}.yml"
        output_path = self.runtime_dir / filename

        with output_path.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(runtime_config, fp, allow_unicode=True, sort_keys=False)

        return output_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_configs(self) -> None:
        self._account_config = self._read_yaml(self.account_config_path)
        if not self._account_config:
            raise ConfigLoadError(f"Account configuration is empty: {self.account_config_path}")

        if self.global_config_path.exists():
            self._global_config = self._read_yaml(self.global_config_path)
            if not isinstance(self._global_config, dict):
                raise ConfigLoadError(
                    f"Global configuration must be a mapping: {self.global_config_path}"
                )
            self._gramaddict_defaults = self._global_config.get("gramaddict", {})
        else:
            self._global_config = {}
            self._gramaddict_defaults = {}

    def _read_yaml(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as fp:
                data = yaml.safe_load(fp) or {}
        except FileNotFoundError as exc:
            raise ConfigLoadError(f"Configuration file not found: {path}") from exc
        except yaml.YAMLError as exc:
            raise ConfigLoadError(f"Failed to parse YAML: {path}") from exc

        return _resolve_env_placeholders(data, self.environment)


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------


def _resolve_env_placeholders(data: Any, environment: Dict[str, str]) -> Any:
    """Recursively replace ${VAR:-default} placeholders in the data structure."""
    if isinstance(data, dict):
        return {key: _resolve_env_placeholders(value, environment) for key, value in data.items()}
    if isinstance(data, list):
        return [_resolve_env_placeholders(item, environment) for item in data]
    if isinstance(data, str):
        return _replace_placeholders_in_string(data, environment)
    return data


def _replace_placeholders_in_string(value: str, environment: Dict[str, str]) -> str:
    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default_value = match.group(2) or ""
        return environment.get(var_name, default_value)

    return _ENV_PATTERN.sub(replacer, value)


def _deep_merge_dicts(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries without mutating the inputs."""
    result = deepcopy(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

