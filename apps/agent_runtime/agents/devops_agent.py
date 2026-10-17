from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import llm_model
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import devops_prompt


class DevopsAgent(BaseAgent):
    def __init__(self, spec_docs: list[str]):
        super().__init__(agent_name="code-devops-agent", agent_type="devops_agent")
        self.spec_docs = spec_docs
        self.model = llm_model
        self.prompt = devops_prompt
    async def run(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state