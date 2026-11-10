from typing import Dict, Any

from langgraph.types import Send

from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext

class CodeOrchestratorAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-code-orchestrator", agent_type="code_orchestrator")
        self.llm = llm_model
        self.system_prompt = None

    async def execute(self, state: AgentContext) -> Dict[str, Any]:
        return {}

    async def code_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Code Orchestrator] Delegating tasks to coding specialists...")
        tasks = state.data.get("tasks",[])
        if not tasks:
            logger.warning("[Node: Code Orchestrator] No tasks retrieved from the State")
            state.data["code_orchestration_status"] = "FAILED"
            return state

        pending_tasks = [
            t for t in tasks
            if t.get("status") in ["PENDING", "FAILED", "UNVERIFIED"] or not t.get("status")
        ]

        if not pending_tasks:
            logger.info("[Node: Code Orchestrator] All tasks are already completed and verified.")
            state.data["code_orchestration_status"] = "VERIFIED"
            state.data["backend_tasks"] = []
            state.data["frontend_tasks"] = []
            state.data["devops_tasks"] = []
            return state

        # Group pending tasks by layer (Step 3 requirement)
        state.data["backend_tasks"] = [t for t in pending_tasks if str(t.get("layer", "")).upper() in ["BACKEND", "DATABASE"]]
        state.data["frontend_tasks"] = [t for t in pending_tasks if str(t.get("layer", "")).upper() == "FRONTEND"]
        state.data["devops_tasks"] = [t for t in pending_tasks if str(t.get("layer", "")).upper() == "DEVOPS"]
        state.data["code_orchestration_status"] = "PENDING"

        return state

    def _route_after_code_orch(self, state: AgentContext)-> str:
        data = state.data
        status = data.get("code_orchestration_status")
        max_iterations = 3

        if data.get("code_orchestration_iterations",0)> max_iterations:
            logger.warning("[Node: Code Orchestrator] Max iterations reached. Breaking loop and routing to reviewer.")
            return "verified"

        if status == "VERIFIED":
            return "verified"

        pending_backend = data.get("backend_tasks", [])
        pending_frontend = data.get("frontend_tasks", [])
        pending_devops = data.get("devops_tasks", [])

        routes = []

        if pending_backend:
            routes.append(Send("backend_agent", state))
        if pending_frontend:
            routes.append(Send("frontend_agent", state))
        if pending_devops:
            routes.append(Send("devops_agent", state))

        if not routes:
            logger.info("[Node: Code Orchestrator] No pending tasks remain. Routing to review agent.")
            return "verified"

        return routes