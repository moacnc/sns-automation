"""
Agent Manager - Central orchestrator for OpenAI Agents

Integrates ConfigGeneratorAgent and PlanningAgent with TaskManager
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from src.agents.config_agent import ConfigGeneratorAgent
    from src.agents.planning_agent import PlanningAgent
except ImportError:
    ConfigGeneratorAgent = None
    PlanningAgent = None


class AgentManager:
    """
    Central manager for AI agents

    Features:
    - Generate configurations from natural language
    - Create intelligent task plans based on account history
    - Integrate with existing TaskManager workflow

    Example:
        >>> from src.agents.agent_manager import AgentManager
        >>> from src.utils.db_handler import DatabaseHandler
        >>>
        >>> db = DatabaseHandler()
        >>> agent_mgr = AgentManager(db_handler=db)
        >>>
        >>> # Generate config from natural language
        >>> config = agent_mgr.generate_config(
        ...     "Grow travel account, 50 followers/week, safe mode",
        ...     username="travel_account"
        ... )
        >>>
        >>> # Get intelligent task plan
        >>> plan = agent_mgr.plan_tasks(
        ...     username="travel_account",
        ...     goals={"followers": 50, "timeframe": "1 week"}
        ... )
    """

    def __init__(
        self,
        db_handler=None,
        api_key: Optional[str] = None,
        enable_config_agent: bool = True,
        enable_planning_agent: bool = True
    ):
        """
        Initialize AgentManager

        Args:
            db_handler: DatabaseHandler instance for PlanningAgent
            api_key: OpenAI API key (None = use env variable)
            enable_config_agent: Enable ConfigGeneratorAgent
            enable_planning_agent: Enable PlanningAgent
        """
        if ConfigGeneratorAgent is None or PlanningAgent is None:
            raise ImportError(
                "Agent modules not found. Make sure src/agents/ is in PYTHONPATH"
            )

        self.db = db_handler
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY required. Set in environment or pass to constructor.\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )

        # Initialize agents
        self.config_agent = None
        self.planning_agent = None

        if enable_config_agent:
            self.config_agent = ConfigGeneratorAgent(api_key=self.api_key)

        if enable_planning_agent:
            self.planning_agent = PlanningAgent(
                db_handler=db_handler,
                api_key=self.api_key
            )

    def generate_config(
        self,
        prompt: str,
        username: str,
        save_to: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate GramAddict configuration from natural language

        Args:
            prompt: Natural language description of goals
            username: Instagram account username
            save_to: Optional path to save config file

        Returns:
            Dictionary with generated configuration

        Example:
            >>> config = agent_mgr.generate_config(
            ...     "Focus on foodie niche, 30 likes per day, very safe",
            ...     username="foodie_account"
            ... )
        """
        if not self.config_agent:
            raise RuntimeError("ConfigGeneratorAgent not enabled")

        if save_to:
            return self.config_agent.generate_and_save(
                prompt=prompt,
                username=username,
                output_path=save_to
            )
        else:
            return self.config_agent.generate(
                prompt=prompt,
                username=username
            )

    def plan_tasks(
        self,
        username: str,
        goals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create intelligent daily task plan

        Args:
            username: Account username
            goals: Optional goals dict (e.g., {"followers": 100, "timeframe": "1 week"})

        Returns:
            Dictionary with plan, reasoning, warnings, confidence

        Example:
            >>> plan = agent_mgr.plan_tasks(
            ...     username="my_account",
            ...     goals={"followers": 50, "timeframe": "1 week"}
            ... )
            >>> print(plan['plan']['daily_likes'])  # 35
            >>> print(plan['reasoning'])  # "Based on 85% success rate..."
        """
        if not self.planning_agent:
            raise RuntimeError("PlanningAgent not enabled")

        return self.planning_agent.plan_daily_tasks(
            username=username,
            goals=goals
        )

    def get_config_with_plan(
        self,
        prompt: str,
        username: str,
        goals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Combined workflow: Generate config + create task plan

        This method:
        1. Analyzes account history (if DB available)
        2. Creates intelligent task plan
        3. Generates config incorporating the plan

        Args:
            prompt: Natural language prompt
            username: Account username
            goals: Optional goals

        Returns:
            Dictionary with 'config', 'plan', and 'metadata'
        """
        result = {
            "config": None,
            "plan": None,
            "metadata": {
                "username": username,
                "prompt": prompt,
                "goals": goals
            }
        }

        # Step 1: Get task plan (if planning agent enabled and DB available)
        if self.planning_agent and self.db:
            try:
                plan = self.plan_tasks(username=username, goals=goals)
                result['plan'] = plan

                # Enhance prompt with plan insights
                if 'plan' in plan and 'daily_likes' in plan['plan']:
                    prompt_enhanced = f"{prompt}\n\nRecommended targets from analysis: "
                    prompt_enhanced += f"{plan['plan']['daily_likes']} likes/day, "
                    prompt_enhanced += f"{plan['plan']['daily_follows']} follows/day"
                    prompt = prompt_enhanced
            except Exception as e:
                # Non-critical, continue with original prompt
                result['metadata']['plan_error'] = str(e)

        # Step 2: Generate config
        if self.config_agent:
            try:
                config = self.generate_config(prompt=prompt, username=username)
                result['config'] = config
            except Exception as e:
                result['metadata']['config_error'] = str(e)

        return result


# Convenience functions for quick usage
def quick_config(prompt: str, username: str, api_key: Optional[str] = None) -> Dict:
    """
    Quick config generation without database

    Example:
        >>> from src.agents.agent_manager import quick_config
        >>> config = quick_config("travel niche, 30 likes/day", "my_account")
    """
    mgr = AgentManager(
        db_handler=None,
        api_key=api_key,
        enable_planning_agent=False
    )
    return mgr.generate_config(prompt=prompt, username=username)


def quick_plan(username: str, db_handler, goals=None, api_key: Optional[str] = None) -> Dict:
    """
    Quick task planning with database

    Example:
        >>> from src.agents.agent_manager import quick_plan
        >>> from src.utils.db_handler import DatabaseHandler
        >>> db = DatabaseHandler()
        >>> plan = quick_plan("my_account", db, goals={"followers": 50})
    """
    mgr = AgentManager(
        db_handler=db_handler,
        api_key=api_key,
        enable_config_agent=False
    )
    return mgr.plan_tasks(username=username, goals=goals)


if __name__ == "__main__":
    import sys
    import json

    print("AgentManager Test\n")

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set")
        print("\nSet it in .env file or export it:")
        print("  export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    # Test config generation
    print("=" * 60)
    print("Testing config generation")
    print("=" * 60)
    try:
        config = quick_config(
            "Grow travel account, 50 followers per week, safe mode",
            username="test_account"
        )
        print("✅ Config generation successful\n")
        import yaml
        print(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
    except Exception as e:
        print(f"❌ Config generation failed: {e}")

    # Test planning (without DB)
    print("\n" + "=" * 60)
    print("Testing task planning (no database)")
    print("=" * 60)
    try:
        mgr = AgentManager(
            db_handler=None,
            enable_config_agent=False,
            enable_planning_agent=True
        )
        plan = mgr.plan_tasks(
            username="test_account",
            goals={"followers": 50, "timeframe": "1 week"}
        )
        print("✅ Planning successful\n")
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Planning failed: {e}")
