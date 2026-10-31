from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext


class FrontendAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-frontend-agent", agent_type="frontend_agent")
        self.model = llm_model
        self.prompt = None
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        return {}

    def frontend_node(self, ctx:AgentContext):
        pass