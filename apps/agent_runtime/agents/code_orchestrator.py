import asyncio
from typing import Dict, Any, List

from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

from apps.agent_runtime.agents.backend_agent import BackendAgent
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.agents.devops_agent import DevopsAgent
from apps.agent_runtime.agents.frontend_agent import FrontendAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts import code_orchestrator_prompt

class CodeOrchestratorAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-code-orchestrator", agent_type="code_orchestrator")
        self.llm = llm_model
        self.system_prompt = code_orchestrator_prompt.code_orch_system_prompt

    async def execute(self, state: AgentContext) -> Dict[str, Any]:
        return {}

    async def code_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Code Orchestrator] Delegating tasks to coding specialists...")
        tasks = state.data.get("tasks",[])
        if not tasks:
            logger.warning("[Node: Code Orchestrator] No tasks retrieved from the State")
            state.data["code_orchestration_status"] = "FAILED"
            return state
        pending_tasks = [ t for t in tasks
                          if t.get("status") in [None, "PENDING", "FAILED", "UNVERIFIED"] or not t.get("status")]

        if not pending_tasks:
            logger.info("==> [Node: Code Orchestrator] All tasks are already completed and verified.")
            state.data["code_status"] = "VERIFIED"
            return state

        logger.info(f"[Node: Code Orchestrator] Found {len(pending_tasks)} pending/failed tasks to process.")
        return state

    def _route_after_code_orch(self, route)-> str:
        if route == "PENDING":
            return "pending"
        elif route == "UNVERIFIED":
            return "unverified"
        elif route == "VERIFIED":
            return "verified"

