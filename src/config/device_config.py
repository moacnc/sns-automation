#!/usr/bin/env python3
"""
Device Configuration System
디바이스를 인식하고 해당 디바이스의 좌표를 자동으로 로드
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Tuple, Optional
from loguru import logger


class DeviceConfig:
    """
    디바이스 정보를 인식하고 해당 디바이스에 맞는 설정 로드
    """

    def __init__(self, config_dir: str = "src/config/devices"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.device_id: Optional[str] = None
        self.device_info: Optional[Dict] = None
        self.coordinates: Optional[Dict] = None

    def detect_device(self, adb_serial: str = None) -> Dict:
        """
        연결된 디바이스 정보 자동 감지

        Returns:
            {
                "serial": "R39M30H71LK",
                "model": "SM-N981N",
                "manufacturer": "samsung",
                "resolution": "1080x2400",
                "android_version": "13",
                "instagram_version": "263.0.0.19.104"
            }
        """
        try:
            # ADB로 디바이스 시리얼 확인
            if not adb_serial:
                result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')[1:]  # 첫 줄 제외
                devices = [line.split()[0] for line in lines if line.strip()]

                if not devices:
                    raise Exception("No device connected")

                adb_serial = devices[0]  # 첫 번째 디바이스 사용

            self.device_id = adb_serial
            logger.info(f"Detected device: {adb_serial}")

            # 디바이스 정보 수집
            device_info = {
                "serial": adb_serial,
                "model": self._adb_getprop("ro.product.model", adb_serial),
                "manufacturer": self._adb_getprop("ro.product.manufacturer", adb_serial),
                "android_version": self._adb_getprop("ro.build.version.release", adb_serial),
            }

            # 해상도 가져오기
            resolution = self._get_screen_resolution(adb_serial)
            device_info["resolution"] = resolution

            # Instagram 버전 확인
            instagram_version = self._get_instagram_version(adb_serial)
            device_info["instagram_version"] = instagram_version

            self.device_info = device_info
            logger.info(f"Device Info: {device_info}")

            return device_info

        except Exception as e:
            logger.error(f"Failed to detect device: {e}")
            raise

    def _adb_getprop(self, prop: str, serial: str) -> str:
        """ADB getprop 실행"""
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "shell", "getprop", prop],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Failed to get prop {prop}: {e}")
            return "unknown"

    def _get_screen_resolution(self, serial: str) -> str:
        """화면 해상도 가져오기"""
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Output: "Physical size: 1080x2400"
            size_line = result.stdout.strip()
            resolution = size_line.split(":")[-1].strip()
            return resolution
        except Exception as e:
            logger.warning(f"Failed to get resolution: {e}")
            return "1080x2400"  # 기본값

    def _get_instagram_version(self, serial: str) -> str:
        """Instagram 버전 확인"""
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "shell", "dumpsys", "package", "com.instagram.android"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # versionName을 찾아서 파싱
            for line in result.stdout.split('\n'):
                if "versionName" in line:
                    version = line.split("=")[-1].strip()
                    return version
            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to get Instagram version: {e}")
            return "unknown"

    def load_or_create_config(self) -> Dict:
        """
        디바이스 설정 파일 로드 또는 생성

        파일 구조:
        src/config/devices/
        └── R39M30H71LK_SM-N981N.json
        """
        if not self.device_info:
            raise Exception("Device not detected. Call detect_device() first.")

        # 설정 파일명: {serial}_{model}.json
        config_filename = f"{self.device_info['serial']}_{self.device_info['model']}.json"
        config_path = self.config_dir / config_filename

        # 기존 설정 파일이 있으면 로드
        if config_path.exists():
            logger.info(f"Loading existing config: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.coordinates = config.get('coordinates', {})
            return config

        # 없으면 새로 생성
        logger.info(f"Creating new config: {config_path}")
        config = self._create_default_config()

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self.coordinates = config['coordinates']
        return config

    def _create_default_config(self) -> Dict:
        """
        디바이스의 기본 설정 생성
        해상도에 맞춰 좌표를 자동으로 생성
        """
        resolution = self.device_info['resolution']
        width, height = map(int, resolution.split('x'))

        # 1080x2400 기준 좌표를 현재 해상도에 맞게 스케일링
        base_width, base_height = 1080, 2400
        scale_x = width / base_width
        scale_y = height / base_height

        def scale_coord(x: int, y: int) -> Tuple[int, int]:
            """좌표를 현재 해상도에 맞게 스케일링"""
            return (int(x * scale_x), int(y * scale_y))

        # 기본 좌표 세트 (1080x2400 기준)
        base_coordinates = {
            # === Navigation Bar (하단) ===
            "nav_home": (108, 2165),
            "nav_search": (324, 2165),
            "nav_reels": (540, 2165),
            "nav_shop": (756, 2165),
            "nav_profile": (972, 2165),

            # === Search Screen ===
            "search_input": (530, 168),
            "search_first_result": (540, 522),
            "search_back_button": (50, 90),

            # === Profile Screen ===
            "profile_follow_button": (257, 630),
            "profile_following_button": (132, 290),
            "profile_message_button": (372, 290),
            "profile_back_button": (37, 93),
            "profile_menu_button": (1043, 93),

            # === DM Screen ===
            "dm_input_field": (400, 2200),
            "dm_send_button": (668, 1420),
            "dm_back_button": (50, 120),

            # === Post Screen ===
            "post_like_button": (100, 1850),
            "post_comment_button": (280, 1850),
            "post_share_button": (460, 1850),
            "post_save_button": (980, 1850),
            "post_back_button": (50, 90),

            # === Story ===
            "story_skip_left": (50, 1200),
            "story_skip_right": (1030, 1200),
            "story_close": (1000, 100),

            # === Common Actions ===
            "keyboard_hide": (540, 2350),  # 키보드 숨기기 (빈 공간 클릭)
            "scroll_up_start": (540, 1800),
            "scroll_up_end": (540, 500),
            "scroll_down_start": (540, 500),
            "scroll_down_end": (540, 1800),
        }

        # 스케일링 적용
        scaled_coordinates = {}
        for key, (x, y) in base_coordinates.items():
            scaled_coordinates[key] = scale_coord(x, y)

        config = {
            "device_info": self.device_info,
            "coordinates": scaled_coordinates,
            "created_at": self._get_timestamp(),
            "last_verified_at": self._get_timestamp(),
            "notes": f"Auto-generated config for {self.device_info['model']} ({resolution})"
        }

        return config

    def _get_timestamp(self) -> str:
        """현재 타임스탬프"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_coordinate(self, key: str) -> Tuple[int, int]:
        """
        좌표 가져오기

        Args:
            key: 좌표 키 (예: "nav_home", "profile_follow_button")

        Returns:
            (x, y) 튜플
        """
        if not self.coordinates:
            raise Exception("Coordinates not loaded. Call load_or_create_config() first.")

        if key not in self.coordinates:
            logger.error(f"Coordinate key not found: {key}")
            raise KeyError(f"Coordinate '{key}' not found in config")

        return tuple(self.coordinates[key])

    def update_coordinate(self, key: str, x: int, y: int) -> None:
        """
        좌표 업데이트 (수동으로 조정할 때 사용)

        Args:
            key: 좌표 키
            x: X 좌표
            y: Y 좌표
        """
        if not self.coordinates:
            raise Exception("Coordinates not loaded.")

        self.coordinates[key] = [x, y]
        logger.info(f"Updated coordinate: {key} = ({x}, {y})")

        # 설정 파일 저장
        self._save_config()

    def _save_config(self) -> None:
        """현재 설정을 파일에 저장"""
        if not self.device_info:
            return

        config_filename = f"{self.device_info['serial']}_{self.device_info['model']}.json"
        config_path = self.config_dir / config_filename

        config = {
            "device_info": self.device_info,
            "coordinates": self.coordinates,
            "last_verified_at": self._get_timestamp(),
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Config saved: {config_path}")

    def verify_coordinates(self) -> Dict[str, bool]:
        """
        좌표 검증 (선택적)
        UI Automator dump와 비교하여 좌표가 정확한지 확인

        Returns:
            {key: is_valid} 딕셔너리
        """
        # TODO: UI Automator dump를 파싱하여 실제 버튼 위치와 비교
        logger.warning("Coordinate verification not implemented yet")
        return {}


# === 전역 인스턴스 ===
_device_config = None


def get_device_config() -> DeviceConfig:
    """
    전역 DeviceConfig 인스턴스 가져오기 (Singleton)
    """
    global _device_config

    if _device_config is None:
        _device_config = DeviceConfig()
        _device_config.detect_device()
        _device_config.load_or_create_config()

    return _device_config


def get_coord(key: str) -> Tuple[int, int]:
    """
    좌표 가져오기 (간편 함수)

    Usage:
        from src.config.device_config import get_coord

        x, y = get_coord("nav_home")
        navigator._adb_tap(x, y)
    """
    config = get_device_config()
    return config.get_coordinate(key)
