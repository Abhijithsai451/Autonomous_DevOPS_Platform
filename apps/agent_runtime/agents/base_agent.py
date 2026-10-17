from abc import ABC, abstractmethod
from typing import Dict, Any

from openai import api_key

from apps.agent_runtime.domain.agent_contract import AgentContext, AgentResult


class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.model = LLMConfig(model_name= model_name, api_key= api_key)
    @abstractmethod
    async def run(self, state: AgentContext) -> Dict[str, Any]:
        """Core execution logic returning state updates."""
        pass

    async def __call__(self, state: AgentContext) -> Dict[str, Any]:
        """Enables passing the agent instance directly into LangGraph nodes."""
        return await self.run(state)
