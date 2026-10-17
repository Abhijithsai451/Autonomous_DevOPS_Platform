from abc import ABC, abstractmethod
from typing import Dict, Any

from openai import api_key

from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import LLMClient
from packages.tracing.spans import start_agent_span


class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.model = LLMClient(model_name= "gpt-4o-mini", api_key= api_key)

    @abstractmethod
    async def execute(self, ctx: AgentContext) -> Dict[str, Any]:
        """Execute agent task using AgentContext and return state delta."""
        pass

    async def __call__(self, ctx: AgentContext) -> Dict[str, Any]:
        """Telemetry-wrapped invocation."""
        with start_agent_span(
                name=f"agent.run.{self.agent_type}",
                attributes={
                    "agent.name": self.agent_name,
                    "agent.type": self.agent_type,
                    "agent.task_id": ctx.task_id,
                    "agent.run_id": ctx.run_id,
                },
        ):
            return await self.execute(ctx)
