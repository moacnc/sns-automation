"""
DMSender - Automated DM sending with GPT-4o personalization

Uses GramAddict for navigation and GPT-4o for personalized message generation.
"""

import os
import time
from typing import Optional, Dict, Any
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv

from .navigation import InstagramNavigator
from .profile_scraper import ProfileScraper

load_dotenv()


class DMSender:
    """Instagram DM automation with AI personalization"""

    def __init__(self, navigator: InstagramNavigator, profile_scraper: ProfileScraper = None):
        """
        Initialize DM Sender

        Args:
            navigator: InstagramNavigator instance
            profile_scraper: ProfileScraper instance (optional)
        """
        self.navigator = navigator
        self.profile_scraper = profile_scraper
        self.device = navigator.get_device()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def send_personalized_dm(
        self,
        username: str,
        campaign_context: str,
        use_profile_info: bool = True
    ) -> Dict[str, Any]:
        """
        Send a personalized DM using GPT-4o

        Args:
            username: Target Instagram username
            campaign_context: Campaign information/template
            use_profile_info: Whether to personalize based on profile info

        Returns:
            Result dictionary
        """
        logger.info(f"Sending personalized DM to @{username}")

        result = {
            "username": username,
            "message_generated": False,
            "message_sent": False,
            "message_text": None,
            "error": None
        }

        try:
            # 1. Get profile info for personalization (optional)
            profile_info = None
            if use_profile_info and self.profile_scraper:
                profile_info = self.profile_scraper.scrape_profile(username, save_screenshot=False)

            # 2. Generate personalized message with GPT-4o
            message_text = self._generate_message(username, campaign_context, profile_info)

            if not message_text:
                result["error"] = "Failed to generate message"
                return result

            result["message_generated"] = True
            result["message_text"] = message_text

            logger.info(f"Generated message: {message_text[:50]}...")

            # 3. Navigate to profile
            if not self.navigator.search_username(username):
                result["error"] = "Failed to navigate to profile"
                return result

            time.sleep(2)

            # 4. Send DM
            if self._send_dm_to_current_profile(message_text):
                result["message_sent"] = True
                logger.info(f"✅ DM sent to @{username}")
            else:
                result["error"] = "Failed to send DM"

            return result

        except Exception as e:
            logger.error(f"Failed to send DM: {e}")
            result["error"] = str(e)
            return result

    def _generate_message(
        self,
        username: str,
        campaign_context: str,
        profile_info: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Generate personalized message using GPT-4o

        Args:
            username: Target username
            campaign_context: Campaign template/context
            profile_info: Profile information for personalization

        Returns:
            Generated message text or None
        """
        try:
            # Build prompt
            prompt = f"""Generate a personalized Instagram DM message.

Target user: @{username}

Campaign context:
{campaign_context}
"""

            if profile_info:
                prompt += f"""
Profile information:
- Name: {profile_info.get('fullname', 'N/A')}
- Bio: {profile_info.get('bio', 'N/A')}
- Verified: {profile_info.get('is_verified', False)}
- Followers: {profile_info.get('follower_count', 'N/A')}
"""

            prompt += """
Requirements:
1. Keep it under 200 characters
2. Be friendly and natural
3. Personalize based on profile info if available
4. Don't use excessive emojis
5. Include a clear call-to-action

Return ONLY the message text, no additional formatting or quotes."""

            # Call GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing personalized, friendly Instagram messages."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )

            message_text = response.choices[0].message.content.strip()

            # Remove quotes if present
            if message_text.startswith('"') and message_text.endswith('"'):
                message_text = message_text[1:-1]

            return message_text

        except Exception as e:
            logger.error(f"Failed to generate message: {e}")
            return None

    def _send_dm_to_current_profile(self, message_text: str) -> bool:
        """
        Send DM to currently opened profile

        Args:
            message_text: Message to send

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find "메시지 보내기" button using uiautomator2
            # Try exact Korean text first
            message_button = self.device(text="메시지 보내기")

            if not message_button.exists(timeout=3):
                # Try English text
                message_button = self.device(textContains="Message")

            if not message_button.exists(timeout=3):
                # Try resource ID
                message_button = self.device(resourceId="com.instagram.android:id/row_profile_header_button_message")

            if not message_button.exists(timeout=3):
                # Fallback: use coordinates (center of button)
                logger.warning("Message button not found by text, using coordinates")
                self.navigator._adb_tap(372, 290)  # "메시지 보내기" button
                logger.info("Clicked message button at coordinates (372, 290)")
            else:
                message_button.click()
                logger.info("Clicked message button")

            time.sleep(3)

            # Find message input field
            message_input = self.device(className="android.widget.EditText")

            if not message_input.exists(timeout=3):
                logger.warning("Message input field not found")
                self.navigator.go_back()
                return False

            # Type message
            message_input.set_text(message_text)
            logger.info(f"Typed message: {message_text[:30]}...")
            time.sleep(2)

            # Find and click send button (blue paper plane icon)
            # Try by description first
            send_button = self.device(description="보내기")  # Korean

            if not send_button.exists(timeout=3):
                send_button = self.device(descriptionContains="Send")  # English

            if not send_button.exists(timeout=3):
                # Try by resource ID
                send_button = self.device(resourceId="com.instagram.android:id/row_thread_composer_send_button")

            if not send_button.exists(timeout=3):
                # Fallback: use coordinates (paper plane button bottom right)
                logger.warning("Send button not found by text, using coordinates")
                self.navigator._adb_tap(668, 1420)  # Send button coordinates
                logger.info("Clicked send button at coordinates (668, 1420)")
            else:
                send_button.click()
                logger.info("Clicked send button")

            logger.info("✅ DM sent successfully")
            time.sleep(3)

            # Go back to profile
            self.navigator.go_back()

            return True

        except Exception as e:
            logger.error(f"Failed to send DM: {e}")
            return False
