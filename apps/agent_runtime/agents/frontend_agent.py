from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import llm_model
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import frontend_prompt


class FrontendAgent(BaseAgent):
    def __init__(self, spec_docs: list[str]):
        super().__init__(agent_name="code-frontend-agent", agent_type="frontend_agent")
        self.spec_docs = spec_docs
        self.model = llm_model
        self.prompt = frontend_prompt
    async def run(self, state: AgentContext)-> Dict[str, Any]:
        return {
            "code_artifacts": {
                "client/index.html": "<!DOCTYPE html><html><body><h1>XYZ App</h1></body></html>"
            }
        }