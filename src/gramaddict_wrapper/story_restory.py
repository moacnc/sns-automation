"""
StoryRestory - Automated story reposting with content analysis

Uses GramAddict for navigation and GPT-4 Vision for content analysis.
"""

import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger

from .navigation import InstagramNavigator
from .vision_analyzer import VisionAnalyzer


class StoryRestory:
    """Instagram Story Restory automation"""

    def __init__(self, navigator: InstagramNavigator, vision: VisionAnalyzer = None):
        """
        Initialize Story Restory

        Args:
            navigator: InstagramNavigator instance
            vision: VisionAnalyzer instance (creates new if None)
        """
        self.navigator = navigator
        self.vision = vision or VisionAnalyzer()
        self.device = navigator.get_device()
        self.screenshots_dir = Path("screenshots/stories")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def restory_from_user(
        self,
        username: str,
        filter_inappropriate: bool = True,
        max_stories: int = 5
    ) -> Dict[str, Any]:
        """
        Repost stories from a specific user

        Args:
            username: Instagram username to restory from
            filter_inappropriate: Whether to filter inappropriate content
            max_stories: Maximum number of stories to repost

        Returns:
            Result dictionary with stats
        """
        logger.info(f"Starting Story Restory from @{username}")

        result = {
            "username": username,
            "stories_checked": 0,
            "stories_reposted": 0,
            "stories_skipped": 0,
            "skipped_reasons": [],
            "success": False
        }

        try:
            # 1. Navigate to user profile
            if not self.navigator.search_username(username):
                logger.error(f"Failed to navigate to @{username}")
                return result

            time.sleep(2)

            # 2. Click on user's story (if available)
            if not self._open_user_story():
                logger.warning(f"No story available from @{username}")
                return result

            # 3. Process stories
            for story_index in range(max_stories):
                result["stories_checked"] += 1

                logger.info(f"Processing story {story_index + 1}/{max_stories}")

                # Capture story screenshot
                screenshot_path = self.screenshots_dir / f"{username}_story_{story_index}.png"
                self.navigator.screenshot(str(screenshot_path))

                # Analyze content
                if filter_inappropriate:
                    content_check = self.vision.check_content_appropriateness(str(screenshot_path))

                    if content_check and not content_check.get("is_appropriate", True):
                        logger.warning(f"Story filtered: {content_check.get('reason')}")
                        result["stories_skipped"] += 1
                        result["skipped_reasons"].append(content_check.get("reason"))
                        # Skip to next story
                        if not self._tap_next_story():
                            break
                        continue

                # Restory the content
                if self._perform_restory():
                    result["stories_reposted"] += 1
                    logger.info(f"✅ Reposted story {story_index + 1}")
                else:
                    logger.warning(f"Failed to repost story {story_index + 1}")
                    result["stories_skipped"] += 1

                # Go to next story
                if not self._tap_next_story():
                    logger.info("No more stories available")
                    break

                time.sleep(2)

            result["success"] = result["stories_reposted"] > 0

            logger.info(f"Story Restory completed: {result['stories_reposted']}/{result['stories_checked']} reposted")
            return result

        except Exception as e:
            logger.error(f"Story Restory failed: {e}")
            return result

    def _open_user_story(self) -> bool:
        """
        Open user's story from profile page

        Returns:
            True if story opened, False otherwise
        """
        try:
            # Look for story ring (usually at top of profile)
            # This uses GramAddict's device.find() with resourceId/className
            from GramAddict.core.resources import ClassName

            # Try to find and click story avatar
            story_avatar = self.device.find(
                className=ClassName.IMAGE_VIEW,
                descriptionMatches=".*[Ss]tory.*"
            )

            if story_avatar.exists():
                story_avatar.click()
                time.sleep(3)
                logger.info("Opened user story")
                return True
            else:
                logger.warning("Story avatar not found")
                return False

        except Exception as e:
            logger.error(f"Failed to open story: {e}")
            return False

    def _perform_restory(self) -> bool:
        """
        Perform the restory action (share story to your story)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Tap on story to show controls
            screen_width, screen_height = self.device.deviceV2.window_size()
            self.device.deviceV2.click(screen_width // 2, screen_height // 2)
            time.sleep(1)

            # Look for share/send button (paper plane icon)
            from GramAddict.core.resources import ClassName

            share_button = self.device.find(
                className=ClassName.IMAGE_VIEW,
                descriptionMatches=".*[Ss]end.*|.*[Ss]hare.*"
            )

            if not share_button.exists():
                logger.warning("Share button not found")
                return False

            share_button.click()
            time.sleep(2)

            # Look for "Add to story" option
            add_to_story = self.device.find(
                textMatches=".*Add.*story.*|.*스토리.*추가.*",
                className=ClassName.TEXT_VIEW
            )

            if not add_to_story.exists():
                logger.warning("'Add to story' option not found")
                self.navigator.go_back()
                return False

            add_to_story.click()
            time.sleep(2)

            # Confirm/Send the story
            send_button = self.device.find(
                descriptionMatches=".*[Ss]end.*|.*[Pp]ost.*|.*[Ss]hare.*"
            )

            if send_button.exists():
                send_button.click()
                time.sleep(3)
                logger.info("Story reposted successfully")
                return True
            else:
                logger.warning("Send button not found")
                self.navigator.go_back()
                return False

        except Exception as e:
            logger.error(f"Failed to perform restory: {e}")
            return False

    def _tap_next_story(self) -> bool:
        """
        Tap to go to next story

        Returns:
            True if successful, False if no more stories
        """
        try:
            # Tap on right side of screen to go to next story
            screen_width, screen_height = self.device.deviceV2.window_size()
            self.device.deviceV2.click(int(screen_width * 0.9), screen_height // 2)
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"Failed to tap next story: {e}")
            return False
