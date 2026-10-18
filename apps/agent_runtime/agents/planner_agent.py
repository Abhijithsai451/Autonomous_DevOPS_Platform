from typing import Any, Dict

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.prompts.planner_prompt import planner_prompt


class PlannerAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        self.prompt = planner_prompt
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state

    async def planner_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"==> [Node: planner] Analyzing prompt: '{state.prompt}'")
        output = await self.planner(state)

        # Direct in-place mutation
        state.input_data["tasks"] = output.get("tasks", [
            "Generate backend REST API with healthz check",
            "Generate frontend client UI",
            "Generate Dockerfile and Kubernetes manifests",
        ])
        state.input_data["status"] = "PLANNING_COMPLETED"
        return state


