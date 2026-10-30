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
        self.team : list[BaseAgent] = [
            FrontendAgent(llm_model),
            BackendAgent(llm_model),
            DevopsAgent(llm_model)
        ]
        self.system_prompt = code_orchestrator_prompt.system_prompt

    async def execute(self, state: AgentContext) -> Dict[str, Any]:
        tasks: List[Dict[str, Any]] = state.data.get("tasks", [])
        task_spec: Dict[str, Any] = state.data.get("task_specification", {})

        # Deterministic filtering by layer:
        backend_tasks = [t for t in tasks if t.get("layer") in ("BACKEND", "DATABASE")]
        frontend_tasks = [t for t in tasks if t.get("layer") == "FRONTEND"]
        devops_tasks = [t for t in tasks if t.get("layer") in ("DEVOPS", "INFRASTRUCTURE")]

        dispatch_coros = []
        if backend_tasks:
            dispatch_coros.append(self.backend_agent.generate_code(backend_tasks, task_spec))
        if frontend_tasks:
            dispatch_coros.append(self.frontend_agent.generate_code(frontend_tasks, task_spec))
        if devops_tasks:
            dispatch_coros.append(self.devops_agent.generate_code(devops_tasks, task_spec))

        # Run assigned agents concurrently
        if not dispatch_coros:
            logger.warning("Code Orchestrator: No tasks mapped to coding sub-agents.")
            return {"code_artifacts": {}, "status": "NO_CODING_TASKS"}

        results = await asyncio.gather(*dispatch_coros, return_exceptions=True)

        merged_artifacts = {}
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Coding sub-agent error: {res}")
                continue
            if isinstance(res, dict) and "artifacts" in res:
                for item in res["artifacts"]:
                    filepath = item.get("filepath")
                    if filepath:
                        merged_artifacts[filepath] = item.get("content", "")

        return {
            "code_artifacts": merged_artifacts,
            "status": "CODING_COMPLETED",
        }

    async def code_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("==> [Node: Code Orchestrator] Delegating tasks to coding specialists...")
        output = await self.execute(state)

        current_artifacts = state.data.setdefault("code_artifacts", {})
        current_artifacts.update(output.get("code_artifacts", {}))
        state.data["status"] = output.get("status", "CODING_COMPLETED")

        logger.info(f"==> [Node: Code Orchestrator] Generated {len(current_artifacts)} files across all specialists.")
        return state


