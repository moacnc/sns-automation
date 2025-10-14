"""
로깅 유틸리티 모듈
Loguru를 사용한 구조화된 로깅
"""

from __future__ import annotations

import sys
from pathlib import Path
from loguru import logger
import yaml


class CustomLogger:
    """커스텀 로거 클래스"""

    def __init__(self, config_path: str = "config/global_config.yml"):
        """
        로거 초기화

        Args:
            config_path: 전역 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self._setup_logger()

    def _load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('logging', {})
        except FileNotFoundError:
            # 기본 설정 반환
            return {
                'log_dir': 'logs/custom',
                'level': 'INFO',
                'max_file_size_mb': 10,
                'backup_count': 30,
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}'
            }

    def _setup_logger(self):
        """로거 설정"""
        # 기본 핸들러 제거
        logger.remove()

        # 콘솔 출력 설정
        logger.add(
            sys.stderr,
            format=self.config.get('format', '{time} | {level} | {message}'),
            level=self.config.get('level', 'INFO'),
            colorize=True
        )

        # 로그 디렉토리 생성
        log_dir = Path(self.config.get('log_dir', 'logs/custom'))
        log_dir.mkdir(parents=True, exist_ok=True)

        # 파일 출력 설정
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            format=self.config.get('format'),
            level=self.config.get('level', 'INFO'),
            rotation=f"{self.config.get('max_file_size_mb', 10)} MB",
            retention=self.config.get('backup_count', 30),
            compression="zip",
            encoding="utf-8"
        )

        # 에러 전용 로그
        logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            format=self.config.get('format'),
            level="ERROR",
            rotation=f"{self.config.get('max_file_size_mb', 10)} MB",
            retention=self.config.get('backup_count', 30),
            compression="zip",
            encoding="utf-8"
        )

    def get_logger(self):
        """로거 인스턴스 반환"""
        return logger


# 전역 로거 인스턴스
_logger_instance = None


def get_logger():
    """
    전역 로거 인스턴스 반환

    Returns:
        loguru.Logger: 로거 인스턴스
    """
    global _logger_instance
    if _logger_instance is None:
        custom_logger = CustomLogger()
        _logger_instance = custom_logger.get_logger()
    return _logger_instance


# 편의 함수
def debug(message: str, **kwargs):
    """디버그 로그"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """정보 로그"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """경고 로그"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """에러 로그"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """치명적 에러 로그"""
    get_logger().critical(message, **kwargs)


if __name__ == "__main__":
    # 테스트
    logger = get_logger()
    logger.info("로거 테스트 시작")
    logger.debug("디버그 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    logger.info("로거 테스트 완료")
