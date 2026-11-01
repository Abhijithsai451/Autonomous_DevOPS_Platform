from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger


class BackendAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.model = llm_model
        self.prompt = None
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        return {}

    def backend_node(self, state:AgentContext):
        tasks = state.data.get("tasks", [])
        backend_tasks = tasks.layer.get("BACKEND" or "DATABASE")
        logger.info(f"[Node: Backend Agent] Found {len(backend_tasks)} Backend and Database tasks to process.")
        return state