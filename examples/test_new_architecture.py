#!/usr/bin/env python3
"""
Test Script for New GramAddict-based Architecture

Tests all major functionality:
1. Profile Scraping
2. Story Restory
3. DM Sending
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gramaddict_wrapper import (
    InstagramNavigator,
    VisionAnalyzer,
    ProfileScraper,
    StoryRestory,
    DMSender
)
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def test_profile_scraping():
    """Test 1: Profile Scraping"""
    print("\n" + "="*70)
    print("TEST 1: Profile Scraping (@liowish)")
    print("="*70 + "\n")

    try:
        # Initialize
        navigator = InstagramNavigator(device_id="R3CN70D9ZBY")
        vision = VisionAnalyzer()
        scraper = ProfileScraper(navigator, vision)

        # Connect
        if not navigator.connect():
            print("❌ Failed to connect to device")
            return False

        # Scrape profile
        profile = scraper.scrape_profile("liowish")

        if profile:
            print(f"\n✅ Profile Scraped Successfully!")
            print(f"   Username: @{profile.get('username')}")
            print(f"   Full Name: {profile.get('fullname')}")
            print(f"   Followers: {profile.get('follower_count')}")
            print(f"   Following: {profile.get('following_count')}")
            print(f"   Posts: {profile.get('post_count')}")
            print(f"   Bio: {profile.get('bio')[:50]}..." if profile.get('bio') else "   Bio: N/A")
            print(f"   Verified: {'✓' if profile.get('is_verified') else '✗'}")
            print(f"   Private: {'✓' if profile.get('is_private') else '✗'}")
            return True
        else:
            print("❌ Failed to scrape profile")
            return False

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_story_restory():
    """Test 2: Story Restory"""
    print("\n" + "="*70)
    print("TEST 2: Story Restory (from @liowish)")
    print("="*70 + "\n")

    try:
        # Initialize
        navigator = InstagramNavigator(device_id="R3CN70D9ZBY")
        vision = VisionAnalyzer()
        story_restory = StoryRestory(navigator, vision)

        # Connect
        if not navigator.connect():
            print("❌ Failed to connect to device")
            return False

        # Perform restory
        result = story_restory.restory_from_user(
            username="liowish",
            filter_inappropriate=True,
            max_stories=2  # Test with just 2 stories
        )

        print(f"\n✅ Story Restory Completed!")
        print(f"   Stories Checked: {result['stories_checked']}")
        print(f"   Stories Reposted: {result['stories_reposted']}")
        print(f"   Stories Skipped: {result['stories_skipped']}")

        if result['skipped_reasons']:
            print(f"   Skip Reasons: {', '.join(result['skipped_reasons'])}")

        return result['success']

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_dm_sending():
    """Test 3: DM Sending"""
    print("\n" + "="*70)
    print("TEST 3: Personalized DM Sending")
    print("="*70 + "\n")

    try:
        # Initialize
        navigator = InstagramNavigator(device_id="R3CN70D9ZBY")
        vision = VisionAnalyzer()
        scraper = ProfileScraper(navigator, vision)
        dm_sender = DMSender(navigator, scraper)

        # Connect
        if not navigator.connect():
            print("❌ Failed to connect to device")
            return False

        # Send personalized DM
        campaign_context = """
        We're reaching out to creative content creators for a collaboration opportunity.
        We'd love to feature your work on our platform!
        """

        result = dm_sender.send_personalized_dm(
            username="liowish",
            campaign_context=campaign_context,
            use_profile_info=True
        )

        if result['message_generated']:
            print(f"\n✅ Message Generated:")
            print(f"   {result['message_text']}")

        if result['message_sent']:
            print(f"\n✅ DM Sent Successfully!")
            return True
        else:
            print(f"\n⚠️  Message generated but not sent: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 GramAddict-based Architecture Test Suite")
    print("="*70)

    results = {
        "Profile Scraping": False,
        "Story Restory": False,
        "DM Sending": False
    }

    # Test 1: Profile Scraping
    try:
        results["Profile Scraping"] = test_profile_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"Profile scraping test failed: {e}")

    # Uncomment to test Story Restory
    # try:
    #     results["Story Restory"] = test_story_restory()
    # except KeyboardInterrupt:
    #     print("\n⚠️  Test interrupted by user")
    # except Exception as e:
    #     logger.error(f"Story restory test failed: {e}")

    # Uncomment to test DM Sending
    # try:
    #     results["DM Sending"] = test_dm_sending()
    # except KeyboardInterrupt:
    #     print("\n⚠️  Test interrupted by user")
    # except Exception as e:
    #     logger.error(f"DM sending test failed: {e}")

    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
