import asyncio
from typing import Dict, Any

from cryptography.hazmat.backends.openssl.backend import Backend

from apps.agent_runtime.agents.backend_agent import BackendAgent
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.agents.devops_agent import DevopsAgent
from apps.agent_runtime.agents.frontend_agent import FrontendAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import llm_model


class CodeOrchestratorAgent(BaseAgent):
    def __init__(self, spec_docs: list[str]):
        super().__init__(agent_name="system-code-orchestrator", agent_type="code_orchestrator")
        self.spec_docs = spec_docs
        self.team : list[BaseAgent] = [
            FrontendAgent,
            BackendAgent,
            DevopsAgent
        ]
    async def run(self, state: AgentContext)-> Dict[str, Any]:
        results = await asyncio.gather(*(agent.run(state) for agent in self.team))
        merged_artifacts = {}
        for res in results:
            merged_artifacts.update(res.get("code_artifacts", {}))

        return {
            "code_artifacts": merged_artifacts,
            "status": "TEAM_CODING_COMPLETED",
        }