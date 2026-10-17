from typing import Any, Dict

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.llm_config import llm_model


class PlannerAgent(BaseAgent):
    def __init__(self, spec_docs: list[str]):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.spec_docs = spec_docs
        self.model = llm_model
    async def run(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state



