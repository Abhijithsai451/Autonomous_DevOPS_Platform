from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
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
                          if t.get("status") in ["PENDING", "FAILED", "UNVERIFIED"] or not t.get("status")]

        if not pending_tasks:
            logger.info("[Node: Code Orchestrator] All tasks are already completed and verified.")
            state.data["code_orchestration_status"] = "VERIFIED"
            return state

        layers_with_work = {str(t.get("layer", "")).upper() for t in pending_tasks}

        state.data["layers_pending"] = list(layers_with_work)
        state.data["code_orchestration_status"] = "PENDING"
        return state

    def _route_after_code_orch(self, state: AgentContext)-> str:
        status = state.data.get("code_orchestration_status", "PENDING").upper()

        if status == "VERIFIED":
            return "verified"

        pending_layers = state.data.get("layers_pending", [])

        if any("BACKEND" in l or "DATABASE" in l for l in pending_layers):
            return "backend_agent"
        elif any("FRONTEND" in l for l in pending_layers):
            return "frontend_agent"
        elif any("DEVOPS" in l or "INFRA" in l for l in pending_layers):
            return "devops_agent"

        return "verified"
