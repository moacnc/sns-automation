"""
Configuration Generator Agent
자연어 입력을 GramAddict YAML 설정으로 변환하는 AI 에이전트
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from agents import Agent
except ImportError:
    print("Warning: openai-agents not installed. Install with: pip install openai-agents")
    Agent = None


class ConfigGeneratorAgent:
    """
    자연어 프롬프트를 GramAddict YAML 설정으로 변환하는 에이전트
    
    Example:
        agent = ConfigGeneratorAgent()
        config = agent.generate(
            "I want to grow my travel Instagram. "
            "Target 100 followers this week. Safe approach."
        )
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        ConfigGeneratorAgent 초기화
        
        Args:
            api_key: OpenAI API key (None이면 환경변수에서 로드)
        """
        if Agent is None:
            raise ImportError(
                "openai-agents is required. Install with: pip install openai-agents"
            )
        
        # API key 설정
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif not os.getenv('OPENAI_API_KEY'):
            raise ValueError(
                "OPENAI_API_KEY must be set in environment or passed as argument"
            )
        
        # Agent 생성
        self.agent = Agent(
            name="ConfigGenerator",
            model="gpt-4o-mini",
            instructions=self._get_instructions()
        )
    
    def _get_instructions(self) -> str:
        """에이전트에 대한 상세 지시사항"""
        return """
You are an expert Instagram automation configuration generator.
Your task is to convert natural language requirements into valid GramAddict YAML configuration.

RULES AND GUIDELINES:

1. SAFETY FIRST - Conservative limits:
   - New accounts: 20-30 likes/day, 10-15 follows/day
   - Established accounts: 40-60 likes/day, 25-35 follows/day
   - Always use speed-multiplier 1.5-2.0 (slower = safer)

2. YAML FORMAT - Must include:
   ```yaml
   username: account_name
   device: DEVICE_ID  # Optional, comment out if not specified
   
   hashtag-posts-recent: hashtag1 hashtag2 hashtag3
   
   total-interactions-limit: 30-50
   total-likes-limit: 20-30
   total-follows-limit: 10-15
   
   likes-count: 1-2
   follow-percentage: 20-30
   
   speed-multiplier: 1.5
   
   # Optional filters
   # min-followers: 100
   # max-followers: 5000
   ```

3. WORKING HOURS:
   - Avoid 00:00-07:00 (suspicious)
   - Spread activity across day: 09:00-12:00, 14:00-17:00, 19:00-22:00

4. HASHTAG SELECTION:
   - Based on user's niche/goals
   - Mix of popular and specific tags
   - 3-5 hashtags recommended

5. RESPONSE FORMAT:
   - Return ONLY valid YAML
   - Include helpful comments
   - Use conservative values if unclear

EXAMPLE USER REQUEST:
"I want to grow my travel blog Instagram. Get 50 followers this week. Be safe."

EXAMPLE RESPONSE:
```yaml
# Travel niche growth configuration - Safe mode
username: travel_account
# device: R3CN70D9ZBY  # Set your device ID

# Hashtags for travel niche
hashtag-posts-recent: travel photography wanderlust travelblogger adventure

# Conservative daily limits (safe for account)
total-interactions-limit: 40-50
total-likes-limit: 30-40
total-follows-limit: 15-20

# Engagement settings
likes-count: 1-2
follow-percentage: 25
speed-multiplier: 1.8

# Optional: Target quality accounts
# min-followers: 100
# max-followers: 5000
# min-posts: 5

debug: false
```

Now, convert the user's request into YAML configuration.
Only output the YAML, no additional text.
"""
    
    def generate(self, prompt: str, username: str = "my_account") -> Dict[str, Any]:
        """
        자연어 프롬프트를 YAML 설정으로 변환
        
        Args:
            prompt: 사용자의 자연어 요청
            username: Instagram 계정명
        
        Returns:
            Dictionary with configuration
        
        Example:
            >>> agent = ConfigGeneratorAgent()
            >>> config = agent.generate(
            ...     "Focus on foodie niche, 30 likes per day, very safe",
            ...     username="foodie_account"
            ... )
        """
        from agents import Runner
        
        # 프롬프트 생성
        full_prompt = f"""
User request: {prompt}
Account username: {username}

Generate GramAddict YAML configuration.
"""
        
        # Agent 실행
        result = Runner.run_sync(
            starting_agent=self.agent,
            context_variables={"username": username},
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        # YAML 파싱
        yaml_text = result.messages[-1]["content"]
        
        # 코드 블록 제거 (```yaml ... ```)
        if "```" in yaml_text:
            lines = yaml_text.split("\n")
            yaml_lines = []
            in_code_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (not yaml_lines and not in_code_block):
                    yaml_lines.append(line)
            yaml_text = "\n".join(yaml_lines)
        
        # YAML 파싱
        try:
            config_dict = yaml.safe_load(yaml_text)
            return config_dict
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse generated YAML: {e}\n\nGenerated text:\n{yaml_text}")
    
    def generate_and_save(
        self,
        prompt: str,
        username: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        설정 생성 후 파일로 저장
        
        Args:
            prompt: 사용자 요청
            username: 계정명
            output_path: 저장 경로 (None이면 자동 생성)
        
        Returns:
            Path to saved configuration file
        """
        config = self.generate(prompt, username)
        
        if output_path is None:
            output_path = Path(f"config/accounts/{username}_generated.yml")
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        
        return output_path


# CLI 사용 예시
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.agents.config_agent <prompt> [username]")
        print("\nExample:")
        print('  python -m src.agents.config_agent "grow travel account, 50 followers/week" travel_account')
        sys.exit(1)
    
    prompt = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "my_account"
    
    try:
        agent = ConfigGeneratorAgent()
        config_path = agent.generate_and_save(prompt, username)
        print(f"✅ Configuration generated: {config_path}")
        print("\nGenerated config:")
        with open(config_path) as f:
            print(f.read())
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
