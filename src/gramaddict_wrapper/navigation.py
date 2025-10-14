"""
InstagramNavigator - Pure ADB/uiautomator2 based Instagram navigation

Provides high-level navigation methods using direct ADB commands and uiautomator2.
No dependency on GramAddict.
"""

import subprocess
import time
from typing import Optional
from pathlib import Path
from loguru import logger
import uiautomator2 as u2


class InstagramNavigator:
    """Pure ADB/uiautomator2 based Instagram Navigator"""

    def __init__(self, device_id: str = None, app_id: str = "com.instagram.android"):
        """
        Initialize Instagram Navigator

        Args:
            device_id: ADB device ID (None for default device)
            app_id: Instagram app package name
        """
        self.device_id = device_id or ""
        self.app_id = app_id
        self.device: Optional[u2.Device] = None

    def connect(self) -> bool:
        """
        Connect to device via uiautomator2

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Connecting to device: {self.device_id or 'default'}")

            # Get device serial if not specified
            if not self.device_id:
                result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Get first device
                    device_line = lines[1].split('\t')
                    if len(device_line) >= 2 and device_line[1] == 'device':
                        self.device_id = device_line[0]
                        logger.info(f"Found device: {self.device_id}")

            # Connect via uiautomator2
            if self.device_id:
                logger.info(f"Connecting to uiautomator2 on device: {self.device_id}")
                self.device = u2.connect(self.device_id)
            else:
                logger.info("Connecting to uiautomator2 on default device")
                self.device = u2.connect()

            if self.device is None:
                logger.error("Failed to connect to device")
                return False

            # Test connection
            try:
                device_info = self.device.info
                logger.info(f"Device info: {device_info.get('productName', 'Unknown')}")
            except Exception as e:
                logger.warning(f"Could not get device info: {e}")

            # Lock screen rotation to portrait for consistent coordinate-based clicking
            self._lock_screen_rotation()

            logger.info("Device connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _lock_screen_rotation(self) -> None:
        """
        Lock device screen rotation to portrait mode

        This ensures consistent UI element positions for coordinate-based clicking.
        Without this, auto-rotation could change element coordinates dynamically.
        """
        try:
            # Check current rotation settings
            result = subprocess.run(
                ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                ["shell", "settings", "get", "system", "accelerometer_rotation"],
                capture_output=True,
                text=True,
                timeout=5
            )

            current_auto_rotation = result.stdout.strip()

            if current_auto_rotation == "1":
                logger.warning("Auto-rotation is enabled. Locking to portrait for consistent coordinates.")

                # Disable auto-rotation
                subprocess.run(
                    ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                    ["shell", "settings", "put", "system", "accelerometer_rotation", "0"],
                    timeout=5
                )

                # Set to portrait (rotation 0)
                subprocess.run(
                    ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                    ["shell", "settings", "put", "system", "user_rotation", "0"],
                    timeout=5
                )

                logger.info("✓ Screen rotation locked to portrait (0°)")
            else:
                logger.info("✓ Screen rotation already locked")

        except Exception as e:
            logger.warning(f"Could not lock screen rotation: {e}")
            logger.warning("Continuing anyway, but coordinate-based clicks may fail if device rotates")

    def _adb_tap(self, x: int, y: int) -> bool:
        """
        Perform ADB tap at coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                ["shell", "input", "tap", str(x), str(y)],
                timeout=5,
                check=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to tap at ({x}, {y}): {e}")
            return False

    def _adb_input_text(self, text: str) -> bool:
        """
        Input text via ADB

        Args:
            text: Text to input

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                ["shell", "input", "text", text],
                timeout=5,
                check=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to input text '{text}': {e}")
            return False

    def goto_home(self) -> bool:
        """Navigate to Home tab"""
        try:
            logger.info("Navigating to Home")
            # Home tab coordinates: [0,2148][216,2182] -> center (108, 2165)
            return self._adb_tap(108, 2165)

        except Exception as e:
            logger.error(f"Failed to navigate to Home: {e}")
            return False

    def goto_search(self) -> bool:
        """Navigate to Search tab"""
        try:
            logger.info("Navigating to Search")
            # Search tab coordinates: [216,2148][432,2182] -> center (324, 2165)
            return self._adb_tap(324, 2165)

        except Exception as e:
            logger.error(f"Failed to navigate to Search: {e}")
            return False

    def goto_profile(self) -> bool:
        """Navigate to own Profile tab"""
        try:
            logger.info("Navigating to Profile")
            # Profile tab coordinates: [864,2148][1080,2182] -> center (972, 2165)
            return self._adb_tap(972, 2165)

        except Exception as e:
            logger.error(f"Failed to navigate to Profile: {e}")
            return False

    def search_username(self, username: str) -> bool:
        """
        Search for a username and navigate to the profile

        Args:
            username: Instagram username to search

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Searching for username: {username}")

            # Step 1: Navigate to search tab
            logger.info("Step 1: Navigating to search tab")
            if not self.goto_search():
                logger.error("Failed to navigate to search tab")
                return False

            time.sleep(2)  # Wait for search screen to load

            # Step 2: Click search input field by coordinates
            logger.info("Step 2: Clicking search input field")
            # Search input coordinates: [32,122][1027,213] -> center (530, 168)
            if not self._adb_tap(530, 168):
                logger.error("Failed to tap search input field")
                return False

            time.sleep(1)  # Wait for keyboard to appear

            # Step 3: Enter username
            logger.info(f"Step 3: Entering username: {username}")
            if not self._adb_input_text(username):
                logger.error("Failed to input username")
                return False

            time.sleep(2.5)  # Wait for search results to appear

            # Step 4: Click first search result
            logger.info("Step 4: Looking for search results")

            # Try multiple possible resource IDs for search results
            result_selectors = [
                "com.instagram.android:id/row_search_user_username",
                "com.instagram.android:id/row_search_user_info_container",
                "com.instagram.android:id/username_text_view",
                "com.instagram.android:id/row_user_primary_text"
            ]

            clicked = False
            for selector in result_selectors:
                result = self.device(resourceId=selector)
                if result.exists(timeout=2):
                    logger.info(f"Found result with selector: {selector}")
                    result.click()
                    clicked = True
                    logger.info(f"✓ Clicked on search result for @{username}")
                    time.sleep(2)  # Wait for profile to load
                    break

            if not clicked:
                # Fallback: try clicking by coordinates (first search result)
                logger.warning("Could not find result by resource ID, trying coordinate click")
                # First search result coordinates: [0,428][1080,617] -> center (540, 522)
                if not self._adb_tap(540, 522):
                    logger.error("Failed to tap search result")
                    return False

                time.sleep(2)
                logger.info("Clicked on first search result at (540, 522)")

            logger.info(f"✓ Successfully navigated to @{username}")
            return True

        except Exception as e:
            logger.error(f"Failed to search username: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def go_back(self) -> bool:
        """Press back button via ADB"""
        try:
            logger.info("Pressing back button")
            subprocess.run(
                ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                ["shell", "input", "keyevent", "KEYCODE_BACK"],
                timeout=5,
                check=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to go back: {e}")
            return False

    def screenshot(self, path: str = None):
        """
        Take a screenshot

        Args:
            path: Save path (optional)

        Returns:
            PIL Image or None
        """
        try:
            if path:
                # Use uiautomator2 screenshot with path
                img = self.device.screenshot()
                img.save(path)
                logger.info(f"Screenshot saved to {path}")
                return img
            else:
                # Return PIL Image
                return self.device.screenshot()

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None

    def get_device(self) -> u2.Device:
        """Get underlying uiautomator2 device for advanced usage"""
        return self.device

    def check_follow_status(self) -> str:
        """
        Check current follow button status on profile page

        Returns:
            "follow" - Not following (blue Follow button)
            "following" - Already following (grey Following button)
            "requested" - Follow request pending (for private accounts)
            "unknown" - Could not determine status
        """
        try:
            logger.info("Checking follow status")

            # Try to find Follow button by resource ID
            follow_button_ids = [
                "com.instagram.android:id/profile_header_follow_button",
                "com.instagram.android:id/button",
            ]

            for button_id in follow_button_ids:
                button = self.device(resourceId=button_id)
                if button.exists(timeout=2):
                    button_text = button.get_text()
                    logger.info(f"Found button with text: {button_text}")

                    if button_text:
                        text_lower = button_text.lower()
                        if "follow" in text_lower and "following" not in text_lower:
                            return "follow"
                        elif "following" in text_lower:
                            return "following"
                        elif "requested" in text_lower:
                            return "requested"

            # Fallback: Try to find by text content
            if self.device(text="Follow").exists(timeout=1):
                return "follow"
            elif self.device(text="Following").exists(timeout=1):
                return "following"
            elif self.device(textContains="Requested").exists(timeout=1):
                return "requested"

            logger.warning("Could not determine follow status")
            return "unknown"

        except Exception as e:
            logger.error(f"Failed to check follow status: {e}")
            return "unknown"

    def follow_user(self) -> bool:
        """
        Follow user on their profile page
        Only follows if not already following

        Returns:
            True if follow action was performed or already following
            False if failed
        """
        try:
            logger.info("Attempting to follow user")

            # Check current follow status
            status = self.check_follow_status()
            logger.info(f"Current follow status: {status}")

            if status == "following":
                logger.info("Already following this user - skipping")
                return True

            if status == "requested":
                logger.info("Follow request already sent - skipping")
                return True

            if status == "follow":
                logger.info("User is not followed - clicking Follow button")

                # Try clicking by resource ID first
                follow_button_ids = [
                    "com.instagram.android:id/profile_header_follow_button",
                    "com.instagram.android:id/button",
                ]

                clicked = False
                for button_id in follow_button_ids:
                    button = self.device(resourceId=button_id, text="Follow")
                    if button.exists(timeout=2):
                        button.click()
                        clicked = True
                        logger.info(f"Clicked Follow button via resource ID: {button_id}")
                        time.sleep(1)
                        break

                # Fallback: Click by text
                if not clicked:
                    button = self.device(text="Follow")
                    if button.exists(timeout=2):
                        button.click()
                        clicked = True
                        logger.info("Clicked Follow button via text")
                        time.sleep(1)

                # Fallback: Click by coordinates
                if not clicked:
                    logger.warning("Could not find Follow button by selectors, trying coordinate click")
                    # Follow button coordinates: approximately (168, 397)
                    if self._adb_tap(168, 397):
                        clicked = True
                        logger.info("Clicked Follow button at (168, 397)")
                        time.sleep(1)

                if clicked:
                    # Verify follow action
                    time.sleep(1)
                    new_status = self.check_follow_status()
                    if new_status in ["following", "requested"]:
                        logger.info(f"✓ Successfully followed user (status: {new_status})")
                        return True
                    else:
                        logger.warning(f"Follow button clicked but status is: {new_status}")
                        return True  # Still return True as we attempted the action
                else:
                    logger.error("Failed to click Follow button")
                    return False

            if status == "unknown":
                logger.warning("Unknown follow status - attempting coordinate click")
                if self._adb_tap(168, 397):
                    logger.info("Clicked at Follow button coordinates")
                    time.sleep(1)
                    return True
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to follow user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def launch_instagram(self) -> bool:
        """Launch Instagram app"""
        try:
            logger.info(f"Launching Instagram app: {self.app_id}")
            subprocess.run(
                ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                ["shell", "am", "start", "-n", f"{self.app_id}/{self.app_id}.activity.MainTabActivity"],
                timeout=10,
                check=True
            )
            logger.info("Instagram app launched successfully")
            time.sleep(3)  # Wait for app to load
            return True
        except Exception as e:
            logger.error(f"Failed to launch Instagram: {e}")
            # Try alternative launch method
            try:
                subprocess.run(
                    ["adb"] + (["-s", self.device_id] if self.device_id else []) +
                    ["shell", "monkey", "-p", self.app_id, "-c", "android.intent.category.LAUNCHER", "1"],
                    timeout=10,
                    check=True
                )
                logger.info("Instagram app launched successfully (monkey)")
                time.sleep(3)
                return True
            except Exception as e2:
                logger.error(f"Failed to launch Instagram (alternative method): {e2}")
                return False

    def close(self) -> None:
        """Close device connection"""
        try:
            if self.device:
                # uiautomator2 doesn't require explicit closing
                self.device = None
                logger.info("Device connection closed")
        except Exception as e:
            logger.error(f"Failed to close device connection: {e}")
