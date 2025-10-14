"""
ProfileScraper - Extract profile information using GramAddict + GPT-4 Vision

Combines GramAddict's reliable navigation with GPT-4 Vision's OCR capabilities.
"""

import time
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger

from .navigation import InstagramNavigator
from .vision_analyzer import VisionAnalyzer


class ProfileScraper:
    """Instagram profile information scraper"""

    def __init__(self, navigator: InstagramNavigator, vision: VisionAnalyzer = None):
        """
        Initialize Profile Scraper

        Args:
            navigator: InstagramNavigator instance
            vision: VisionAnalyzer instance (creates new if None)
        """
        self.navigator = navigator
        self.vision = vision or VisionAnalyzer()
        self.screenshots_dir = Path("screenshots/profiles")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def scrape_profile(self, username: str, save_screenshot: bool = True) -> Optional[Dict[str, Any]]:
        """
        Scrape profile information for a given username

        Args:
            username: Instagram username (without @)
            save_screenshot: Whether to save the profile screenshot

        Returns:
            Profile information dictionary or None
        """
        logger.info(f"Scraping profile: @{username}")

        try:
            # 1. Navigate to profile using GramAddict
            if not self.navigator.search_username(username):
                logger.error(f"Failed to navigate to @{username}")
                return None

            # Wait for profile to load
            time.sleep(3)

            # 2. Capture screenshot
            screenshot_path = self.screenshots_dir / f"{username}_profile.png"
            image = self.navigator.screenshot(str(screenshot_path))

            if image is None:
                logger.error("Failed to capture screenshot")
                return None

            logger.info(f"Screenshot saved: {screenshot_path}")

            # 3. Analyze with GPT-4 Vision
            profile_info = self.vision.analyze_profile_screenshot(str(screenshot_path))

            if profile_info is None:
                logger.error("Failed to extract profile information")
                return None

            # 4. Add metadata
            profile_info["scraped_username"] = username
            profile_info["screenshot_path"] = str(screenshot_path) if save_screenshot else None

            # Clean up screenshot if not saving
            if not save_screenshot:
                try:
                    screenshot_path.unlink()
                except:
                    pass

            logger.info(f"✅ Profile scraped successfully: @{username}")
            return profile_info

        except Exception as e:
            logger.error(f"Failed to scrape profile: {e}")
            return None

    def get_follower_count(self, username: str) -> Optional[str]:
        """
        Quick method to get only follower count

        Args:
            username: Instagram username

        Returns:
            Follower count string or None
        """
        profile = self.scrape_profile(username, save_screenshot=False)
        return profile.get('follower_count') if profile else None

    def is_verified(self, username: str) -> bool:
        """
        Check if account is verified

        Args:
            username: Instagram username

        Returns:
            True if verified, False otherwise
        """
        profile = self.scrape_profile(username, save_screenshot=False)
        return profile.get('is_verified', False) if profile else False

    def is_private(self, username: str) -> bool:
        """
        Check if account is private

        Args:
            username: Instagram username

        Returns:
            True if private, False otherwise
        """
        profile = self.scrape_profile(username, save_screenshot=False)
        return profile.get('is_private', False) if profile else False
