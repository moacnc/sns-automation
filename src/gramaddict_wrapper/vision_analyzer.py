"""
VisionAnalyzer - GPT-4 Vision for image analysis only

This module uses GPT-4 Vision ONLY for:
1. Profile information extraction (OCR)
2. Story content analysis
3. Image/video content understanding

NOT for navigation or coordinate finding.
"""

import os
import base64
import json
from typing import Optional, Dict, Any
from pathlib import Path
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


class VisionAnalyzer:
    """GPT-4 Vision analyzer for image understanding"""

    def __init__(self):
        """Initialize GPT-4 Vision client"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"

    def analyze_profile_screenshot(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract profile information from screenshot using GPT-4 Vision

        Args:
            image_path: Path to profile screenshot

        Returns:
            Profile information dictionary or None
            {
                "username": str,
                "fullname": str,
                "bio": str,
                "post_count": int,
                "follower_count": str,
                "following_count": str,
                "is_verified": bool,
                "is_private": bool,
                "is_business": bool
            }
        """
        logger.info("Analyzing profile screenshot with GPT-4 Vision...")

        prompt = """Analyze this Instagram profile screenshot and extract the following information in JSON format:

{
  "username": "Instagram username (without @)",
  "fullname": "Full display name",
  "bio": "Complete bio text",
  "post_count": number of posts (integer),
  "follower_count": "follower count as shown (e.g., '1.2K', '500')",
  "following_count": "following count as shown",
  "is_verified": true if verified badge visible, false otherwise,
  "is_private": true if private account, false otherwise,
  "is_business": true if business/creator account, false otherwise
}

If any information is not visible, use null.
Return ONLY valid JSON, no additional text."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info(f"Profile extracted: @{result.get('username', 'unknown')}")
                logger.debug(f"Followers: {result.get('follower_count')}, Following: {result.get('following_count')}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze profile: {e}")
            return None

    def analyze_story_content(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze story content (text, image description, video description)

        Args:
            image_path: Path to story screenshot

        Returns:
            Story content analysis or None
            {
                "text_content": str,
                "visual_description": str,
                "content_type": "photo" | "video" | "text",
                "contains_product": bool,
                "mentions": [list of @mentions],
                "hashtags": [list of #hashtags]
            }
        """
        logger.info("Analyzing story content with GPT-4 Vision...")

        prompt = """Analyze this Instagram story and extract content information in JSON format:

{
  "text_content": "All visible text in the story",
  "visual_description": "Describe the visual content (what's shown in image/video)",
  "content_type": "photo" or "video" or "text",
  "contains_product": true if product/shopping content visible, false otherwise,
  "mentions": ["list", "of", "@mentions"],
  "hashtags": ["list", "of", "#hashtags"]
}

Return ONLY valid JSON, no additional text."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info(f"Story content: {result.get('content_type')}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze story: {e}")
            return None

    def check_content_appropriateness(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Check if content is appropriate for reposting/interaction

        Args:
            image_path: Path to content screenshot

        Returns:
            Appropriateness analysis or None
            {
                "is_appropriate": bool,
                "contains_violence": bool,
                "contains_nudity": bool,
                "contains_hate_speech": bool,
                "reason": str
            }
        """
        logger.info("Checking content appropriateness...")

        prompt = """Analyze this content for appropriateness and safety. Return JSON:

{
  "is_appropriate": true if safe for reposting, false otherwise,
  "contains_violence": true/false,
  "contains_nudity": true/false,
  "contains_hate_speech": true/false,
  "reason": "brief explanation of the decision"
}

Return ONLY valid JSON, no additional text."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info(f"Content appropriate: {result.get('is_appropriate')}")
            return result

        except Exception as e:
            logger.error(f"Failed to check appropriateness: {e}")
            return None

    def _call_vision_api(self, image_path: str, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Internal method to call GPT-4 Vision API

        Args:
            image_path: Path to image
            prompt: Prompt for analysis

        Returns:
            Parsed JSON response or None
        """
        try:
            # Validate image exists
            if not Path(image_path).exists():
                logger.error(f"Image not found: {image_path}")
                return None

            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            result = json.loads(content.strip())
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Response content: {content}")
            return None

        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return None
