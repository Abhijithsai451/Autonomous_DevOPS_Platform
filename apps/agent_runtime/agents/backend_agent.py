from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import llm_model


class BackendAgent(BaseAgent):
    def __init__(self, spec_docs: list[str]):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.spec_docs = spec_docs
        self.model = llm_model
    async def run(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state