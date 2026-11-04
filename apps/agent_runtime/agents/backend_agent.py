from pathlib import Path
from typing import Dict, Any
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

SANDBOX_DIR = Path("/tmp/agent_sandbox")

class BackendAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.model = llm_model
        self.prompt = None

    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        return {}

    def backend_node(self, state:AgentContext):
        logger.info("[Node: Backend Agent] Starting backend task implementation...")

        backend_tasks = state.data.get("backend_tasks", [])
        if not backend_tasks:
            logger.warning("[Node: Backend Agent] No backend tasks found in state.")
            return state

        if "codebase" not in state.data:
            state.data["codebase"] = {}

        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

        return state