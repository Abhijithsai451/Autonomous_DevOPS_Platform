import asyncio
from typing import Dict, Any

from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

from apps.agent_runtime.agents.backend_agent import BackendAgent
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.agents.devops_agent import DevopsAgent
from apps.agent_runtime.agents.frontend_agent import FrontendAgent
from apps.agent_runtime.domain.agent_contract import AgentContext


class CodeOrchestratorAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-code-orchestrator", agent_type="code_orchestrator")
        self.llm = llm_model
        self.team : list[BaseAgent] = [
            FrontendAgent(llm_model),
            BackendAgent(llm_model),
            DevopsAgent(llm_model)
        ]

    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        results = await asyncio.gather(*(agent.execute(state) for agent in self.team))
        """
        merged_artifacts = {}
        for res in results:
            merged_artifacts.update(res.get("code_artifacts", {}))
        """
        return {
            "code_artifacts": "merged_artifacts",
            "status": "TEAM_CODING_COMPLETED",
        }

    async def code_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("==> [Node: code_orchestrator] Executing coding agents team (Frontend, Backend, DevOps)...")
        output = await self.execute(state)
        """
        new_artifacts = output.get("code_artifacts", {})

        logger.info(f"==> [Node: code_orchestrator] Generated files: {list(new_artifacts.keys())}")

        # Direct in-place update of code_artifacts
        current_artifacts = state.input_data.setdefault("code_artifacts", {})
        current_artifacts.update(new_artifacts)
        state.input_data["status"] = output.get("status", "CODING_COMPLETED")
        """
        return state


