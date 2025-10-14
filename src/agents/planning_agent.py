"""
Planning Agent
계정 통계를 분석하여 최적의 작업 계획을 수립하는 AI 에이전트
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

try:
    from agents import Agent
except ImportError:
    Agent = None


class PlanningAgent:
    """
    Instagram 계정 통계를 분석하여 최적의 작업 계획을 생성하는 에이전트
    
    Features:
    - 과거 성과 분석
    - 목표 기반 작업 계획
    - 안전 제한 준수
    - 최적 시간대 추천
    """
    
    def __init__(self, db_handler=None, api_key: Optional[str] = None):
        """
        PlanningAgent 초기화
        
        Args:
            db_handler: DatabaseHandler 인스턴스
            api_key: OpenAI API key
        """
        if Agent is None:
            raise ImportError("openai-agents required")
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY required")
        
        self.db = db_handler
        
        # Agent 생성
        self.agent = Agent(
            name="TaskPlanner",
            model="gpt-4o-mini",
            instructions=self._get_instructions()
        )
        
        # Tools 등록
        if self.db:
            self._register_tools()
    
    def _get_instructions(self) -> str:
        """에이전트 지시사항"""
        return """
You are an expert Instagram growth strategist and task planner.

Your role:
1. Analyze account performance data
2. Create optimal daily/weekly engagement plans
3. Ensure safety (avoid bans/blocks)
4. Recommend best times and targets

SAFETY RULES:
- Never exceed Instagram's daily limits
- Gradual increase only (10-20% per week)
- Account age matters:
  * New (0-2 weeks): 20-30 likes, 10-15 follows/day
  * Growing (2-8 weeks): 30-50 likes, 15-25 follows/day
  * Established (8+ weeks): 40-80 likes, 25-40 follows/day

ANALYSIS APPROACH:
1. Review recent session data (likes, follows, errors)
2. Calculate success rate and engagement patterns
3. Identify best-performing hashtags/times
4. Detect warning signs (errors, blocks)

OUTPUT FORMAT:
```json
{
  "plan": {
    "daily_likes": 35,
    "daily_follows": 20,
    "recommended_hashtags": ["travel", "photography"],
    "best_times": ["09:00-11:00", "15:00-17:00"],
    "speed_multiplier": 1.8
  },
  "reasoning": "Based on 85% success rate in recent sessions...",
  "warnings": ["Slight increase in errors, recommend slower pace"],
  "confidence": 0.85
}
```

Use available tools to get account statistics, then provide recommendations.
"""
    
    def _register_tools(self):
        """DB 조회 도구 등록"""
        
        @self.agent.tool
        def get_recent_sessions(username: str, limit: int = 10) -> List[Dict]:
            """
            Get recent session statistics for the account.
            
            Args:
                username: Instagram account username
                limit: Number of recent sessions to retrieve
            
            Returns:
                List of session dictionaries with stats
            """
            if not self.db:
                return []
            try:
                sessions = self.db.get_recent_sessions(username, limit)
                return sessions
            except Exception as e:
                return [{"error": str(e)}]
        
        @self.agent.tool
        def calculate_success_rate(username: str, days: int = 7) -> Dict:
            """
            Calculate success rate and performance metrics.
            
            Args:
                username: Account username
                days: Number of days to analyze
            
            Returns:
                Dictionary with success rate and metrics
            """
            if not self.db:
                return {"error": "Database not available"}
            
            try:
                sessions = self.db.get_recent_sessions(username, limit=50)
                
                if not sessions:
                    return {"success_rate": 0, "total_sessions": 0}
                
                # 기간 필터링
                cutoff = datetime.now() - timedelta(days=days)
                recent = [
                    s for s in sessions
                    if s.get('start_time') and s['start_time'] > cutoff
                ]
                
                total = len(recent)
                completed = sum(1 for s in recent if s.get('status') == 'completed')
                
                total_likes = sum(s.get('total_likes', 0) for s in recent)
                total_follows = sum(s.get('total_follows', 0) for s in recent)
                total_errors = sum(s.get('errors', 0) for s in recent)
                
                return {
                    "success_rate": completed / total if total > 0 else 0,
                    "total_sessions": total,
                    "avg_likes_per_session": total_likes / total if total > 0 else 0,
                    "avg_follows_per_session": total_follows / total if total > 0 else 0,
                    "error_rate": total_errors / total if total > 0 else 0,
                    "period_days": days
                }
            except Exception as e:
                return {"error": str(e)}
    
    def plan_daily_tasks(
        self,
        username: str,
        goals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        오늘의 작업 계획 수립
        
        Args:
            username: 계정명
            goals: 목표 (예: {"followers": 100, "timeframe": "1 week"})
        
        Returns:
            작업 계획 및 추천사항
        """
        from agents import Runner
        
        goals = goals or {}
        
        prompt = f"""
Analyze account '{username}' and create today's optimal task plan.

Goals: {goals if goals else "General growth and engagement"}

Steps:
1. Use get_recent_sessions to retrieve recent performance
2. Use calculate_success_rate to analyze success patterns
3. Based on data, recommend:
   - Daily like/follow targets
   - Best hashtags
   - Optimal times
   - Safety measures

Provide a complete JSON plan.
"""
        
        result = Runner.run_sync(
            starting_agent=self.agent,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 응답 파싱
        response = result.messages[-1]["content"]
        
        # JSON 추출
        import json
        import re
        
        # JSON 블록 찾기
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            plan_json = json.loads(json_match.group(1))
        else:
            # JSON만 있는 경우
            try:
                plan_json = json.loads(response)
            except:
                plan_json = {
                    "plan": {"error": "Failed to parse response"},
                    "raw_response": response
                }
        
        return plan_json


if __name__ == "__main__":
    # 테스트
    print("PlanningAgent test")
    print("Note: Requires OPENAI_API_KEY environment variable")
    
    try:
        agent = PlanningAgent()
        plan = agent.plan_daily_tasks("test_account")
        print("\nGenerated plan:")
        import json
        print(json.dumps(plan, indent=2))
    except Exception as e:
        print(f"Error: {e}")
