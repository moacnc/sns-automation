#!/usr/bin/env python3
"""
Test the improved autonomous Gemini Computer Use wrapper
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from computer_use_wrapper import GeminiComputerUseAgent

# Load environment
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

logger.info("=" * 60)
logger.info("🧪 Testing Autonomous Gemini Computer Use")
logger.info("=" * 60)


def progress_callback(event):
    """Print progress events"""
    event_type = event.get('type', 'unknown')
    message = event.get('message', '')

    if event_type == 'info':
        logger.info(f"ℹ️  {message}")
    elif event_type == 'thinking':
        logger.info(f"🤔 {message}")
    elif event_type == 'gemini_text':
        logger.success(f"💭 {message}")
    elif event_type == 'action':
        logger.warning(f"⚡ {message}")
    elif event_type == 'round_start':
        round_num = event.get('round', '?')
        logger.info(f"🔄 Round {round_num} starting...")
    elif event_type == 'stopped':
        logger.error(f"🛑 {message}")
    elif event_type == 'error':
        logger.error(f"❌ {message}")
    else:
        logger.debug(f"Event: {event}")


def main():
    # Test task: Simple Google search
    task = "Go to google.com and search for 'Python programming'. Show me what you find."

    logger.info(f"📋 Task: {task}")
    logger.info("")

    try:
        # Create agent
        with GeminiComputerUseAgent() as agent:
            # Set progress callback
            agent.progress_callback = progress_callback

            # Start browser (visible)
            logger.info("🚀 Starting browser...")
            agent.start_browser(headless=False)
            logger.info("✅ Browser started!")
            logger.info("")

            # Execute task
            logger.info("🎯 Executing task...")
            logger.info("")

            result = agent.execute_task(task, max_steps=10)

            # Print results
            logger.info("")
            logger.info("=" * 60)
            logger.info("📊 RESULTS")
            logger.info("=" * 60)
            logger.info(f"Status: {result['status']}")
            logger.info(f"Rounds: {result.get('rounds', 'N/A')}")
            logger.info(f"Actions: {result['actions_count']}")
            logger.info("")
            logger.info("Actions taken:")
            for i, action in enumerate(result['actions'], 1):
                logger.info(f"  {i}. {action}")
            logger.info("")
            logger.info("Gemini's response:")
            logger.info(result['response'])
            logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
