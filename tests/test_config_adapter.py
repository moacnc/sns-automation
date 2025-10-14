"""
Configuration Adapter 테스트
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from src.gramaddict_adapter.config import (
    GramAddictConfigAdapter,
    ConfigLoadError,
    _resolve_env_placeholders,
    _deep_merge_dicts,
)


class TestConfigAdapter:
    """GramAddictConfigAdapter 테스트"""

    @pytest.fixture
    def temp_config_dir(self):
        """임시 설정 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_account_config(self, temp_config_dir):
        """샘플 계정 설정 파일 생성"""
        config = {
            "username": "test_user",
            "device": "test_device",
            "interactions": [
                {
                    "interact-hashtag-posts": {
                        "hashtags": ["test"],
                        "amount": "10-20",
                    }
                }
            ],
        }
        config_path = temp_config_dir / "account.yml"
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)
        return config_path

    @pytest.fixture
    def sample_global_config(self, temp_config_dir):
        """샘플 전역 설정 파일 생성"""
        config = {
            "gramaddict": {
                "log_dir": "logs/test",
                "executable": "gramaddict",
            }
        }
        config_path = temp_config_dir / "global.yml"
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)
        return config_path

    def test_load_config_success(self, sample_account_config, sample_global_config, temp_config_dir):
        """설정 로드 성공 테스트"""
        adapter = GramAddictConfigAdapter(
            sample_account_config,
            sample_global_config,
            runtime_dir=temp_config_dir / "runtime",
        )
        assert adapter.account_config["username"] == "test_user"
        assert adapter.global_config["gramaddict"]["executable"] == "gramaddict"

    def test_load_config_not_found(self, temp_config_dir):
        """존재하지 않는 설정 파일 테스트"""
        with pytest.raises(ConfigLoadError):
            GramAddictConfigAdapter(
                temp_config_dir / "nonexistent.yml",
                runtime_dir=temp_config_dir / "runtime",
            )

    def test_env_placeholder_resolution(self):
        """환경변수 플레이스홀더 치환 테스트"""
        data = {
            "host": "${DB_HOST:-localhost}",
            "port": "${DB_PORT:-5432}",
        }
        env = {"DB_HOST": "testhost"}
        result = _resolve_env_placeholders(data, env)
        assert result["host"] == "testhost"
        assert result["port"] == "5432"  # 기본값

    def test_deep_merge_dicts(self):
        """딕셔너리 딥 머지 테스트"""
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        overrides = {"b": {"d": 4, "e": 5}, "f": 6}
        result = _deep_merge_dicts(base, overrides)
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 4
        assert result["b"]["e"] == 5
        assert result["f"] == 6

    def test_build_runtime_config(self, sample_account_config, sample_global_config, temp_config_dir):
        """런타임 설정 생성 테스트"""
        adapter = GramAddictConfigAdapter(
            sample_account_config,
            sample_global_config,
            runtime_dir=temp_config_dir / "runtime",
        )
        runtime_config = adapter.build_runtime_config("test_session_123")
        assert runtime_config["_meta"]["session_id"] == "test_session_123"
        assert runtime_config["_meta"]["account"] == "test_user"

    def test_prepare_runtime_paths(self, sample_account_config, sample_global_config, temp_config_dir):
        """런타임 경로 준비 테스트"""
        adapter = GramAddictConfigAdapter(
            sample_account_config,
            sample_global_config,
            runtime_dir=temp_config_dir / "runtime",
        )
        paths = adapter.prepare_runtime_paths("test_session_456")
        assert paths.session_id == "test_session_456"
        assert paths.log_dir.exists()
        assert paths.screenshot_dir.exists()
        assert paths.crash_dir.exists()

    def test_write_runtime_config(self, sample_account_config, sample_global_config, temp_config_dir):
        """런타임 설정 파일 작성 테스트"""
        adapter = GramAddictConfigAdapter(
            sample_account_config,
            sample_global_config,
            runtime_dir=temp_config_dir / "runtime",
        )
        output_path = adapter.write_runtime_config("test_session_789")
        assert output_path.exists()
        with open(output_path) as f:
            config = yaml.safe_load(f)
        assert config["_meta"]["session_id"] == "test_session_789"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
