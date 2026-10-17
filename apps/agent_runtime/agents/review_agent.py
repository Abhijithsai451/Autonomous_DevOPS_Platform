from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.review_prompt import review_prompt


class ReviewAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="code-review-agent", agent_type="review_agent")
        self.model = llm_model
        self.prompt = review_prompt
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state

    def review_node(self, ctx:AgentContext):
        pass