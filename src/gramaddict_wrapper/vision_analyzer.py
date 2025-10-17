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

        prompt = """Analyze this Instagram profile screenshot carefully and extract ALL information in JSON format.

IMPORTANT: Look at the top section below the profile picture - you'll see THREE numbers:
- Posts (게시물) - leftmost number
- Followers (팔로워) - middle number
- Following (팔로잉) - rightmost number

Extract these numbers EXACTLY as shown:

{
  "username": "Instagram username (without @)",
  "fullname": "Full display name",
  "bio": "Complete bio text",
  "posts_count": "NUMBER OF POSTS (게시물) - the LEFTMOST number",
  "follower_count": "FOLLOWER count (팔로워) - middle number",
  "following_count": "FOLLOWING count (팔로잉) - rightmost number",
  "is_verified": true if blue verified checkmark visible, false otherwise,
  "is_private": true if private account (shows lock icon), false otherwise,
  "is_business": true if business/creator account, false otherwise,
  "external_url": "any clickable link in bio"
}

If any information is not clearly visible, use null.
Return ONLY valid JSON, no additional text or explanation."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info(f"Profile extracted: @{result.get('username', 'unknown')}")
                logger.debug(f"Followers: {result.get('follower_count')}, Following: {result.get('following_count')}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze profile: {e}")
            return None

    def analyze_profile_advanced(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        고급 프로필 분석 - 성향, 카테고리, 인플루언서 타입 등

        Args:
            image_path: Path to profile screenshot

        Returns:
            Advanced profile analysis
            {
                "account_type": "personal" | "business" | "influencer" | "brand",
                "content_category": ["fashion", "food", "travel", ...],
                "engagement_quality": "high" | "medium" | "low",
                "authenticity_score": 0-100,
                "target_audience": "description",
                "profile_aesthetic": "description",
                "influencer_tier": "nano" | "micro" | "macro" | "mega" | null
            }
        """
        logger.info("Performing advanced profile analysis...")

        prompt = """Analyze this Instagram profile deeply and provide strategic insights in JSON format:

{
  "account_type": "Classify as: personal, business, influencer, creator, or brand",
  "content_categories": ["list main content themes: fashion, beauty, food, travel, fitness, tech, lifestyle, etc"],
  "engagement_quality": "Estimate based on follower count: high (>1000 followers), medium (100-1000), or low (<100)",
  "authenticity_assessment": "Does this look like a real, active account? Brief assessment",
  "target_audience": "Who is the likely target audience? (age group, interests, demographics)",
  "profile_aesthetic": "Describe the visual style and branding (professional, casual, artistic, minimal, etc)",
  "influencer_tier": "Based on followers: mega (>1M), macro (100K-1M), micro (10K-100K), nano (<10K), or null if not influencer",
  "bio_sentiment": "Analyze bio tone: professional, casual, friendly, promotional, creative, etc",
  "potential_collaboration": "Would this account be good for brand partnerships? Why?"
}

Provide thoughtful, strategic analysis. Return ONLY valid JSON."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info(f"Advanced analysis complete: {result.get('account_type', 'unknown')} account")
            return result
        except Exception as e:
            logger.error(f"Failed to perform advanced analysis: {e}")
            return None

    def analyze_grid_posts(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        프로필 그리드 포스팅 분석 - 콘텐츠 성향 파악

        Args:
            image_path: Path to profile screenshot (showing post grid)

        Returns:
            Grid post analysis
            {
                "visual_themes": ["colors", "styles"],
                "content_consistency": "high" | "medium" | "low",
                "posting_style": "description",
                "brand_presence": bool
            }
        """
        logger.info("Analyzing profile grid posts...")

        prompt = """Analyze the Instagram post grid visible in this profile screenshot:

{
  "visual_themes": ["Dominant colors, visual styles, themes you observe in the grid"],
  "content_consistency": "Is the content visually consistent? Rate: high, medium, or low",
  "posting_style": "Describe the posting pattern and style (professional photography, casual snapshots, curated aesthetic, etc)",
  "dominant_subjects": ["What are the main subjects in posts? people, products, landscapes, food, etc"],
  "brand_collaborations_visible": true if you see obvious brand/product placements in posts,
  "grid_aesthetic_quality": "Rate the overall visual appeal: professional, amateur, artistic, casual",
  "content_variety": "Does the content vary or is it very focused on one theme?"
}

Analyze what's visible in the grid section. Return ONLY valid JSON."""

        try:
            result = self._call_vision_api(image_path, prompt)
            if result:
                logger.info("Grid post analysis complete")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze grid posts: {e}")
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
