"""
Smart Task Manager - AI-enhanced TaskManager with OpenAI Agents integration

Extends TaskManager with:
- Natural language configuration generation
- Intelligent task planning based on account history
- Adaptive safety recommendations
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Any
import tempfile
import yaml

from src.wrapper.task_manager import TaskManager
from src.utils.logger import get_logger

# Optional imports for agents
try:
    from src.agents.agent_manager import AgentManager
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    AgentManager = None


class SmartTaskManager(TaskManager):
    """
    AI-enhanced TaskManager with intelligent planning and configuration

    Features:
    1. Natural language config generation
    2. Data-driven task planning
    3. Safety monitoring and recommendations
    4. Adaptive execution based on performance

    Example:
        >>> # Traditional approach
        >>> tm = TaskManager("config/accounts/my_account.yml")
        >>> tm.run()
        >>>
        >>> # AI-enhanced approach
        >>> smart_tm = SmartTaskManager.from_prompt(
        ...     "Grow travel account, 50 followers/week, safe mode",
        ...     username="travel_account"
        ... )
        >>> plan = smart_tm.get_intelligent_plan()
        >>> smart_tm.run_with_plan(plan)
    """

    def __init__(
        self,
        config_path: str | Path,
        global_config_path: str | Path = "config/global_config.yml",
        *,
        db_handler=None,
        enable_agents: bool = True,
        agent_api_key: Optional[str] = None
    ):
        """
        Initialize SmartTaskManager

        Args:
            config_path: Path to account config
            global_config_path: Path to global config
            db_handler: DatabaseHandler instance
            enable_agents: Enable AI agents (requires OPENAI_API_KEY)
            agent_api_key: OpenAI API key for agents
        """
        # Initialize parent TaskManager
        super().__init__(
            config_path=config_path,
            global_config_path=global_config_path,
            db_handler=db_handler
        )

        self.agent_manager = None
        self._agents_enabled = False

        # Try to initialize agents if enabled
        if enable_agents and AGENTS_AVAILABLE:
            try:
                self.agent_manager = AgentManager(
                    db_handler=self.db,
                    api_key=agent_api_key
                )
                self._agents_enabled = True
                self.logger.info("AI Agents 활성화됨")
            except Exception as e:
                self.logger.warning(f"AI Agents 초기화 실패 (기본 모드로 계속): {e}")
        elif enable_agents and not AGENTS_AVAILABLE:
            self.logger.warning("AI Agents 모듈을 찾을 수 없습니다. 기본 모드로 실행됩니다.")

    @classmethod
    def from_prompt(
        cls,
        prompt: str,
        username: str,
        global_config_path: str | Path = "config/global_config.yml",
        *,
        db_handler=None,
        save_config: bool = True,
        agent_api_key: Optional[str] = None
    ) -> "SmartTaskManager":
        """
        Create SmartTaskManager from natural language prompt

        Args:
            prompt: Natural language description (e.g., "travel niche, 30 likes/day")
            username: Instagram account username
            global_config_path: Path to global config
            db_handler: DatabaseHandler instance
            save_config: Save generated config to file
            agent_api_key: OpenAI API key

        Returns:
            SmartTaskManager instance

        Example:
            >>> tm = SmartTaskManager.from_prompt(
            ...     "Focus on food content, 25 likes per day, very safe",
            ...     username="foodie_account"
            ... )
        """
        logger = get_logger()

        if not AGENTS_AVAILABLE:
            raise RuntimeError(
                "AI Agents not available. Install requirements:\n"
                "  pip install openai-agents openai"
            )

        # Generate config using AI
        logger.info(f"자연어 프롬프트로 설정 생성 중: '{prompt}'")

        try:
            agent_mgr = AgentManager(
                db_handler=db_handler,
                api_key=agent_api_key,
                enable_planning_agent=False  # Just need config for now
            )

            if save_config:
                # Save to config/accounts/
                config_path = Path(f"config/accounts/{username}_ai_generated.yml")
                config_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate and save
                config_dict = agent_mgr.generate_config(
                    prompt=prompt,
                    username=username
                )

                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config_dict, f, allow_unicode=True, sort_keys=False)

                logger.info(f"AI 생성 설정 저장됨: {config_path}")
            else:
                # Use temporary config
                config_dict = agent_mgr.generate_config(
                    prompt=prompt,
                    username=username
                )

                # Create temporary file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.yml',
                    delete=False,
                    encoding='utf-8'
                ) as f:
                    yaml.safe_dump(config_dict, f, allow_unicode=True, sort_keys=False)
                    config_path = Path(f.name)

                logger.info(f"임시 설정 파일 생성됨: {config_path}")

        except Exception as e:
            logger.error(f"AI 설정 생성 실패: {e}")
            raise

        # Create SmartTaskManager with generated config
        return cls(
            config_path=config_path,
            global_config_path=global_config_path,
            db_handler=db_handler,
            enable_agents=True,
            agent_api_key=agent_api_key
        )

    def get_intelligent_plan(
        self,
        goals: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI-generated task plan based on account history

        Args:
            goals: Optional goals (e.g., {"followers": 100, "timeframe": "1 week"})

        Returns:
            Plan dictionary with recommendations, or None if agents disabled

        Example:
            >>> plan = tm.get_intelligent_plan(
            ...     goals={"followers": 50, "timeframe": "1 week"}
            ... )
            >>> print(plan['plan']['daily_likes'])  # 35
            >>> print(plan['reasoning'])
        """
        if not self._agents_enabled:
            self.logger.warning("AI Agents가 비활성화되어 있습니다.")
            return None

        try:
            plan = self.agent_manager.plan_tasks(
                username=self.username,
                goals=goals
            )
            self.logger.info("AI 계획 생성 완료")
            return plan
        except Exception as e:
            self.logger.error(f"AI 계획 생성 실패: {e}")
            return None

    def run_with_plan(
        self,
        plan: Optional[Dict[str, Any]] = None,
        *,
        config_overrides: Optional[Dict] = None,
        cli_args: Optional[list[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        use_lock: bool = True,
        lock_timeout: int = 300
    ):
        """
        Run session with AI-generated plan

        Args:
            plan: AI plan (if None, will generate one)
            config_overrides: Additional config overrides
            cli_args: CLI arguments
            environment: Environment variables
            use_lock: Use session lock
            lock_timeout: Lock timeout in seconds

        Returns:
            SessionExecutionResult

        Example:
            >>> plan = tm.get_intelligent_plan(goals={"followers": 50})
            >>> result = tm.run_with_plan(plan)
        """
        # Get plan if not provided
        if plan is None and self._agents_enabled:
            self.logger.info("AI 계획 자동 생성 중...")
            plan = self.get_intelligent_plan()

        # Apply plan recommendations to config overrides
        if plan and 'plan' in plan:
            plan_config = plan['plan']
            overrides = config_overrides or {}

            # Map plan to config overrides
            if 'daily_likes' in plan_config:
                overrides['total-likes-limit'] = plan_config['daily_likes']
            if 'daily_follows' in plan_config:
                overrides['total-follows-limit'] = plan_config['daily_follows']
            if 'speed_multiplier' in plan_config:
                overrides['speed-multiplier'] = plan_config['speed_multiplier']
            if 'recommended_hashtags' in plan_config:
                overrides['hashtag-posts-recent'] = ' '.join(plan_config['recommended_hashtags'])

            # Log plan application
            self.logger.info("AI 계획 적용:")
            self.logger.info(f"  - Daily likes: {plan_config.get('daily_likes')}")
            self.logger.info(f"  - Daily follows: {plan_config.get('daily_follows')}")
            self.logger.info(f"  - Speed multiplier: {plan_config.get('speed_multiplier')}")

            # Show warnings if any
            if 'warnings' in plan:
                for warning in plan['warnings']:
                    self.logger.warning(f"AI 경고: {warning}")

            config_overrides = overrides

        # Run with overrides
        return super().run(
            config_overrides=config_overrides,
            cli_args=cli_args,
            environment=environment,
            use_lock=use_lock,
            lock_timeout=lock_timeout
        )

    @property
    def agents_enabled(self) -> bool:
        """Check if AI agents are enabled and functional"""
        return self._agents_enabled


# Convenience functions
def create_smart_task_manager(
    prompt: str,
    username: str,
    **kwargs
) -> SmartTaskManager:
    """
    Quick creation of SmartTaskManager from natural language

    Example:
        >>> from src.wrapper.smart_task_manager import create_smart_task_manager
        >>> tm = create_smart_task_manager(
        ...     "travel niche, 30 likes per day, safe mode",
        ...     username="my_account"
        ... )
        >>> tm.run_with_plan()
    """
    return SmartTaskManager.from_prompt(prompt, username, **kwargs)


if __name__ == "__main__":
    import sys

    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set")
        print("\nSet it in .env file or export:")
        print("  export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    # Test: Create from prompt
    print("=" * 60)
    print("SmartTaskManager Test")
    print("=" * 60)

    try:
        tm = SmartTaskManager.from_prompt(
            "Grow travel account, safe mode, 30 likes per day",
            username="test_smart",
            save_config=True
        )
        print("✅ SmartTaskManager created from prompt")
        print(f"   Username: {tm.username}")
        print(f"   Agents enabled: {tm.agents_enabled}")

        # Get intelligent plan
        if tm.agents_enabled:
            print("\n" + "=" * 60)
            print("Getting intelligent plan...")
            print("=" * 60)

            plan = tm.get_intelligent_plan(
                goals={"followers": 50, "timeframe": "1 week"}
            )

            if plan:
                print("✅ Plan generated successfully")
                import json
                print(json.dumps(plan, indent=2, ensure_ascii=False))
            else:
                print("⚠️  Plan generation returned None")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
