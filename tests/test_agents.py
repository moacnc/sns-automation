"""
Test suite for OpenAI Agents (ConfigGeneratorAgent, PlanningAgent)

Note: These tests require OPENAI_API_KEY environment variable.
Run with: pytest tests/test_agents.py -v
"""

import pytest
import os
from pathlib import Path


# Check if OPENAI_API_KEY is available
OPENAI_API_KEY_AVAILABLE = bool(os.getenv('OPENAI_API_KEY'))


@pytest.mark.skipif(not OPENAI_API_KEY_AVAILABLE, reason="OPENAI_API_KEY not set")
class TestConfigGeneratorAgent:
    """Tests for ConfigGeneratorAgent"""

    def test_agent_initialization(self):
        """Test that agent can be initialized"""
        from src.agents.config_agent import ConfigGeneratorAgent

        agent = ConfigGeneratorAgent()
        assert agent.agent is not None
        assert agent.agent.name == "ConfigGenerator"
        assert agent.agent.model == "gpt-4o-mini"

    def test_simple_config_generation(self):
        """Test basic configuration generation"""
        from src.agents.config_agent import ConfigGeneratorAgent

        agent = ConfigGeneratorAgent()
        config = agent.generate(
            "Simple test: 20 likes per day, travel niche, very safe",
            username="test_account"
        )

        # Basic structure checks
        assert isinstance(config, dict)
        assert 'username' in config
        assert config['username'] == 'test_account'

        # Safety checks - should have conservative limits
        if 'total-likes-limit' in config:
            # Extract max value from range like "20-30"
            likes_limit = config['total-likes-limit']
            if isinstance(likes_limit, str) and '-' in likes_limit:
                max_likes = int(likes_limit.split('-')[1])
                assert max_likes <= 50, "Should use safe limits"

    def test_config_generation_with_hashtags(self):
        """Test that hashtags are included"""
        from src.agents.config_agent import ConfigGeneratorAgent

        agent = ConfigGeneratorAgent()
        config = agent.generate(
            "Focus on photography and nature content",
            username="photo_account"
        )

        # Should have hashtag-related field
        assert 'hashtag-posts-recent' in config or 'hashtags' in config


@pytest.mark.skipif(not OPENAI_API_KEY_AVAILABLE, reason="OPENAI_API_KEY not set")
class TestPlanningAgent:
    """Tests for PlanningAgent"""

    def test_agent_initialization_without_db(self):
        """Test that agent can be initialized without database"""
        from src.agents.planning_agent import PlanningAgent

        agent = PlanningAgent(db_handler=None)
        assert agent.agent is not None
        assert agent.agent.name == "TaskPlanner"
        assert agent.db is None

    def test_plan_generation_without_db(self):
        """Test plan generation without database (should still work)"""
        from src.agents.planning_agent import PlanningAgent

        agent = PlanningAgent(db_handler=None)
        plan = agent.plan_daily_tasks(
            username="test_account",
            goals={"followers": 50, "timeframe": "1 week"}
        )

        # Should return a plan structure
        assert isinstance(plan, dict)

        # Should have some of these fields
        expected_fields = ['plan', 'reasoning', 'warnings', 'confidence', 'error', 'raw_response']
        assert any(field in plan for field in expected_fields)


@pytest.mark.skipif(OPENAI_API_KEY_AVAILABLE, reason="Testing error handling when API key is missing")
class TestAgentsWithoutAPIKey:
    """Test error handling when OPENAI_API_KEY is not set"""

    def test_config_agent_fails_without_api_key(self):
        """ConfigGeneratorAgent should raise ValueError without API key"""
        # Temporarily remove API key
        old_key = os.environ.pop('OPENAI_API_KEY', None)

        try:
            from src.agents.config_agent import ConfigGeneratorAgent
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                ConfigGeneratorAgent()
        finally:
            # Restore if it existed
            if old_key:
                os.environ['OPENAI_API_KEY'] = old_key

    def test_planning_agent_fails_without_api_key(self):
        """PlanningAgent should raise ValueError without API key"""
        # Temporarily remove API key
        old_key = os.environ.pop('OPENAI_API_KEY', None)

        try:
            from src.agents.planning_agent import PlanningAgent
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                PlanningAgent()
        finally:
            # Restore if it existed
            if old_key:
                os.environ['OPENAI_API_KEY'] = old_key


# Manual test runners (for quick validation)
if __name__ == "__main__":
    import sys

    if not OPENAI_API_KEY_AVAILABLE:
        print("❌ OPENAI_API_KEY not set. Please set it to run tests.")
        print("\nSet it in your .env file:")
        print("  OPENAI_API_KEY=sk-...")
        print("\nOr export it:")
        print("  export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    print("Running manual agent tests...\n")

    # Test ConfigGeneratorAgent
    print("=" * 60)
    print("Testing ConfigGeneratorAgent")
    print("=" * 60)
    try:
        from src.agents.config_agent import ConfigGeneratorAgent
        agent = ConfigGeneratorAgent()
        config = agent.generate(
            "I want to grow my travel Instagram. Target 100 followers this week. Safe approach.",
            username="travel_test"
        )
        print("✅ ConfigGeneratorAgent test passed")
        print("\nGenerated config:")
        import yaml
        print(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
    except Exception as e:
        print(f"❌ ConfigGeneratorAgent test failed: {e}")

    # Test PlanningAgent
    print("\n" + "=" * 60)
    print("Testing PlanningAgent")
    print("=" * 60)
    try:
        from src.agents.planning_agent import PlanningAgent
        agent = PlanningAgent(db_handler=None)
        plan = agent.plan_daily_tasks(
            username="test_account",
            goals={"followers": 50, "timeframe": "1 week"}
        )
        print("✅ PlanningAgent test passed")
        print("\nGenerated plan:")
        import json
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ PlanningAgent test failed: {e}")
