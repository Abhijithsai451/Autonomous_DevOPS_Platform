from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.deploy_prompt import deploy_prompt


class DeployAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-deploy-agent", agent_type="deploy_agent")
        self.model = llm_model
        self.prompt = deploy_prompt
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state
    def deploy_node(self, ctx:AgentContext):
        pass