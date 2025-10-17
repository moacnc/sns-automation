"""
Multi-Agent System for Gemini Browser UI

This package contains specialized agents:
- SearchAgent: Google Search Grounding for web searches
- OrchestratorAgent: Task planning and agent coordination
- ComputerUseAgent: Browser automation and interaction
"""

from .search_agent import SearchAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = ['SearchAgent', 'OrchestratorAgent']
