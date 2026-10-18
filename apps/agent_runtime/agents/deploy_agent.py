from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
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

    async def deploy_node(self, state: AgentContext) -> AgentContext:
        logger.info("==> [Node: deployer] Deploying code and manifests...")
        await self.deployer(state)

        # Direct in-place mutations
        state.input_data["github_repo_url"] = f"https://github.com/my-org/project-{state.task_id[:6]}"
        state.input_data["deployment_url"] = f"https://app-{state.task_id[:6]}.cluster.internal"
        state.input_data["monitoring_url"] = f"https://grafana.internal/d/system?app={state.task_id[:6]}"
        state.input_data["status"] = "DEPLOYED"
        return state